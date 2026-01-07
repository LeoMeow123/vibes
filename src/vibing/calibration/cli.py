"""CLI for charuco distortion checker."""

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

from vibing.calibration.distortion_checker import (
    ARUCO_DICT_MAP,
    CharucoBoardConfig,
    DistortionMetrics,
    check_batch,
    check_video,
)


def save_results_csv(
    results: dict[str, DistortionMetrics],
    output_path: Path,
) -> None:
    """Save batch results to CSV file."""
    with open(output_path, "w", newline="") as f:
        fieldnames = [
            "video",
            "frames_detected",
            "line_straightness",
            "spacing_uniformity",
            "reprojection_error",
            "needs_undistortion",
            "recommendation",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for video_name, metrics in results.items():
            writer.writerow(
                {
                    "video": video_name,
                    "frames_detected": metrics.frames_detected,
                    "line_straightness": (
                        f"{metrics.line_straightness:.4f}"
                        if metrics.frames_detected > 0
                        else "N/A"
                    ),
                    "spacing_uniformity": (
                        f"{metrics.spacing_uniformity:.4f}"
                        if metrics.frames_detected > 0
                        else "N/A"
                    ),
                    "reprojection_error": (
                        f"{metrics.reprojection_error:.4f}"
                        if metrics.frames_detected > 0
                        else "N/A"
                    ),
                    "needs_undistortion": metrics.needs_undistortion,
                    "recommendation": metrics.recommendation,
                }
            )


def save_results_json(
    results: dict[str, DistortionMetrics],
    output_path: Path,
) -> None:
    """Save batch results to JSON file."""
    json_results = {
        "timestamp": datetime.now().isoformat(),
        "results": {name: m.to_dict() for name, m in results.items()},
    }

    with open(output_path, "w") as f:
        json.dump(json_results, f, indent=2)


def print_summary(results: dict[str, DistortionMetrics]) -> None:
    """Print batch summary to console."""
    total = len(results)
    ok = sum(1 for m in results.values() if m.needs_undistortion is False)
    needs_undist = sum(1 for m in results.values() if m.needs_undistortion is True)
    no_board = sum(1 for m in results.values() if m.needs_undistortion is None)

    print("\n" + "=" * 70)
    print("BATCH SUMMARY")
    print("=" * 70)

    for name, metrics in results.items():
        print(f"{name:50s} -> {metrics.recommendation}")

    print("=" * 70)
    print(f"Total videos processed: {total}")
    print(f"Videos OK (no undistortion needed): {ok}")
    print(f"Videos needing undistortion: {needs_undist}")
    print(f"Videos with no board detected: {no_board}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Check video/image distortion using charuco board analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check a single video
  vibing-distortion-check video.mp4

  # Check all videos in a directory
  vibing-distortion-check /path/to/videos --batch

  # Custom board configuration
  vibing-distortion-check video.mp4 --squares-x 10 --squares-y 7

  # Save results to files
  vibing-distortion-check /path/to/videos --batch --output-csv results.csv
        """,
    )

    parser.add_argument(
        "path",
        type=Path,
        help="Path to video file or directory (with --batch)",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process all videos in directory",
    )
    parser.add_argument(
        "--num-frames",
        type=int,
        default=10,
        help="Number of frames to sample per video (default: 10)",
    )

    # Board configuration
    board_group = parser.add_argument_group("Board Configuration")
    board_group.add_argument(
        "--squares-x",
        type=int,
        default=14,
        help="Number of squares in X direction (default: 14)",
    )
    board_group.add_argument(
        "--squares-y",
        type=int,
        default=9,
        help="Number of squares in Y direction (default: 9)",
    )
    board_group.add_argument(
        "--square-length",
        type=float,
        default=0.02,
        help="Square side length in meters (default: 0.02)",
    )
    board_group.add_argument(
        "--marker-length",
        type=float,
        default=0.015,
        help="Marker side length in meters (default: 0.015)",
    )
    board_group.add_argument(
        "--dictionary",
        type=str,
        default="DICT_5X5_250",
        choices=list(ARUCO_DICT_MAP.keys()),
        help="ArUco dictionary type (default: DICT_5X5_250)",
    )

    # Output options
    output_group = parser.add_argument_group("Output Options")
    output_group.add_argument(
        "--output-csv",
        type=Path,
        help="Save results to CSV file",
    )
    output_group.add_argument(
        "--output-json",
        type=Path,
        help="Save results to JSON file",
    )
    output_group.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress verbose output",
    )

    args = parser.parse_args()

    # Build config
    config = CharucoBoardConfig(
        squares_x=args.squares_x,
        squares_y=args.squares_y,
        square_length=args.square_length,
        marker_length=args.marker_length,
        dictionary=args.dictionary,
    )

    verbose = not args.quiet

    if args.batch:
        if not args.path.is_dir():
            parser.error(f"Not a directory: {args.path}")

        results = check_batch(
            args.path,
            config=config,
            num_frames=args.num_frames,
            verbose=verbose,
        )

        if verbose:
            print_summary(results)

        # Save outputs
        if args.output_csv:
            save_results_csv(results, args.output_csv)
            print(f"Results saved to: {args.output_csv}")

        if args.output_json:
            save_results_json(results, args.output_json)
            print(f"Results saved to: {args.output_json}")

    else:
        if not args.path.exists():
            parser.error(f"File not found: {args.path}")

        metrics = check_video(
            args.path,
            config=config,
            num_frames=args.num_frames,
            verbose=verbose,
        )

        # Save single result if requested
        if args.output_csv or args.output_json:
            results = {args.path.name: metrics}
            if args.output_csv:
                save_results_csv(results, args.output_csv)
                print(f"Results saved to: {args.output_csv}")
            if args.output_json:
                save_results_json(results, args.output_json)
                print(f"Results saved to: {args.output_json}")


if __name__ == "__main__":
    main()
