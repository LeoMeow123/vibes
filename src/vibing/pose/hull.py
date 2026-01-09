"""
Body hull calculation utilities.

Compute convex hulls from body keypoints for spatial occupancy analysis.
The body hull represents the 2D footprint of the animal and can be used
to calculate region coverage, spatial extent, and body area.
"""

from typing import Optional, Union
import numpy as np
from numpy.typing import ArrayLike
from scipy.spatial import ConvexHull

try:
    from shapely.geometry import Polygon

    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False


def body_hull(
    points: ArrayLike,
    min_points: int = 3,
    min_area: float = 0.0,
    return_type: str = "polygon",
) -> Optional[Union["Polygon", np.ndarray]]:
    """
    Compute convex hull polygon from body keypoints.

    Filters out NaN/invalid points before computing the hull.
    Useful for calculating body coverage in regions of interest.

    Args:
        points: Array of shape (N, 2) with (x, y) coordinates of body keypoints.
                NaN values are automatically filtered out.
        min_points: Minimum valid points required to compute hull (default: 3).
        min_area: Minimum hull area to return a valid result (default: 0).
                  Hulls smaller than this return None.
        return_type: What to return:
                     - "polygon": Shapely Polygon (requires shapely)
                     - "vertices": Numpy array of hull vertices
                     - "both": Tuple of (Polygon, vertices)

    Returns:
        - If return_type="polygon": Shapely Polygon or None
        - If return_type="vertices": Array of shape (K, 2) with hull vertices or None
        - If return_type="both": Tuple of (Polygon, vertices) or None

    Example:
        >>> points = np.array([[0, 0], [10, 0], [5, 10], [np.nan, np.nan]])
        >>> hull = body_hull(points, return_type="polygon")
        >>> hull.area
        50.0

        >>> vertices = body_hull(points, return_type="vertices")
        >>> vertices.shape
        (3, 2)
    """
    P = np.asarray(points, dtype=np.float64)

    if P.ndim != 2 or P.shape[1] != 2:
        raise ValueError(f"Expected shape (N, 2), got {P.shape}")

    # Filter out invalid points
    valid_mask = np.all(np.isfinite(P), axis=1)
    P = P[valid_mask]

    if P.shape[0] < min_points:
        return None

    # Compute convex hull
    try:
        hull = ConvexHull(P)
    except Exception:
        # scipy raises various exceptions for degenerate cases
        return None

    vertices = P[hull.vertices]

    # Check minimum area
    if hull.volume < min_area:  # In 2D, volume is actually area
        return None

    if return_type == "vertices":
        return vertices

    if return_type in ("polygon", "both"):
        if not HAS_SHAPELY:
            raise ImportError(
                "shapely is required for polygon output. "
                "Install with: pip install shapely"
            )

        poly = Polygon(vertices)
        if not poly.is_valid:
            poly = poly.buffer(0)

        if poly.area < min_area:
            return None

        if return_type == "both":
            return poly, vertices
        return poly

    raise ValueError(f"Unknown return_type: {return_type}")


def body_hull_area(
    points: ArrayLike,
    min_points: int = 3,
) -> float:
    """
    Calculate the area of the body hull.

    Convenience function when you only need the area, not the polygon.

    Args:
        points: Array of shape (N, 2) with body keypoint coordinates.
        min_points: Minimum valid points required (default: 3).

    Returns:
        Hull area in square pixels, or 0.0 if hull cannot be computed.

    Example:
        >>> points = np.array([[0, 0], [10, 0], [10, 10], [0, 10]])
        >>> body_hull_area(points)
        100.0
    """
    P = np.asarray(points, dtype=np.float64)

    if P.ndim != 2 or P.shape[1] != 2:
        raise ValueError(f"Expected shape (N, 2), got {P.shape}")

    # Filter out invalid points
    valid_mask = np.all(np.isfinite(P), axis=1)
    P = P[valid_mask]

    if P.shape[0] < min_points:
        return 0.0

    try:
        hull = ConvexHull(P)
        return float(hull.volume)  # In 2D, volume is area
    except Exception:
        return 0.0


