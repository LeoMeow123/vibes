"""Tests for vibing.pose.quality module."""

import numpy as np
import pytest

from vibing.pose.quality import (
    KeypointFlags,
    FrameFlags,
    QualityConfig,
    QualityReport,
    SkeletonMap,
    check_body_length,
    check_hull_anomalies,
    check_pose_quality,
    check_spatial_outliers,
    check_temporal_jumps,
    detect_skeleton,
    _compute_body_lengths,
    _compute_hull_metrics,
    _normalize_name,
)


# ---------------------------------------------------------------------------
# Fixtures — reusable test data
# ---------------------------------------------------------------------------

@pytest.fixture
def clean_tracks():
    """Well-behaved (T=200, J=7, 2) tracks with known body length ~50px."""
    rng = np.random.RandomState(42)
    T, J = 200, 7
    # Base position drifts slowly
    base = np.cumsum(rng.randn(T, 1, 2) * 0.5, axis=0) + 300
    # Keypoints scatter around base within ~25px
    offsets = rng.randn(T, J, 2) * 8
    # Fix snout (idx 0) and tailbase (idx 6) for a ~50px body length
    offsets[:, 0, :] = [25, 0]
    offsets[:, 6, :] = [-25, 0]
    return base + offsets


@pytest.fixture
def node_names_mouse():
    return ["snout", "left_ear", "right_ear", "spine1", "spine2", "left_hip", "tailbase"]


@pytest.fixture
def default_config():
    return QualityConfig()


# ---------------------------------------------------------------------------
# _normalize_name
# ---------------------------------------------------------------------------

def test_normalize_name_basic():
    assert _normalize_name("Snout") == "snout"
    assert _normalize_name("tail_base") == "tailbase"
    assert _normalize_name("Left-Ear") == "leftear"
    assert _normalize_name("SPINE.1") == "spine1"


# ---------------------------------------------------------------------------
# detect_skeleton
# ---------------------------------------------------------------------------

def test_detect_skeleton_mouse(node_names_mouse):
    skel = detect_skeleton(node_names_mouse)
    assert skel.snout_index == 0
    assert skel.tailbase_index == 6
    assert 0 in skel.head_indices  # snout
    assert 1 in skel.head_indices  # left_ear
    assert 2 in skel.head_indices  # right_ear
    assert 6 in skel.tail_indices  # tailbase
    assert skel.is_known_skeleton is True


def test_detect_skeleton_dlc_style():
    names = ["nose", "left_ear", "right_ear", "neck", "tail_base", "tail_tip"]
    skel = detect_skeleton(names)
    assert skel.snout_index == 0
    assert skel.tailbase_index == 4
    assert skel.is_known_skeleton is True


def test_detect_skeleton_unknown():
    names = ["pt0", "pt1", "pt2", "pt3"]
    skel = detect_skeleton(names)
    assert skel.snout_index is None
    assert skel.tailbase_index is None
    assert skel.is_known_skeleton is False


def test_detect_skeleton_partial():
    """Only head nodes, no tail — still 'known' since head_indices non-empty."""
    names = ["snout", "ear_left", "pt0", "pt1"]
    skel = detect_skeleton(names)
    assert skel.snout_index == 0
    assert skel.tailbase_index is None
    assert skel.is_known_skeleton is True


def test_detect_skeleton_empty():
    skel = detect_skeleton([])
    assert skel.is_known_skeleton is False
    assert skel.node_names == []


# ---------------------------------------------------------------------------
# _compute_body_lengths
# ---------------------------------------------------------------------------

def test_body_lengths_known_skeleton(clean_tracks, node_names_mouse):
    skel = detect_skeleton(node_names_mouse)
    bl = _compute_body_lengths(clean_tracks, skel)
    assert bl.shape == (200,)
    # snout–tailbase offset is ~50px
    np.testing.assert_allclose(np.nanmedian(bl), 50.0, atol=2.0)


def test_body_lengths_unknown_skeleton(clean_tracks):
    skel = SkeletonMap()  # unknown
    bl = _compute_body_lengths(clean_tracks, skel)
    assert bl.shape == (200,)
    # Fallback: max pairwise distance — should be >= 50
    assert np.nanmedian(bl) > 40


def test_body_lengths_with_nans():
    tracks = np.full((5, 3, 2), np.nan)
    skel = SkeletonMap()
    bl = _compute_body_lengths(tracks, skel)
    assert np.all(np.isnan(bl))


# ---------------------------------------------------------------------------
# _compute_hull_metrics
# ---------------------------------------------------------------------------

