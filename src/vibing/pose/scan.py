"""
Batch pose quality scanning.

Scan all ``.slp`` files in a directory, run quality checks on each,
and write a JSON manifest summarising which files need review.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

import numpy as np

from vibing.pose.quality import QualityConfig, QualityReport, check_slp_quality

# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

_FILENAME_RE = re.compile(r"Day(\d+)_(\w+)_Trial(\d+)")


def _parse_slp_filename(name: str) -> Optional[dict]:
    """Extract day/mouse_id/trial from a standard SLP filename.

    >>> _parse_slp_filename("Day1_15666_Trial3.slp")
    {'day': 1, 'mouse_id': '15666', 'trial': 3}
    >>> _parse_slp_filename("random_file.slp") is None
    True
    """
    m = _FILENAME_RE.search(name)
    if m is None:
        return None
    return {
        "day": int(m.group(1)),
        "mouse_id": m.group(2),
        "trial": int(m.group(3)),
    }


def _extract_flagged_indices(
    bool_array: np.ndarray,
    max_count: int,
) -> list:
    """Return indices where *bool_array* is True, truncated to *max_count*.

    If the full list exceeds *max_count*, the returned list is truncated and
    a sentinel string ``"...truncated at {max_count}/{total}"`` is appended.
    """
    indices = np.flatnonzero(bool_array).tolist()
    if len(indices) <= max_count:
        return indices
    total = len(indices)
    return indices[:max_count] + [f"...truncated at {max_count}/{total}"]


def _report_to_manifest_entry(
    filename: str,
    rel_path: str,
    report: QualityReport,
    max_flagged: int,
    metadata: Optional[dict],
) -> dict:
    """Convert a :class:`QualityReport` to a JSON-serialisable manifest entry."""
    kf = report.keypoint_flags
    ff = report.frame_flags
    T = ff.any_flagged.shape[0]

    # Keypoint flags (T, J) → frame-level (T,) via .any(axis=1)
    kp_frame_spatial = kf.spatial_outlier.any(axis=1)
    kp_frame_jump = kf.temporal_jump.any(axis=1)
    kp_frame_missing = kf.missing.any(axis=1)

    # Union of *anomaly* flags for "any" — missing is informational, not an
    # anomaly (partial keypoint visibility is normal for detailed skeletons).
    # The insufficient_keypoints frame flag already catches frames where too
    # few keypoints are visible.
    any_anomaly = (
        kp_frame_spatial
        | kp_frame_jump
        | ff.body_too_long
        | ff.body_too_short
        | ff.hull_area_anomaly
        | ff.aspect_ratio_anomaly
        | ff.insufficient_keypoints
    )
    total_flagged = int(any_anomaly.sum())
    flagged_frac = total_flagged / T if T > 0 else 0.0

    # Recommendation based on anomaly fraction (excluding missing)
    if flagged_frac < 0.01:
        recommendation = "GOOD"
    elif flagged_frac < 0.05:
        recommendation = "REVIEW"
    else:
        recommendation = "POOR"

    entry = {
        "filename": filename,
        "path": rel_path,
        "status": "ok",
        "recommendation": recommendation,
        "total_frames": int(T),
        "total_flagged_frames": total_flagged,
        "flagged_fraction": round(flagged_frac, 4),
        "median_body_length_px": round(float(report.median_body_length), 2),
        "median_hull_area_px2": round(float(report.median_hull_area), 2),
        "keypoint_counts": {
            "spatial_outlier": int(kf.spatial_outlier.sum()),
            "temporal_jump": int(kf.temporal_jump.sum()),
            "missing": int(kf.missing.sum()),
        },
        "frame_counts": {
            "body_too_long": int(ff.body_too_long.sum()),
            "body_too_short": int(ff.body_too_short.sum()),
            "hull_area_anomaly": int(ff.hull_area_anomaly.sum()),
            "aspect_ratio_anomaly": int(ff.aspect_ratio_anomaly.sum()),
            "insufficient_keypoints": int(ff.insufficient_keypoints.sum()),
        },
        "flagged_frames": {
            "spatial_outlier": _extract_flagged_indices(kp_frame_spatial, max_flagged),
            "temporal_jump": _extract_flagged_indices(kp_frame_jump, max_flagged),
            "missing": _extract_flagged_indices(kp_frame_missing, max_flagged),
            "body_too_long": _extract_flagged_indices(ff.body_too_long, max_flagged),
            "body_too_short": _extract_flagged_indices(ff.body_too_short, max_flagged),
            "hull_area_anomaly": _extract_flagged_indices(
                ff.hull_area_anomaly, max_flagged
            ),
            "aspect_ratio_anomaly": _extract_flagged_indices(
                ff.aspect_ratio_anomaly, max_flagged
            ),
            "insufficient_keypoints": _extract_flagged_indices(
                ff.insufficient_keypoints, max_flagged
            ),
            "any": _extract_flagged_indices(any_anomaly, max_flagged),
        },
    }

    if metadata is not None:
        entry["metadata"] = metadata

    return entry


# ---------------------------------------------------------------------------
# Config serialisation
# ---------------------------------------------------------------------------

def _config_to_dict(config: QualityConfig) -> dict:
    """Serialise a QualityConfig to a JSON-safe dict."""
    d = asdict(config)
    # pixel_scale is not JSON-serialisable; store a string representation
    ps = d.pop("pixel_scale", None)
    if ps is not None:
        d["pixel_scale"] = str(config.pixel_scale)
    else:
        d["pixel_scale"] = None
    return d


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scan_slp_quality(
    slp_dir: Union[str, Path],
    output_path: Union[str, Path, None] = None,
    config: Optional[QualityConfig] = None,
    *,
    patterns: Optional[list[str]] = None,
    recursive: bool = False,
    instance: int = 0,
    max_flagged_per_category: int = 500,
    verbose: bool = True,
) -> dict:
    """Batch-scan ``.slp`` files for pose quality issues.

    Walks *slp_dir* for files matching *patterns*, runs
    :func:`~vibing.pose.quality.check_slp_quality` on each, and writes
    a JSON manifest summarising per-file quality.

    Args:
        slp_dir: Directory containing ``.slp`` files.
        output_path: Where to write the JSON manifest.  Defaults to
            ``slp_dir / "quality_manifest.json"``.
        config: Quality thresholds.  ``None`` → sensible defaults.
        patterns: Glob patterns for file discovery (default ``["*.slp"]``).
        recursive: If ``True``, use ``rglob`` instead of ``glob``.
        instance: Which animal instance to analyse (default 0).
        max_flagged_per_category: Cap on flagged frame indices stored
            per category in the manifest (default 500).  Exact counts
            are always available in ``frame_counts`` / ``keypoint_counts``.
        verbose: Print progress to stdout.

    Returns:
        The manifest dictionary (also written to *output_path*).
    """
    slp_dir = Path(slp_dir)
    if not slp_dir.is_dir():
        raise FileNotFoundError(f"Directory not found: {slp_dir}")

    if output_path is None:
        output_path = slp_dir / "quality_manifest.json"
    else:
        output_path = Path(output_path)

    if config is None:
        config = QualityConfig()

    if patterns is None:
        patterns = ["*.slp"]

    # Discover files
    glob_fn = slp_dir.rglob if recursive else slp_dir.glob
    slp_files: list[Path] = []
    for pat in patterns:
        slp_files.extend(glob_fn(pat))
    slp_files = sorted(set(slp_files))

    if verbose:
        print(f"Found {len(slp_files)} .slp file(s) in {slp_dir}")

    # Process each file
    files_entries: list[dict] = []
    counts = {"good": 0, "review": 0, "poor": 0, "error": 0}

    for i, slp_path in enumerate(slp_files):
        rel_path = str(slp_path.relative_to(slp_dir))
        fname = slp_path.name
        metadata = _parse_slp_filename(fname)

        if verbose:
            print(f"  [{i + 1}/{len(slp_files)}] {fname} ... ", end="", flush=True)

        try:
            report = check_slp_quality(slp_path, instance=instance, config=config)
            entry = _report_to_manifest_entry(
                fname, rel_path, report, max_flagged_per_category, metadata
            )
            rec = entry["recommendation"]
            counts[rec.lower()] += 1
            if verbose:
                print(
                    f"{rec}  "
                    f"({entry['total_flagged_frames']}/{entry['total_frames']} frames)"
                )
        except Exception as exc:
            entry = {
                "filename": fname,
                "path": rel_path,
                "status": "error",
                "error_message": str(exc),
            }
            if metadata is not None:
                entry["metadata"] = metadata
            counts["error"] += 1
            if verbose:
                print(f"ERROR: {exc}")

        files_entries.append(entry)

    # Build manifest
    manifest = {
        "version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "scan_dir": str(slp_dir),
        "config": _config_to_dict(config),
        "summary": {
            "total_files": len(slp_files),
            **counts,
        },
        "files": files_entries,
    }

    # Write to disk
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2)

    if verbose:
        print(
            f"\nManifest written to {output_path}\n"
            f"  GOOD: {counts['good']}  REVIEW: {counts['review']}  "
            f"POOR: {counts['poor']}  ERROR: {counts['error']}"
        )

    return manifest
