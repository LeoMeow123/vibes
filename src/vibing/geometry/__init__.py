"""
Geometry utilities for spatial analysis.

This module provides tools for geometric calculations commonly used in
behavioral analysis, such as measuring penetration depth into regions
and converting pixel measurements to real-world units.
"""

from vibing.geometry.depth import (
    depth_from_boundary,
    points_depth_from_boundary,
    signed_distance,
)
from vibing.geometry.scale import (
    PixelScale,
    compute_scale,
    px_to_real,
)

__all__ = [
    # Depth/distance
    "depth_from_boundary",
    "points_depth_from_boundary",
    "signed_distance",
    # Scale conversion
    "PixelScale",
    "compute_scale",
    "px_to_real",
]