def test_hull_metrics_basic(clean_tracks):
    areas, ratios = _compute_hull_metrics(clean_tracks)
    assert areas.shape == (200,)
    assert ratios.shape == (200,)
    # Areas should be positive for well-formed tracks
    assert (areas > 0).sum() > 190
    # Aspect ratios should be >= 1 (by definition, long/short)
    valid_ar = ratios[np.isfinite(ratios)]
    assert valid_ar.min() >= 1.0
    # Median should be reasonable for a compact body
    assert np.median(valid_ar) < 10.0


def test_hull_metrics_all_nan():
    tracks = np.full((5, 4, 2), np.nan)
    areas, ratios = _compute_hull_metrics(tracks)
    np.testing.assert_array_equal(areas, 0.0)
    assert np.all(np.isnan(ratios))


# ---------------------------------------------------------------------------
# check_spatial_outliers
# ---------------------------------------------------------------------------

def test_spatial_outliers_clean(clean_tracks, default_config):
    bl = np.full(200, 50.0)
    flags = check_spatial_outliers(clean_tracks, bl, default_config)
    assert flags.shape == (200, 7)
    # Clean tracks should have very few outliers
    assert flags.sum() < 10


def test_spatial_outliers_with_injected_outlier(clean_tracks, default_config):
    tracks = clean_tracks.copy()
    # Move keypoint 3 far away in frame 50
    tracks[50, 3, :] += 500
    bl = np.full(200, 50.0)
    flags = check_spatial_outliers(tracks, bl, default_config)
    assert flags[50, 3] is np.True_


def test_spatial_outliers_zero_body_length(clean_tracks, default_config):
    bl = np.zeros(200)
    flags = check_spatial_outliers(clean_tracks, bl, default_config)
    # Should return all False when body length is zero
    assert flags.sum() == 0


# ---------------------------------------------------------------------------
# check_temporal_jumps
# ---------------------------------------------------------------------------

def test_temporal_jumps_clean(clean_tracks, default_config):
    bl = np.full(200, 50.0)
    flags = check_temporal_jumps(clean_tracks, bl, default_config)
    assert flags.shape == (200, 7)
    assert flags[0].sum() == 0  # Frame 0 is never flagged
    # Clean tracks should have very few jumps
    assert flags.sum() < 5


def test_temporal_jumps_with_teleport(clean_tracks, default_config):
    tracks = clean_tracks.copy()
    # Teleport keypoint 2 at frame 100
    tracks[100, 2, :] += 300
    bl = np.full(200, 50.0)
    flags = check_temporal_jumps(tracks, bl, default_config)
    # Should flag frame 100 (jump in) and frame 101 (jump back)
    assert flags[100, 2]
    assert flags[101, 2]


def test_temporal_jumps_frame_zero_never_flagged():
    tracks = np.zeros((3, 2, 2))
    tracks[0] = [[0, 0], [10, 10]]
    tracks[1] = [[1000, 1000], [10, 10]]  # Huge jump for kp 0
    tracks[2] = [[1001, 1001], [10, 10]]
    bl = np.full(3, 14.14)
    cfg = QualityConfig()
    flags = check_temporal_jumps(tracks, bl, cfg)
    assert not flags[0].any()
    assert flags[1, 0]


# ---------------------------------------------------------------------------
# check_body_length
# ---------------------------------------------------------------------------

def test_body_length_normal():
    bl = np.full(100, 50.0)
    cfg = QualityConfig()
    too_short, too_long = check_body_length(bl, cfg)
    assert too_short.sum() == 0
    assert too_long.sum() == 0


def test_body_length_short_frames():
    bl = np.full(100, 50.0)
    bl[10:15] = 5.0  # Very short
    cfg = QualityConfig(min_body_length_factor=0.3)
    too_short, too_long = check_body_length(bl, cfg)
    assert too_short[10:15].all()
    assert too_long.sum() == 0


def test_body_length_long_frames():
    bl = np.full(100, 50.0)
    bl[20:25] = 200.0  # Very long
    cfg = QualityConfig(max_body_length_factor=2.5)
    too_short, too_long = check_body_length(bl, cfg)
    assert too_long[20:25].all()


def test_body_length_all_nan():
    bl = np.full(10, np.nan)
    cfg = QualityConfig()
    too_short, too_long = check_body_length(bl, cfg)
    assert too_short.sum() == 0
    assert too_long.sum() == 0


# ---------------------------------------------------------------------------
# check_hull_anomalies
# ---------------------------------------------------------------------------

