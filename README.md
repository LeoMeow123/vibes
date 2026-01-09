# vibing

A collection of small but useful tools for scientific publications and projects.

## Modules

| Module | Description |
|--------|-------------|
| `calibration` | Detect lens distortion using charuco boards |
| `sleap_convert` | Convert SLEAP predictions to ROI polygons |
| `geometry` | Pixel↔cm conversion, depth from boundaries |
| `pose` | Interpolate tracking gaps, body hulls, region checks |

## Standalone Tools

These functions work independently for common tasks:

| Function | What it does | Example use case |
|----------|--------------|------------------|
| `geometry.PixelScale` | Convert pixels ↔ real units (cm/mm) | "My ruler is 500px = 10cm, convert all measurements" |
| `geometry.depth_from_boundary` | How far a point is inside a region | "How deep is the snout in the arm?" |
| `pose.interpolate_gaps` | Fill short gaps in tracking data | "SLEAP lost tracking for 3 frames, fill it in" |
| `pose.body_hull` | Convex hull from body keypoints | "What's the body footprint polygon?" |
| `pose.body_hull_coverage` | % of body inside a region | "What fraction of the mouse is in zone A?" |
| `calibration.check_video` | Measure lens distortion | "Does this GoPro video need undistortion?" |

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
Spatial analysis and unit conversion utilities.

**Pixel-to-real conversion:**
- `PixelScale` - Convert between pixels and real units (cm, mm, etc.)
- `px_to_real` - Quick one-off conversion
- `compute_scale` - Create scale from two reference points

**Depth/distance:**
- `depth_from_boundary` - Calculate penetration depth into a region
- `signed_distance` - Signed distance to polygon (negative = inside)

```python
from vibing.geometry import PixelScale, depth_from_boundary
from shapely.geometry import box

# Pixel to cm conversion: ruler is 500px = 10cm
scale = PixelScale.from_reference(pixels=500, real_distance=10, unit="cm")
print(scale.to_real(250))  # 5.0 cm
print(scale.to_real_area(2500))  # 1.0 cm²

# Or from two labeled points
scale = PixelScale.from_two_points((100, 100), (600, 100), real_distance=20, unit="cm")

# Depth from boundary
region = box(0, 0, 100, 100)
depth = depth_from_boundary((50, 50), region)  # 50.0 (distance to nearest edge)
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
from vibing.geometry import PixelScale
from vibing.pose import interpolate_gaps, body_hull

# Convert pixels to cm using a reference measurement
scale = PixelScale.from_reference(pixels=500, real_distance=10, unit="cm")
print(scale.to_real(250))  # 5.0 cm

# Fill short gaps in tracking data
track = np.array([[0, 0], [np.nan, np.nan], [2, 2], [3, 3]])
filled = interpolate_gaps(track, max_gap=7)
print(filled[1])  # [1., 1.] - gap interpolated

# Compute body footprint from keypoints
points = np.array([[0, 0], [10, 0], [10, 10], [0, 10]])
hull = body_hull(points)
print(hull.area)  # 100.0
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
