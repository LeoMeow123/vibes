"""
Track analysis utilities.

Compute velocity, distance, and dwell time from pose tracking data.
"""

from typing import Optional, Union
import numpy as np
from numpy.typing import ArrayLike

try:
    from shapely.geometry import Polygon, Point
    HAS_SHAPELY = True
except ImportError:
    HAS_SHAPELY = False


def track_velocity(
    track: ArrayLike,
    fps: float = 30.0,
    smooth_window: Optional[int] = None,
) -> np.ndarray:
    """
    Compute instantaneous velocity from tracking data.

    Velocity is computed as displacement per frame, then converted to units/second.

    Args:
        track: Array of shape (T, 2) with (x, y) coordinates over time
        fps: Frames per second for velocity calculation
        smooth_window: Optional smoothing window size (odd number).
                      If provided, applies moving average smoothing.

    Returns:
        Array of shape (T,) with velocity at each frame (units/second).
        First frame velocity is set to 0.

    Example:
        >>> track = np.array([[0, 0], [1, 0], [2, 0], [3, 0]])
        >>> velocity = track_velocity(track, fps=30)
        >>> velocity  # 30 units/second (1 pixel/frame * 30 fps)
        array([ 0., 30., 30., 30.])
    """
    track = np.asarray(track, dtype=np.float64)

    if track.ndim != 2 or track.shape[1] != 2:
        raise ValueError(f"Expected shape (T, 2), got {track.shape}")

    T = track.shape[0]
    velocity = np.zeros(T)

    # Compute displacement between consecutive frames
    diff = np.diff(track, axis=0)  # (T-1, 2)
    displacement = np.sqrt(np.sum(diff ** 2, axis=1))  # (T-1,)

    # Convert to units per second
    velocity[1:] = displacement * fps

    # Handle NaN values
    velocity[~np.isfinite(velocity)] = 0.0

    # Optional smoothing
    if smooth_window is not None and smooth_window > 1:
        velocity = _smooth_1d(velocity, smooth_window)

    return velocity


def track_speed(
    track: ArrayLike,
    fps: float = 30.0,
    window: int = 1,
) -> np.ndarray:
    """
    Compute speed (magnitude of velocity) over a time window.

    Similar to track_velocity but can average over multiple frames
    for smoother estimates.

    Args:
        track: Array of shape (T, 2) with (x, y) coordinates
        fps: Frames per second
        window: Number of frames to average over (default: 1)

    Returns:
        Array of shape (T,) with speed at each frame (units/second)

    Example:
        >>> track = np.array([[0, 0], [3, 4], [6, 8], [9, 12]])
        >>> speed = track_speed(track, fps=10, window=1)
        >>> speed[1]  # sqrt(3^2 + 4^2) * 10 = 50
        50.0
    """
    track = np.asarray(track, dtype=np.float64)
    T = track.shape[0]
    speed = np.zeros(T)

    for i in range(window, T):
        start_idx = i - window
        displacement = np.sqrt(np.sum((track[i] - track[start_idx]) ** 2))
        time_elapsed = window / fps
        speed[i] = displacement / time_elapsed if time_elapsed > 0 else 0.0

    # Handle NaN
    speed[~np.isfinite(speed)] = 0.0

    return speed


def track_distance(
    track: ArrayLike,
    start_frame: Optional[int] = None,
    end_frame: Optional[int] = None,
) -> float:
    """
    Compute total distance traveled along a track.

    Sums up displacement between consecutive frames, ignoring gaps (NaN values).

    Args:
        track: Array of shape (T, 2) with (x, y) coordinates
        start_frame: Optional start frame (inclusive, default: 0)
        end_frame: Optional end frame (exclusive, default: end)

    Returns:
        Total distance traveled in coordinate units (pixels)

    Example:
        >>> track = np.array([[0, 0], [3, 4], [6, 8]])
        >>> track_distance(track)  # 5 + 5 = 10
        10.0
    """
    track = np.asarray(track, dtype=np.float64)

    if track.ndim != 2 or track.shape[1] != 2:
        raise ValueError(f"Expected shape (T, 2), got {track.shape}")

    # Slice if bounds provided
    if start_frame is not None or end_frame is not None:
        start_frame = start_frame or 0
        end_frame = end_frame or len(track)
        track = track[start_frame:end_frame]

    # Compute displacement between consecutive frames
    diff = np.diff(track, axis=0)

    # Filter out NaN displacements
    valid_mask = np.all(np.isfinite(diff), axis=1)
    valid_diff = diff[valid_mask]

    # Sum up distances
    distances = np.sqrt(np.sum(valid_diff ** 2, axis=1))
    return float(np.sum(distances))