def test_hull_anomalies_normal():
    areas = np.full(100, 1000.0)
    ratios = np.full(100, 2.0)
    cfg = QualityConfig()
    hull_flag, ar_flag = check_hull_anomalies(areas, ratios, cfg)
    assert hull_flag.sum() == 0
    assert ar_flag.sum() == 0


def test_hull_anomalies_extreme_area():
    areas = np.full(100, 1000.0)
    areas[5] = 50.0  # Very small
    areas[10] = 10000.0  # Very large
    ratios = np.full(100, 2.0)
    cfg = QualityConfig(hull_area_min_factor=0.2, hull_area_max_factor=3.0)
    hull_flag, ar_flag = check_hull_anomalies(areas, ratios, cfg)
    assert hull_flag[5]
    assert hull_flag[10]


def test_hull_anomalies_extreme_aspect_ratio():
    areas = np.full(100, 1000.0)
    ratios = np.full(100, 2.0)
    ratios[42] = 8.0
    cfg = QualityConfig(aspect_ratio_max=5.0)
    hull_flag, ar_flag = check_hull_anomalies(areas, ratios, cfg)
    assert ar_flag[42]
    assert ar_flag.sum() == 1


# ---------------------------------------------------------------------------
# KeypointFlags / FrameFlags dataclasses
# ---------------------------------------------------------------------------

def test_keypoint_flags_any_flagged():
    T, J = 10, 3
    kf = KeypointFlags(
        spatial_outlier=np.zeros((T, J), dtype=bool),
        temporal_jump=np.zeros((T, J), dtype=bool),
        missing=np.zeros((T, J), dtype=bool),
    )
    assert kf.any_flagged.sum() == 0
    kf.spatial_outlier[2, 1] = True
    assert kf.any_flagged[2, 1]


def test_keypoint_flags_flagged_fraction():
    T, J = 10, 4
    kf = KeypointFlags(
        spatial_outlier=np.zeros((T, J), dtype=bool),
        temporal_jump=np.zeros((T, J), dtype=bool),
        missing=np.zeros((T, J), dtype=bool),
    )
    assert kf.flagged_fraction() == 0.0
    kf.temporal_jump[0, 0] = True
    assert kf.flagged_fraction() == pytest.approx(1 / 40)


def test_frame_flags_any_flagged():
    T = 20
    ff = FrameFlags(
        body_too_long=np.zeros(T, dtype=bool),
        body_too_short=np.zeros(T, dtype=bool),
        hull_area_anomaly=np.zeros(T, dtype=bool),
        aspect_ratio_anomaly=np.zeros(T, dtype=bool),
        insufficient_keypoints=np.zeros(T, dtype=bool),
    )
    assert ff.any_flagged.sum() == 0
    ff.hull_area_anomaly[5] = True
    assert ff.any_flagged[5]


# ---------------------------------------------------------------------------
# QualityReport
# ---------------------------------------------------------------------------

def test_quality_report_recommendation_good(node_names_mouse):
    """Tightly controlled tracks should score GOOD."""
    rng = np.random.RandomState(0)
    T, J = 200, 7
    base = np.cumsum(rng.randn(T, 1, 2) * 0.2, axis=0) + 300
    # Small consistent offsets per keypoint — same every frame
    kp_offsets = np.array([
        [25, 0], [15, 10], [15, -10], [5, 0], [-5, 0], [-15, 5], [-25, 0]
    ], dtype=np.float64)
    tracks = base + kp_offsets[None, :, :]
    # Add tiny noise
    tracks += rng.randn(T, J, 2) * 0.5
    report = check_pose_quality(tracks, node_names=node_names_mouse)
    assert report.recommendation == "GOOD"
    assert report.flagged_fraction < 0.01


def test_quality_report_summary_keys(clean_tracks):
    report = check_pose_quality(clean_tracks)
    s = report.summary()
    assert "total_frames" in s
    assert "total_flagged_frames" in s
    assert "flagged_fraction" in s
    assert "recommendation" in s
    assert "median_body_length_px" in s
    assert "median_hull_area_px2" in s
    assert "keypoint_flags" in s
    assert "frame_flags" in s


def test_quality_report_total_flagged_frames():
    """Inject anomalies and verify total_flagged_frames counts correctly."""
    rng = np.random.RandomState(99)
    tracks = rng.randn(50, 5, 2) * 10 + 200
    # Inject spatial outlier
    tracks[10, 0, :] += 1000
    # Inject NaN frame
    tracks[20, :, :] = np.nan
    report = check_pose_quality(tracks)
    assert report.total_flagged_frames >= 2


# ---------------------------------------------------------------------------
# check_pose_quality — integration
# ---------------------------------------------------------------------------

