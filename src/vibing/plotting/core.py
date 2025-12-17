"""Core plotting utilities."""

from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def setup_figure(
    width: float = 6.0,
    height: float = 4.0,
    dpi: int = 150,
    style: Literal["default", "paper", "presentation"] = "default",
) -> tuple[Figure, plt.Axes]:
    """Set up a figure with common settings for scientific plots.

    Args:
        width: Figure width in inches.
        height: Figure height in inches.
        dpi: Dots per inch.
        style: Plot style preset.

    Returns:
        Tuple of (figure, axes).
    """
    # TODO: Implement your custom figure setup here
    fig, ax = plt.subplots(figsize=(width, height), dpi=dpi)
    return fig, ax


def save_figure(
    fig: Figure,
    path: str | Path,
    formats: list[str] | None = None,
    dpi: int = 300,
    transparent: bool = False,
) -> list[Path]:
    """Save figure in multiple formats.

    Args:
        fig: Matplotlib figure to save.
        path: Output path (without extension).
        formats: List of formats to save. Default: ['png', 'pdf'].
        dpi: Resolution for raster formats.
        transparent: Whether to use transparent background.

    Returns:
        List of saved file paths.
    """
    if formats is None:
        formats = ["png", "pdf"]

    path = Path(path)
    saved_paths = []

    for fmt in formats:
        output_path = path.with_suffix(f".{fmt}")
        fig.savefig(
            output_path,
            dpi=dpi,
            transparent=transparent,
            bbox_inches="tight",
        )
        saved_paths.append(output_path)

    return saved_paths
