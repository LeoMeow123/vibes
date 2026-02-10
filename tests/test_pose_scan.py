"""Tests for vibing.pose.scan module."""

import json
from pathlib import Path

import numpy as np
import pytest

from vibing.pose.quality import (
    FrameFlags,
    KeypointFlags,
    QualityConfig,
    QualityReport,
    SkeletonMap,
)
from vibing.pose.scan import (
    _extract_flagged_indices,
    _parse_slp_filename,
    _report_to_manifest_entry,
    scan_slp_quality,
)


# ---------------------------------------------------------------------------
# _parse_slp_filename
# ---------------------------------------------------------------------------

def test_parse_slp_filename_valid():
    result = _parse_slp_filename("Day1_15666_Trial3.slp")
    assert result == {"day": 1, "mouse_id": "15666", "trial": 3}


def test_parse_slp_filename_valid_multidigit():
    result = _parse_slp_filename("Day12_ABC01_Trial10.preds.v2.slp")
    assert result == {"day": 12, "mouse_id": "ABC01", "trial": 10}


def test_parse_slp_filename_invalid():
    assert _parse_slp_filename("random_file.slp") is None
    assert _parse_slp_filename("tracking.slp") is None
    assert _parse_slp_filename("") is None


# ---------------------------------------------------------------------------
# _extract_flagged_indices
# ---------------------------------------------------------------------------

def test_extract_flagged_indices_no_truncation():
    arr = np.array([False, True, False, True, False])
    result = _extract_flagged_indices(arr, max_count=500)
    assert result == [1, 3]


def test_extract_flagged_indices_empty():
    arr = np.zeros(100, dtype=bool)
    result = _extract_flagged_indices(arr, max_count=500)
    assert result == []


def test_extract_flagged_indices_with_truncation():
    arr = np.ones(20, dtype=bool)
    result = _extract_flagged_indices(arr, max_count=5)
    assert len(result) == 6  # 5 indices + sentinel
    assert result[:5] == [0, 1, 2, 3, 4]
    assert "...truncated at 5/20" in result[-1]


def test_extract_flagged_indices_exact_limit():
    arr = np.ones(5, dtype=bool)
    result = _extract_flagged_indices(arr, max_count=5)
    assert result == [0, 1, 2, 3, 4]


# ---------------------------------------------------------------------------
# _report_to_manifest_entry
# ---------------------------------------------------------------------------

def _make_report(T=100, J=7):
    """Build a minimal QualityReport for testing."""
    kf = KeypointFlags(
        spatial_outlier=np.zeros((T, J), dtype=bool),
        temporal_jump=np.zeros((T, J), dtype=bool),
        missing=np.zeros((T, J), dtype=bool),
    )
    # Flag a few things
    kf.spatial_outlier[10, 2] = True
    kf.temporal_jump[20, 3] = True
    kf.missing[30, :] = True

    ff = FrameFlags(
        body_too_long=np.zeros(T, dtype=bool),
        body_too_short=np.zeros(T, dtype=bool),
        hull_area_anomaly=np.zeros(T, dtype=bool),
        aspect_ratio_anomaly=np.zeros(T, dtype=bool),
        insufficient_keypoints=np.zeros(T, dtype=bool),
    )
    ff.body_too_long[50] = True
    ff.insufficient_keypoints[30] = True

    return QualityReport(
        keypoint_flags=kf,
        frame_flags=ff,
        skeleton_map=SkeletonMap(),
        config=QualityConfig(),
        median_body_length=50.0,
        median_hull_area=1200.0,
        body_lengths=np.full(T, 50.0),
        hull_areas=np.full(T, 1200.0),
    )


def test_report_to_manifest_entry():
    report = _make_report()
    entry = _report_to_manifest_entry(
        "Day1_15666_Trial3.slp",
        "pose/Day1_15666_Trial3.slp",
        report,
        max_flagged=500,
        metadata={"day": 1, "mouse_id": "15666", "trial": 3},
    )

    # Should be JSON-serialisable
    json_str = json.dumps(entry)
    assert isinstance(json_str, str)

    assert entry["filename"] == "Day1_15666_Trial3.slp"
    assert entry["status"] == "ok"
    assert entry["recommendation"] in ("GOOD", "REVIEW", "POOR")
    assert entry["total_frames"] == 100
    assert entry["total_flagged_frames"] >= 1
    assert entry["metadata"]["day"] == 1
    assert 10 in entry["flagged_frames"]["spatial_outlier"]
    assert 20 in entry["flagged_frames"]["temporal_jump"]
    assert 50 in entry["flagged_frames"]["body_too_long"]
    assert "any" in entry["flagged_frames"]
    assert entry["keypoint_counts"]["spatial_outlier"] == 1
    assert entry["frame_counts"]["body_too_long"] == 1


