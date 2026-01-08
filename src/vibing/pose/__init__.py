"""
Pose analysis utilities.

This module provides tools for analyzing pose estimation data,
including checking body part locations relative to regions of interest.
"""

from vibing.pose.region import (
    bodypart_in_region,
    bodyparts_in_region,
    count_bodyparts_in_region,
)

__all__ = [
    "bodypart_in_region",
    "bodyparts_in_region",
    "count_bodyparts_in_region",
]
