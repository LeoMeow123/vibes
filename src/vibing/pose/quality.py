"""
Pose quality assessment via body-relative keypoint anomaly detection.

Detect spatially anomalous keypoints that pass confidence filtering but are
geometrically wrong — e.g., a snout 500px from the body, or a frame where
the mouse appears unrealistically long.  All thresholds are expressed as
multiples of the animal's own median body length (snout→tailbase), making
checks scale-invariant across camera setups.  An optional ``PixelScale``
enables absolute checks (e.g., "mouse can't be >15 cm").
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional, Union

import numpy as np
from numpy.typing import ArrayLike

from vibing.pose.hull import body_hull_area

try:
    from vibing.geometry.scale import PixelScale
except ImportError:  # pragma: no cover
    PixelScale = None  # type: ignore[assignment,misc]


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class QualityConfig:
    """
    Thresholds for pose quality checks.

    All spatial thresholds are expressed as multiples of the animal's
    median body length, making them scale-invariant.

    Attributes:
        spatial_outlier_factor: Flag keypoint if its distance from the
            centroid of the other keypoints exceeds this × median body length.
        temporal_jump_factor: Flag keypoint if its frame-to-frame
            displacement exceeds this × median body length.
        min_body_length_factor: Flag frame if body length < this × median.
        max_body_length_factor: Flag frame if body length > this × median.
        hull_area_min_factor: Flag frame if hull area < this × median area.
        hull_area_max_factor: Flag frame if hull area > this × median area.
        aspect_ratio_max: Flag frame if axis-aligned bounding-box aspect
            ratio exceeds this value.
        min_valid_keypoints: Minimum finite keypoints required per frame.
        fps: Recording frame rate (used for velocity-based absolute checks).
        pixel_scale: Optional ``PixelScale`` for absolute cm checks.
        max_body_length_cm: Absolute upper bound on body length (cm).
        min_body_length_cm: Absolute lower bound on body length (cm).
        max_displacement_cm_per_s: Absolute max keypoint speed (cm/s).

    Example:
        >>> cfg = QualityConfig(spatial_outlier_factor=3.0, fps=60.0)
        >>> cfg.spatial_outlier_factor
        3.0
    """

    spatial_outlier_factor: float = 2.0
    temporal_jump_factor: float = 1.5
    min_body_length_factor: float = 0.3
    max_body_length_factor: float = 2.5
    hull_area_min_factor: float = 0.2
    hull_area_max_factor: float = 3.0
    aspect_ratio_max: float = 5.0
    min_valid_keypoints: int = 3
    fps: float = 120.0
    pixel_scale: Optional[object] = None  # PixelScale when available
    max_body_length_cm: float = 15.0
    min_body_length_cm: float = 3.0
    max_displacement_cm_per_s: float = 150.0


@dataclass
class SkeletonMap:
    """
    Mapping from node names to semantic roles (head, tail, paw, …).

    Populated by ``detect_skeleton``.  When the skeleton layout is not
    recognised, ``is_known_skeleton`` is ``False`` and index fields are
    empty lists / ``None``.

    Attributes:
        node_names: All node names in order.
        head_indices: Indices of head-related nodes.
        tail_indices: Indices of tail-related nodes.
        paw_indices: Indices of paw / foot nodes.
        body_indices: Indices of trunk / body nodes.
        snout_index: Index of snout node (or None).
        tailbase_index: Index of tailbase node (or None).
        is_known_skeleton: Whether the skeleton was recognised.
    """

    node_names: list[str] = field(default_factory=list)
    head_indices: list[int] = field(default_factory=list)
    tail_indices: list[int] = field(default_factory=list)
    paw_indices: list[int] = field(default_factory=list)
    body_indices: list[int] = field(default_factory=list)
    snout_index: Optional[int] = None
    tailbase_index: Optional[int] = None
    is_known_skeleton: bool = False


@dataclass
class KeypointFlags:
    """
    Per-keypoint anomaly flags, each array of shape ``(T, J)``.

    Attributes:
        spatial_outlier: Keypoint far from centroid of other keypoints.
        temporal_jump: Keypoint jumped unreasonably between frames.
        missing: Keypoint has NaN / non-finite coordinates.
    """

    spatial_outlier: np.ndarray  # (T, J) bool
    temporal_jump: np.ndarray  # (T, J) bool
    missing: np.ndarray  # (T, J) bool

    @property
    def any_flagged(self) -> np.ndarray:
        """Bool array ``(T, J)`` — True where any flag is set."""
        return self.spatial_outlier | self.temporal_jump | self.missing

    def flagged_fraction(self) -> float:
        """Fraction of (frame, keypoint) entries that are flagged."""
        total = self.any_flagged.size
        if total == 0:
            return 0.0
        return float(self.any_flagged.sum()) / total


@dataclass
class FrameFlags:
    """
    Per-frame anomaly flags, each array of shape ``(T,)``.

    Attributes:
        body_too_long: Body length exceeds upper threshold.
        body_too_short: Body length below lower threshold.
        hull_area_anomaly: Hull area outside expected range.
        aspect_ratio_anomaly: Bounding-box aspect ratio too extreme.
        insufficient_keypoints: Fewer than ``min_valid_keypoints`` visible.
    """

    body_too_long: np.ndarray  # (T,) bool
    body_too_short: np.ndarray  # (T,) bool
    hull_area_anomaly: np.ndarray  # (T,) bool
    aspect_ratio_anomaly: np.ndarray  # (T,) bool
    insufficient_keypoints: np.ndarray  # (T,) bool

    @property
    def any_flagged(self) -> np.ndarray:
        """Bool array ``(T,)`` — True where any flag is set."""
        return (
            self.body_too_long
            | self.body_too_short
            | self.hull_area_anomaly
            | self.aspect_ratio_anomaly
            | self.insufficient_keypoints
        )


@dataclass
class QualityReport:
    """
    Top-level result of ``check_pose_quality``.

    Attributes:
        keypoint_flags: Per-keypoint anomaly flags.
        frame_flags: Per-frame anomaly flags.
        skeleton_map: Detected skeleton role mapping.
        config: Configuration used for the checks.
        median_body_length: Median snout–tailbase distance (pixels).
        median_hull_area: Median convex-hull area (pixels²).
        body_lengths: Per-frame body lengths, shape ``(T,)``.
        hull_areas: Per-frame hull areas, shape ``(T,)``.
    """

    keypoint_flags: KeypointFlags
    frame_flags: FrameFlags
    skeleton_map: SkeletonMap
    config: QualityConfig
    median_body_length: float
    median_hull_area: float
    body_lengths: np.ndarray
    hull_areas: np.ndarray

    @property
    def total_flagged_frames(self) -> int:
        """Number of frames flagged by *any* frame-level or keypoint check."""
        kp_any = self.keypoint_flags.any_flagged.any(axis=1)  # (T,)
        return int((self.frame_flags.any_flagged | kp_any).sum())

    @property
    def flagged_fraction(self) -> float:
        """Fraction of frames flagged by any check."""
        T = self.frame_flags.any_flagged.shape[0]
        if T == 0:
            return 0.0
        return self.total_flagged_frames / T

    @property
    def recommendation(self) -> str:
        """Quality label: ``"GOOD"`` (<1%), ``"REVIEW"`` (<5%), ``"POOR"`` (>=5%)."""
        frac = self.flagged_fraction
        if frac < 0.01:
            return "GOOD"
        if frac < 0.05:
            return "REVIEW"
        return "POOR"

    def summary(self) -> dict:
        """
        JSON-serialisable summary of the quality report.

        Returns:
            Dictionary with frame counts, flagged fractions, and
            recommendation.

        Example:
            >>> report.summary()["recommendation"]
            'GOOD'
        """
        T = self.frame_flags.any_flagged.shape[0]
        kp_flags = self.keypoint_flags
        ff = self.frame_flags
        return {
            "total_frames": int(T),
            "total_flagged_frames": self.total_flagged_frames,
            "flagged_fraction": round(self.flagged_fraction, 4),
            "recommendation": self.recommendation,
            "median_body_length_px": round(float(self.median_body_length), 2),
            "median_hull_area_px2": round(float(self.median_hull_area), 2),
            "keypoint_flags": {
                "spatial_outlier": int(kp_flags.spatial_outlier.sum()),
                "temporal_jump": int(kp_flags.temporal_jump.sum()),
                "missing": int(kp_flags.missing.sum()),
            },
            "frame_flags": {
                "body_too_long": int(ff.body_too_long.sum()),
                "body_too_short": int(ff.body_too_short.sum()),
                "hull_area_anomaly": int(ff.hull_area_anomaly.sum()),
                "aspect_ratio_anomaly": int(ff.aspect_ratio_anomaly.sum()),
                "insufficient_keypoints": int(ff.insufficient_keypoints.sum()),
            },
        }


# ---------------------------------------------------------------------------
# Skeleton detection
# ---------------------------------------------------------------------------

_HEAD_PATTERNS = re.compile(r"snout|nose|head|ear", re.IGNORECASE)
_TAIL_PATTERNS = re.compile(r"tail", re.IGNORECASE)
_TAILBASE_PATTERNS = re.compile(
    r"tailbase|tail_base|tail\.base|tail root", re.IGNORECASE
)
_SNOUT_PATTERNS = re.compile(r"snout|nose", re.IGNORECASE)
_PAW_PATTERNS = re.compile(r"paw|foot|hand|forelimb|hindlimb", re.IGNORECASE)
_BODY_PATTERNS = re.compile(
    r"spine|back|shoulder|hip|centroid|belly|trunk", re.IGNORECASE
)


def _normalize_name(name: str) -> str:
    """Lowercase and strip non-alphanumeric characters."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def detect_skeleton(node_names: list[str]) -> SkeletonMap:
    """
    Auto-detect skeleton roles from node names.

    Matches node names against common patterns for head, tail, paw,
    and body nodes used by SLEAP and DeepLabCut.  Falls back to an
    unknown skeleton when names are not recognised.

    Args:
        node_names: List of keypoint / node names from the skeleton.

    Returns:
        ``SkeletonMap`` with detected role indices.

    Example:
        >>> skel = detect_skeleton(["snout", "left_ear", "spine1", "tailbase"])
        >>> skel.snout_index
        0
        >>> skel.tailbase_index
        3
        >>> skel.is_known_skeleton
        True
    """
    smap = SkeletonMap(node_names=list(node_names))

    for i, name in enumerate(node_names):
        if _HEAD_PATTERNS.search(name):
            smap.head_indices.append(i)
        if _TAIL_PATTERNS.search(name):
            smap.tail_indices.append(i)
        if _PAW_PATTERNS.search(name):
            smap.paw_indices.append(i)
        if _BODY_PATTERNS.search(name):
            smap.body_indices.append(i)

    # Specific key nodes — first match wins
    for i, name in enumerate(node_names):
        if smap.snout_index is None and _SNOUT_PATTERNS.search(name):
            smap.snout_index = i
    for i, name in enumerate(node_names):
        if smap.tailbase_index is None and _TAILBASE_PATTERNS.search(name):
            smap.tailbase_index = i

    smap.is_known_skeleton = (smap.snout_index is not None
                              or smap.tailbase_index is not None
                              or len(smap.head_indices) > 0)

    return smap


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _compute_body_lengths(
    tracks: np.ndarray,
    skeleton_map: SkeletonMap,
) -> np.ndarray:
    """
    Compute per-frame body length.

    If snout and tailbase are known, uses their Euclidean distance.
    Otherwise falls back to the maximum pairwise distance among all
    valid keypoints in each frame.

    Returns:
        Array of shape ``(T,)`` with body lengths (NaN where unavailable).
    """
    T, J, _ = tracks.shape
    lengths = np.full(T, np.nan)

    if skeleton_map.snout_index is not None and skeleton_map.tailbase_index is not None:
        s = tracks[:, skeleton_map.snout_index, :]  # (T, 2)
        t = tracks[:, skeleton_map.tailbase_index, :]  # (T, 2)
        diff = s - t
        valid = np.all(np.isfinite(diff), axis=1)
        lengths[valid] = np.linalg.norm(diff[valid], axis=1)
    else:
        # Fallback: max pairwise distance among valid keypoints
        for frame in range(T):
            pts = tracks[frame]  # (J, 2)
            valid_mask = np.all(np.isfinite(pts), axis=1)
            pts_valid = pts[valid_mask]
            if pts_valid.shape[0] < 2:
                continue
            # Pairwise distances via broadcasting
            diffs = pts_valid[:, None, :] - pts_valid[None, :, :]
            dists = np.linalg.norm(diffs, axis=2)
            lengths[frame] = dists.max()

    return lengths


