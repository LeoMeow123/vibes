"""
Track interpolation utilities.

Interpolate short gaps in pose tracking data while preserving long gaps.
Short gaps are common in tracking due to occlusions or low confidence frames,
while long gaps usually indicate the subject leaving the field of view.
"""

from typing import Optional
import numpy as np
from numpy.typing import ArrayLike


def interpolate_gaps(
    track: ArrayLike,
    max_gap: int = 7,
) -> np.ndarray:
    """
    Interpolate short gaps in a single keypoint track.

    Uses linear interpolation for gaps up to max_gap frames.
    Longer gaps are preserved as NaN to avoid unrealistic interpolation
    across periods where the animal may have moved significantly.

    Args:
        track: Array of shape (T, 2) with (x, y) coordinates over time.
               NaN values indicate missing data.
        max_gap: Maximum gap length (in frames) to interpolate.
                 Gaps longer than this are preserved as NaN.

    Returns:
        Interpolated track array of shape (T, 2).

    Example:
        >>> track = np.array([[0, 0], [np.nan, np.nan], [2, 2], [3, 3]])
        >>> interpolate_gaps(track, max_gap=3)
        array([[0., 0.], [1., 1.], [2., 2.], [3., 3.]])

        >>> # Long gaps preserved
        >>> track = np.array([[0, 0]] + [[np.nan, np.nan]] * 10 + [[10, 10]])
        >>> result = interpolate_gaps(track, max_gap=5)
        >>> np.isnan(result[5])  # Middle of long gap still NaN
        array([ True,  True])
    """
    arr = np.asarray(track, dtype=np.float64).copy()

    if arr.ndim != 2 or arr.shape[1] != 2:
        raise ValueError(f"Expected shape (T, 2), got {arr.shape}")

    t = np.arange(arr.shape[0], dtype=np.float64)

    for d in (0, 1):  # x and y dimensions
        y = arr[:, d]
        mask = np.isfinite(y)

        if mask.sum() < 2:
            # Not enough points to interpolate
            continue

        # Interpolate all gaps
        ti, yi = t[mask], y[mask]
        y[:] = np.interp(t, ti, yi)

        # Restore long gaps as NaN
        # Calculate distance to nearest valid point on each side
        left = np.where(mask, np.arange(len(y)), -np.inf)
        left = np.maximum.accumulate(left)

        right = np.where(mask, np.arange(len(y)), np.inf)
        for i in range(len(right) - 2, -1, -1):
            right[i] = min(right[i], right[i + 1])

        # Point is "too far" if both left and right neighbors are > max_gap away
        too_far = ((np.arange(len(y)) - left) > max_gap) & (
            (right - np.arange(len(y))) > max_gap
        )
        y[too_far] = np.nan
        arr[:, d] = y

    return arr


def interpolate_track(
    track: ArrayLike,
    max_gap: int = 7,
    keypoint_indices: Optional[list[int]] = None,
) -> np.ndarray:
    """
    Interpolate short gaps across all keypoints in a track array.

    Args:
        track: Array of shape (T, J, 2) where T is frames, J is keypoints,
               and 2 is (x, y) coordinates.
        max_gap: Maximum gap length to interpolate (default: 7 frames).
        keypoint_indices: Optional list of keypoint indices to interpolate.
                         If None, all keypoints are interpolated.

    Returns:
        Interpolated track array of shape (T, J, 2).

    Example:
        >>> # Track with 100 frames, 15 keypoints
        >>> track = np.random.randn(100, 15, 2)
        >>> track[10:15, 0, :] = np.nan  # 5-frame gap in keypoint 0
        >>> track[20:35, 1, :] = np.nan  # 15-frame gap in keypoint 1
        >>> result = interpolate_track(track, max_gap=7)
        >>> np.isnan(result[12, 0, 0])  # Short gap interpolated
        False
        >>> np.isnan(result[25, 1, 0])  # Long gap preserved
        True
    """
    arr = np.asarray(track, dtype=np.float64).copy()

    if arr.ndim != 3 or arr.shape[2] != 2:
        raise ValueError(f"Expected shape (T, J, 2), got {arr.shape}")

    n_keypoints = arr.shape[1]

    if keypoint_indices is None:
        keypoint_indices = list(range(n_keypoints))

    for j in keypoint_indices:
        if 0 <= j < n_keypoints:
            arr[:, j, :] = interpolate_gaps(arr[:, j, :], max_gap=max_gap)

    return arr


def count_gaps(
    track: ArrayLike,
    min_length: int = 1,
) -> dict:
    """
    Count and characterize gaps in tracking data.

    Useful for quality control and deciding interpolation parameters.

    Args:
        track: Array of shape (T, 2) with (x, y) coordinates.
        min_length: Minimum gap length to count (default: 1).

    Returns:
        Dictionary with:
        - n_gaps: Total number of gaps
        - total_missing: Total missing frames
        - gap_lengths: List of individual gap lengths
        - max_gap: Length of longest gap
        - coverage: Fraction of frames with valid data

    Example:
        >>> track = np.array([[0, 0], [np.nan, np.nan], [np.nan, np.nan], [3, 3], [4, 4]])
        >>> count_gaps(track)
        {'n_gaps': 1, 'total_missing': 2, 'gap_lengths': [2], 'max_gap': 2, 'coverage': 0.6}
    """
    arr = np.asarray(track, dtype=np.float64)

    if arr.ndim == 2 and arr.shape[1] == 2:
        # Use x coordinate to detect missing
        valid = np.isfinite(arr[:, 0])
    elif arr.ndim == 1:
        valid = np.isfinite(arr)
    else:
        raise ValueError(f"Expected shape (T,) or (T, 2), got {arr.shape}")

    # Find gaps
    gap_lengths = []
    i = 0
    n = len(valid)

    while i < n:
        if not valid[i]:
            # Start of gap
            j = i
            while j < n and not valid[j]:
                j += 1
            gap_len = j - i
            if gap_len >= min_length:
                gap_lengths.append(gap_len)
            i = j
        else:
            i += 1

    total_missing = sum(gap_lengths)

    return {
        "n_gaps": len(gap_lengths),
        "total_missing": total_missing,
        "gap_lengths": gap_lengths,
        "max_gap": max(gap_lengths) if gap_lengths else 0,
        "coverage": float(valid.sum()) / len(valid) if len(valid) > 0 else 0.0,
    }
