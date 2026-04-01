"""
Video utilities for metadata extraction, batch processing, and parallel analysis.

This module provides tools for extracting video metadata like FPS, frame count,
and dimensions with robust fallback methods, plus a generic parallel processing
framework for batch operations.
"""

from vibing.video.batch import (
    count_total_frames,
    scan_videos,
)
from vibing.video.info import (
    VideoInfo,
    get_dimensions,
    get_duration,
    get_frame_count,
    get_video_info,
    read_fps,
)
from vibing.video.parallel import (
    ParallelResult,
    find_videos,
    make_worker,
    process_videos,
    run_parallel,
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
    # Parallel
    "ParallelResult",
    "run_parallel",
    "find_videos",
    "process_videos",
    "make_worker",
]
