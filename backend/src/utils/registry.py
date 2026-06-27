# Hardcoded catalog of all 12 operations with param schemas, categories, capabilities, and input/output types.
# Source of truth for validation gates (registry lookup, param validation, type compatibility).
# Not stored in the DB — changes require a deploy.

from enum import Enum
from typing import Optional, Union
from dataclasses import dataclass, field


class ArtifactType(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    GIF = "gif"


class OperationCategory(str, Enum):
    TRANSFORMATIVE = "transformative"
    COMBINATORY = "combinatory"
    CONVERSION = "conversion"


class OperationCapability(str, Enum):
    TRANSFORM = "transform"
    EXTRACT = "extract"
    COMBINE = "combine"
    ANALYZE = "analyze"
    GENERATE = "generate"


class ParamType(str, Enum):
    STRING = "string"
    ENUM = "enum"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    URL = "url"
    OBJECT = "object"


@dataclass
class ParamDefinition:
    type: ParamType
    required: bool
    default: Optional[Union[str, int, float, bool, list]] = None
    values: Optional[list[str]] = None       # for enum type only
    min: Optional[Union[int, float]] = None  # for integer/float only
    max: Optional[Union[int, float]] = None  # for integer/float only
    items: Optional["ParamDefinition"] = None  # for array type only
    min_items: Optional[int] = None          # for array type only
    max_items: Optional[int] = None          # for array type only


@dataclass
class OperationDefinition:
    name: str
    category: OperationCategory
    capability: OperationCapability
    input_types: list[ArtifactType]
    output_type: list[ArtifactType]  # list because polymorphic ops produce matching type
    params: dict[str, ParamDefinition] = field(default_factory=dict)


REGISTRY: dict[str, OperationDefinition] = {

    # -------------------------------------------------------------------------
    # TRANSFORMATIVE  |  Capability: TRANSFORM
    # Take one input artifact, produce one output artifact. Pipeline continues.
    # -------------------------------------------------------------------------

    "trim": OperationDefinition(
        name="trim",
        category=OperationCategory.TRANSFORMATIVE,
        capability=OperationCapability.TRANSFORM,
        input_types=[ArtifactType.VIDEO, ArtifactType.AUDIO],
        output_type=[ArtifactType.VIDEO, ArtifactType.AUDIO],  # mirrors input type
        params={
            "start": ParamDefinition(
                type=ParamType.FLOAT,
                required=True,
                min=0.0,
            ),
            "end": ParamDefinition(
                type=ParamType.FLOAT,
                required=True,
                min=0.0,
            ),
        },
    ),

    "cut": OperationDefinition(
        name="cut",
        category=OperationCategory.TRANSFORMATIVE,
        capability=OperationCapability.TRANSFORM,
        input_types=[ArtifactType.VIDEO, ArtifactType.AUDIO],
        output_type=[ArtifactType.VIDEO, ArtifactType.AUDIO],
        params={
            "segments": ParamDefinition(
                type=ParamType.ARRAY,
                required=True,
                items=ParamDefinition(type=ParamType.OBJECT, required=True),
                min_items=1,
                max_items=50,
            ),
        },
    ),

    "compress": OperationDefinition(
        name="compress",
        category=OperationCategory.TRANSFORMATIVE,
        capability=OperationCapability.TRANSFORM,
        input_types=[ArtifactType.VIDEO, ArtifactType.AUDIO],
        output_type=[ArtifactType.VIDEO, ArtifactType.AUDIO],
        params={
            "quality": ParamDefinition(
                type=ParamType.ENUM,
                required=False,
                default="medium",
                values=["low", "medium", "high"],
            ),
        },
    ),

    "transcode": OperationDefinition(
        name="transcode",
        category=OperationCategory.TRANSFORMATIVE,
        capability=OperationCapability.TRANSFORM,
        input_types=[ArtifactType.VIDEO],
        output_type=[ArtifactType.VIDEO],
        params={
            "format": ParamDefinition(
                type=ParamType.ENUM,
                required=True,
                values=["mp4", "webm", "mov"],
            ),
        },
    ),

    "resize": OperationDefinition(
        name="resize",
        category=OperationCategory.TRANSFORMATIVE,
        capability=OperationCapability.TRANSFORM,
        input_types=[ArtifactType.VIDEO],
        output_type=[ArtifactType.VIDEO],
        params={
            "width": ParamDefinition(
                type=ParamType.INTEGER,
                required=False,
                min=1,
                max=7680,
            ),
            "height": ParamDefinition(
                type=ParamType.INTEGER,
                required=False,
                min=1,
                max=4320,
            ),
            "preset": ParamDefinition(
                type=ParamType.ENUM,
                required=False,
                values=["360p", "480p", "720p", "1080p", "4k"],
            ),
        },
    ),

    "watermark": OperationDefinition(
        name="watermark",
        category=OperationCategory.TRANSFORMATIVE,
        capability=OperationCapability.TRANSFORM,
        input_types=[ArtifactType.VIDEO],
        output_type=[ArtifactType.VIDEO],
        params={
            "image_url": ParamDefinition(
                type=ParamType.URL,
                required=True,
            ),
            "position": ParamDefinition(
                type=ParamType.ENUM,
                required=False,
                default="bottom_right",
                values=[
                    "top_left", "top_right",
                    "bottom_left", "bottom_right",
                    "center",
                ],
            ),
        },
    ),

    "subtitle": OperationDefinition(
        name="subtitle",
        category=OperationCategory.TRANSFORMATIVE,
        capability=OperationCapability.TRANSFORM,
        input_types=[ArtifactType.VIDEO],
        output_type=[ArtifactType.VIDEO],
        params={
            "file_url": ParamDefinition(
                type=ParamType.URL,
                required=False,
            ),
            "auto": ParamDefinition(
                type=ParamType.BOOLEAN,
                required=False,
                default=False,
            ),
        },
    ),

    "mute": OperationDefinition(
        name="mute",
        category=OperationCategory.TRANSFORMATIVE,
        capability=OperationCapability.TRANSFORM,
        input_types=[ArtifactType.VIDEO],
        output_type=[ArtifactType.VIDEO],
        params={},
    ),

    # -------------------------------------------------------------------------
    # COMBINATORY  |  Capability: COMBINE
    # Takes multiple input artifacts, produces one output. Pipeline continues.
    # -------------------------------------------------------------------------

    "join": OperationDefinition(
        name="join",
        category=OperationCategory.COMBINATORY,
        capability=OperationCapability.COMBINE,
        input_types=[ArtifactType.VIDEO, ArtifactType.AUDIO],
        output_type=[ArtifactType.VIDEO, ArtifactType.AUDIO],
        params={
            "clips": ParamDefinition(
                type=ParamType.ARRAY,
                required=True,
                items=ParamDefinition(type=ParamType.URL, required=True),
                min_items=2,
                max_items=10,
            ),
        },
    ),

    # -------------------------------------------------------------------------
    # CONVERSION  |  Capability: EXTRACT / GENERATE
    # Changes the asset's media type (e.g. video → audio). Pipeline continues.
    # -------------------------------------------------------------------------

    "extract_audio": OperationDefinition(
        name="extract_audio",
        category=OperationCategory.CONVERSION,
        capability=OperationCapability.EXTRACT,
        input_types=[ArtifactType.VIDEO],
        output_type=[ArtifactType.AUDIO],
        params={
            "format": ParamDefinition(
                type=ParamType.ENUM,
                required=False,
                default="mp3",
                values=["mp3", "aac"],
            ),
        },
    ),

    "thumbnail": OperationDefinition(
        name="thumbnail",
        category=OperationCategory.CONVERSION,
        capability=OperationCapability.EXTRACT,
        input_types=[ArtifactType.VIDEO],
        output_type=[ArtifactType.IMAGE],
        params={
            "timestamp": ParamDefinition(
                type=ParamType.FLOAT,
                required=True,
                min=0.0,
            ),
        },
    ),

    "gif": OperationDefinition(
        name="gif",
        category=OperationCategory.CONVERSION,
        capability=OperationCapability.GENERATE,
        input_types=[ArtifactType.VIDEO],
        output_type=[ArtifactType.GIF],
        params={
            "start": ParamDefinition(
                type=ParamType.FLOAT,
                required=True,
                min=0.0,
            ),
            "end": ParamDefinition(
                type=ParamType.FLOAT,
                required=True,
                min=0.0,
            ),
            "fps": ParamDefinition(
                type=ParamType.INTEGER,
                required=False,
                default=15,
                min=1,
                max=30,
            ),
        },
    ),
}


def get_operation(name: str) -> Optional[OperationDefinition]:
    """Retrieve an operation definition by name. Returns None if not found."""
    return REGISTRY.get(name)


def is_conversion(name: str) -> bool:
    """Check if an operation changes the asset's media type."""
    op = get_operation(name)
    return op is not None and op.category == OperationCategory.CONVERSION


def operation_exists(name: str) -> bool:
    """Check if an operation exists in the registry."""
    return name in REGISTRY


def get_capability(name: str) -> Optional[OperationCapability]:
    """Retrieve the product capability for an operation."""
    op = get_operation(name)
    return op.capability if op else None