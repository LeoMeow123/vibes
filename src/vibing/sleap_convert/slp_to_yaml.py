"""
Convert SLEAP predictions to ROI YAML format.

This module provides tools to extract keypoints from SLEAP files and
convert them to ROI polygon definitions using configurable templates.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np
import yaml

try:
    import sleap_io as sio
except ImportError:
    sio = None


@dataclass
class PolygonDef:
    """Definition for a single ROI polygon."""

    name: str
    corners: list[str]  # Keypoint names for corners [TL, BL, BR, TR]
    color: str = "#808080"


@dataclass
class ROITemplate:
    """Template defining how keypoints map to ROI polygons."""

    name: str
    polygons: list[PolygonDef]
    required_keypoints: list[str] = field(default_factory=list)
    description: str = ""

    def validate(self, keypoints: dict[str, tuple[float, float]]) -> tuple[bool, str]:
        """Check if all required keypoints are present."""
        if not self.required_keypoints:
            # Auto-collect from polygon definitions
            required = set()
            for poly in self.polygons:
                required.update(poly.corners)
            self.required_keypoints = list(required)

        missing = [k for k in self.required_keypoints if k not in keypoints]
        if missing:
            return False, f"Missing {len(missing)} keypoints: {', '.join(missing[:5])}"
        return True, "OK"


# =============================================================================
# Built-in Templates
# =============================================================================

TMAZE_HORIZONTAL = ROITemplate(
    name="tmaze_horizontal",
    description="Horizontal T-maze with 7 regions and corner sharing",
    polygons=[
        PolygonDef(
            name="arm_right",
            corners=[
                "arm_right.top_left",
                "junction.top_left",  # shared
                "junction.top_right",  # shared
                "arm_right.top_right",
            ],
            color="#2ca02c",
        ),
        PolygonDef(
            name="junction",
            corners=[
                "junction.top_left",
                "junction.bottom_left",
                "junction.bottom_right",
                "junction.top_right",
            ],
            color="#98df8a",
        ),
        PolygonDef(
            name="arm_left",
            corners=[
                "junction.bottom_left",  # shared
                "arm_left.bottom_left",
                "arm_left.bottom_right",
                "junction.bottom_right",  # shared
            ],
            color="#d62728",
        ),
        PolygonDef(
            name="segment4",
            corners=[
                "segment4.top_left",
                "segment4.bottom_left",
                "junction.bottom_left",  # shared
                "junction.top_left",  # shared
            ],
            color="#ff9896",
        ),
        PolygonDef(
            name="segment3",
            corners=[
                "segment3.top_left",
                "segment3.bottom_left",
                "segment4.bottom_left",  # shared
                "segment4.top_left",  # shared
            ],
            color="#9467bd",
        ),
        PolygonDef(
            name="segment2",
            corners=[
                "segment2.top_left",
                "segment2.bottom_left",
                "segment3.bottom_left",  # shared
                "segment3.top_left",  # shared
            ],
            color="#c5b0d5",
        ),
        PolygonDef(
            name="segment1",
            corners=[
                "segment1.top_left",
                "segment1.bottom_left",
                "segment2.bottom_left",  # shared
                "segment2.top_left",  # shared
            ],
            color="#8c564b",
        ),
    ],
    required_keypoints=[
        "arm_right.top_left",
        "arm_right.top_right",
        "junction.top_left",
        "junction.top_right",
        "junction.bottom_left",
        "junction.bottom_right",
        "arm_left.bottom_left",
        "arm_left.bottom_right",
        "segment1.top_left",
        "segment1.bottom_left",
        "segment2.top_left",
        "segment2.bottom_left",
        "segment3.top_left",
        "segment3.bottom_left",
        "segment4.top_left",
        "segment4.bottom_left",
    ],
)

# Registry of built-in templates
TEMPLATES = {
    "tmaze_horizontal": TMAZE_HORIZONTAL,
}


# =============================================================================
# Keypoint Extraction
# =============================================================================


def _normalize_name(name: str) -> str:
    """Normalize keypoint name for matching."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _build_name_index(
    names: list[str],
) -> tuple[dict[str, int], dict[str, int]]:
    """Build exact and normalized name -> index mappings."""
    exact = {name: i for i, name in enumerate(names)}
    normalized = {_normalize_name(name): i for i, name in enumerate(names)}
    return exact, normalized


def _lookup_index(
    name: str,
    exact: dict[str, int],
    normalized: dict[str, int],
) -> Optional[int]:
    """Look up keypoint index by name (exact or normalized)."""
    if name in exact:
        return exact[name]
    return normalized.get(_normalize_name(name))


