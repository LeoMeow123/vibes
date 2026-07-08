# Drink / Eat Annotator

Frame-accurate **bout** annotator for scoring **drinking** and **eating** in HCM
home-cage videos — multi-animal, browser-only, no install. A focused, purpose-built
companion to the generic event-annotator, matching the eating/drinking pipeline's
nose/head-in-zone *bout* model (start → end, with duration).

## Use
1. Open `index.html` (or the hosted page).
2. **Open a video** (local file or paste a URL — HCM `.mp4` chunks stream fine), or drag one onto the player.
3. Set **FPS** (default 30) or click **detect**. Frame accuracy depends on this.
4. Pick the **active animal** (`0`–`9`).
5. Press **`D`** to start a *drinking* bout, **`D`** again to end it. Same with **`E`** for *eating*.
6. Bouts appear in the sidebar list and on the per-animal **timeline**. Click to seek/select; nudge edges with `[` / `]`.
7. **Export CSV** (or JSON) for comparison against the pipeline.

## Keyboard
| Key | Action |
|---|---|
| `Space` | play / pause |
| `←` `→` | ±1 frame · `Shift`+arrows = ±10 |
| `,` `.` | frame step |
| `0`–`9` | select active animal |
| `D` / `E` | start / end a drinking / eating bout (active animal) |
| `[` / `]` | set selected bout's start / end to current frame |
| `Del` | delete selected bout · `Esc` cancel open bout / deselect |

## CSV output
```csv
video,animal,behavior,start_frame,end_frame,start_time_s,end_time_s,duration_s
"cam_01.00.mp4",1,Drinking,340,520,11.333,17.333,6.000
"cam_01.00.mp4",0,Eating,900,1180,30.000,39.333,9.333
```
Frames are `round(time × fps)`; times are `frame / fps`. Auto-saves to `localStorage`
per video, so a reload resumes where you left off.

## Notes
- Animal IDs are assigned manually (0–9). It does **not** parse `.slp` pose files;
  it's a lightweight scorer. (SLP overlay could be added later.)
- Duration/frames are only as accurate as the FPS you set — use **detect** or enter the true value.
