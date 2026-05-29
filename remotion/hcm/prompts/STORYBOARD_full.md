# 🐭 "THE HOME-CAGE SAGA" — Anime Storyboard / Shot List (v2)

**Format:** ~4–5 min anime-style explainer · Audience: lab-internal (colleagues + PIs) · Tone: fun, playful, dramatic
**Protagonist:** Stylized silhouette/avatar of Leo ("the Researcher")
**System name:** SAAPS — Salk AI Animal Phenotyping System

**How to use this doc:** Each scene has (1) a *visual prompt* to paste into an AI video tool (Runway / Kling / Pika) one shot at a time, (2) your *narration* line, (3) the *on-screen caption*, and (4) the *exact asset file* to drop in.

**Recurring style note (paste into every AI-video clip prompt):** *"Anime style, cel-shaded, dramatic shonen-action lighting, dynamic camera, vibrant colors, clean linework, 16:9."*

---

## 📁 ASSET FILENAME KEY (your uploads)

| Short name | File | What it shows |
|---|---|---|
| **WIRES-BOX** | IMG_5660 / IMG_5658 | Box of tangled red/black soldered wires, blue tape |
| **WIRES-SPOOL** | IMG_5661 | Wire spools, zip ties, parts |
| **PARTS-BOXES** | IMG_5662 | Labeled boxes "Wires Processed / Network Cables / DO NOT TAKE!!" |
| **CAM-RAIL-1** | IMG_5659 | Industrial camera + lens mounted on rail over clear cage |
| **CAM-RAIL-2** | IMG_5657 | Camera/rail close, red power wire |
| **CAGE-ACRYLIC** | IMG_5656 | Empty acrylic cage towers + NDR-120-12 power supply |
| **SAAPS-DIAGRAM** | 1779988108748 | Full system architecture diagram (hero) |
| **RIG-LIVE** | 1779988133190 | Live multi-cage rig, mice + water bottles + green cables |
| **LABELS-PLAIN** | 1779988163315 | Component callouts: Camera Bar / Power Supply / LED bars |
| **LABELS-CHECKS** | 1779988188804 | Same + "Consistent FOV / High SNR / Low blur" checkmarks |
| **CART-SCALE** | 1779988228333 | Full cart, two shelves of cage arrays (scale) |
| **SALK-SUNSET** | 1779988294915 | Iconic Salk courtyard at sunset |
| **SALK-AERIAL** | 1779988318512 | Salk top-view aerial map w/ numbered buildings |
| **SLACK-GPU** | 1779988446443 | Daily GPU Status Report (Slack), red "runai offline" |
| **SLACK-HEALTH** | 1779988456342 | HCM Recording Health alert (⚠️ transfer delayed, crashes) |
| **DASHBOARD** | 1779988477499 | HCM Monitor dashboard (510 days, 25,381 crash artifacts) |
| **FILMSTRIP** | 1779988497740 | Per-camera + 24h visual timeline of real mouse frames |
| **GITHUB-GRAPH** | 1779988820448 | GitHub contributions: 41 commits to hcm-dashboard in a month |

---

## 📐 REAL FACTS (use these — verified from your dashboard)

- **510 recording days** (2024-09-24 → 2026-05-27)
- **63,897 total videos**, inference **85.1%** complete
- **25,381 crash artifacts** (tiny files <1MB, 35% of all videos)
- **69.8% hour coverage** (34,165 / 48,960 camera-hours)
- **4 cameras today** — cohorts: Cam1 WT, Cam2 APP, Cam3 WT, Cam4 APP (3 mice each)
- **Geography:** recording in **Building 1 (EBS)** → processing on **3rd floor (main)** → inference on **5th floor, Building 5** → back to network storage
- **Stack:** Acquisition PC → **VAST** network storage → **NVIDIA Triton** Inference Server on **GPU nodes** (run:ai)
- **The dream / scale-up:** 20–40 cages ≈ **300 TB** — more than the institute moves daily
- Recording rate ~50 · inference rate ~120