def test_check_pose_quality_basic(clean_tracks, node_names_mouse):
    report = check_pose_quality(clean_tracks, node_names=node_names_mouse)
    assert isinstance(report, QualityReport)
    assert report.median_body_length > 0
    assert report.body_lengths.shape == (200,)
    assert report.hull_areas.shape == (200,)


def test_check_pose_quality_no_node_names(clean_tracks):
    report = check_pose_quality(clean_tracks)
    assert isinstance(report, QualityReport)
    assert report.skeleton_map.is_known_skeleton is False


def test_check_pose_quality_bad_shape():
    with pytest.raises(ValueError, match="Expected tracks shape"):
        check_pose_quality(np.zeros((10, 5)))


def test_check_pose_quality_node_names_mismatch():
    tracks = np.zeros((10, 5, 2))
    with pytest.raises(ValueError, match="node_names length"):
        check_pose_quality(tracks, node_names=["a", "b", "c"])


def test_check_pose_quality_all_nan():
    tracks = np.full((30, 4, 2), np.nan)
    report = check_pose_quality(tracks)
    assert report.recommendation in ("GOOD", "REVIEW", "POOR")
    assert report.frame_flags.insufficient_keypoints.all()


def test_check_pose_quality_injected_anomalies():
    """Multiple anomaly types in one run."""
    rng = np.random.RandomState(7)
    T, J = 300, 6
    base = np.cumsum(rng.randn(T, 1, 2) * 0.3, axis=0) + 300
    offsets = rng.randn(T, J, 2) * 5
    offsets[:, 0, :] = [20, 0]   # snout
    offsets[:, 5, :] = [-20, 0]  # tailbase
    tracks = base + offsets

    # Spatial outlier
    tracks[50, 2, :] += 500
    # Temporal jump
    tracks[100, 3, :] += 400
    # Missing keypoints
    tracks[150, :, :] = np.nan

    names = ["snout", "ear_L", "ear_R", "spine", "hip", "tailbase"]
    report = check_pose_quality(tracks, node_names=names)

    # The injected outlier should be caught
    assert report.keypoint_flags.spatial_outlier[50, 2]
    # The temporal jump should be caught
    assert report.keypoint_flags.temporal_jump[100, 3]
    # The NaN frame should be flagged as insufficient + missing
    assert report.frame_flags.insufficient_keypoints[150]
    assert report.keypoint_flags.missing[150].all()


def test_check_pose_quality_custom_config(clean_tracks):
    cfg = QualityConfig(spatial_outlier_factor=100.0, temporal_jump_factor=100.0)
    report = check_pose_quality(clean_tracks, config=cfg)
    # With very loose thresholds, nothing should be flagged for spatial/temporal
    assert report.keypoint_flags.spatial_outlier.sum() == 0
    assert report.keypoint_flags.temporal_jump.sum() == 0


# ---------------------------------------------------------------------------
# PixelScale integration
# ---------------------------------------------------------------------------

def test_body_length_with_pixel_scale():
    """Absolute cm checks via PixelScale."""
    from vibing.geometry.scale import PixelScale

    scale = PixelScale(px_per_unit=10.0, unit="cm")  # 10 px/cm
    bl = np.full(50, 100.0)  # 100px = 10cm body → within default 3–15cm
    cfg = QualityConfig(pixel_scale=scale)
    too_short, too_long = check_body_length(bl, cfg)
    assert too_short.sum() == 0
    assert too_long.sum() == 0

    # Now make body 2px = 0.2cm → below min_body_length_cm=3.0
    bl[10] = 2.0
    too_short, too_long = check_body_length(bl, cfg)
    assert too_short[10]


def test_temporal_jumps_with_pixel_scale():
    """Absolute speed check via PixelScale."""
    from vibing.geometry.scale import PixelScale

    scale = PixelScale(px_per_unit=10.0, unit="cm")  # 10 px/cm
    T, J = 10, 2
    tracks = np.zeros((T, J, 2))
    tracks[:, 0, 0] = np.arange(T) * 1.0  # Slow drift
    tracks[:, 1, 0] = np.arange(T) * 1.0

    # Inject large jump: 2000px in one frame → 200cm at 10px/cm
    # At 120fps that's 200*120 = 24000 cm/s → way above 150 cm/s
    tracks[5, 0, 0] += 2000
    bl = np.full(T, 50.0)
    cfg = QualityConfig(pixel_scale=scale, fps=120.0)
    flags = check_temporal_jumps(tracks, bl, cfg)
    assert flags[5, 0]
