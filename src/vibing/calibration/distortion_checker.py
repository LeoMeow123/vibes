"""
Charuco board distortion checker for camera calibration assessment.

This module analyzes charuco boards in video frames to quantify lens distortion
and determine whether undistortion is necessary before processing.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

# ArUco dictionary mapping
ARUCO_DICT_MAP = {
    "DICT_4X4_50": cv2.aruco.DICT_4X4_50,
    "DICT_4X4_100": cv2.aruco.DICT_4X4_100,
    "DICT_4X4_250": cv2.aruco.DICT_4X4_250,
    "DICT_5X5_50": cv2.aruco.DICT_5X5_50,
    "DICT_5X5_100": cv2.aruco.DICT_5X5_100,
    "DICT_5X5_250": cv2.aruco.DICT_5X5_250,
    "DICT_6X6_50": cv2.aruco.DICT_6X6_50,
    "DICT_6X6_100": cv2.aruco.DICT_6X6_100,
    "DICT_6X6_250": cv2.aruco.DICT_6X6_250,
    "DICT_7X7_50": cv2.aruco.DICT_7X7_50,
    "DICT_7X7_100": cv2.aruco.DICT_7X7_100,
    "DICT_7X7_250": cv2.aruco.DICT_7X7_250,
    "DICT_ARUCO_ORIGINAL": cv2.aruco.DICT_ARUCO_ORIGINAL,
}


@dataclass
class CharucoBoardConfig:
    """Configuration for a Charuco board."""

    squares_x: int = 14
    squares_y: int = 9
    square_length: float = 0.02  # meters
    marker_length: float = 0.015  # meters
    dictionary: str = "DICT_5X5_250"

    @property
    def aruco_dict(self) -> int:
        """Get the OpenCV ArUco dictionary constant."""
        return ARUCO_DICT_MAP.get(self.dictionary, cv2.aruco.DICT_5X5_250)


@dataclass
class DistortionMetrics:
    """Results from distortion analysis."""

    line_straightness: float  # RMS deviation from straight lines (pixels)
    spacing_uniformity: float  # Coefficient of variation of corner distances
    reprojection_error: float  # RMS reprojection error (pixels)
    frames_detected: int  # Number of frames with successful detection
    needs_undistortion: Optional[bool]  # Recommendation (None if no detection)

    # Default thresholds
    LINE_THRESHOLD: float = 2.0  # pixels
    SPACING_THRESHOLD: float = 0.05  # coefficient of variation
    REPROJ_THRESHOLD: float = 5.0  # pixels

    def __post_init__(self):
        """Compute recommendation based on thresholds."""
        if self.frames_detected == 0:
            self.needs_undistortion = None
        elif self.needs_undistortion is None:
            self.needs_undistortion = (
                self.line_straightness > self.LINE_THRESHOLD
                or self.spacing_uniformity > self.SPACING_THRESHOLD
                or self.reprojection_error > self.REPROJ_THRESHOLD
            )

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "line_straightness": (
                float(self.line_straightness)
                if np.isfinite(self.line_straightness)
                else None
            ),
            "spacing_uniformity": (
                float(self.spacing_uniformity)
                if np.isfinite(self.spacing_uniformity)
                else None
            ),
            "reprojection_error": (
                float(self.reprojection_error)
                if np.isfinite(self.reprojection_error)
                else None
            ),
            "frames_detected": self.frames_detected,
            "needs_undistortion": self.needs_undistortion,
        }

    @property
    def recommendation(self) -> str:
        """Get human-readable recommendation string."""
        if self.needs_undistortion is None:
            return "NO_BOARD_DETECTED"
        elif self.needs_undistortion:
            return "UNDISTORTION_NEEDED"
        else:
            return "OK"


def detect_charuco_board(
    image: np.ndarray,
    config: CharucoBoardConfig,
) -> tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]:
    """
    Detect charuco board in an image.

    Args:
        image: Input image (grayscale or BGR)
        config: Charuco board configuration

    Returns:
        Tuple of (corners, ids, marker_corners):
            - corners: Detected charuco corner positions (N, 1, 2)
            - ids: Corner IDs (N, 1)
            - marker_corners: Detected marker corners
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    # Create charuco board
    aruco_dict = cv2.aruco.getPredefinedDictionary(config.aruco_dict)
    board = cv2.aruco.CharucoBoard(
        (config.squares_x, config.squares_y),
        config.square_length,
        config.marker_length,
        aruco_dict,
    )

    # Create CharucoDetector
    charuco_params = cv2.aruco.CharucoParameters()
    detector_params = cv2.aruco.DetectorParameters()
    charuco_detector = cv2.aruco.CharucoDetector(
        board, charuco_params, detector_params
    )

    # Detect charuco corners
    charuco_corners, charuco_ids, marker_corners, _ = charuco_detector.detectBoard(
        gray
    )

    if charuco_corners is not None and len(charuco_corners) > 0:
        return charuco_corners, charuco_ids, marker_corners

    return None, None, None


