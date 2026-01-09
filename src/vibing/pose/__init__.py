"""
Pose analysis utilities.

This module provides tools for analyzing pose estimation data:
- Region checking: Determine if body parts are inside regions of interest
- Interpolation: Fill short gaps in tracking data
- Hull calculation: Compute convex hulls for spatial analysis
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
]