> Honesty note baked into script: TODAY = 4 cameras, 510 days, 64K videos. THE DREAM = 40 cages, 300 TB. Script keeps current vs. aspirational clearly separated.

---

## 🎬 ACT 0 — COLD OPEN: "The Impossible Quest" (~30 s)

### Scene 1 — Establishing shot → title
- **Asset:** **SALK-SUNSET** (open on the real Salk courtyard, slow push-in, then stylize to anime)
- **Visual prompt:** Iconic modernist research institute courtyard at sunset, long symmetrical water channel pointing to the ocean horizon, a lone researcher silhouette standing center, epic golden light. Anime style, cel-shaded.
- **Narration:** "Why does almost nobody do long-term home-cage monitoring? Because the disease we study doesn't play fair."
- **Caption:** *THE HOME-CAGE SAGA*

### Scene 2 — The 24-month timeline gag
- **Asset:** none (BUILT GRAPHIC — timeline)
- **Visual prompt:** Animated horizontal bars; short disease models = tiny bars, then one giant bar "Alzheimer's — up to 24 months" dwarfs them; prior home-cage studies shown as 1–2 month stubs. Anime infographic.
- **Narration:** "Most models mutate fast. Alzheimer's takes its time — up to twenty-four months. One cage for two years gives you a single n. Not nearly enough."
- **Caption:** *AD ≈ 24 months · prior home-cage studies ≈ 1–2 months*

### Scene 3 — The quest declared
- **Asset:** none (AI video)
- **Visual prompt:** Researcher silhouette raises a fist; cages multiply behind into a vast glowing grid; "level up" aura. Anime style.
- **Narration:** "To get real numbers we need many cages, recording every second, for months. So — let the boss battles begin."
- **Caption:** *BOSS BATTLES: 5*

---

## ⚔️ ACT 1 — BOSS 1: "The Raw Hardware" (~45 s)

### Scene 4 — The naive attempt fails
- **Asset:** none (AI video)
- **Visual prompt:** A cartoon smartphone taped atop a mouse cage glows red, overheats, comic smoke, buzzer "X". Anime gag style.
- **Narration:** "First instinct: stick a phone or webcam on top. It overheats in hours. No twenty-four-seven. Game over."
- **Caption:** *Consumer cameras: melt.*

### Scene 5 — The bare-wires reveal
- **Asset:** **WIRES-BOX** → then **WIRES-SPOOL** (dramatic spotlight reveal, overlay anime sparks/glow)
- **Visual prompt:** Spotlight reveal of a chaotic tangle of red/black wires, soldered tips, zip ties on a workbench, sparks, "epic gear unlocked" glow. Anime style.
- **Narration:** "Industrial cameras don't overheat — but they're raw. They expect an electrical engineer: soldering, wiring, line after line."
- **Caption:** *"These cameras expect an EE. I am becoming one."*

### Scene 6 — The real high-tech rig + why it's worth it
- **Asset:** **LABELS-CHECKS** (reveal callouts one by one: Camera Bar, Camera, LED Light Bars → ✓ Consistent FOV ✓ High SNR ✓ Low blur ✓ Stable capture ✓ Consistent illumination)
- **Visual prompt:** Technical hero shot of a camera bar, industrial camera, and LED light bars with glowing anime callout lines and green check sparkles. Anime infographic style.
- **Narration:** "But raw buys you everything that matters: consistent field of view, high signal, low blur, stable capture, even illumination."
- **Caption:** *Raw gear → real data.*

### Scene 7 — Why not 4 phones?
- **Asset:** none (AI video)
- **Visual prompt:** Four phones float above four cages; clocks tick out of sync, frame counters spin at different speeds, glitch FX. Anime style.
- **Narration:** "And you can't just use four phones — different start times, different frame counts, laggy software. Chaos."
- **Caption:** *4 phones ≠ synced.*