def compute_line_straightness(
    corners: np.ndarray,
    ids: np.ndarray,
    squares_x: int,
    squares_y: int,
) -> float:
    """
    Measure how straight the board edges are. Distortion causes edge bowing.

    Args:
        corners: (N, 1, 2) array of detected corner positions
        ids: (N, 1) array of corner IDs
        squares_x: Number of squares in X
        squares_y: Number of squares in Y

    Returns:
        RMS deviation from straight lines (pixels) - lower is better
    """
    if corners is None or len(corners) < 4:
        return np.inf

    corners = corners.reshape(-1, 2)
    ids = ids.flatten()

    # Organize corners by row and column
    # CharucoBoard corner indexing: row * (squares_x - 1) + col
    corner_dict = {}
    for corner, corner_id in zip(corners, ids):
        row = corner_id // (squares_x - 1)
        col = corner_id % (squares_x - 1)
        corner_dict[(row, col)] = corner

    deviations = []

    # Check horizontal lines (rows)
    for row in range(squares_y - 1):
        row_corners = [
            corner_dict[(row, col)]
            for col in range(squares_x - 1)
            if (row, col) in corner_dict
        ]

        if len(row_corners) >= 3:
            row_corners = np.array(row_corners)
            vx, vy, x0, y0 = cv2.fitLine(
                row_corners.astype(np.float32), cv2.DIST_L2, 0, 0.01, 0.01
            )
            vx, vy, x0, y0 = vx[0], vy[0], x0[0], y0[0]

            for pt in row_corners:
                dist = abs(vy * pt[0] - vx * pt[1] + (vx * y0 - vy * x0))
                deviations.append(dist)

    # Check vertical lines (columns)
    for col in range(squares_x - 1):
        col_corners = [
            corner_dict[(row, col)]
            for row in range(squares_y - 1)
            if (row, col) in corner_dict
        ]

        if len(col_corners) >= 3:
            col_corners = np.array(col_corners)
            vx, vy, x0, y0 = cv2.fitLine(
                col_corners.astype(np.float32), cv2.DIST_L2, 0, 0.01, 0.01
            )
            vx, vy, x0, y0 = vx[0], vy[0], x0[0], y0[0]

            for pt in col_corners:
                dist = abs(vy * pt[0] - vx * pt[1] + (vx * y0 - vy * x0))
                deviations.append(dist)

    if len(deviations) == 0:
        return np.inf

    return float(np.sqrt(np.mean(np.array(deviations) ** 2)))


