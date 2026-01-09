"""
Video utilities for metadata extraction and analysis.

This module provides tools for extracting video metadata like FPS, frame count,
and dimensions with robust fallback methods.
"""

from vibing.video.info import (
    VideoInfo,
    get_video_info,
    read_fps,
    get_frame_count,
    get_duration,
    get_dimensions,
)
from vibing.video.batch import (
    count_total_frames,
    scan_videos,
)

__all__ = [
    # Info
    "VideoInfo",
    "get_video_info",
    "read_fps",
    "get_frame_count",
    "get_duration",
    "get_dimensions",
    # Batch
    "count_total_frames",
    "scan_videos",
]
