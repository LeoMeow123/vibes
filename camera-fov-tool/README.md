# Lab Camera Comparison Tool

Browser-based comparison and planning tool for lab camera systems — DJI Action 6, GoPro HERO 13, and Basler ace 2.

**Solves**: Choosing the right camera, lens, and mounting distance for animal tracking experiments. Instead of trial-and-error, plan your setup with real specs, interactive FOV diagrams, and personalized recommendations.

## Live Demo

[Launch Camera Comparison Tool](https://leomeow123.github.io/vibes/camera-fov-tool/)

## Pages

### Overview
Side-by-side cards for all three cameras with key specs at a glance: sensor, resolution, FPS, FOV, color, battery, app quality, overheating, and price.

### Full Specs
Comprehensive comparison table covering sensor & optics, resolution & frame rate, color & sensitivity, recording & storage, synchronization & triggering, and physical specs. Best-in-class values highlighted.

### App & Software
Star ratings and real-world experience for each camera's companion software:
- **DJI Mimo** — synchronized preview + recording, instant response, zero connection failures
- **GoPro Quik** — ~50% connection failure rate, recording lag, phone preview OR camera view only
- **Basler Pylon + [Multi-Cam Sync](https://github.com/LeoMeow123/multi-cam-sync)** — lab-built Electron app with Arduino hardware trigger for sub-microsecond multi-camera synchronization

Also includes a "When to Use Each Camera" decision matrix by experiment type.

### FOV Calculator
Interactive calculator for planning camera placement:
- **Camera presets**: DJI Action 6 (4K/1080p), GoPro HERO 13 (4K/5.3K), Basler with 6/8/12/16mm lenses, or custom
- **Arena presets**: T-Maze, Open Field, Linear Track, Home Cage, EPM, Barnes Maze, MWM, SpaceCage
- **Draggable camera** on the side-view diagram — drag up/down to adjust distance in real-time
- **Distance slider** for fine control
- **Compare mode** — overlay two cameras on the same diagram
- **Animal tracking feasibility** — enter animal body width, see pixel count and SLEAP suitability
- **Pixel density heatmap** — top-down view shows green (center, best) to red (edges, degraded)
- **Hover tooltip** — mouse over top view to see position, pixel coordinates, and density
- **Recording estimator** — enter FPS + duration, see file size, bitrate, battery/thermal limits
- **Setup checklist** — auto-generated based on current settings
- **Export as PNG** — save the diagram for lab notebooks

Key formulas:
```
FOV = 2 × arctan(sensor_size / (2 × focal_length))
coverage = 2 × distance × tan(FOV / 2)
distance = object_size / (2 × tan(FOV / 2))
pixel_density = resolution / coverage
```

### Recommend (Wizard)
7-step questionnaire that scores each camera based on your needs:
1. Arena size
2. Lighting conditions (normal / dim / dark+IR)
3. Frame rate requirements
4. Multi-camera synchronization needs
5. Recording duration
6. Color requirements
7. Budget

Shows ranked results with scores and reasoning for each recommendation.

### Multi-Cam Planner
Interactive top-down arena view for planning multi-camera setups:
- Click to add DJI, GoPro, or Basler cameras
- Drag cameras to reposition around the arena
- Coverage ellipses show each camera's field of view at the configured height
- Arena presets (same list as FOV calculator) or custom dimensions
- Camera list with coverage dimensions

### Theory & Tutorial
Educational sections covering:
1. **Field of View** — formula, HFOV vs VFOV, sensor size vs focal length
2. **Distance & Coverage** — how to calculate mounting height for a given arena
3. **Pixel Density (GSD)** — minimum requirements for SLEAP pose estimation
4. **Global vs Rolling Shutter** — why Basler's global shutter matters for fast motion
5. **Lens Distortion** — interactive comparison with per-mode presets:
   - DJI: Wide / Standard / Linear (corrected)
   - GoPro: Wide / Linear (corrected) / Narrow
   - Basler: 6mm / 8mm / 12mm+ / cheap wide-angle
   - Custom k1/k2 input for real calibration data from `vibing.calibration`
   - Links to [tmaze-undistort](https://github.com/LeoMeow123/tmaze-undistort) and [spacecage-undistort](https://github.com/talmolab/spacecage-undistort)
6. **Top-Down vs Bottom-Up Mounting** — practical considerations for each

## Camera Specs (verified from official sources)

| Spec | DJI Action 6 | GoPro HERO 13 | Basler a2A1920-165g5m |
|------|-------------|---------------|----------------------|
| Sensor | 1/1.1" square CMOS | 1/1.9" CMOS | Sony IMX392, 1/2.3" |
| Pixel size | ~2.4µm | ~1.55µm | 3.45µm |
| Aperture | f/2.0–f/4.0 variable | f/2.5 | Lens-dependent |
| FOV | 155° (182° w/ boost) | 156° | 58°×39° (6mm lens) |
| Max resolution | 8K/30fps | 5.3K/30fps | 1920×1200/168fps |
| Color | RGB, 10-bit | RGB, 10-bit | Monochrome, 12-bit |
| Shutter | Rolling | Rolling | Global |
| Recording | ~4 hrs, no overheat | ~90 min 4K (overheats) | Unlimited |
| Sync | App (Wi-Fi) | Unreliable | Hardware trigger (sub-µs) |
| Price | ~$436 | ~$359 | ~$985 + lens |

Sources: [dji.com](https://www.dji.com/osmo-action-6), [gopro.com](https://gopro.com/en/us/shop/cameras/buy/hero13black/CHDHX-131-master.html), [docs.baslerweb.com](https://docs.baslerweb.com/a2a1920-165g5mbas)

## Features

- Dark/light theme toggle (persisted)
- Export diagram as PNG
- All calculations run in-browser — no server required
- Single HTML file, no build step
- Mobile-responsive layout

## Local Development

```bash
# Serve from repo root
python3 -m http.server 8000
# Open http://localhost:8000/camera-fov-tool/
```