def body_hull_centroid(
    points: ArrayLike,
    min_points: int = 3,
) -> Optional[tuple[float, float]]:
    """
    Calculate the centroid of the body hull.

    The centroid is the geometric center of the convex hull,
    useful for tracking the "center of mass" of the animal.

    Args:
        points: Array of shape (N, 2) with body keypoint coordinates.
        min_points: Minimum valid points required (default: 3).

    Returns:
        Tuple (x, y) of centroid coordinates, or None if hull cannot be computed.

    Example:
        >>> points = np.array([[0, 0], [10, 0], [10, 10], [0, 10]])
        >>> body_hull_centroid(points)
        (5.0, 5.0)
    """
    result = body_hull(points, min_points=min_points, return_type="polygon")

    if result is None:
        return None

    centroid = result.centroid
    return (float(centroid.x), float(centroid.y))


def body_hull_series(
    tracks: ArrayLike,
    keypoint_indices: Optional[list[int]] = None,
    min_points: int = 3,
    min_area: float = 0.0,
) -> list[Optional["Polygon"]]:
    """
    Compute body hull for each frame in a tracking series.

    Args:
        tracks: Array of shape (T, J, 2) with T frames, J keypoints.
        keypoint_indices: Which keypoints to use for hull (default: all).
        min_points: Minimum valid points per frame (default: 3).
        min_area: Minimum hull area to be valid (default: 0).

    Returns:
        List of T Shapely Polygons (or None for invalid frames).

    Example:
        >>> tracks = np.random.randn(100, 15, 2) * 50 + 100
        >>> hulls = body_hull_series(tracks)
        >>> len(hulls)
        100
    """
    if not HAS_SHAPELY:
        raise ImportError(
            "shapely is required for body_hull_series. "
            "Install with: pip install shapely"
        )

    tracks = np.asarray(tracks, dtype=np.float64)

    if tracks.ndim != 3 or tracks.shape[2] != 2:
        raise ValueError(f"Expected shape (T, J, 2), got {tracks.shape}")

    T, J = tracks.shape[:2]

    if keypoint_indices is None:
        keypoint_indices = list(range(J))

    hulls = []
    for t in range(T):
        points = tracks[t, keypoint_indices, :]
        hull = body_hull(
            points,
            min_points=min_points,
            min_area=min_area,
            return_type="polygon",
        )
        hulls.append(hull)

    return hulls


def body_hull_coverage(
    points: ArrayLike,
    region: "Polygon",
    min_points: int = 3,
) -> float:
    """
    Calculate percentage of body hull overlapping with a region.

    Useful for determining how much of the animal is "inside" a zone.

    Args:
        points: Array of shape (N, 2) with body keypoint coordinates.
        region: Shapely Polygon defining the region of interest.
        min_points: Minimum valid points required (default: 3).

    Returns:
        Percentage (0-100) of body hull area inside the region.
        Returns 0.0 if hull cannot be computed.

    Example:
        >>> from shapely.geometry import box
        >>> region = box(0, 0, 50, 50)
        >>> points = np.array([[25, 25], [75, 25], [75, 75], [25, 75]])
        >>> body_hull_coverage(points, region)  # 25% overlap
        25.0
    """
    if not HAS_SHAPELY:
        raise ImportError(
            "shapely is required for body_hull_coverage. "
            "Install with: pip install shapely"
        )

    hull = body_hull(points, min_points=min_points, return_type="polygon")

    if hull is None or hull.area == 0:
        return 0.0

    if not region.is_valid:
        region = region.buffer(0)

    intersection = hull.intersection(region)
    intersection_area = intersection.area if not intersection.is_empty else 0.0

    return 100.0 * intersection_area / hull.area