def _compute_hull_metrics(
    tracks: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Compute per-frame hull area and bounding-box aspect ratio.

    Returns:
        ``(hull_areas, aspect_ratios)`` — each shape ``(T,)``.
        Frames with insufficient keypoints get 0.0 / NaN respectively.
    """
    T = tracks.shape[0]
    hull_areas = np.zeros(T, dtype=np.float64)
    aspect_ratios = np.full(T, np.nan)

    for frame in range(T):
        pts = tracks[frame]  # (J, 2)
        valid_mask = np.all(np.isfinite(pts), axis=1)
        pts_valid = pts[valid_mask]

        if pts_valid.shape[0] >= 3:
            hull_areas[frame] = body_hull_area(pts_valid)

        if pts_valid.shape[0] >= 2:
            mins = pts_valid.min(axis=0)
            maxs = pts_valid.max(axis=0)
            extents = maxs - mins
            short = extents.min()
            long = extents.max()
            if short > 0:
                aspect_ratios[frame] = long / short
            else:
                aspect_ratios[frame] = np.nan

    return hull_areas, aspect_ratios


# ---------------------------------------------------------------------------
# Core check functions
# ---------------------------------------------------------------------------

def check_spatial_outliers(
    tracks: np.ndarray,
    body_lengths: np.ndarray,
    config: QualityConfig,
) -> np.ndarray:
    """
    Flag keypoints far from the centroid of the other keypoints.

    For each frame, the centroid is computed from all *other* valid
    keypoints.  A keypoint is flagged when its distance from that
    centroid exceeds ``config.spatial_outlier_factor × median_body_length``.

    Args:
        tracks: Array of shape ``(T, J, 2)``.
        body_lengths: Per-frame body lengths, shape ``(T,)``.
        config: Quality configuration.

    Returns:
        Boolean array of shape ``(T, J)`` — True where flagged.
    """
    T, J, _ = tracks.shape
    flags = np.zeros((T, J), dtype=bool)

    median_bl = float(np.nanmedian(body_lengths))
    if not np.isfinite(median_bl) or median_bl <= 0:
        return flags

    threshold = config.spatial_outlier_factor * median_bl

    for frame in range(T):
        pts = tracks[frame]  # (J, 2)
        valid = np.all(np.isfinite(pts), axis=1)
        n_valid = valid.sum()
        if n_valid < 2:
            continue

        for j in range(J):
            if not valid[j]:
                continue
            # Centroid of all OTHER valid keypoints
            others_mask = valid.copy()
            others_mask[j] = False
            if others_mask.sum() == 0:
                continue
            centroid = pts[others_mask].mean(axis=0)
            dist = np.linalg.norm(pts[j] - centroid)
            if dist > threshold:
                flags[frame, j] = True

    return flags


def check_temporal_jumps(
    tracks: np.ndarray,
    body_lengths: np.ndarray,
    config: QualityConfig,
) -> np.ndarray:
    """
    Flag keypoints with unreasonably large frame-to-frame displacement.

    A keypoint is flagged when its displacement between consecutive
    frames exceeds ``config.temporal_jump_factor × median_body_length``.
    Frame 0 is never flagged.

    If ``config.pixel_scale`` is set, an additional absolute speed check
    is applied using ``config.max_displacement_cm_per_s``.

    Args:
        tracks: Array of shape ``(T, J, 2)``.
        body_lengths: Per-frame body lengths, shape ``(T,)``.
        config: Quality configuration.

    Returns:
        Boolean array of shape ``(T, J)`` — True where flagged.
    """
    T, J, _ = tracks.shape
    flags = np.zeros((T, J), dtype=bool)

    median_bl = float(np.nanmedian(body_lengths))
    if not np.isfinite(median_bl) or median_bl <= 0:
        return flags

    threshold = config.temporal_jump_factor * median_bl

    # Vectorised displacement
    disp = np.linalg.norm(tracks[1:] - tracks[:-1], axis=2)  # (T-1, J)

    # NaN where either frame has NaN coords
    valid_cur = np.all(np.isfinite(tracks[1:]), axis=2)   # (T-1, J)
    valid_prev = np.all(np.isfinite(tracks[:-1]), axis=2)  # (T-1, J)
    both_valid = valid_cur & valid_prev

    rel_flags = (disp > threshold) & both_valid

    # Absolute speed check
    if config.pixel_scale is not None and hasattr(config.pixel_scale, "to_real"):
        max_disp_px = config.pixel_scale.to_pixels(
            config.max_displacement_cm_per_s / config.fps
        )
        rel_flags = rel_flags | ((disp > max_disp_px) & both_valid)

    flags[1:] = rel_flags
    return flags


def check_body_length(
    body_lengths: np.ndarray,
    config: QualityConfig,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Flag frames where body length is outside expected range.

    Args:
        body_lengths: Per-frame body lengths, shape ``(T,)``.
        config: Quality configuration.

    Returns:
        ``(too_short, too_long)`` — each a boolean array of shape ``(T,)``.
    """
    T = body_lengths.shape[0]
    too_short = np.zeros(T, dtype=bool)
    too_long = np.zeros(T, dtype=bool)

    median_bl = float(np.nanmedian(body_lengths))
    if not np.isfinite(median_bl) or median_bl <= 0:
        return too_short, too_long

    valid = np.isfinite(body_lengths)
    too_short[valid] = body_lengths[valid] < config.min_body_length_factor * median_bl
    too_long[valid] = body_lengths[valid] > config.max_body_length_factor * median_bl

    # Absolute cm checks
    if config.pixel_scale is not None and hasattr(config.pixel_scale, "to_real"):
        bl_cm = config.pixel_scale.to_real(body_lengths)
        bl_cm_valid = np.isfinite(bl_cm)
        too_short[bl_cm_valid] |= bl_cm[bl_cm_valid] < config.min_body_length_cm
        too_long[bl_cm_valid] |= bl_cm[bl_cm_valid] > config.max_body_length_cm

    return too_short, too_long


def check_hull_anomalies(
    hull_areas: np.ndarray,
    aspect_ratios: np.ndarray,
    config: QualityConfig,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Flag frames with anomalous hull area or bounding-box aspect ratio.

    Args:
        hull_areas: Per-frame hull areas, shape ``(T,)``.
        aspect_ratios: Per-frame bbox aspect ratios, shape ``(T,)``.
        config: Quality configuration.

    Returns:
        ``(hull_area_anomaly, aspect_ratio_anomaly)`` — each boolean
        array of shape ``(T,)``.
    """
    T = hull_areas.shape[0]
    hull_flag = np.zeros(T, dtype=bool)
    ar_flag = np.zeros(T, dtype=bool)

    # Hull area — ignore zeros (invalid hull frames)
    valid_area = hull_areas > 0
    if valid_area.any():
        median_area = float(np.median(hull_areas[valid_area]))
        if median_area > 0:
            hull_flag[valid_area] = (
                (hull_areas[valid_area] < config.hull_area_min_factor * median_area)
                | (hull_areas[valid_area] > config.hull_area_max_factor * median_area)
            )

    # Aspect ratio
    valid_ar = np.isfinite(aspect_ratios)
    ar_flag[valid_ar] = aspect_ratios[valid_ar] > config.aspect_ratio_max

    return hull_flag, ar_flag


# ---------------------------------------------------------------------------
# High-level API
# ---------------------------------------------------------------------------

def check_pose_quality(
    tracks: ArrayLike,
    node_names: Optional[list[str]] = None,
    config: Optional[QualityConfig] = None,
) -> QualityReport:
    """
    Run all pose quality checks on a tracks array.

    This is the main entry point.  It computes body-relative
    spatial statistics and flags geometric anomalies that survive
    confidence filtering.

    Args:
        tracks: Array of shape ``(T, J, 2)`` with keypoint coordinates.
                NaN values indicate missing / low-confidence keypoints.
        node_names: Optional list of ``J`` node names for skeleton
                    detection.  If ``None``, geometric-only checks are used.
        config: Optional ``QualityConfig``.  Defaults are suitable for
                120 fps mouse tracking.

    Returns:
        ``QualityReport`` with per-keypoint and per-frame flags,
        computed metrics, and a quality recommendation.

    Example:
        >>> import numpy as np
        >>> tracks = np.random.randn(500, 7, 2) * 10 + 100
        >>> report = check_pose_quality(tracks)
        >>> report.recommendation
        'GOOD'
    """
    if config is None:
        config = QualityConfig()

    tracks = np.asarray(tracks, dtype=np.float64)
    if tracks.ndim != 3 or tracks.shape[2] != 2:
        raise ValueError(f"Expected tracks shape (T, J, 2), got {tracks.shape}")

    T, J, _ = tracks.shape

    # Skeleton detection
    if node_names is not None:
        if len(node_names) != J:
            raise ValueError(
                f"node_names length ({len(node_names)}) != number of "
                f"keypoints ({J})"
            )
        skeleton_map = detect_skeleton(node_names)
    else:
        skeleton_map = SkeletonMap()

    # Compute metrics
    body_lengths = _compute_body_lengths(tracks, skeleton_map)
    hull_areas, aspect_ratios = _compute_hull_metrics(tracks)

    median_bl = float(np.nanmedian(body_lengths))
    if not np.isfinite(median_bl):
        median_bl = 0.0

    valid_area = hull_areas[hull_areas > 0]
    median_ha = float(np.median(valid_area)) if valid_area.size > 0 else 0.0

    # Missing keypoints
    missing = ~np.all(np.isfinite(tracks), axis=2)  # (T, J)

    # Insufficient keypoints per frame
    n_valid = np.sum(np.all(np.isfinite(tracks), axis=2), axis=1)  # (T,)
    insufficient = n_valid < config.min_valid_keypoints

    # Run checks
    spatial_outlier = check_spatial_outliers(tracks, body_lengths, config)
    temporal_jump = check_temporal_jumps(tracks, body_lengths, config)
    too_short, too_long = check_body_length(body_lengths, config)
    hull_anomaly, ar_anomaly = check_hull_anomalies(
        hull_areas, aspect_ratios, config
    )

    kp_flags = KeypointFlags(
        spatial_outlier=spatial_outlier,
        temporal_jump=temporal_jump,
        missing=missing,
    )

    frame_flags = FrameFlags(
        body_too_long=too_long,
        body_too_short=too_short,
        hull_area_anomaly=hull_anomaly,
        aspect_ratio_anomaly=ar_anomaly,
        insufficient_keypoints=insufficient,
    )

    return QualityReport(
        keypoint_flags=kp_flags,
        frame_flags=frame_flags,
        skeleton_map=skeleton_map,
        config=config,
        median_body_length=median_bl,
        median_hull_area=median_ha,
        body_lengths=body_lengths,
        hull_areas=hull_areas,
    )


def check_slp_quality(
    slp_path: Union[str, object],
    instance: int = 0,
    config: Optional[QualityConfig] = None,
) -> QualityReport:
    """
    Run pose quality checks on a SLEAP ``.slp`` file.

    Convenience wrapper that loads tracking data via ``sleap-io`` and
    calls ``check_pose_quality``.

    Args:
        slp_path: Path to a ``.slp`` file.
        instance: Which instance (animal) to analyse (default: 0).
        config: Optional ``QualityConfig``.

    Returns:
        ``QualityReport``.

    Raises:
        ImportError: If ``sleap-io`` is not installed.

    Example:
        >>> report = check_slp_quality("tracking.slp")
        >>> print(report.summary())
    """
    try:
        import sleap_io as sio
    except ImportError:
        raise ImportError(
            "sleap-io is required for check_slp_quality. "
            "Install with: pip install 'vibing[sleap]'"
        )

    labels = sio.load_slp(str(slp_path))
    node_names = [n.name for n in labels.skeleton.nodes]

    # Build (T, J, 2) array
    T = len(labels.labeled_frames)
    J = len(node_names)
    tracks = np.full((T, J, 2), np.nan)

    for t, lf in enumerate(labels.labeled_frames):
        if instance < len(lf.instances):
            inst = lf.instances[instance]
            pts = inst.numpy()  # (J, 2) — NaN where not visible
            valid = np.all(np.isfinite(pts), axis=1)
            tracks[t, valid, :] = pts[valid]

    return check_pose_quality(tracks, node_names=node_names, config=config)
