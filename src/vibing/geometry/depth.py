"""
Depth from boundary calculations.

Measure how far a point has penetrated into a polygon region.
Useful for behavioral analysis where you need to know "how deep"
an animal has entered a specific zone.
"""

from typing import Union
import numpy as np
from numpy.typing import ArrayLike

try:
    from shapely.geometry import Point, Polygon
    from shapely.geometry.base import BaseGeometry
    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False


def _require_shapely():
    if not HAS_SHAPELY:
        raise ImportError(
            "shapely is required for geometry operations. "
            "Install with: pip install shapely"
        )


def signed_distance(
    point: Union[tuple[float, float], ArrayLike],
    polygon: "Polygon",
) -> float:
    """
    Calculate signed distance from a point to a polygon boundary.

    Args:
        point: (x, y) coordinates
        polygon: Shapely Polygon object

    Returns:
        Signed distance:
        - Negative if point is inside the polygon (depth into region)
        - Positive if point is outside the polygon (distance to region)
        - Zero if point is exactly on the boundary
    """
    _require_shapely()

    pt = Point(point) if not isinstance(point, Point) else point

    if not polygon.is_valid:
        polygon = polygon.buffer(0)

    dist = pt.distance(polygon.boundary)

    if polygon.contains(pt):
        return -dist  # Inside = negative (depth)
    else:
        return dist   # Outside = positive


def depth_from_boundary(
    point: Union[tuple[float, float], ArrayLike],
    polygon: "Polygon",
    return_absolute: bool = False,
) -> float:
    """
    Calculate penetration depth from a point to a polygon boundary.

    This is the primary function for measuring how far a point has
    penetrated into a region. Commonly used for detecting committed
    entries in behavioral tasks.

    Args:
        point: (x, y) coordinates
        polygon: Shapely Polygon object defining the region
        return_absolute: If True, return absolute distance (always positive)

    Returns:
        Depth value:
        - Positive if point is inside (penetration depth)
        - Negative if point is outside (distance to enter)
        - If return_absolute=True, always returns positive value

    Example:
        >>> from shapely.geometry import Polygon, box
        >>> region = box(0, 0, 100, 100)  # 100x100 square
        >>> depth_from_boundary((50, 50), region)  # Center
        50.0
        >>> depth_from_boundary((10, 50), region)  # Near left edge
        10.0
        >>> depth_from_boundary((-10, 50), region)  # Outside left
        -10.0
    """
    _require_shapely()

    # Flip sign: we want positive = inside (depth), negative = outside
    dist = -signed_distance(point, polygon)

    if return_absolute:
        return abs(dist)
    return dist


def points_depth_from_boundary(
    points: ArrayLike,
    polygon: "Polygon",
    return_absolute: bool = False,
) -> np.ndarray:
    """
    Calculate penetration depth for multiple points.

    Efficiently processes an array of points against a polygon boundary.

    Args:
        points: Array of shape (N, 2) with (x, y) coordinates
        polygon: Shapely Polygon object defining the region
        return_absolute: If True, return absolute distances

    Returns:
        Array of shape (N,) with depth values for each point.
        NaN values in input produce NaN in output.

    Example:
        >>> from shapely.geometry import box
        >>> region = box(0, 0, 100, 100)
        >>> pts = np.array([[50, 50], [10, 50], [-10, 50], [np.nan, np.nan]])
        >>> points_depth_from_boundary(pts, region)
        array([50., 10., -10., nan])
    """
    _require_shapely()

    points = np.asarray(points, dtype=np.float64)
    if points.ndim == 1:
        points = points.reshape(1, -1)

    if points.shape[1] != 2:
        raise ValueError(f"Expected points with shape (N, 2), got {points.shape}")

    depths = np.full(len(points), np.nan)

    for i, pt in enumerate(points):
        if np.all(np.isfinite(pt)):
            depths[i] = depth_from_boundary(pt, polygon, return_absolute)

    return depths


def is_inside(
    point: Union[tuple[float, float], ArrayLike],
    polygon: "Polygon",
) -> bool:
    """
    Check if a point is inside a polygon.

    Args:
        point: (x, y) coordinates
        polygon: Shapely Polygon object

    Returns:
        True if point is inside or on boundary, False otherwise
    """
    _require_shapely()

    pt = Point(point) if not isinstance(point, Point) else point

    if not polygon.is_valid:
        polygon = polygon.buffer(0)

    return polygon.contains(pt) or polygon.boundary.contains(pt)


def points_inside(
    points: ArrayLike,
    polygon: "Polygon",
) -> np.ndarray:
    """
    Check which points are inside a polygon.

    Args:
        points: Array of shape (N, 2) with (x, y) coordinates
        polygon: Shapely Polygon object

    Returns:
        Boolean array of shape (N,). NaN points return False.
    """
    _require_shapely()

    points = np.asarray(points, dtype=np.float64)
    if points.ndim == 1:
        points = points.reshape(1, -1)

    inside = np.zeros(len(points), dtype=bool)

    for i, pt in enumerate(points):
        if np.all(np.isfinite(pt)):
            inside[i] = is_inside(pt, polygon)

    return inside