---

## ⚔️ ACT 2 — BOSS 2: "The Sync Demon" (~40 s)

### Scene 8 — Stalling-windows demo
- **Asset:** none (BUILT GRAPHIC — sync demo)
- **Visual prompt:** Desktop where many app windows pop open; the later ones freeze and stack frozen; a grinning "lag demon" looms behind. Anime style.
- **Narration:** "Open a dozen recording programs at once and the late ones just freeze. They won't start clean. They won't stay in step."
- **Caption:** *The Sync Demon appears.*

### Scene 9 — The orchestrated system
- **Asset:** none (AI video) → optionally cut to **CAM-RAIL-1**
- **Visual prompt:** Frozen windows snap into a glowing synchronized grid pulsing in rhythm like a conductor's orchestra, harmony lines connecting them. Anime style.
- **Narration:** "So we built a delicate orchestrated system — every camera, every stream, started and clocked together."
- **Caption:** *Sync Demon: defeated.*

---

## ⚔️ ACT 3 — BOSS 3: "The Data Tsunami / The Freeway" (~80 s — HERO SECTION)

### Scene 10 — The encoder front line
- **Asset:** none (AI video)
- **Visual prompt:** Raw video streams pour into a glowing "encoder" engine on CPU/GPU chips, heat shimmer, data compressing into neat packets. Anime style.
- **Narration:** "Every feed is encoded right at the capture machine — CPUs and GPUs working hard before the data even moves."
- **Caption:** *Encode at the source.*

### Scene 11 — The scale reveal (+ honesty beat)
- **Asset:** **CART-SCALE** (real cart of cage arrays) → push into anime tsunami
- **Visual prompt:** A colossal wave made of glowing video files towers over a tiny researcher; "300 TB" blazes in the sky. Epic anime disaster-scale shot.
- **Narration:** "Today it's four cameras. Scale to the dream — twenty, forty cages — and it's three hundred terabytes. More than the whole institute moves in a day. And it never stops."
- **Caption:** *Today: 4 cams · The dream: 40 cages ≈ 300 TB*

### Scene 12 — Why not local drives?
- **Asset:** none (AI video)
- **Visual prompt:** A hard drive cracks and shatters with a sad comic face; beside it a snail carries a drive across a huge campus. Anime gag style.
- **Narration:** "Local drives? They break — and your data dies with them. Slow, hand-hauled, no space, nobody maintaining them."
- **Caption:** *Local drive = single point of failure.*

### Scene 13 — THE FREEWAY HERO SHOT ⭐ (geographically real)
- **Asset:** **SALK-AERIAL** (animate light-trails over the real map)
- **Visual prompt:** Top-down night view of the Salk Institute; **Building 1 (EBS)** lights up as the recording source; streams of light flow like night freeway traffic to **3rd-floor compute**, then surge up to the **5th floor of Building 5** for inference, then flow back down to a glowing VAST storage vault. Tron-like light trails, sweeping cinematic camera. Anime style.
- **Narration:** "Here's the dream made real. Data lights up in Building 1, races to the third-floor machines, climbs to the fifth floor for inference on Triton, then flows back down to VAST storage. Recording at fifty, inference at one-twenty."
- **Caption:** *Bldg 1 → 3rd floor → 5th floor → VAST*

### Scene 14 — Playful Salk flourish (optional)
- **Asset:** **SALK-SUNSET** (anime-ified) or AI video
- **Visual prompt:** The institute's iconic twin buildings as a charming anime landmark, mascot mice waving. Anime style.
- **Narration:** "(beat / light humor)"
- **Caption:** *Salk Institute, but make it anime.*

---

## ⚔️ ACT 4 — BOSS 4: "Build It By Hand" (~50 s)