def _get_point_xy(instance, idx: int) -> tuple[float, float]:
    """Extract (x, y) coordinates from a SLEAP instance point."""
    if hasattr(instance, "points"):
        pts = instance.points
        if 0 <= idx < len(pts):
            rec = pts[idx]
            # Try structured array with 'xy' field
            if hasattr(rec, "dtype") and hasattr(rec.dtype, "names"):
                if rec.dtype.names and "xy" in rec.dtype.names:
                    xy = rec["xy"]
                    arr = np.asarray(xy, dtype=np.float64).reshape(-1)
                    if arr.size >= 2:
                        return (float(arr[0]), float(arr[1]))
            # Try as plain array
            try:
                arr = np.asarray(rec, dtype=np.float64).reshape(-1)
                if arr.size >= 2:
                    return (float(arr[0]), float(arr[1]))
            except Exception:
                pass

    # Try dict-like access
    try:
        d = instance[idx]
        if isinstance(d, dict):
            if "x" in d and "y" in d:
                return (float(d["x"]), float(d["y"]))
            if "xy" in d:
                arr = np.asarray(d["xy"], dtype=np.float64).reshape(-1)
                if arr.size >= 2:
                    return (float(arr[0]), float(arr[1]))
    except Exception:
        pass

    return (np.nan, np.nan)


def _is_valid_point(pt: tuple[float, float]) -> bool:
    """Check if point has valid (finite) coordinates."""
    return np.isfinite(pt[0]) and np.isfinite(pt[1])


def _get_skeleton_names(labels) -> list[str]:
    """Get skeleton node names from SLEAP labels."""
    if hasattr(labels, "skeleton") and hasattr(labels.skeleton, "nodes"):
        return [n.name for n in labels.skeleton.nodes]
    if len(labels) > 0:
        lf = labels[0]
        if lf.instances and hasattr(lf.instances[0], "skeleton"):
            return [n.name for n in lf.instances[0].skeleton.nodes]
    raise ValueError("Cannot determine skeleton node names from labels.")


def extract_keypoints(
    slp_path: Path | str,
    frame: int = 0,
    instance: int = 0,
) -> dict[str, tuple[float, float]]:
    """
    Extract keypoint coordinates from a SLEAP file.

    Args:
        slp_path: Path to .slp file
        frame: Frame index to extract from (default: 0)
        instance: Instance index within frame (default: 0)

    Returns:
        Dictionary mapping keypoint names to (x, y) coordinates.
        Only includes keypoints with valid (finite) coordinates.
    """
    if sio is None:
        raise ImportError("sleap-io is required. Install with: pip install sleap-io")

    labels = sio.load_file(str(slp_path))

    if len(labels) <= frame:
        raise ValueError(f"Frame {frame} not found (file has {len(labels)} frames)")

    lf = labels[frame]
    if not lf.instances or len(lf.instances) <= instance:
        raise ValueError(f"Instance {instance} not found in frame {frame}")

    inst = lf.instances[instance]
    skeleton_names = _get_skeleton_names(labels)
    exact, normalized = _build_name_index(skeleton_names)

    keypoints = {}
    for name in skeleton_names:
        idx = _lookup_index(name, exact, normalized)
        if idx is not None:
            pt = _get_point_xy(inst, idx)
            if _is_valid_point(pt):
                keypoints[name] = pt

    return keypoints


def get_video_dimensions(slp_path: Path | str) -> tuple[int, int]:
    """
    Get video dimensions from SLEAP file.

    Returns:
        (width, height) tuple, or (4096, 4096) as fallback
    """
    if sio is None:
        raise ImportError("sleap-io is required. Install with: pip install sleap-io")

    labels = sio.load_file(str(slp_path))
    video = labels.videos[0] if getattr(labels, "videos", None) else None

    if video and hasattr(video, "shape") and len(video.shape) >= 3:
        if len(video.shape) == 4:
            _, H, W, _ = video.shape
        else:
            H, W, _ = video.shape
        return (int(W), int(H))

    return (4096, 4096)  # fallback


def get_video_path(slp_path: Path | str) -> str:
    """Get video file path from SLEAP file."""
    if sio is None:
        raise ImportError("sleap-io is required. Install with: pip install sleap-io")

    labels = sio.load_file(str(slp_path))
    video = labels.videos[0] if getattr(labels, "videos", None) else None
    return video.filename if (video and hasattr(video, "filename")) else ""


# =============================================================================
# ROI Construction
# =============================================================================


def _compute_perimeter(coords: list[list[float]]) -> float:
    """Compute polygon perimeter."""
    perimeter = 0.0
    n = len(coords)
    for i in range(n):
        x1, y1 = coords[i]
        x2, y2 = coords[(i + 1) % n]
        perimeter += ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
    return perimeter


def _compute_area(coords: list[list[float]]) -> float:
    """Compute polygon area using shoelace formula."""
    area = 0.0
    n = len(coords)
    for i in range(n):
        x1, y1 = coords[i]
        x2, y2 = coords[(i + 1) % n]
        area += x1 * y2 - x2 * y1
    return abs(area) * 0.5


def _clamp_point(
    pt: tuple[float, float],
    width: int,
    height: int,
) -> tuple[float, float]:
    """Clamp point to image bounds."""
    x = min(max(pt[0], 0.0), width - 1)
    y = min(max(pt[1], 0.0), height - 1)
    return (x, y)


