# ── Pipeline validation gates ──────────────────────────────────────────
#
# Five sequential gates. If any fails, the request is rejected immediately
# with a clear BadRequest. Nothing proceeds until the current gate passes.
#
#   Gate 1: Schema validation   (Pydantic — CreateJobRequest)
#   Gate 2: Registry lookup     (operation names exist)
#   Gate 3: Param validation    (required, types, enums, bounds)
#   Gate 4: Type compatibility  (source → step 0, step N → step N+1)
#   Gate 5: Pipeline spec       (build enriched spec for DB storage)
# ──────────────────────────────────────────────────────────────────────────

from src.utils.registry import (
    ArtifactType,
    ParamType,
    get_operation,
    operation_exists,
    OperationDefinition,
)
from src.core.exception_base import BadRequest
from src.utils.log import get_logger

logger = get_logger(__name__)


# ── Gate 1: Schema validation ──────────────────────────────────────────
# Handled entirely by Pydantic on CreateJobRequest:
#   - source is an HttpUrl (rejects invalid URLs at 422)
#   - pipeline is list[PipelineOperation] with min_length=1
# If the body is malformed, FastAPI rejects it before any gate runs.
# No additional code needed here.


# ── Gate 2: Registry lookup ────────────────────────────────────────────
def validate_registry(pipeline: list[dict]) -> None:
    """Every operation name must exist in the operation registry.

    Rejects on the first unknown operation with a positional error so the
    client knows exactly which step is wrong.
    """
    for i, step in enumerate(pipeline):
        name = step["operation"]
        if not operation_exists(name):
            # Build the valid-ops string separately so the f-string expression
            # doesn't span multiple lines — Python 3.10's tokenizer chokes on
            # newlines inside a single f"...".
            valid_ops = ', '.join(sorted([
                'trim', 'cut', 'compress', 'transcode', 'resize',
                'watermark', 'subtitle', 'mute',
                'join', 'extract_audio', 'thumbnail', 'gif',
            ]))
            raise BadRequest(
                f"Unknown operation '{name}' at position {i}. "
                f"Valid operations: {valid_ops}"
            )
    logger.debug(f"Gate 2 passed — {len(pipeline)} operation names valid")


# ── Gate 3: Param validation ───────────────────────────────────────────
def _validate_param_value(
    param_name: str,
    value: object,
    definition: "ParamDefinition",
    position: int,
    op_name: str,
) -> None:
    """Validate a single param value against its definition."""
    ctx = f"'{param_name}' for '{op_name}' at position {position}"

    if definition.type == ParamType.STRING:
        if not isinstance(value, str):
            raise BadRequest(f"Param {ctx} must be a string")

    elif definition.type == ParamType.ENUM:
        if value not in definition.values:
            allowed = ", ".join(definition.values)
            raise BadRequest(
                f"Param {ctx} got '{value}'. Allowed values: {allowed}"
            )

    elif definition.type == ParamType.INTEGER:
        if not isinstance(value, int) or isinstance(value, bool):
            raise BadRequest(f"Param {ctx} must be an integer")
        if definition.min is not None and value < definition.min:
            raise BadRequest(
                f"Param {ctx} must be >= {definition.min}, got {value}"
            )
        if definition.max is not None and value > definition.max:
            raise BadRequest(
                f"Param {ctx} must be <= {definition.max}, got {value}"
            )

    elif definition.type == ParamType.FLOAT:
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise BadRequest(f"Param {ctx} must be a number")
        if definition.min is not None and value < definition.min:
            raise BadRequest(
                f"Param {ctx} must be >= {definition.min}, got {value}"
            )
        if definition.max is not None and value > definition.max:
            raise BadRequest(
                f"Param {ctx} must be <= {definition.max}, got {value}"
            )

    elif definition.type == ParamType.BOOLEAN:
        if not isinstance(value, bool):
            raise BadRequest(f"Param {ctx} must be true or false")

    elif definition.type == ParamType.URL:
        if not isinstance(value, str):
            raise BadRequest(f"Param {ctx} must be a URL string")

    elif definition.type == ParamType.ARRAY:
        if not isinstance(value, list):
            raise BadRequest(f"Param {ctx} must be an array")
        if definition.min_items is not None and len(value) < definition.min_items:
            raise BadRequest(
                f"Param {ctx} must have at least {definition.min_items} items, "
                f"got {len(value)}"
            )
        if definition.max_items is not None and len(value) > definition.max_items:
            raise BadRequest(
                f"Param {ctx} must have at most {definition.max_items} items, "
                f"got {len(value)}"
            )
        if definition.items is not None:
            for j, item in enumerate(value):
                _validate_param_value(
                    f"{param_name}[{j}]", item, definition.items, position, op_name
                )

    elif definition.type == ParamType.OBJECT:
        if not isinstance(value, dict):
            raise BadRequest(f"Param {ctx} must be an object")


