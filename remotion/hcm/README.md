# THE HOME-CAGE SAGA — Remotion Video

A ~2.5 min anime-style motion graphics explainer about SAAPS (Salk AI Animal Phenotyping System)
for long-term home-cage monitoring of Alzheimer's mouse models. Built entirely in **Remotion** —
all 21 scenes are fully coded motion graphics (no external AI video clips needed).

## Quick start

```bash
cd /home/exx/vast/leo/remotion
npm install
npx remotion studio          # preview in browser
npx remotion render Saga out/home_cage_saga.mp4 --codec h264   # render MP4
```

## How this was built

1. **Scaffolded** a Remotion 4.x project with `create-video`.
2. **Copied** all 19 photos from `hcm/images/` into `public/images/` (8 folders).
3. **Ported** 4 reference HTML animations (freeway, SAAPS pipeline, timeline, sync demo) into React components using `useCurrentFrame()` + `interpolate()`.
4. **Built** 17 additional coded scenes as React components — every scene that was originally planned as an "AI video clip" was replaced with hand-coded motion graphics (animated SVGs, emoji, interpolated transforms).
5. **Wired** all 21 scenes into a `TransitionSeries` with 12-frame fade/slide transitions.
6. **Iterated** on Scene 13 (Freeway) through multiple rounds of coordinate tuning against the real Salk aerial map, adding GPU heat source, 6-lane data freeway, Salk traffic contrast, and 300 TB explosion finale.
7. **Rendered** final MP4 at 1920x1080, 30fps.

## Scene list (21 scenes, ~150s)

| # | Scene | Duration | Type | Description |
|---|-------|----------|------|-------------|
| 1 | Establishing | 8s | Photo | Salk courtyard sunset, Ken Burns, title card |
| 2 | Timeline | 9s | Coded | 3 horizontal bars: fast models vs AD 24-month timeline |
| 3 | Quest Declared | 6s | Coded | Silhouette + cage grid + "BOSS BATTLES: 5" |
| 4 | Phone Melts | 5s | Coded | Phone overheats on cage, smoke, big X |
| 5 | Bare Wires | 7s | Photo | Spotlight reveal of tangled wires, crossfade to soldered |
| 6 | Rig Worth It | 8s | Photo | Camera component labels with checkmark callouts |
| 7 | Four Phones | 6s | Coded | 4 phones with drifting clocks, drift detection |
| 8 | Sync Demon | 7s | Coded | 4 recorder windows, 2 freeze, demon emoji |
| 9 | Orchestrated | 5s | Coded | Chaos -> synchronized grid snapping into place |
| 10 | Encoder | 6s | Coded | Raw streams -> encoder engine -> compressed packets |
| 11 | Scale Reveal | 7s | Photo | Cart photo + "300 TB" dramatic text |
| 12 | Local Drives | 8s | Coded | Bus/tunnel gag: small bus -> big bus -> crash -> streaming |
| 13 | Freeway | 15s | Coded | HERO: Lee Lab GPUs, 3AM night, data freeway, 300 TB explosion |
| 14 | Live Rig | 8s | Photo | Live rig photo with pulsing green glow |
| 15 | SAAPS | 9s | Coded | 9-node pipeline diagram lighting up in sequence |
| 16 | Math Montage | 6s | Coded | Floating equations + parts boxes photo |
| 17 | Army of Bugs | 6s | Coded | Bug swarm crawling over software windows |
| 18 | Team vs Me | 8s | Coded | Split: 15 engineer emojis VS lone researcher -> GitHub graph |
| 19 | Watchtower | 9s | Photo | Dashboard screenshot + Slack GPU alert overlay |
| 20 | Slack Feed | 7s | Coded | Dynamic Slack #hcm-alerts: 10PM -> 2AM -> 9AM messages |
| 21 | End Card | 7s | Photo | Filmstrip pull-back + "to be continued" |

## Key technical details

- **Framework:** Remotion 4.0.468, React, TypeScript
- **Resolution:** 1920x1080 @ 30fps
- **Fonts:** Space Grotesk (display), JetBrains Mono (mono) via `@remotion/google-fonts`
- **Transitions:** `TransitionSeries` with `fade()` and `slide()`, 12-frame overlap
- **Animation:** All via `useCurrentFrame()` + `interpolate()` + `Easing` (NO CSS animations)
- **Images:** `<Img>` + `staticFile()` from `public/images/`
- **Ken Burns:** Reusable component with interpolated scale/translate

## Scene 13 — The Freeway (hero scene)

The showpiece scene. 15 seconds, 5 phases:

1. **Daytime (0-4s):** Lee Lab on 5th floor of Bldg 5 glows as a GPU heat source (8x Blackwell), orbiting GPU chips shimmer
2. **Night transition (4-6s):** Map darkens, "3:00 AM" clock appears, saturation drops
3. **Freeway ramp-up (6-8s):** 70 data "cars" flow along 6 bezier lanes from Bldg 1 (EBS) to Talmo Lab (3rd floor)
4. **Contrast reveal (8-12.5s):** 7 PC nodes appear around Talmo Lab, dim white Salk traffic lines appear on right-side buildings for contrast
5. **300 TB Explosion (12.5-15s):** Data floods 15 underground routes across entire campus, burst rings radiate, screen shakes, "300 TB overwhelms Salk underground"

Coordinate system: `pct(xPct, yPct)` maps image percentages to Remotion pixel coordinates, calibrated against the real `salk_aerial_map.png`.

## File structure

```
remotion/
  src/
    Root.tsx              # Composition definition (21 scenes, durations, fps)
    Saga.tsx              # TransitionSeries wiring all scenes
    styles.ts             # Fonts (Space Grotesk, JetBrains Mono) + color palette
    components/
      Caption.tsx         # Reusable bottom-center pill caption
      KenBurns.tsx        # Reusable Ken Burns photo component
    scenes/
      Scene01_Establishing.tsx  through  Scene22_EndCard.tsx
  public/
    images/               # 19 photos in 8 folders
  out/
    home_cage_saga.mp4    # Rendered output
```

## Color palette

| Name | Hex | Use |
|------|-----|-----|
| bg | #0a0e1a | Dark background |
| acquisition | #6db3ff | Data acquisition, freeway lanes |
| compute | #7be88a | GPU/compute, success states |
| training | #ffc46b | Model training, warnings |
| danger | #ff6b6b | Errors, overheating, alerts |
| source | #ff8a3c | Data source (Bldg 1) |
| ink | #eef1f8 | Primary text |
| muted | #8c97b8 | Secondary text |

## Real facts (from dashboard)

- 510 recording days (2024-09-24 to 2026-05-27)
- 63,897 total videos, 85.1% inference complete
- 25,381 crash artifacts caught
- 4 cameras today (WT/APP cohorts, 3 mice each)
- Building 1 (EBS) -> Talmo Lab 3rd floor -> Lee Lab 5th floor Bldg 5
- Stack: Acquisition PC -> VAST NAS -> NVIDIA Triton on GPU nodes (run:ai)
- Dream scale: 40 cages = 300 TB
