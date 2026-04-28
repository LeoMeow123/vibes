---
name: sleap
description: >
  Reference for working with SLEAP pose estimation files (.slp, .h5, .pkg.slp).
  Use when the user needs to load, inspect, manipulate, or extract data from
  SLEAP pose files, or when writing code that interacts with sleap-io.
  Covers the sleap-io 0.5.x Python API, common patterns, and known pitfalls.
user-invocable: true
argument-hint: "[task description]"
---

# SLEAP File Reference (sleap-io 0.5.x)

## Quick Start

```python
import sleap_io as sio
import numpy as np

labels = sio.load_file("path/to/file.slp")  # also .h5, .pkg.slp
```

## Core Objects

### Labels (top-level container)
```python
labels = sio.load_file("file.slp")
labels.labeled_frames   # list of LabeledFrame
labels.skeleton          # Skeleton object
labels.videos            # list of Video objects
len(labels)              # number of labeled frames
labels[0]                # first LabeledFrame
```

### Skeleton
```python
sk = labels.skeleton
sk.nodes                 # list of Node objects
[n.name for n in sk.nodes]  # node names
sk.edges                 # list of Edge objects (source, destination)
sk.index("snout")        # int index of node by name
```

### Video
```python
v = labels.videos[0]
v.filename               # str — path stored INSIDE the .slp file
v.shape                  # (n_frames, height, width, channels)
v.backend                # MediaVideo or HDF5Video
```

### LabeledFrame
```python
lf = labels[0]
lf.frame_idx             # int — frame number in video
lf.instances             # list of Instance or PredictedInstance
len(lf.instances)        # number of animals/instances in this frame
```

### Instance / PredictedInstance
```python
inst = lf.instances[0]
inst.numpy()             # np.ndarray shape (n_nodes, 2) — xy coordinates
inst.skeleton            # Skeleton reference
inst.score               # float — instance-level confidence (PredictedInstance only)
inst.tracking_score      # float — tracking confidence (PredictedInstance only)
inst.track               # Track object or None
```

### Points (PredictedPointsArray)
```python
pts = inst.points        # structured numpy array
pts.dtype.names          # ('xy', 'score', 'visible', 'complete', 'name')
pts['xy']                # (n_nodes, 2) — same as inst.numpy()
pts['score']             # (n_nodes,) — per-keypoint confidence
pts['visible']           # (n_nodes,) — bool
pts['name']              # (n_nodes,) — node name strings

# WARNING: pts[i] is a numpy.void, NOT a Point object
# Access fields like: pts[i]['score'], NOT pts[i].score
```

## Common Patterns

### Build trajectory array (T x J x 2)
```python
n_total_frames = labels.videos[0].shape[0]
n_nodes = len(labels.skeleton.nodes)
trx = np.full((n_total_frames, n_nodes, 2), np.nan)
for lf in labels:
    if lf.instances:
        trx[lf.frame_idx] = lf.instances[0].numpy()
# trx[frame, node, xy] — NaN for unlabeled frames
```

### Pick best instance per frame (multi-animal)
```python
def pick_best(lf):
    if not lf.instances:
        return None
    return max(lf.instances, key=lambda i: getattr(i, 'score', 0))
```

### Compute per-keypoint confidence
```python
conf = np.zeros((n_total_frames, n_nodes))
for lf in labels:
    if lf.instances:
        inst = lf.instances[0]
        conf[lf.frame_idx] = inst.points['score']
```

### Get node index for downstream use
```python
snout_idx = labels.skeleton.index("snout")
tailbase_idx = labels.skeleton.index("tailbase")
tailtip_idx = labels.skeleton.index("tailtip")
hindL_idx = labels.skeleton.index("hindpawL1")
hindR_idx = labels.skeleton.index("hindpawR1")
```

### Read FPS from video metadata
```python
import cv2
cap = cv2.VideoCapture(str(video_path))
fps = cap.get(cv2.CAP_PROP_FPS)
cap.release()
```

## Rendering & Visualization

### sleap-io rendering (preferred — sleap-io >= 0.5.x)

`sleap.io.visuals` is **deprecated**. Use `sleap_io.render_video()` and
`sleap_io.render_image()` instead. Requires `pip install sleap-io[render]`
(adds `skia-python` dependency).

```python
import sleap_io as sio

labels = sio.load_file("predictions.slp")

# Render full video with skeleton overlay → saves to file
sio.render_video(labels, "output.mp4")

# Render specific frame range
sio.render_video(labels, "clip.mp4", start=100, end=200)

# Render at half resolution (faster)
sio.render_video(labels, "preview.mp4", preset="draft")  # or scale=0.5

# Render single frame → returns numpy array
img = sio.render_image(labels, frame_idx=0)

# Save single frame to file
sio.render_image(labels, "frame_0.png", frame_idx=0)
```

