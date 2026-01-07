# vibing

A collection of small but useful tools for scientific publications and projects.

## Installation

### From PyPI (recommended)
```bash
# Using uv
uv pip install vibing

# Using pip
pip install vibing

# With optional dependencies
uv pip install "vibing[calibration]"  # Camera calibration tools (opencv)
uv pip install "vibing[sleap]"        # SLEAP conversion tools
uv pip install "vibing[all]"          # Everything
```

### Run CLI without installing (uvx)
```bash
# Run distortion checker directly
uvx --from "vibing[calibration]" vibing-distortion-check video.mp4

# Or install as a tool
uv tool install "vibing[calibration]"
vibing-distortion-check video.mp4
```

### From GitHub
```bash
# Install from git
uv pip install "git+https://github.com/LeoMeow123/vibes.git[calibration]"

# Run without installing
uv tool run --from "git+https://github.com/LeoMeow123/vibes.git[calibration]" vibing-distortion-check video.mp4
```

### From source
```bash
git clone https://github.com/LeoMeow123/vibes.git
cd vibes
uv pip install -e ".[all]"
```

## Tools

### Calibration (`vibing.calibration`)
Camera calibration and distortion analysis tools.
- `check_video` - Analyze video for lens distortion using charuco board
- `check_image` - Analyze single image for distortion
- `check_batch` - Batch process directory of videos
- `CharucoBoardConfig` - Configure charuco board parameters
- `DistortionMetrics` - Distortion analysis results

**CLI:** `vibing-distortion-check`
```bash
# Check single video
vibing-distortion-check video.mp4

# Batch process directory
vibing-distortion-check /path/to/videos --batch --output-csv results.csv

# Custom board configuration
vibing-distortion-check video.mp4 --squares-x 10 --squares-y 7
```

### Optimization (`vibing.optimization`)
Gradient-based and gradient-free optimization wrappers.
- `minimize_lbfgsb` - L-BFGS-B optimization
- `minimize_gradient_free` - Gradient-free methods (Nelder-Mead, Powell, COBYLA)

### Plotting (`vibing.plotting`)
Utilities for creating publication-quality figures.
- `setup_figure` - Set up figures with consistent styling
- `save_figure` - Save figures in multiple formats

### Powerwell (`vibing.powerwell`)
Powerwell analysis tools.
- *Coming soon*

### Undistortion (`vibing.undistortion`)
Video undistortion and perspective correction pipelines using OpenCV.
- [spacecage-undistort](https://github.com/talmolab/spacecage-undistort) - Fisheye lens distortion correction for NASA SpaceCage experiments with ROI-based calibration and SLEAP coordinate transformation
- [tmaze-undistort](https://github.com/LeoMeow123/tmaze-undistort) - T-maze video processing with lens distortion removal and perspective transformation to top-down views using labeled ROIs and known physical dimensions

### SLEAP Convert (`vibing.sleap_convert`)
Convert SLEAP predictions to ROI polygon YAML format.
- `slp_to_roi_yaml` - Convert single SLP file to ROI YAML
- `convert_batch` - Batch convert directory of SLP files
- `extract_keypoints` - Extract keypoints from SLP (low-level)
- `ROITemplate` - Define custom polygon templates for any arena

**CLI:** `vibing-slp-to-yaml`
```bash
# Convert single file
vibing-slp-to-yaml predictions.slp -o output.yml

# Batch convert directory
vibing-slp-to-yaml /path/to/slps --batch -o /path/to/yamls

# List available templates
vibing-slp-to-yaml --list-templates
```

**Built-in templates:** `tmaze_horizontal` (7-region T-maze with corner sharing)

## Quick Start

```python
import numpy as np
from vibing.optimization import minimize_lbfgsb
from vibing.plotting import setup_figure, save_figure

# Optimization example
def objective(x):
    return (x[0] - 1) ** 2 + (x[1] - 2) ** 2

result = minimize_lbfgsb(objective, np.array([0.0, 0.0]))
print(f"Optimal x: {result['x']}")

# Plotting example
fig, ax = setup_figure(width=6, height=4)
ax.plot([1, 2, 3], [1, 4, 9])
save_figure(fig, "my_plot", formats=["png", "pdf"])
```

## Development

```bash
# Clone and install in dev mode
git clone https://github.com/LeoMeow123/vibes.git
cd vibes
uv pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check src/
```

## License

MIT License