def compute_spacing_uniformity(
    corners: np.ndarray,
    ids: np.ndarray,
    squares_x: int,
) -> float:
    """
    Measure uniformity of corner spacing. Distortion causes non-uniform spacing.

    Args:
        corners: (N, 1, 2) array of corner positions
        ids: (N, 1) array of corner IDs
        squares_x: Number of squares in X

    Returns:
        Coefficient of variation of distances - lower is better (< 0.05 is good)
    """
    if corners is None or len(corners) < 2:
        return np.inf

    corners = corners.reshape(-1, 2)
    ids = ids.flatten()

    # Calculate distances between adjacent corners
    corner_dict = {}
    for corner, corner_id in zip(corners, ids):
        row = corner_id // (squares_x - 1)
        col = corner_id % (squares_x - 1)
        corner_dict[(row, col)] = corner

    distances = []
    for (row, col), corner in corner_dict.items():
        # Horizontal distance
        if (row, col + 1) in corner_dict:
            dist = np.linalg.norm(corner - corner_dict[(row, col + 1)])
            distances.append(dist)
        # Vertical distance
        if (row + 1, col) in corner_dict:
            dist = np.linalg.norm(corner - corner_dict[(row + 1, col)])
            distances.append(dist)

    if len(distances) == 0:
        return np.inf

    distances = np.array(distances)
    return float(np.std(distances) / np.mean(distances))


def compute_reprojection_error(
    corners: np.ndarray,
    ids: np.ndarray,
    image_size: tuple[int, int],
    config: CharucoBoardConfig,
) -> float:
    """
    Compute reprojection error after initial calibration.
    High error indicates significant distortion.

    Args:
        corners: Detected charuco corners
        ids: Corner IDs
        image_size: (width, height) of image
        config: Charuco board configuration

    Returns:
        RMS reprojection error in pixels
    """
    if corners is None or len(corners) < 4:
        return np.inf

    # Create board
    aruco_dict = cv2.aruco.getPredefinedDictionary(config.aruco_dict)
    board = cv2.aruco.CharucoBoard(
        (config.squares_x, config.squares_y),
        config.square_length,
        config.marker_length,
        aruco_dict,
    )

    # Get 3D object points for detected corners
    obj_points = board.getChessboardCorners()[ids.flatten()]

    # Simple calibration with no distortion assumed
    w, h = image_size
    K_init = np.array(
        [[w, 0, w / 2], [0, w, h / 2], [0, 0, 1]], dtype=np.float64
    )
    dist_init = np.zeros(5, dtype=np.float64)

    # Estimate pose
    ret, rvec, tvec = cv2.solvePnP(
        obj_points.astype(np.float32),
        corners.astype(np.float32),
        K_init,
        dist_init,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )

    # Reproject points
    reprojected, _ = cv2.projectPoints(obj_points, rvec, tvec, K_init, dist_init)
    reprojected = reprojected.reshape(-1, 2)
    corners_2d = corners.reshape(-1, 2)

    # Calculate RMS error
    errors = np.linalg.norm(corners_2d - reprojected, axis=1)
    return float(np.sqrt(np.mean(errors**2)))


def check_image(
    image: np.ndarray,
    config: Optional[CharucoBoardConfig] = None,
) -> DistortionMetrics:
    """
    Check a single image for distortion.

    Args:
        image: Input image (BGR or grayscale)
        config: Charuco board configuration (uses defaults if None)

    Returns:
        DistortionMetrics with analysis results
    """
    if config is None:
        config = CharucoBoardConfig()

    corners, ids, _ = detect_charuco_board(image, config)

    if corners is None:
        return DistortionMetrics(
            line_straightness=np.inf,
            spacing_uniformity=np.inf,
            reprojection_error=np.inf,
            frames_detected=0,
            needs_undistortion=None,
        )

    h, w = image.shape[:2]
    line_score = compute_line_straightness(
        corners, ids, config.squares_x, config.squares_y
    )
    spacing_score = compute_spacing_uniformity(corners, ids, config.squares_x)
    reproj_error = compute_reprojection_error(corners, ids, (w, h), config)

    return DistortionMetrics(
        line_straightness=line_score,
        spacing_uniformity=spacing_score,
        reprojection_error=reproj_error,
        frames_detected=1,
        needs_undistortion=None,  # Will be computed in __post_init__
    )


