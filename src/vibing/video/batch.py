"""
Batch video operations.

Utilities for processing multiple videos at once.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Union

from vibing.video.info import get_frame_count, get_video_info, VideoInfo


@dataclass
class BatchSummary:
    """
    Summary of batch video scan.

    Attributes:
        total_frames: Total frames across all videos
        total_duration: Total duration in seconds
        n_videos: Number of videos processed
        n_errors: Number of videos that failed
        errors: List of paths that failed
    """
    total_frames: int
    total_duration: float
    n_videos: int
    n_errors: int
    errors: list[Path]

    def __repr__(self) -> str:
        hours = self.total_duration / 3600
        return (
            f"BatchSummary({self.n_videos} videos, "
            f"{self.total_frames:,} frames, {hours:.1f} hours)"
        )


def count_total_frames(
    video_dir: Union[str, Path],
    extensions: tuple[str, ...] = (".mp4", ".avi", ".mov"),
    recursive: bool = False,
    verbose: bool = True,
) -> tuple[int, int]:
    """
    Count total frames across all videos in a directory.

    Useful for pre-flight checks before batch processing.

    Args:
        video_dir: Directory containing video files
        extensions: Video file extensions to include
        recursive: Search subdirectories
        verbose: Print progress

    Returns:
        Tuple of (total_frames, num_videos)

    Example:
        >>> total, n_videos = count_total_frames("/path/to/videos")
        >>> print(f"{total:,} frames across {n_videos} videos")
    """
    video_dir = Path(video_dir)
    total = 0
    n_videos = 0
    zeros = []

    # Find all video files
    video_files = []
    for ext in extensions:
        pattern = f"**/*{ext}" if recursive else f"*{ext}"
        video_files.extend(video_dir.glob(pattern))

    for video_path in sorted(video_files):
        n = get_frame_count(video_path)
        total += n
        n_videos += 1

        if n == 0:
            zeros.append(str(video_path))

        if verbose and n_videos % 50 == 0:
            print(f"...processed {n_videos} videos, running total = {total:,} frames")

    if verbose:
        print(f"Videos scanned: {n_videos}")
        print(f"Total frames: {total:,}")
        if zeros:
            print(f"Warning: {len(zeros)} video(s) returned 0 frames")
            for z in zeros[:5]:
                print(f"  - {z}")
            if len(zeros) > 5:
                print(f"  ... and {len(zeros) - 5} more")

    return total, n_videos


def scan_videos(
    video_dir: Union[str, Path],
    extensions: tuple[str, ...] = (".mp4", ".avi", ".mov"),
    recursive: bool = False,
) -> list[VideoInfo]:
    """
    Scan directory and get info for all videos.

    Args:
        video_dir: Directory containing video files
        extensions: Video file extensions to include
        recursive: Search subdirectories

    Returns:
        List of VideoInfo objects

    Example:
        >>> videos = scan_videos("/path/to/videos")
        >>> for v in videos:
        ...     print(f"{v.path.name}: {v.fps} FPS, {v.frame_count} frames")
    """
    video_dir = Path(video_dir)
    results = []

    video_files = []
    for ext in extensions:
        pattern = f"**/*{ext}" if recursive else f"*{ext}"
        video_files.extend(video_dir.glob(pattern))

    for video_path in sorted(video_files):
        try:
            info = get_video_info(video_path)
            results.append(info)
        except Exception:
            # Skip videos that can't be read
            pass

    return results


def get_batch_summary(
    video_dir: Union[str, Path],
    extensions: tuple[str, ...] = (".mp4", ".avi", ".mov"),
    recursive: bool = False,
) -> BatchSummary:
    """
    Get comprehensive summary of videos in a directory.

    Args:
        video_dir: Directory containing video files
        extensions: Video file extensions to include
        recursive: Search subdirectories

    Returns:
        BatchSummary with totals and any errors

    Example:
        >>> summary = get_batch_summary("/path/to/videos")
        >>> print(f"{summary.total_frames:,} frames, {summary.total_duration/3600:.1f} hours")
    """
    video_dir = Path(video_dir)
    total_frames = 0
    total_duration = 0.0
    n_videos = 0
    errors = []

    video_files = []
    for ext in extensions:
        pattern = f"**/*{ext}" if recursive else f"*{ext}"
        video_files.extend(video_dir.glob(pattern))

    for video_path in sorted(video_files):
        try:
            info = get_video_info(video_path)
            total_frames += info.frame_count
            total_duration += info.duration
            n_videos += 1
        except Exception:
            errors.append(video_path)

    return BatchSummary(
        total_frames=total_frames,
        total_duration=total_duration,
        n_videos=n_videos,
        n_errors=len(errors),
        errors=errors,
    )