### Scene 15 — Manual assembly → the live rig
- **Asset:** **RIG-LIVE** (hero) — the working rig with mice, water bottles, green cable bundles
- **Visual prompt:** Fast montage of hands assembling clear cages, embedding tiny IR/LED bars into transparent walls, routing wires, "crafting" sparkles; end on the finished live rig glowing. Anime montage style.
- **Narration:** "Forty, fifty cages — nobody had built this before. We assembled them by hand: LED and infrared bars inside each clear cage, wired into one power supply."
- **Caption:** *Hand-built. And it's alive.*

### Scene 16 — The architecture (animate the real diagram)
- **Asset:** **SAAPS-DIAGRAM** (BUILT ANIMATION — boxes light up in sequence)
- **Visual prompt:** The SAAPS architecture diagram with each stage illuminating in order: Home cage → Camera(s) → Acquisition PC → VAST storage → curation → training → Triton inference on GPU nodes → back. Glowing flow lines. Clean infographic.
- **Narration:** "Cameras and lights into one supply; cameras into a switch; the switch into one computer. Four cages per machine — so scaling means serious compute."
- **Caption:** *Home cage → PC → VAST → Triton → GPU nodes*

### Scene 17 — The math montage
- **Asset:** **PARTS-BOXES** (the "DO NOT TAKE!!" boxes as a gag cutaway) + AI video whiteboard
- **Visual prompt:** Researcher at a glowing whiteboard of equations — bandwidth, transfer frequency, clock sync, auto-naming, encoder settings — formulas swirling. Anime study-montage.
- **Narration:** "Behind it all: bandwidth math, transfer frequency, keeping clocks aligned, code for direct transfer and auto-naming to storage, encoder tuning. A delicate machine."
- **Caption:** *bandwidth · sync · auto-naming · encoding*

---

## ⚔️ ACT 5 — FINAL BOSS: "Eternal Vigilance" (~55 s)

### Scene 18 — The army of bugs
- **Asset:** none (AI video)
- **Visual prompt:** Swarms of cute-but-menacing cartoon "bug" creatures crawling over stacked software windows; the whole system glows with them. Anime style.
- **Narration:** "Now multiply it. Every program has its bugs — tens, hundreds. Run them together and you stand on a mountain of them."
- **Caption:** *Every system runs on bugs.*

### Scene 19 — Big teams vs. one researcher (with proof)
- **Asset:** AI video split-screen → cut to **GITHUB-GRAPH** (green squares fill in as the punchline)
- **Visual prompt:** Split screen: a huge army of engineers maintaining glowing apps vs. one lone researcher with a determined grin; then a GitHub-style contribution grid fills with green squares like a power meter charging. Anime comedic contrast.
- **Narration:** "Big companies have whole teams keeping their apps alive. Us? A little short-handed — forty-one commits in a month, just keeping the dashboard breathing."
- **Caption:** *Them: a team. Me: 41 commits this month.*

### Scene 20 — The watchtower (real dashboard + Slack)
- **Asset:** **DASHBOARD** (hero) → cut to **SLACK-GPU** (note the red "runai offline" dot)
- **Visual prompt:** A glowing command-center dashboard with green/red health tiles; a red node pings into a Slack alert with a dramatic "!". Anime style.
- **Narration:** "So we built a watchtower: a dashboard and Slack bot that flag everything — transfer, quality, inference — the second something breaks. Five-hundred-ten days. Sixty-four thousand videos. Twenty-five thousand crash artifacts caught."
- **Caption:** *510 days · 63,897 videos · 25,381 crashes caught*

### Scene 21 — The 2 AM alarm
- **Asset:** **SLACK-HEALTH** (the ⚠️ "Transfer delayed / crashes / degraded" alert) → AI video of researcher waking
- **Visual prompt:** A bleary anime researcher bolts upright at 2 AM, phone glowing with a Slack warning, throws on a jacket, tired-heroic, moonlight. Anime style, bittersweet-funny.
- **Narration:** "And sometimes the watchtower wakes you. Two a.m. … four a.m. … to go save the recording yourself."
- **Caption:** *02:00 — ⚠️ transfer delayed. The recording must go on.*