def check_video(
    video_path: Path | str,
    config: Optional[CharucoBoardConfig] = None,
    num_frames: int = 10,
    verbose: bool = False,
) -> DistortionMetrics:
    """
    Check a video for distortion by sampling multiple frames.

    Args:
        video_path: Path to video file
        config: Charuco board configuration (uses defaults if None)
        num_frames: Number of frames to sample
        verbose: Print detailed results

    Returns:
        DistortionMetrics with averaged analysis results
    """
    if config is None:
        config = CharucoBoardConfig()

    video_path = Path(video_path)
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Sample frames evenly
    frame_indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)

    line_scores = []
    spacing_scores = []
    reproj_errors = []

    for frame_idx in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ret, frame = cap.read()

        if not ret:
            continue

        corners, ids, _ = detect_charuco_board(frame, config)

        if corners is not None:
            line_scores.append(
                compute_line_straightness(
                    corners, ids, config.squares_x, config.squares_y
                )
            )
            spacing_scores.append(
                compute_spacing_uniformity(corners, ids, config.squares_x)
            )
            reproj_errors.append(
                compute_reprojection_error(corners, ids, (width, height), config)
            )

    cap.release()

    if len(line_scores) == 0:
        if verbose:
            print("WARNING: No charuco board detected in any frame!")
        return DistortionMetrics(
            line_straightness=np.inf,
            spacing_uniformity=np.inf,
            reprojection_error=np.inf,
            frames_detected=0,
            needs_undistortion=None,
        )

    metrics = DistortionMetrics(
        line_straightness=float(np.mean(line_scores)),
        spacing_uniformity=float(np.mean(spacing_scores)),
        reprojection_error=float(np.mean(reproj_errors)),
        frames_detected=len(line_scores),
        needs_undistortion=None,  # Will be computed in __post_init__
    )

    if verbose:
        print(f"\n{'='*60}")
        print(f"Distortion Analysis for: {video_path.name}")
        print(f"{'='*60}")
        print(f"Frames analyzed: {metrics.frames_detected}/{num_frames}")
        print("\nMetrics:")
        print(
            f"  Line straightness:      {metrics.line_straightness:.3f} px "
            f"(threshold: {metrics.LINE_THRESHOLD:.1f} px)"
        )
        print(
            f"  Spacing uniformity:     {metrics.spacing_uniformity:.4f} "
            f"(threshold: {metrics.SPACING_THRESHOLD:.2f})"
        )
        print(
            f"  Reprojection error:     {metrics.reprojection_error:.3f} px "
            f"(threshold: {metrics.REPROJ_THRESHOLD:.1f} px)"
        )
        print(f"\n{'='*60}")
        print(f"Recommendation: {metrics.recommendation}")
        print(f"{'='*60}\n")

    return metrics


def check_batch(
    video_dir: Path | str,
    config: Optional[CharucoBoardConfig] = None,
    num_frames: int = 10,
    extensions: tuple[str, ...] = (".mp4", ".avi", ".mov"),
    verbose: bool = False,
) -> dict[str, DistortionMetrics]:
    """
    Check all videos in a directory for distortion.

    Args:
        video_dir: Directory containing video files
        config: Charuco board configuration (uses defaults if None)
        num_frames: Number of frames to sample per video
        extensions: Video file extensions to process
        verbose: Print detailed results

    Returns:
        Dictionary mapping video names to their DistortionMetrics
    """
    video_dir = Path(video_dir)
    if not video_dir.is_dir():
        raise ValueError(f"Not a directory: {video_dir}")

    video_files = []
    for ext in extensions:
        video_files.extend(video_dir.glob(f"*{ext}"))
        video_files.extend(video_dir.glob(f"*{ext.upper()}"))

    if len(video_files) == 0:
        raise ValueError(f"No video files found in {video_dir}")

    if verbose:
        print(f"Found {len(video_files)} videos to analyze\n")

    results = {}
    for video_path in sorted(video_files):
        try:
            metrics = check_video(video_path, config, num_frames, verbose)
            results[video_path.name] = metrics
        except Exception as e:
            if verbose:
                print(f"Error processing {video_path.name}: {e}")
            results[video_path.name] = DistortionMetrics(
                line_straightness=np.inf,
                spacing_uniformity=np.inf,
                reprojection_error=np.inf,
                frames_detected=0,
                needs_undistortion=None,
            )

    return results
