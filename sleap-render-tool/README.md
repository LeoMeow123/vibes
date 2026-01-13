# SLEAP Render Tool

Browser-based tool for previewing SLEAP skeleton overlays on video before export.

**Solves**: The "render first, preview later" problem with CLI `sleap-render`. Now you can adjust visualization settings in real-time and only export when satisfied.

## Features

- **Load SLP + Video**: Load SLEAP predictions (.slp) and associated video separately
- **Live Preview**: See skeleton overlay on video frames instantly
- **Adjustable Settings**:
  - Node size and edge width
  - Show/hide nodes, edges, labels
  - Multiple color palettes (Default, Viridis, Rainbow, Single color)
- **Frame Navigation**: Play/pause, step frame-by-frame, seek to any frame
- **Export**: Save current frame as PNG (video/GIF export coming soon)
- **Keyboard Shortcuts**: Space (play/pause), Arrow keys (navigate)

## Usage

1. Open `index.html` in a browser (Chrome/Edge recommended)
2. Drag-and-drop or click to load:
   - Your `.slp` file (SLEAP predictions or labels)
   - Your video file (MP4, WebM, MOV)
3. Adjust visualization settings as needed
4. Navigate to the frame you want
5. Export as PNG

## Technical Details

- Uses [h5wasm](https://github.com/usnistgov/h5wasm) to parse SLEAP HDF5 files in the browser
- Web Worker for non-blocking file loading
- HTML5 Canvas for rendering
- No server required - runs entirely in browser

## Limitations

- Video formats must be supported by your browser (MP4 H.264, WebM VP9 work best)
- Large SLP files may take a moment to load
- FPS is assumed to be 30 (configurable in code)
- GIF/WebM export not yet implemented

## Local Development

```bash
# Serve locally
python -m http.server 8000
# Then open http://localhost:8000/sleap-render-tool/
```
