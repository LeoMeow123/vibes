"""
Geometry utilities for spatial analysis.

This module provides tools for geometric calculations commonly used in
behavioral analysis, such as measuring penetration depth into regions.
"""

from vibing.geometry.depth import (
    depth_from_boundary,
    signed_distance,
    points_depth_from_boundary,
)

__all__ = [
    "depth_from_boundary",
    "signed_distance",
    "points_depth_from_boundary",
]
