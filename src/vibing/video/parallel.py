"""
Parallel processing framework for batch video operations.

Provides a generic framework for processing items in parallel with progress
tracking, error handling, and status reporting.
"""

import logging
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Literal, Optional, Union


@dataclass
class ParallelResult:
    """
    Result from parallel processing.

    Attributes:
        results: List of individual results from worker function
        counts: Dictionary with status counts (ok, error, skip)
        total: Total items processed
        ok: Number of successful items
        errors: Number of failed items
        skipped: Number of skipped items
    """

    results: list[dict] = field(default_factory=list)
    counts: dict[str, int] = field(
        default_factory=lambda: {"ok": 0, "error": 0, "skip": 0}
    )

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def ok(self) -> int:
        return self.counts["ok"]

    @property
    def errors(self) -> int:
        return self.counts["error"]

    @property
    def skipped(self) -> int:
        return self.counts["skip"]

    def __repr__(self) -> str:
        return (
            f"ParallelResult(total={self.total}, ok={self.ok}, "
            f"skip={self.skipped}, error={self.errors})"
        )


def run_parallel(
    items: list[Any],
    worker_fn: Callable[[Any], dict],
    n_workers: int = 4,
    desc: str = "Processing",
    executor_type: Literal["process", "thread"] = "process",
    logger: Optional[logging.Logger] = None,
    progress_interval: int = 50,
) -> ParallelResult:
    """
    Run a worker function on items in parallel.

    Generic framework for parallel processing with progress logging and
    automatic status counting.

    Args:
        items: List of items to process (can be any type)
        worker_fn: Function that takes an item and returns a dict with 'status' key.
                   Status values: "ok", "error", "skip*" (anything starting with "skip")
        n_workers: Number of parallel workers (default: 4)
        desc: Description for progress logging (default: "Processing")
        executor_type: "process" for CPU-bound, "thread" for I/O-bound
        logger: Optional logger instance (creates one if not provided)
        progress_interval: Log progress every N items (default: 50)

    Returns:
        ParallelResult with all results and status counts

    Example:
        >>> def process_video(path):
        ...     try:
        ...         # ... do something with path
        ...         return {"status": "ok", "path": path, "frames": 1000}
        ...     except Exception as e:
        ...         return {"status": "error", "path": path, "error": str(e)}
        ...
        >>> result = run_parallel(video_paths, process_video, n_workers=8)
        >>> print(f"Processed {result.ok}/{result.total} successfully")

    Note:
        The worker function must be picklable when using executor_type="process".
        For lambda functions or closures, use executor_type="thread".
    """
    log = logger or logging.getLogger(__name__)
    total = len(items)

    if total == 0:
        log.warning(f"{desc}: No items to process")
        return ParallelResult()

    log.info(f"{desc}: {total} items with {n_workers} workers ({executor_type})")

    result = ParallelResult()
    n_done = 0

    # Choose executor type
    if executor_type == "process":
        executor_cls = ProcessPoolExecutor
    else:
        executor_cls = ThreadPoolExecutor

    with executor_cls(max_workers=n_workers) as executor:
        futures = {executor.submit(worker_fn, item): item for item in items}

        for future in as_completed(futures):
            n_done += 1
            item = futures[future]

            try:
                item_result = future.result()
                result.results.append(item_result)

                status = item_result.get("status", "ok")
                if status == "ok":
                    result.counts["ok"] += 1
                elif status.startswith("skip"):
                    result.counts["skip"] += 1
                else:
                    result.counts["error"] += 1

            except Exception as e:
                log.error(f"Exception processing {item}: {e}")
                result.counts["error"] += 1
                result.results.append({
                    "status": "error", "item": item, "error": str(e)
                })

            # Progress logging
            if n_done % progress_interval == 0 or n_done == total:
                log.info(
                    f"{desc}: {n_done}/{total} "
                    f"(ok={result.counts['ok']}, skip={result.counts['skip']}, "
                    f"error={result.counts['error']})"
                )

    log.info(
        f"{desc} complete: ok={result.counts['ok']}, skip={result.counts['skip']}, "
        f"error={result.counts['error']}"
    )

    return result