### Scene 22 — The end card
- **Asset:** **FILMSTRIP** (the 24h grid of real mouse frames, Cam 1–4) → pull back
- **Visual prompt:** A wall of real 24-hour mouse-monitoring frames glowing in a grid; researcher stands before it, calm triumphant dawn light. Anime style.
- **Narration:** "This is how the home-cage data is really collected. One boss at a time."
- **Caption:** *THE HOME-CAGE SAGA — to be continued.*

---

## 📋 PRODUCTION CHECKLIST

**Built graphics (I make these in Claude, screen-record them):**
- Scene 2 — 24-month timeline
- Scene 8 — stalling-windows sync demo
- Scene 16 — animated SAAPS diagram
- Scene 13 — animated Salk freeway map (over SALK-AERIAL)

**AI-video clips to generate (Runway/Kling/Pika) — use recurring style note:**
3, 4, 7, 9, 10, 12, 14, 18, 19, 21 (character/epic scenes)

**Real photos placed:** Scenes 1, 5, 6, 11, 15, 16, 17, 19, 20, 21, 22 — all assigned ✅

**Assembly:** generate/record each beat → import to CapCut or DaVinci Resolve → lay narration → add music → export MP4.

---

## 🎙️ NARRATION SCRIPT (record in one pass)

> Why does almost nobody do long-term home-cage monitoring? Because the disease we study doesn't play fair.
> Most models mutate fast. Alzheimer's takes its time — up to twenty-four months. One cage for two years gives you a single n. Not nearly enough.
> To get real numbers we need many cages, recording every second, for months. So — let the boss battles begin.
> First instinct: stick a phone or webcam on top. It overheats in hours. No twenty-four-seven. Game over.
> Industrial cameras don't overheat — but they're raw. They expect an electrical engineer: soldering, wiring, line after line.
> But raw buys you everything that matters: consistent field of view, high signal, low blur, stable capture, even illumination.
> And you can't just use four phones — different start times, different frame counts, laggy software. Chaos.
> Open a dozen recording programs at once and the late ones just freeze. They won't start clean. They won't stay in step.
> So we built a delicate orchestrated system — every camera, every stream, started and clocked together.
> Every feed is encoded right at the capture machine — CPUs and GPUs working hard before the data even moves.
> Today it's four cameras. Scale to the dream — twenty, forty cages — and it's three hundred terabytes. More than the whole institute moves in a day. And it never stops.
> Local drives? They break — and your data dies with them. Slow, hand-hauled, no space, nobody maintaining them.
> Here's the dream made real. Data lights up in Building 1, races to the third-floor machines, climbs to the fifth floor for inference on Triton, then flows back down to VAST storage. Recording at fifty, inference at one-twenty.
> Forty, fifty cages — nobody had built this before. We assembled them by hand: LED and infrared bars inside each clear cage, wired into one power supply.
> Cameras and lights into one supply; cameras into a switch; the switch into one computer. Four cages per machine — so scaling means serious compute.
> Behind it all: bandwidth math, transfer frequency, keeping clocks aligned, code for direct transfer and auto-naming to storage, encoder tuning. A delicate machine.
> Now multiply it. Every program has its bugs — tens, hundreds. Run them together and you stand on a mountain of them.
> Big companies have whole teams keeping their apps alive. Us? A little short-handed — forty-one commits in a month, just keeping the dashboard breathing.
> So we built a watchtower: a dashboard and Slack bot that flag everything — transfer, quality, inference — the second something breaks. Five-hundred-ten days. Sixty-four thousand videos. Twenty-five thousand crash artifacts caught.
> And sometimes the watchtower wakes you. Two a.m. … four a.m. … to go save the recording yourself.
> This is how the home-cage data is really collected. One boss at a time.
