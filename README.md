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
uv pip install "vibing[geometry]"     # Geometry and pose tools (shapely)
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

### Geometry (`vibing.geometry`)
Spatial analysis utilities for points and polygons.
- `depth_from_boundary` - Calculate penetration depth into a region
- `signed_distance` - Signed distance to polygon (negative = inside)
- `points_depth_from_boundary` - Batch depth calculation
- `is_inside` / `points_inside` - Point containment checks

```python
from vibing.geometry import depth_from_boundary
from shapely.geometry import box

region = box(0, 0, 100, 100)
depth = depth_from_boundary((50, 50), region)  # Returns 50.0 (distance to edge)
```

### Pose (`vibing.pose`)
Tools for analyzing pose estimation data from SLEAP or similar trackers.

**Region checking:**
- `bodypart_in_region` - Check if keypoint is inside polygon
- `bodyparts_in_region` - Batch check multiple keypoints
- `check_bodyparts_by_name` - Check named body parts (e.g., "at least one hindpaw")
- `count_bodyparts_in_region` - Count keypoints inside region

**Track interpolation:**
- `interpolate_gaps` - Fill short gaps in single keypoint track
- `interpolate_track` - Interpolate all keypoints in (T, J, 2) array
- `count_gaps` - Quality control: count and characterize gaps

**Body hull:**
- `body_hull` - Convex hull from body keypoints (Polygon or vertices)
- `body_hull_area` - Calculate hull area
- `body_hull_centroid` - Get hull center point
- `body_hull_series` - Compute hull for each frame in a track
- `body_hull_coverage` - Percentage of hull overlapping with ROI

```python
from vibing.pose import interpolate_gaps, body_hull, body_hull_coverage
from shapely.geometry import box
import numpy as np

# Interpolate short gaps in tracking data
track = np.array([[0, 0], [np.nan, np.nan], [2, 2], [3, 3]])
result = interpolate_gaps(track, max_gap=7)  # Gap filled: [1, 1]

# Compute body hull from keypoints
points = np.array([[0, 0], [10, 0], [10, 10], [0, 10]])
hull = body_hull(points)  # Shapely Polygon
print(hull.area)  # 100.0

# Calculate coverage in region
region = box(0, 0, 50, 50)
pct = body_hull_coverage(points, region)  # 25.0%
```

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
