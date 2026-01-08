"""
Body part region checking utilities.

Check whether specific body parts (keypoints) are located within
regions of interest (ROIs). Commonly used for behavioral analysis
to determine if specific body parts have entered a zone.
"""

from typing import Union
import numpy as np
from numpy.typing import ArrayLike

try:
    from shapely.geometry import Point, Polygon
    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False


def _require_shapely():
    if not HAS_SHAPELY:
        raise ImportError(
            "shapely is required for region operations. "
            "Install with: pip install shapely"
        )


def bodypart_in_region(
    point: Union[tuple[float, float], ArrayLike],
    polygon: "Polygon",
) -> bool:
    """
    Check if a single body part (keypoint) is inside a region.

    Args:
        point: (x, y) coordinates of the body part
        polygon: Shapely Polygon defining the region

    Returns:
        True if the point is inside the polygon (including boundary)

    Example:
        >>> from shapely.geometry import box
        >>> region = box(0, 0, 100, 100)
        >>> bodypart_in_region((50, 50), region)
        True
        >>> bodypart_in_region((150, 50), region)
        False
    """
    _require_shapely()

    # Handle NaN/invalid points
    pt_arr = np.asarray(point, dtype=np.float64)
    if not np.all(np.isfinite(pt_arr)):
        return False

    pt = Point(point)

    if not polygon.is_valid:
        polygon = polygon.buffer(0)

    return polygon.contains(pt) or polygon.boundary.contains(pt)


def bodyparts_in_region(
    points: ArrayLike,
    polygon: "Polygon",
) -> np.ndarray:
    """
    Check which body parts are inside a region.

    Args:
        points: Array of shape (N, 2) with (x, y) coordinates for N body parts
        polygon: Shapely Polygon defining the region

    Returns:
        Boolean array of shape (N,) indicating which points are inside.
        NaN/invalid points return False.

    Example:
        >>> from shapely.geometry import box
        >>> region = box(0, 0, 100, 100)
        >>> pts = np.array([[50, 50], [150, 50], [np.nan, np.nan]])
        >>> bodyparts_in_region(pts, region)
        array([ True, False, False])
    """
    _require_shapely()

    points = np.asarray(points, dtype=np.float64)
    if points.ndim == 1:
        points = points.reshape(1, -1)

    if points.shape[1] != 2:
        raise ValueError(f"Expected shape (N, 2), got {points.shape}")

    inside = np.zeros(len(points), dtype=bool)

    for i, pt in enumerate(points):
        inside[i] = bodypart_in_region(pt, polygon)

    return inside


def count_bodyparts_in_region(
    points: ArrayLike,
    polygon: "Polygon",
) -> int:
    """
    Count how many body parts are inside a region.

    Args:
        points: Array of shape (N, 2) with (x, y) coordinates
        polygon: Shapely Polygon defining the region

    Returns:
        Number of points inside the region

    Example:
        >>> from shapely.geometry import box
        >>> region = box(0, 0, 100, 100)
        >>> pts = np.array([[50, 50], [150, 50], [25, 75]])
        >>> count_bodyparts_in_region(pts, region)
        2
    """
    return int(bodyparts_in_region(points, polygon).sum())


def check_bodyparts_by_name(
    pose_dict: dict[str, tuple[float, float]],
    polygon: "Polygon",
    bodypart_names: list[str],
    min_count: int = 1,
) -> bool:
    """
    Check if enough named body parts are inside a region.

    Useful for checking conditions like "at least one hindpaw in the arm".

    Args:
        pose_dict: Dictionary mapping body part names to (x, y) coordinates
        polygon: Shapely Polygon defining the region
        bodypart_names: List of body part names to check
        min_count: Minimum number that must be inside (default: 1)

    Returns:
        True if at least min_count body parts are inside

    Example:
        >>> from shapely.geometry import box
        >>> region = box(0, 0, 100, 100)
        >>> pose = {"snout": (50, 50), "hindpawL": (150, 50), "hindpawR": (25, 75)}
        >>> check_bodyparts_by_name(pose, region, ["hindpawL", "hindpawR"], min_count=1)
        True
    """
    _require_shapely()

    count = 0
    for name in bodypart_names:
        if name in pose_dict:
            pt = pose_dict[name]
            if bodypart_in_region(pt, polygon):
                count += 1
                if count >= min_count:
                    return True

    return count >= min_count


def extract_bodyparts(
    pose_array: ArrayLike,
    skeleton_names: list[str],
    bodypart_names: list[str],
) -> np.ndarray:
    """
    Extract specific body parts from a pose array by name.

    Args:
        pose_array: Array of shape (J, 2) with all keypoint coordinates
        skeleton_names: List of all keypoint names in order
        bodypart_names: Names of body parts to extract

    Returns:
        Array of shape (len(bodypart_names), 2) with extracted coordinates.
        Returns NaN for body parts not found in skeleton.

    Example:
        >>> skeleton = ["snout", "forepawL", "forepawR", "hindpawL", "hindpawR"]
        >>> pose = np.array([[10, 20], [30, 40], [50, 60], [70, 80], [90, 100]])
        >>> extract_bodyparts(pose, skeleton, ["hindpawL", "hindpawR"])
        array([[70., 80.], [90., 100.]])
    """
    pose_array = np.asarray(pose_array, dtype=np.float64)
    name_to_idx = {name: i for i, name in enumerate(skeleton_names)}

    result = np.full((len(bodypart_names), 2), np.nan)

    for i, name in enumerate(bodypart_names):
        if name in name_to_idx:
            idx = name_to_idx[name]
            if idx < len(pose_array):
                result[i] = pose_array[idx]

    return result
