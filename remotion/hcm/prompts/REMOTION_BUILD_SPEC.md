# 🎞️ REMOTION BUILD SPEC — "The Home-Cage Saga"

Hand this whole folder to **Claude Code**. This file tells it exactly what video to build.

---

## 0. WHAT THIS IS
A ~4–5 minute anime-style explainer about building a long-term home-cage monitoring system for
Alzheimer's research, told as a series of "boss battles." Audience: the lab (colleagues + PIs).
Tone: fun, playful, dramatic, self-deprecating.

There are THREE kinds of scene:
1. **Coded motion graphics** — Remotion builds these from scratch (diagrams, charts, the freeway, the pile-up). Specs below.
2. **Real-photo scenes** — Remotion shows your images with motion (Ken Burns), animated callouts, captions. Images are in `/images`.
3. **AI-video clips** — generated elsewhere (see `prompts/AI_VIDEO_PROMPTS.md`), dropped in as `<Video>`. Leave placeholder gaps for these.

---

## 1. PROJECT SETUP (Claude Code: do this first)
```bash
npm create video@latest -- --template blank saga
cd saga
npm i
# fonts: @remotion/google-fonts ; for charts you can hand-roll SVG (no extra dep needed)
```
- Composition: **1920×1080, 30fps**.
- Put user images in `public/images/...` (copy from this package's `/images`).
- AI clips (when ready) go in `public/aiclips/scene03.mp4` etc. Until then, render a labeled placeholder card.
- One `<Series>` of scenes is the simplest top-level structure. Each scene = its own component.

Reference HTML for the four already-built graphics is in `/built_animations` — **port these to React/Remotion**,
don't iframe them. They show the exact look, timing, and copy to reproduce.

---

## 2. GLOBAL STYLE
- **Fonts:** display = "Space Grotesk" (bold); mono captions = "JetBrains Mono". (via @remotion/google-fonts)
- **Palette:** bg `#0a0e1a` (near-black navy); acquisition blue `#6db3ff`; compute green `#7be88a`;
  training amber `#ffc46b`; danger/bug red `#ff6b6b`; source orange `#ff8a3c`.
- **Captions:** bottom-center pill, mono font, `rgba(10,14,28,.85)` bg, 1px border `#2a3550`, fade in/out.
- **Transitions:** use `@remotion/transitions` — `fade` (0.4s) between most scenes; a `slide` up for act breaks.
- **Audio:** leave an `<Audio>` track slot for the narration VO + a music bed. Add markers per scene.

---

## 3. SCENE-BY-SCENE TIMELINE
Format: `# | scene | seconds | type | asset | caption`
(Build at 30fps. Durations are starting points — adjust to the VO.)

| # | Scene | sec | Type | Asset / build | Caption |
|---|-------|-----|------|---------------|---------|
| 1 | Establishing → title | 8 | photo+text | `05_salk/salk_courtyard_sunset.png` slow push-in → title card | THE HOME-CAGE SAGA |
| 2 | 24-month timeline | 9 | **CODED** | port `built_animations/timeline_24mo.html` | AD ≈ 24 months · prior studies ≈ 1–2 mo |
| 3 | Quest declared | 6 | AI-clip | `aiclips/scene03.mp4` (placeholder) | BOSS BATTLES: 5 |
| 4 | Phone melts (gag) | 5 | AI-clip | `aiclips/scene04.mp4` | Consumer cameras: melt. |
| 5 | Bare-wires reveal | 7 | photo+text | `01_hardware_wiring/wires_box_tangled.jpeg` (spotlight push-in) → cut `wires_box_soldered.jpeg` | "These cameras expect an EE. I am becoming one." |
| 6 | Real rig + why worth it | 8 | photo+callouts | `02_cameras/component_labels_checkmarks.png` — reveal ✓FOV ✓SNR ✓low-blur ✓stable ✓illum one by one | Raw gear → real data. |
| 7 | 4 phones out of sync | 6 | AI-clip | `aiclips/scene07.mp4` | 4 phones ≠ synced. |
| 8 | The Sync Demon | 7 | **CODED** | port `built_animations/sync_demon.html` | The Sync Demon appears. |
| 9 | Orchestrated system | 5 | AI-clip | `aiclips/scene09.mp4` → opt. cut to `02_cameras/camera_on_rail_1.jpeg` | Sync Demon: defeated. |
| 10 | Encoder front line | 6 | AI-clip | `aiclips/scene10.mp4` | Encode at the source. |
| 11 | Scale reveal (tsunami) | 7 | photo→AI | `04_scale/full_cart_cage_arrays.png` pan up → AI tsunami `aiclips/scene11.mp4` | Today: 4 cams · The dream: 40 cages ≈ 300 TB |
| 12 | No local drives | 6 | AI-clip | `aiclips/scene12.mp4` (snail) OR coded pile-up (see §4) OR bus | Local drive = single point of failure. |
| 13 | **THE FREEWAY** ⭐ | 10 | **CODED** | port `built_animations/salk_freeway.html` (uses `05_salk/salk_aerial_map.png`) | Bldg 1 → 3rd floor → 5th floor → VAST |
| 14 | Salk flourish | 5 | AI-clip | `aiclips/scene14.mp4` | Salk Institute, but make it anime. |
| 15 | Hand-built rig | 8 | photo+text | `03_cage_build/live_rig_with_mice.png` (parallax, LED glow) | Hand-built. And it's alive. |
| 16 | Architecture | 9 | **CODED** | port `built_animations/saaps_animated.html` (or animate `06_architecture/saaps_system_diagram.png`) | Home cage → PC → VAST → Triton → GPU nodes |
| 17 | Math montage | 6 | photo+text | `01_hardware_wiring/parts_boxes_donottake.jpeg` gag cutaway + animated equations overlay | bandwidth · sync · auto-naming · encoding |
| 18 | Army of bugs | 6 | AI-clip | `aiclips/scene18.mp4` | Every system runs on bugs. |
| 19 | Team vs. me | 8 | AI→photo | `aiclips/scene19.mp4` → cut to `08_personal/github_41_commits.png` (green squares fill in) | Them: a team. Me: 41 commits this month. |
| 20 | The watchtower | 9 | photo+text | `07_monitoring/dashboard_full.png` (Ken Burns over tiles) → `07_monitoring/slack_gpu_status.png` | 510 days · 63,897 videos · 25,381 crashes caught |
| 21 | 2 AM alarm | 7 | photo→AI | `07_monitoring/slack_recording_health.png` (⚠️ alert zoom) → `aiclips/scene21.mp4` | 02:00 — ⚠️ transfer delayed. The recording must go on. |
| 22 | End card | 7 | photo+text | `07_monitoring/dashboard_filmstrip.png` (24h mouse grid) pull-back + title | THE HOME-CAGE SAGA — to be continued. |

**Total ≈ 165s of built/photo + AI clips → lands ~4–4.5 min with VO pacing.**

---

## 4. CODED SCENE SPECS (what Remotion must build from scratch)

### 4a. Timeline (Scene 2) — port from `timeline_24mo.html`
Three horizontal bars grow left-to-right with spring easing, staggered:
- "Fast-mutating models" → ~10% width (blue), label "weeks"
- "Prior home-cage studies" → ~17% width (light blue), label "1–2 mo"
- "Alzheimer's disease" → 100% width (red→amber gradient), label "up to 24 months"
Then punchline text fades in: "One cage, 24 months → a single n. Not enough."
Axis under bars: 0 / 6mo / 12mo / 18mo / 24mo.

### 4b. Sync Demon (Scene 8) — port from `sync_demon.html`
Four "recorder" windows pop in (spring scale). cam_01 healthy green "50 fps"; cam_02 drifts to "38 fps";
cam_03 & cam_04 show "— fps" and get a rotated red "FROZEN" stamp + scanline glitch overlay.
A 👹 demon emoji/graphic fades in bottom-right. Captions track the beats.

### 4c. Salk Freeway (Scene 13) ⭐ — port from `salk_freeway.html`
Background = `05_salk/salk_aerial_map.png`, darkened (brightness .5, night vignette).
Three glowing nodes + animated stroke-dashoffset light-trails, in sequence:
1. **Building 1 · EBS** (orange, "RECORDING SOURCE") at lower portion of map
2. trail up to **3rd floor · COMPUTE** (blue) mid-map
3. trail up to **5th floor · Bldg 5 · TRITON INFERENCE** (green) upper map
4. trail back down to **VAST STORAGE** (purple) mid-right
Caption beats: "Data lights up in Building 1" → "Races to the 3rd-floor machines" →
"Climbs to the 5th floor for inference on Triton" → "Flows back down to VAST" → "Record 50 → Infer 120 → Store".
NOTE: HTML is scaled portrait; in Remotion, place the map to fill frame height and animate nodes in its coordinate space.

### 4d. SAAPS pipeline (Scene 16) — port from `saaps_animated.html`
9 nodes light up in sequence with a traveling pulse along edges:
Home cage → Camera(s) → Acquisition PC → VAST storage → Dataset curation → Train&Eval → Models →
Triton Inference → GPU nodes → (loop back to Acquisition PC = "results return").
Group labels fade in: DATA ACQUISITION (blue), MODEL TRAINING (amber), COMPUTE INFRASTRUCTURE (green).

### 4e. (OPTIONAL) Real-time pile-up (Scene 12 alt) — NOT yet built, build if wanted
A conveyor belt enters frame from the right carrying "video block" boxes at a fixed rate.
A small "transfer" outlet on the left drains them slower than they arrive → boxes visibly pile up and
overflow the frame. Then toggle "REAL-TIME ON" → drain speed matches arrival → pile clears.
Caption: "Record nonstop → must transfer in real-time, or it buries you."
(This is the coded cousin of the "bus" AI prompt. Either/both.)

---

## 5. REAL-PHOTO SCENE RECIPES (reusable Remotion patterns)
- **Ken Burns:** interpolate `scale` 1.0→1.08 and a slight `translate` over the scene; `overflow:hidden` parent.
- **Spotlight reveal (Scene 5):** start dark (`brightness .2`), animate a radial-gradient mask / brightness up to 1.0.
- **Callout reveal (Scene 6):** the image already has printed labels; animate small glowing dots + the green ✓ items
  appearing one-by-one with `spring()` opacity/scale, sequenced.
- **GitHub fill (Scene 19):** overlay animated green squares (or just a left-to-right wipe mask) across the
  contribution grid so it looks like it "charges up"; then stamp "41 commits".
- **Alert zoom (Scene 21):** Ken Burns hard-zoom into the ⚠️ "Transfer delayed" row of the Slack image; add a
  pulsing red glow ring; shake very slightly for urgency.

---

## 6. CAPTIONS & VO
- All caption strings are in the table above (and in `SCRIPT_AND_CAPTIONS.md`).
- Narration script (record in one pass) is in `SCRIPT_AND_CAPTIONS.md`. Drop the VO as one `<Audio>`,
  or split per-scene. Time scene durations to the VO once recorded.
- Add a soft music bed at low volume; duck under VO.

---

## 7. RENDER
```bash
npx remotion render saga out/saga.mp4 --codec=h264 --crf=18
```
Render a draft early (even with placeholder AI cards) to check pacing, then swap AI clips in as you generate them.

---

## 8. BUILD ORDER (recommended for Claude Code)
1. Project scaffold + global style + fonts + caption component.
2. Port the 4 coded scenes (2, 8, 13, 16) — these are spec'd and proven.
3. Build the photo scenes (1, 5, 6, 11, 15, 17, 20, 21, 22) with Ken Burns + callouts.
4. Add placeholder cards for AI scenes (3,4,7,9,10,12,14,18,19,21).
5. Wire up `<Series>`, transitions, captions.
6. Draft render → adjust timing.
7. Generate AI clips (prompts in `prompts/AI_VIDEO_PROMPTS.md`), drop in, final render.