def find_videos(
    video_dir: Union[str, Path],
    extensions: tuple[str, ...] = (".mp4", ".avi", ".mov"),
    pattern: Optional[str] = None,
    recursive: bool = False,
) -> list[Path]:
    """
    Find video files in a directory.

    Args:
        video_dir: Directory to search
        extensions: Video file extensions to include
        pattern: Optional glob pattern (e.g., "Day*_*.mp4"). Overrides extensions.
        recursive: Search subdirectories (default: False)

    Returns:
        Sorted list of video paths

    Example:
        >>> videos = find_videos("/path/to/data")
        >>> videos = find_videos("/path/to/data", pattern="Day*_Trial*.mp4")
        >>> videos = find_videos("/path/to/data", recursive=True)
    """
    video_dir = Path(video_dir)

    if pattern:
        if recursive:
            return sorted(video_dir.rglob(pattern))
        return sorted(video_dir.glob(pattern))

    videos = []
    for ext in extensions:
        if recursive:
            videos.extend(video_dir.rglob(f"*{ext}"))
        else:
            videos.extend(video_dir.glob(f"*{ext}"))

    return sorted(set(videos))


def process_videos(
    video_dir: Union[str, Path],
    worker_fn: Callable[[Path], dict],
    n_workers: int = 4,
    extensions: tuple[str, ...] = (".mp4", ".avi", ".mov"),
    pattern: Optional[str] = None,
    recursive: bool = False,
    executor_type: Literal["process", "thread"] = "process",
    desc: str = "Processing videos",
    logger: Optional[logging.Logger] = None,
) -> ParallelResult:
    """
    Process all videos in a directory in parallel.

    Convenience function that combines find_videos() and run_parallel().

    Args:
        video_dir: Directory containing videos
        worker_fn: Function that processes a Path and returns dict with 'status' key
        n_workers: Number of parallel workers
        extensions: Video file extensions to include
        pattern: Optional glob pattern (overrides extensions)
        recursive: Search subdirectories
        executor_type: "process" for CPU-bound, "thread" for I/O-bound
        desc: Description for progress logging
        logger: Optional logger instance

    Returns:
        ParallelResult with all results

    Example:
        >>> def analyze_video(path: Path) -> dict:
        ...     # Your analysis code here
        ...     return {"status": "ok", "path": str(path), "result": ...}
        ...
        >>> result = process_videos(
        ...     "/path/to/videos",
        ...     analyze_video,
        ...     n_workers=8,
        ...     pattern="Day*_*.mp4"
        ... )
        >>> print(f"Analyzed {result.ok} videos")
    """
    videos = find_videos(
        video_dir,
        extensions=extensions,
        pattern=pattern,
        recursive=recursive,
    )

    return run_parallel(
        items=videos,
        worker_fn=worker_fn,
        n_workers=n_workers,
        desc=desc,
        executor_type=executor_type,
        logger=logger,
    )


def make_worker(
    process_fn: Callable[..., Any],
    output_key: str = "result",
    **fixed_kwargs,
) -> Callable[[Any], dict]:
    """
    Create a worker function from a simple processing function.

    Wraps a function that may raise exceptions into a worker function
    that returns {"status": "ok"/"error", ...} dicts suitable for run_parallel().

    Args:
        process_fn: Function to wrap (takes item as first arg)
        output_key: Key name for the result in output dict (default: "result")
        **fixed_kwargs: Additional fixed arguments to pass to process_fn

    Returns:
        Worker function suitable for run_parallel()

    Example:
        >>> def analyze(video_path, threshold=0.5):
        ...     # May raise exception
        ...     return compute_something(video_path, threshold)
        ...
        >>> worker = make_worker(analyze, output_key="score", threshold=0.8)
        >>> result = run_parallel(paths, worker)
    """

    def worker(item: Any) -> dict:
        try:
            output = process_fn(item, **fixed_kwargs)
            return {"status": "ok", "item": item, output_key: output}
        except Exception as e:
            return {"status": "error", "item": item, "error": str(e)}

    return worker