def build_rois(
    keypoints: dict[str, tuple[float, float]],
    template: ROITemplate | str,
    image_size: Optional[tuple[int, int]] = None,
    clamp_to_bounds: bool = True,
) -> list[dict]:
    """
    Build ROI definitions from keypoints using a template.

    Args:
        keypoints: Dictionary mapping keypoint names to (x, y) coordinates
        template: ROITemplate instance or name of built-in template
        image_size: (width, height) for clamping coordinates
        clamp_to_bounds: Whether to clamp coordinates to image bounds

    Returns:
        List of ROI dictionaries ready for YAML export
    """
    # Resolve template
    if isinstance(template, str):
        if template not in TEMPLATES:
            raise ValueError(
                f"Unknown template: {template}. "
                f"Available: {list(TEMPLATES.keys())}"
            )
        template = TEMPLATES[template]

    # Validate keypoints
    valid, msg = template.validate(keypoints)
    if not valid:
        raise ValueError(f"Template validation failed: {msg}")

    # Default image size for clamping
    width, height = image_size or (4096, 4096)

    rois = []
    for i, poly_def in enumerate(template.polygons, start=1):
        # Get corner coordinates
        coords = []
        for corner_name in poly_def.corners:
            if corner_name not in keypoints:
                raise ValueError(
                    f"Missing keypoint '{corner_name}' for polygon '{poly_def.name}'"
                )
            pt = keypoints[corner_name]
            if clamp_to_bounds:
                pt = _clamp_point(pt, width, height)
            coords.append([float(pt[0]), float(pt[1])])

        rois.append(
            {
                "id": i,
                "name": poly_def.name,
                "type": "polygon",
                "coordinates": coords,
                "color": poly_def.color,
                "properties": {
                    "vertex_count": len(coords),
                    "perimeter": _compute_perimeter(coords),
                    "area": _compute_area(coords),
                },
            }
        )

    return rois


# =============================================================================
# YAML Export
# =============================================================================


def save_roi_yaml(
    rois: list[dict],
    output_path: Path | str,
    video_path: str = "",
    metadata: Optional[dict] = None,
) -> None:
    """
    Save ROI definitions to YAML file.

    Args:
        rois: List of ROI dictionaries
        output_path: Path to output YAML file
        video_path: Associated video file path
        metadata: Additional metadata to include
    """
    data = {
        "image_file": video_path,
        "roi_count": len(rois),
        "rois": rois,
        "metadata": metadata
        or {
            "created_with": "vibing.sleap_convert",
            "format_version": "1.0",
        },
    }

    with open(output_path, "w") as f:
        yaml.safe_dump(data, f, sort_keys=False)


# =============================================================================
# High-level API
# =============================================================================


def slp_to_roi_yaml(
    slp_path: Path | str,
    output_path: Path | str,
    template: ROITemplate | str = "tmaze_horizontal",
    frame: int = 0,
    instance: int = 0,
) -> dict:
    """
    Convert SLEAP predictions to ROI YAML format.

    Args:
        slp_path: Path to .slp file
        output_path: Path to output YAML file
        template: ROITemplate instance or name of built-in template
        frame: Frame index to extract from (default: 0)
        instance: Instance index within frame (default: 0)

    Returns:
        Dictionary with conversion info (keypoint_count, roi_count, etc.)
    """
    slp_path = Path(slp_path)
    output_path = Path(output_path)

    # Extract keypoints
    keypoints = extract_keypoints(slp_path, frame=frame, instance=instance)

    # Get video info
    image_size = get_video_dimensions(slp_path)
    video_path = get_video_path(slp_path)

    # Build ROIs
    rois = build_rois(keypoints, template, image_size=image_size)

    # Save YAML
    save_roi_yaml(rois, output_path, video_path=video_path)

    return {
        "slp_path": str(slp_path),
        "output_path": str(output_path),
        "keypoint_count": len(keypoints),
        "roi_count": len(rois),
        "image_size": image_size,
    }


def convert_batch(
    slp_dir: Path | str,
    output_dir: Path | str,
    template: ROITemplate | str = "tmaze_horizontal",
    patterns: list[str] = None,
    overwrite: bool = False,
) -> dict[str, dict]:
    """
    Batch convert SLP files to ROI YAML.

    Args:
        slp_dir: Directory containing SLP files
        output_dir: Directory for output YAML files
        template: ROITemplate or name of built-in template
        patterns: Glob patterns for SLP files (default: ["*.slp"])
        overwrite: Whether to overwrite existing YAML files

    Returns:
        Dictionary mapping filenames to results or error messages
    """
    slp_dir = Path(slp_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if patterns is None:
        patterns = ["*.slp"]

    # Collect SLP files
    slp_files = []
    for pattern in patterns:
        slp_files.extend(slp_dir.glob(pattern))
    slp_files = sorted(set(slp_files))

    results = {}
    for slp_path in slp_files:
        yaml_path = output_dir / (slp_path.stem + ".yml")

        if not overwrite and yaml_path.exists():
            results[slp_path.name] = {"status": "skip", "message": "already exists"}
            continue

        try:
            info = slp_to_roi_yaml(slp_path, yaml_path, template=template)
            results[slp_path.name] = {"status": "ok", **info}
        except Exception as e:
            results[slp_path.name] = {"status": "error", "message": str(e)}

    return results