def validate_params(pipeline: list[dict]) -> None:
    """Validate each operation's params against its registry definition.

    Checks performed per param:
    - Required params are present
    - Param type matches the registry definition
    - Enum values are within the allowed set
    - Integer/float values respect min/max bounds
    - Array params respect min_items/max_items and item type
    - Unknown params are rejected (no extra keys allowed)
    """
    for i, step in enumerate(pipeline):
        op_def = get_operation(step["operation"])
        submitted = step.get("params", {})
        op_name = op_def.name

        # Reject unknown params
        for key in submitted:
            if key not in op_def.params:
                raise BadRequest(
                    f"Unknown param '{key}' for '{op_name}' at position {i}"
                )

        # Check required params and validate submitted values
        for name, param_def in op_def.params.items():
            if param_def.required and name not in submitted:
                raise BadRequest(
                    f"Missing required param '{name}' for '{op_name}' at position {i}"
                )

            if name in submitted:
                _validate_param_value(
                    name, submitted[name], param_def, i, op_name
                )
    logger.debug(f"Gate 3 passed — params valid for {len(pipeline)} operations")


# ── Gate 4: Type compatibility validation ────────────────────────────────
def validate_type_compatibility(source_type: str, pipeline: list[dict]) -> None:
    """Walk the pipeline and verify type flow between adjacent steps.

    1.  The source artifact type must match step 0's input_types.
    2.  Each step's output_type must intersect with the next step's input_types.

    Uses operation-level matching — each operation declares what it accepts
    and what it produces. No phase constraints, only data compatibility.
    """
    try:
        current_types = {ArtifactType(source_type)}
    except ValueError:
        raise BadRequest(f"Unknown source type '{source_type}'")

    for i, step in enumerate(pipeline):
        op_def = get_operation(step["operation"])
        op_inputs = set(op_def.input_types)

        if not current_types.intersection(op_inputs):
            current_names = ", ".join(t.value for t in current_types)
            input_names = ", ".join(t.value for t in op_def.input_types)
            raise BadRequest(
                f"Type mismatch at position {i}: "
                f"'{op_def.name}' accepts [{input_names}] "
                f"but previous step produces [{current_names}]"
            )

        current_types = set(op_def.output_type)

    logger.debug(f"Gate 4 passed — type compatibility OK")


# ── Gate 5: Pipeline spec construction ───────────────────────────────────
def build_pipeline_spec(pipeline: list[dict]) -> list[dict]:
    """All gates passed — build the enriched pipeline spec for DB storage.

    Each step is annotated with category, capability, input_types, and
    output_type from the registry so downstream consumers (dispatch, workers)
    can operate without re-querying the registry.
    """
    spec = []
    for step in pipeline:
        op_def = get_operation(step["operation"])
        spec.append({
            "operation": step["operation"],
            "category": op_def.category.value,
            "capability": op_def.capability.value,
            "input_types": [t.value for t in op_def.input_types],
            "output_type": [t.value for t in op_def.output_type],
            "params": step.get("params", {}),
        })
    logger.info(f"Gate 5 — built enriched spec with {len(spec)} steps: {[s['operation'] for s in spec]}")
    return spec


# ── Orchestrator ─────────────────────────────────────────────────────────
def validate_and_build_pipeline(
    source: str, #already validated by pydantic 
    source_type: str,
    pipeline: list[dict],
) -> list[dict]:
    """Run all five gates in sequence.

    Args:
        source:       Source URL string (already validated as HttpUrl by Pydantic).
        source_type:  "video" or "audio" — the type of the source artifact.
        pipeline:     List of {operation, params} dicts from the request body.

    Returns:
        The enriched pipeline spec (list of dicts) ready for DB storage.

    Raises:
        BadRequest on the first validation failure, with a message that
        identifies exactly what failed and where.
    """
    # Gate 1: Schema — handled by Pydantic on CreateJobRequest

    try:
        # Gate 2: Registry
        validate_registry(pipeline)

        # Gate 3: Params
        validate_params(pipeline)

        # Gate 4: Type compatibility
        validate_type_compatibility(source_type, pipeline)

        # Gate 5: Build spec
        return build_pipeline_spec(pipeline)

    except BadRequest:
        raise
    except Exception as e:
        logger.error(f"Unexpected validation error: {e}")
        raise BadRequest("Unexpected validation error")