def cumulative_distance(track: ArrayLike) -> np.ndarray:
    """
    Compute cumulative distance traveled at each frame.

    Args:
        track: Array of shape (T, 2) with (x, y) coordinates

    Returns:
        Array of shape (T,) with cumulative distance at each frame.
        First frame is 0.

    Example:
        >>> track = np.array([[0, 0], [3, 4], [6, 8]])
        >>> cumulative_distance(track)
        array([ 0.,  5., 10.])
    """
    track = np.asarray(track, dtype=np.float64)
    T = track.shape[0]
    cum_dist = np.zeros(T)

    diff = np.diff(track, axis=0)
    distances = np.sqrt(np.sum(diff ** 2, axis=1))

    # Handle NaN
    distances[~np.isfinite(distances)] = 0.0

    cum_dist[1:] = np.cumsum(distances)

    return cum_dist


def region_dwell_time(
    track: ArrayLike,
    region: "Polygon",
    fps: float = 30.0,
) -> dict:
    """
    Compute time spent inside a region.

    Args:
        track: Array of shape (T, 2) with (x, y) coordinates
        region: Shapely Polygon defining the region
        fps: Frames per second

    Returns:
        Dictionary with:
        - frames_inside: Number of frames inside region
        - time_inside: Time in seconds inside region
        - fraction: Fraction of total time inside
        - entries: Number of times animal entered region
        - mean_bout: Mean duration of each visit (seconds)

    Example:
        >>> from shapely.geometry import box
        >>> region = box(0, 0, 100, 100)
        >>> track = np.array([[50, 50], [50, 50], [150, 50], [50, 50]])
        >>> result = region_dwell_time(track, region, fps=30)
        >>> result['frames_inside']
        3
    """
    if not HAS_SHAPELY:
        raise ImportError(
            "shapely is required for region_dwell_time. "
            "Install with: pip install shapely"
        )

    track = np.asarray(track, dtype=np.float64)
    T = track.shape[0]

    if not region.is_valid:
        region = region.buffer(0)

    # Check each frame
    inside = np.zeros(T, dtype=bool)
    for i in range(T):
        pt = track[i]
        if np.all(np.isfinite(pt)):
            inside[i] = region.contains(Point(pt))

    frames_inside = int(inside.sum())
    time_inside = frames_inside / fps

    # Count entries (transitions from outside to inside)
    entries = 0
    bouts = []
    in_bout = False
    bout_start = 0

    for i in range(T):
        if inside[i] and not in_bout:
            # Entry
            entries += 1
            in_bout = True
            bout_start = i
        elif not inside[i] and in_bout:
            # Exit
            in_bout = False
            bouts.append(i - bout_start)

    # Handle case where still inside at end
    if in_bout:
        bouts.append(T - bout_start)

    mean_bout = (sum(bouts) / len(bouts) / fps) if bouts else 0.0

    return {
        "frames_inside": frames_inside,
        "time_inside": time_inside,
        "fraction": frames_inside / T if T > 0 else 0.0,
        "entries": entries,
        "mean_bout": mean_bout,
    }


def region_dwell_frames(
    track: ArrayLike,
    region: "Polygon",
) -> np.ndarray:
    """
    Get boolean mask of frames where point is inside region.

    Args:
        track: Array of shape (T, 2) with (x, y) coordinates
        region: Shapely Polygon defining the region

    Returns:
        Boolean array of shape (T,) - True when inside region

    Example:
        >>> from shapely.geometry import box
        >>> region = box(0, 0, 100, 100)
        >>> track = np.array([[50, 50], [150, 50], [50, 50]])
        >>> region_dwell_frames(track, region)
        array([ True, False,  True])
    """
    if not HAS_SHAPELY:
        raise ImportError("shapely is required")

    track = np.asarray(track, dtype=np.float64)
    T = track.shape[0]

    if not region.is_valid:
        region = region.buffer(0)

    inside = np.zeros(T, dtype=bool)
    for i in range(T):
        pt = track[i]
        if np.all(np.isfinite(pt)):
            inside[i] = region.contains(Point(pt))

    return inside


def multi_region_dwell(
    track: ArrayLike,
    regions: dict[str, "Polygon"],
    fps: float = 30.0,
) -> dict[str, dict]:
    """
    Compute dwell time for multiple regions.

    Args:
        track: Array of shape (T, 2) with (x, y) coordinates
        regions: Dictionary mapping region names to Polygons
        fps: Frames per second

    Returns:
        Dictionary mapping region names to dwell results

    Example:
        >>> from shapely.geometry import box
        >>> regions = {"left": box(0, 0, 50, 100), "right": box(50, 0, 100, 100)}
        >>> results = multi_region_dwell(track, regions, fps=30)
        >>> print(results["left"]["time_inside"])
    """
    results = {}
    for name, region in regions.items():
        results[name] = region_dwell_time(track, region, fps)
    return results


def _smooth_1d(arr: np.ndarray, window: int) -> np.ndarray:
    """Apply simple moving average smoothing."""
    if window <= 1:
        return arr
    kernel = np.ones(window) / window
    # Pad to handle edges
    padded = np.pad(arr, (window // 2, window // 2), mode='edge')
    smoothed = np.convolve(padded, kernel, mode='valid')
    return smoothed[:len(arr)]
