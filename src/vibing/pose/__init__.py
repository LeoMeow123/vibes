"""
Pose analysis utilities.

This module provides tools for analyzing pose estimation data:
- Region checking: Determine if body parts are inside regions of interest
- Interpolation: Fill short gaps in tracking data
- Hull calculation: Compute convex hulls for spatial analysis
- Track analysis: Velocity, distance, and dwell time
- Quality assessment: Body-relative keypoint anomaly detection
"""

from vibing.pose.region import (
    bodypart_in_region,
    bodyparts_in_region,
    check_bodyparts_by_name,
    count_bodyparts_in_region,
    extract_bodyparts,
)
from vibing.pose.interpolate import (
    count_gaps,
    interpolate_gaps,
    interpolate_track,
)
from vibing.pose.hull import (
    body_hull,
    body_hull_area,
    body_hull_centroid,
    body_hull_coverage,
    body_hull_series,
)
from vibing.pose.analysis import (
    cumulative_distance,
    multi_region_dwell,
    region_dwell_frames,
    region_dwell_time,
    track_distance,
    track_speed,
    track_velocity,
)
from vibing.pose.quality import (
    QualityConfig,
    QualityReport,
    SkeletonMap,
    check_pose_quality,
    check_slp_quality,
    detect_skeleton,
)
from vibing.pose.scan import scan_slp_quality

__all__ = [
    # Region checking
    "bodypart_in_region",
    "bodyparts_in_region",
    "check_bodyparts_by_name",
    "count_bodyparts_in_region",
    "extract_bodyparts",
    # Interpolation
    "count_gaps",
    "interpolate_gaps",
    "interpolate_track",
    # Hull calculation
    "body_hull",
    "body_hull_area",
    "body_hull_centroid",
    "body_hull_coverage",
    "body_hull_series",
    # Track analysis
    "cumulative_distance",
    "multi_region_dwell",
    "region_dwell_frames",
    "region_dwell_time",
    "track_distance",
    "track_speed",
    "track_velocity",
    # Quality assessment
    "QualityConfig",
    "QualityReport",
    "SkeletonMap",
    "check_pose_quality",
    "check_slp_quality",
    "detect_skeleton",
    # Batch scanning
    "scan_slp_quality",
]
