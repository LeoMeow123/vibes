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