def test_report_to_manifest_entry_missing_excluded_from_any():
    """Missing keypoints should NOT inflate 'any' or total_flagged_frames."""
    T, J = 100, 7
    kf = KeypointFlags(
        spatial_outlier=np.zeros((T, J), dtype=bool),
        temporal_jump=np.zeros((T, J), dtype=bool),
        missing=np.zeros((T, J), dtype=bool),
    )
    # Make 80% of frames have at least one missing keypoint
    kf.missing[:80, 0] = True

    ff = FrameFlags(
        body_too_long=np.zeros(T, dtype=bool),
        body_too_short=np.zeros(T, dtype=bool),
        hull_area_anomaly=np.zeros(T, dtype=bool),
        aspect_ratio_anomaly=np.zeros(T, dtype=bool),
        insufficient_keypoints=np.zeros(T, dtype=bool),
    )
    # Only 2 actual anomalies
    ff.body_too_long[50] = True
    ff.hull_area_anomaly[60] = True

    report = QualityReport(
        keypoint_flags=kf,
        frame_flags=ff,
        skeleton_map=SkeletonMap(),
        config=QualityConfig(),
        median_body_length=50.0,
        median_hull_area=1200.0,
        body_lengths=np.full(T, 50.0),
        hull_areas=np.full(T, 1200.0),
    )
    entry = _report_to_manifest_entry(
        "test.slp", "test.slp", report, max_flagged=500, metadata=None,
    )
    # "any" should only have 2 frames (the real anomalies), not 80+
    any_frames = [f for f in entry["flagged_frames"]["any"] if isinstance(f, int)]
    assert len(any_frames) == 2
    assert 50 in any_frames
    assert 60 in any_frames
    # total_flagged_frames should reflect anomalies only
    assert entry["total_flagged_frames"] == 2
    # Missing info is still present
    assert entry["keypoint_counts"]["missing"] == 80
    assert entry["recommendation"] == "REVIEW"  # 2/100 = 2% → REVIEW


def test_report_to_manifest_entry_no_metadata():
    report = _make_report()
    entry = _report_to_manifest_entry(
        "tracking.slp", "tracking.slp", report, max_flagged=500, metadata=None,
    )
    assert "metadata" not in entry


# ---------------------------------------------------------------------------
# scan_slp_quality — end-to-end
# ---------------------------------------------------------------------------

SLP_DIR = Path("/root/vast/leo/GoPro-Tmaze-pipline/test_output/pose")


@pytest.mark.skipif(
    not SLP_DIR.exists() or not list(SLP_DIR.glob("*.slp")),
    reason="No .slp test files available",
)
def test_scan_slp_quality_end_to_end(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    result = scan_slp_quality(
        SLP_DIR,
        output_path=manifest_path,
        verbose=False,
    )

    # Manifest written to disk
    assert manifest_path.exists()
    with open(manifest_path) as f:
        on_disk = json.load(f)

    # Structure checks
    assert result["version"] == 1
    assert "created_at" in result
    assert "summary" in result
    assert "files" in result
    assert result["summary"]["total_files"] > 0
    assert result["summary"]["total_files"] == len(result["files"])

    # At least one file should have processed successfully
    ok_files = [f for f in result["files"] if f["status"] == "ok"]
    assert len(ok_files) > 0

    # Verify on-disk matches returned dict
    assert on_disk["summary"]["total_files"] == result["summary"]["total_files"]


@pytest.mark.skipif(
    not SLP_DIR.exists() or not list(SLP_DIR.glob("*.slp")),
    reason="No .slp test files available",
)
def test_scan_slp_quality_recursive(tmp_path):
    # The SLP_DIR may have files in subdirectories too
    manifest_path = tmp_path / "manifest.json"
    result = scan_slp_quality(
        SLP_DIR.parent,  # test_output/
        output_path=manifest_path,
        recursive=True,
        verbose=False,
    )
    assert result["summary"]["total_files"] >= 1


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_scan_slp_quality_nonexistent_dir():
    with pytest.raises(FileNotFoundError):
        scan_slp_quality("/nonexistent/path/to/nowhere")


def test_scan_slp_quality_error_handling(tmp_path):
    """A corrupt .slp file should produce an error entry, not crash."""
    bad_file = tmp_path / "corrupt.slp"
    bad_file.write_text("this is not a valid slp file")

    result = scan_slp_quality(tmp_path, verbose=False)

    assert result["summary"]["total_files"] == 1
    assert result["summary"]["error"] == 1
    assert result["files"][0]["status"] == "error"
    assert "error_message" in result["files"][0]


def test_scan_slp_quality_empty_dir(tmp_path):
    """Empty directory should produce a valid manifest with zero files."""
    result = scan_slp_quality(tmp_path, verbose=False)
    assert result["summary"]["total_files"] == 0
    assert result["files"] == []
