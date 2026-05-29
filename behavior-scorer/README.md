# Behavior Scorer

Lightweight browser-based tool for scoring behaviors in video files. No install needed — just open `index.html`.

## Quick Start

```bash
# Option 1: Open directly
open index.html          # macOS
xdg-open index.html      # Linux
start index.html         # Windows

# Option 2: Via Python server (if file:// doesn't work)
python3 -m http.server 8080
# then open http://localhost:8080
```

## Features

- **Load a folder** of videos (mp4, avi, mov, mkv, webm) — sorted alphabetically
- **Two configurable hotkeys** — name them and pick the key before loading
- **Every keypress logs**: video filename, timestamp (ms precision), frame number, behavior label
- **Auto-saves** to browser localStorage after every event — no data loss on crash/close
- **Resume** previous session if you reload the page
- **Export CSV** with all events (Ctrl+E)
- **Undo** last event (Ctrl+Z)
- **Auto-advance** to next video when current one ends
- **Frame stepping** with `,` and `.` keys
- **Playback speed** control (0.25x–2x)

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| A / S (configurable) | Score behavior 1 / 2 |
| Space | Play / Pause |
| Left / Right arrow | Skip -5s / +5s |
| Shift + Left / Right | Previous / Next video |
| , / . | Step back / forward one frame |
| Ctrl+Z | Undo last event |
| Ctrl+E | Export CSV |

## CSV Output Format

```csv
video,time_sec,frame,behavior
"video_001.mp4",12.345,370,"Grooming"
"video_001.mp4",45.678,1370,"Rearing"
```

## Why not BORIS?

BORIS is powerful but heavy. For simple "watch and count" scoring with many short videos:
- No install, no Python, no dependencies
- Instant video switching (no lag/freeze)
- Auto-save prevents data loss
- Resume sessions across browser restarts