**Key `render_video` parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `save_path` | None | Output path. If None, returns list of arrays |
| `start` / `end` | None | Frame range (inclusive start, exclusive end) |
| `frame_inds` | None | Specific frame indices to render |
| `preset` | None | `"preview"` (0.25x), `"draft"` (0.5x), `"final"` (1.0x) |
| `scale` | 1.0 | Output scale factor |
| `show_nodes` | True | Draw keypoint markers |
| `show_edges` | True | Draw skeleton edges |
| `show_centroids` | True | Draw instance centroids |
| `marker_size` | 4.0 | Keypoint marker size in pixels |
| `line_width` | 2.0 | Edge line width |
| `color_by` | "auto" | `"instance"`, `"node"`, `"edge"`, `"track"`, or `"auto"` |
| `palette` | "standard" | `"standard"`, `"alphabet"`, `"five+"`, `"solarized"`, `"distinct"` |
| `marker_shape` | "circle" | `"circle"`, `"square"`, `"diamond"`, `"triangle"`, `"cross"`, `"plus"` |
| `fps` | None | Output FPS (reads from video if None) |
| `codec` | "libx264" | Video codec |
| `crf` | 25 | Quality (lower = better, 18-30 typical) |
| `crop` | None | `(x1, y1, x2, y2)` pixels or `(0.0-1.0)` normalized |
| `overlay` | None | Segmentation masks, ROIs, bounding boxes, or label images |
| `background` | "video" | `"video"` or RGB tuple like `(0, 0, 0)` for black |
| `include_unlabeled` | None | Include frames without predictions |

**Overlay drawing helpers** (for custom rendering):
```python
from sleap_io import draw_rois, draw_masks, draw_bboxes, draw_label_image
```

### sleap-render CLI (full `sleap` package only)

The `sleap-render` command comes from the full `sleap` package (NOT `sleap-io`).
It uses the **deprecated** `sleap.io.visuals` module internally.

```bash
# Basic: render predictions on video
sleap-render predictions.slp -o output.mp4

# Specific frames
sleap-render predictions.slp -o clip.mp4 --frames 100-200

# Customize appearance
sleap-render predictions.slp -o output.mp4 \
    --scale 0.5 \
    --marker_size 6 \
    --palette alphabet \
    --distinctly_color instances \
    --edge_is_wedge 1

# Change FPS
sleap-render predictions.slp -o output.mp4 -f 30
```

**Key `sleap-render` flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `-o` / `--output` | auto | Output video path |
| `-f` / `--fps` | from video | Output FPS |
| `--scale` | 1.0 | Output scale factor |
| `--frames` | all | Frame range (`100-200`) or list (`1,2,3`) |
| `--video-index` | 0 | Which video in the labels file |
| `--show_edges` | 1 | Draw skeleton edges (0/1) |
| `--edge_is_wedge` | 0 | Draw edges as wedges (0/1) |
| `--marker_size` | 4 | Keypoint marker size in pixels |
| `--palette` | standard | `standard`, `alphabet`, `five+`, `solarized` |
| `--distinctly_color` | nodes | Color by `instances`, `edges`, or `nodes` |

### save_video (write raw frames)
```python
import sleap_io as sio
import numpy as np

# Save numpy frames to video (no skeleton overlay)
frames = np.random.randint(0, 255, (100, 480, 640, 3), dtype=np.uint8)
sio.save_video(frames, "raw.mp4", fps=30, codec="libx264", crf=25)
```

## Known Pitfalls

### 1. video.filename vs filesystem path
The `.slp` file stores the ORIGINAL video path at training/inference time in
`labels.videos[0].filename`. If videos were renamed or moved, this path is STALE.

**Always use the filesystem path (from your metadata/directory listing), NOT
`video.filename`, for file lookups (YMLs, other associated files).**

```python
# BAD — uses internal name that may be stale
stem = Path(labels.videos[0].filename).stem

# GOOD — use the actual file path you loaded from
stem = video_path.stem
```

This caused a calibration bug in the T-maze pipeline where `video.filename`
returned original GoPro names (e.g., `GX016467`) while YMLs used renamed
names (e.g., `Day10_15547_Trial1`).

### 2. Frames vs labeled frames
`len(labels)` = number of LABELED frames (with predictions), NOT total video frames.
Total frames = `labels.videos[0].shape[0]`. Unlabeled frames are NOT in `labels`.

### 3. NaN keypoints
Missing/low-confidence keypoints have `(NaN, NaN)` coordinates. Always check:
```python
valid = ~np.isnan(trx[frame, node, 0])
```

### 4. Multi-instance handling
`lf.instances` can have multiple instances (multi-animal tracking). For
single-animal videos, always take `lf.instances[0]` or `pick_best(lf)`.

### 5. sleap vs sleap-io
- `sleap` = full SLEAP package (training, inference, GUI) — heavy dependency
- `sleap-io` = lightweight I/O library — `pip install sleap-io`
- For loading/reading files, `sleap-io` is sufficient and preferred
- For rendering, `sleap-io[render]` has the modern API (`render_video`, `render_image`)
- The `sleap-render` CLI comes from full `sleap`, uses deprecated `sleap.io.visuals`

### 6. File format differences
| Format | Extension | Notes |
|--------|-----------|-------|
| Labels (SLP) | `.slp` | Default SLEAP format, stores predictions + video refs |
| Labels (pkg) | `.pkg.slp` | Self-contained, includes video frames |
| Analysis (H5) | `.analysis.h5` | Exported from SLEAP, flat arrays |
| Predictions | `.predictions.slp` | Output from `sleap-track` |

All loadable with `sio.load_file()`.

### 7. Labels constructor uses `skeletons=` (plural)
```python
# WRONG
sio.Labels(labeled_frames=frames, skeleton=sk)
# RIGHT
sio.Labels(labeled_frames=frames, skeletons=[sk])
```

## Environment

- Package: `sleap-io` (NOT full `sleap`)
- Install: `pip install sleap-io` or `uv pip install sleap-io`
- Current version on workstation: 0.5.8

## Task: $ARGUMENTS
