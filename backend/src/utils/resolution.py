# ── Resolution and aspect ratio helpers ─────────────────────────────────────────
# Provides lookup tables and utilities for mapping between aspect ratios, orientation,
# quality presets, and exact pixel dimensions for FFmpeg operations.

from typing import TypedDict


class ResolutionDimensions(TypedDict):
    width: int
    height: int


# Default preset used when orientation is specified but resolution is not.
DEFAULT_PRESET = "1080p"

# Maps (aspect_ratio, preset) → exact pixel dimensions.
LOOKUP_TABLE: dict[tuple[str, str], ResolutionDimensions] = {
    # 360p
    ("16:9", "360p"): ResolutionDimensions(width=640, height=360),
    ("9:16", "360p"): ResolutionDimensions(width=360, height=640),
    ("1:1", "360p"): ResolutionDimensions(width=360, height=360),
    # 480p
    ("16:9", "480p"): ResolutionDimensions(width=854, height=480),
    ("9:16", "480p"): ResolutionDimensions(width=480, height=854),
    ("1:1", "480p"): ResolutionDimensions(width=480, height=480),
    # 720p
    ("16:9", "720p"): ResolutionDimensions(width=1280, height=720),
    ("9:16", "720p"): ResolutionDimensions(width=720, height=1280),
    ("1:1", "720p"): ResolutionDimensions(width=720, height=720),
    # 1080p
    ("16:9", "1080p"): ResolutionDimensions(width=1920, height=1080),
    ("9:16", "1080p"): ResolutionDimensions(width=1080, height=1920),
    ("1:1", "1080p"): ResolutionDimensions(width=1080, height=1080),
    # 1440p
    ("16:9", "1440p"): ResolutionDimensions(width=2560, height=1440),
    ("9:16", "1440p"): ResolutionDimensions(width=1440, height=2560),
    ("1:1", "1440p"): ResolutionDimensions(width=1440, height=1440),
    # 4k
    ("16:9", "4k"): ResolutionDimensions(width=3840, height=2160),
    ("9:16", "4k"): ResolutionDimensions(width=2160, height=3840),
    ("1:1", "4k"): ResolutionDimensions(width=2160, height=2160),
}


def derive_aspect_ratio(width: int, height: int) -> str:
    """Derive the aspect ratio string from raw pixel dimensions.

    Compares the width/height ratio against standard ratios using a tolerance
    threshold to account for rounding. Returns '16:9', '9:16', '1:1', or
    raises ValueError if the ratio does not match any known aspect ratio.
    """
    if width <= 0 or height <= 0:
        raise ValueError(f"Invalid dimensions: {width}x{height}")

    ratio = width / height

    # Use tolerance for floating-point comparison.
    tolerance = 0.02

    candidates = {
        "16:9": 16 / 9,
        "9:16": 9 / 16,
        "1:1": 1.0,
    }

    for ar, expected in candidates.items():
        if abs(ratio - expected) < tolerance:
            return ar

    raise ValueError(
        f"Cannot derive aspect ratio from {width}x{height}: "
        f"ratio={ratio:.3f}. Known ratios: 16:9, 9:16, 1:1"
    )


def derive_orientation(width: int, height: int) -> str:
    """Derive the orientation from raw pixel dimensions.

    Returns 'landscape' if width > height, 'portrait' if height > width,
    'square' if width == height.
    """
    if width > height:
        return "landscape"
    if height > width:
        return "portrait"
    return "square"


def get_resolution_preset(width: int, height: int) -> str:
    """Determine the quality preset string from raw pixel dimensions.

    Returns the closest matching preset string ('360p', '480p', '720p', '1080p', '1440p', '4k')
    based on the shorter edge. Raises ValueError if dimensions are below 360p threshold.
    """
    shorter_edge = min(width, height)

    preset_thresholds = [
        (2160, "4k"),
        (1440, "1440p"),
        (1080, "1080p"),
        (720, "720p"),
        (480, "480p"),
        (360, "360p"),
    ]

    for threshold, preset in preset_thresholds:
        if shorter_edge >= threshold:
            return preset

    raise ValueError(
        f"Cannot determine preset for {width}x{height}: "
        f"shorter edge ({shorter_edge}) is below 360p threshold"
    )


def get_dimensions(aspect_ratio: str, preset: str) -> ResolutionDimensions:
    """Look up exact pixel dimensions for a given aspect ratio and quality preset.

    Raises KeyError if the (aspect_ratio, preset) combination is not in the lookup table.
    """
    key = (aspect_ratio, preset)
    if key not in LOOKUP_TABLE:
        raise KeyError(
            f"No dimensions found for aspect_ratio={aspect_ratio!r}, preset={preset!r}. "
            f"Known aspect ratios: 16:9, 9:16, 1:1. Known presets: 360p, 480p, 720p, 1080p, 1440p, 4k."
        )
    return LOOKUP_TABLE[key]


def ensure_even(dimensions: ResolutionDimensions) -> ResolutionDimensions:
    """Floor width and height to even numbers (libx264 requires even dimensions).

    Subtracts 1 from any odd dimension, which always shrinks and guarantees
    the result stays within the target box.
    """
    return ResolutionDimensions(
        width=dimensions["width"] if dimensions["width"] % 2 == 0 else dimensions["width"] - 1,
        height=dimensions["height"] if dimensions["height"] % 2 == 0 else dimensions["height"] - 1,
    )
