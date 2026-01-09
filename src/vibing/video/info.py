"""
Video metadata extraction with robust fallback methods.

Provides FPS, frame count, dimensions, and duration extraction
with multiple fallback strategies for reliability.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union
import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


def _require_cv2():
    if not HAS_CV2:
        raise ImportError(
            "opencv-python is required for video operations. "
            "Install with: pip install opencv-python"
        )


@dataclass
class VideoInfo:
    """
    Comprehensive video metadata.

    Attributes:
        path: Path to video file
        fps: Frames per second
        frame_count: Total number of frames
        width: Video width in pixels
        height: Video height in pixels
        duration: Duration in seconds
        codec: Video codec (fourcc)

    Example:
        >>> info = get_video_info("video.mp4")
        >>> print(f"{info.frame_count} frames at {info.fps} FPS = {info.duration:.1f}s")
    """
    path: Path
    fps: float
    frame_count: int
    width: int
    height: int
    duration: float
    codec: str = ""

    def __repr__(self) -> str:
        return (
            f"VideoInfo({self.path.name}: {self.width}x{self.height}, "
            f"{self.frame_count} frames, {self.fps:.1f} FPS, {self.duration:.1f}s)"
        )


def get_video_info(
    video_path: Union[str, Path],
    sleap_labels=None,
) -> VideoInfo:
    """
    Get comprehensive video metadata.

    Args:
        video_path: Path to video file
        sleap_labels: Optional SLEAP labels object for metadata fallback

    Returns:
        VideoInfo with all metadata

    Example:
        >>> info = get_video_info("experiment.mp4")
        >>> print(info.fps, info.frame_count, info.duration)
    """
    _require_cv2()

    video_path = Path(video_path)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    try:
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
        codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
    finally:
        cap.release()

    # Try SLEAP fallback for FPS if needed
    if (not np.isfinite(fps) or fps <= 0) and sleap_labels is not None:
        fps = _read_fps_from_sleap(sleap_labels) or 30.0

    # Ensure valid values
    fps = float(fps) if np.isfinite(fps) and fps > 0 else 30.0
    frame_count = max(0, frame_count)

    duration = frame_count / fps if fps > 0 else 0.0

    return VideoInfo(
        path=video_path,
        fps=fps,
        frame_count=frame_count,
        width=width,
        height=height,
        duration=duration,
        codec=codec,
    )


def read_fps(
    video_path: Union[str, Path],
    sleap_labels=None,
    default: float = 30.0,
) -> float:
    """
    Read FPS from video with multiple fallback methods.

    Tries in order:
    1. SLEAP labels metadata (if provided)
    2. OpenCV video capture
    3. Default value

    Args:
        video_path: Path to video file
        sleap_labels: Optional SLEAP labels or video object
        default: Default FPS if detection fails (default: 30.0)

    Returns:
        Video FPS (frames per second)

    Example:
        >>> fps = read_fps("video.mp4")
        >>> fps = read_fps("video.mp4", sleap_labels=labels, default=120.0)
    """
    # Try SLEAP metadata first
    if sleap_labels is not None:
        fps = _read_fps_from_sleap(sleap_labels)
        if fps is not None:
            return fps

    # Try OpenCV
    if HAS_CV2:
        try:
            cap = cv2.VideoCapture(str(video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            if np.isfinite(fps) and fps > 0:
                return float(fps)
        except Exception:
            pass

    return default


def _read_fps_from_sleap(sleap_obj) -> Optional[float]:
    """Extract FPS from SLEAP labels or video object."""
    # Try direct attributes
    for attr in ("fps", "frame_rate", "frame_rate_hz", "frameRate"):
        if hasattr(sleap_obj, attr):
            try:
                v = float(getattr(sleap_obj, attr))
                if np.isfinite(v) and v > 0:
                    return v
            except Exception:
                pass

    # Try metadata dict
    for meta_attr in ("metadata", "info", "source_video"):
        meta = getattr(sleap_obj, meta_attr, None)
        if isinstance(meta, dict):
            for k in ("fps", "frame_rate", "frameRate"):
                if k in meta:
                    try:
                        v = float(meta[k])
                        if np.isfinite(v) and v > 0:
                            return v
                    except Exception:
                        pass

    # Try videos list (for Labels object)
    if hasattr(sleap_obj, "videos") and sleap_obj.videos:
        return _read_fps_from_sleap(sleap_obj.videos[0])

    return None


def get_frame_count(
    video_path: Union[str, Path],
    sleap_labels=None,
) -> int:
    """
    Get frame count from a video file.

    Args:
        video_path: Path to video file
        sleap_labels: Optional SLEAP labels for frame count

    Returns:
        Number of frames in video (0 if unable to determine)

    Example:
        >>> n_frames = get_frame_count("video.mp4")
    """
    video_path = Path(video_path)

    # Try SLEAP labels
    if sleap_labels is not None:
        n = _get_frame_count_from_sleap(sleap_labels)
        if n > 0:
            return n

    # Try associated .slp file
    slp_path = video_path.with_suffix(".slp")
    if slp_path.exists():
        try:
            import sleap_io as sio
            labels = sio.load_file(str(slp_path))
            n = _get_frame_count_from_sleap(labels)
            if n > 0:
                return n
        except Exception:
            pass

    # Fallback to OpenCV
    if HAS_CV2:
        try:
            cap = cv2.VideoCapture(str(video_path))
            n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            cap.release()
            if n > 0:
                return n
        except Exception:
            pass

    return 0


def _get_frame_count_from_sleap(sleap_obj) -> int:
    """Extract frame count from SLEAP object."""
    # Try videos list
    if hasattr(sleap_obj, "videos") and sleap_obj.videos:
        video = sleap_obj.videos[0]
        if hasattr(video, "frames") and video.frames is not None:
            return int(video.frames)
        if hasattr(video, "shape") and len(video.shape) > 0:
            return int(video.shape[0])
        try:
            return int(len(video))
        except Exception:
            pass

    # Try direct attributes
    if hasattr(sleap_obj, "frames") and sleap_obj.frames is not None:
        return int(sleap_obj.frames)
    if hasattr(sleap_obj, "shape") and len(sleap_obj.shape) > 0:
        return int(sleap_obj.shape[0])

    return 0


def get_duration(
    video_path: Union[str, Path],
    sleap_labels=None,
) -> float:
    """
    Get video duration in seconds.

    Args:
        video_path: Path to video file
        sleap_labels: Optional SLEAP labels

    Returns:
        Duration in seconds

    Example:
        >>> duration = get_duration("video.mp4")
        >>> print(f"Video is {duration:.1f} seconds long")
    """
    fps = read_fps(video_path, sleap_labels)
    frames = get_frame_count(video_path, sleap_labels)
    return frames / fps if fps > 0 else 0.0


def get_dimensions(video_path: Union[str, Path]) -> tuple[int, int]:
    """
    Get video dimensions (width, height).

    Args:
        video_path: Path to video file

    Returns:
        Tuple of (width, height) in pixels

    Example:
        >>> width, height = get_dimensions("video.mp4")
        >>> print(f"Resolution: {width}x{height}")
    """
    _require_cv2()

    cap = cv2.VideoCapture(str(video_path))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()
    return width, height
