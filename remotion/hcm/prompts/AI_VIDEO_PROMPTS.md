# 🎬 AI-VIDEO PROMPTS — Character & Anime Scenes

These are the scenes that need a **generative AI video tool** (Runway Gen-3 / Kling / Pika / Hailuo).
Remotion CANNOT generate these — it animates code, shapes, and your images. Generate these clips
separately, export as MP4, then drop them into the Remotion timeline as `<Video>` clips.

**PASTE THIS STYLE SUFFIX ONTO EVERY PROMPT** (keeps a consistent look across clips):
> *"Anime style, cel-shaded, dramatic shonen-action lighting, dynamic camera move, vibrant saturated colors, clean bold linework, film grain, 16:9 cinematic."*

**Tool tips:**
- **Kling** (kling.ai) — best for character motion + dramatic camera, generous free clips. Start here.
- **Runway Gen-3** — most controllable, good image-to-video (you can feed a reference frame).
- **Pika / Hailuo** — fast, good for short gag shots.
- Generate **5–8 sec** per clip. Make 2–3 variations of each, pick the best.
- For consistency of the "researcher silhouette," generate one good character clip first, then use
  it as an image reference (image-to-video) for the others where the tool supports it.

---

## SCENE 3 — The quest declared
**Prompt:** A lone researcher silhouette stands before a vast dark wall of glowing mouse cages stretching into the distance; they raise a fist with determination; the cages multiply behind them into an enormous grid; a "level-up" energy aura pulses outward. [STYLE SUFFIX]
**Duration:** 6s · **Caption to overlay later:** *BOSS BATTLES: 5*

## SCENE 4 — The naive attempt fails (gag)
**Prompt:** Comedic anime shot: a smartphone is taped to the top of a clear mouse cage; it glows red, vibrates, overheats with puffs of cartoon smoke, then a big red "X" buzzer flashes. Exaggerated comedic timing. [STYLE SUFFIX]
**Duration:** 5s · **Caption:** *Consumer cameras: melt.*

## SCENE 7 — Four phones out of sync
**Prompt:** Four smartphones float in a row above four mouse cages; each phone's clock and frame-counter spins at a different speed, drifting out of sync; glitch and stutter effects ripple between them; growing visual chaos. [STYLE SUFFIX]
**Duration:** 6s · **Caption:** *4 phones ≠ synced.*

## SCENE 9 — The orchestrated system (resolve)
**Prompt:** Chaotic frozen UI windows snap into a glowing, perfectly synchronized grid that pulses in rhythm like an orchestra led by an unseen conductor; harmonious light-lines connect every node; calm restored. [STYLE SUFFIX]
**Duration:** 5s · **Caption:** *Sync Demon: defeated.*

## SCENE 10 — The encoder front line
**Prompt:** Raw streams of video pour like glowing rivers into a humming machine engine labeled with CPU/GPU chips; heat shimmer rises; the data compresses into neat glowing packets that shoot out the other side. [STYLE SUFFIX]
**Duration:** 6s · **Caption:** *Encode at the source.*

## SCENE 12 — Why not local drives (gag)
**Prompt:** Anime gag: a single hard drive cracks down the middle and shatters with a sad cartoon face; beside it, a tired snail slowly carries another hard drive across an enormous campus map. Comedic, slightly melancholy. [STYLE SUFFIX]
**Duration:** 6s · **Caption:** *Local drive = single point of failure.*

## SCENE 12-ALT — THE BUS metaphor (your original idea — optional alternative to the snail)
**Prompt:** Anime: a single city bus tries to make impossibly many pickups across a sprawling research campus at rush hour; passengers (glowing data packets) pile up faster than the bus can carry them; the queue grows endlessly; comedic overwhelm. [STYLE SUFFIX]
**Duration:** 7s · **Caption:** *One bus can't make every pickup.*
> NOTE: I'm ALSO building a coded "pile-up" version in Remotion (see remotion spec). Use whichever you like, or both.

## SCENE 14 — Playful Salk flourish
**Prompt:** The iconic twin concrete buildings of a seaside modernist research institute, reimagined as a charming anime landmark at golden hour; tiny cute mascot mice wave from the courtyard; whimsical and warm. [STYLE SUFFIX]
**Duration:** 5s · **Caption:** *Salk Institute, but make it anime.*

## SCENE 18 — The army of bugs
**Prompt:** Swarms of cute-but-menacing little cartoon "bug" creatures crawl across stacked glowing software windows; they multiply across the whole system; mischievous chaos energy. [STYLE SUFFIX]
**Duration:** 6s · **Caption:** *Every system runs on bugs.*

## SCENE 19 — Big team vs. one researcher
**Prompt:** Split-screen anime: on the left, a vast army of engineers in formation maintaining giant glowing apps; on the right, one lone tired-but-determined researcher holding a mop, standing alone. Comedic contrast, heroic underdog framing. [STYLE SUFFIX]
**Duration:** 6s · **Caption:** *Them: a team. Me: 41 commits this month.*
> Then cut to the real GitHub graph (handled in Remotion — see spec).

## SCENE 21 — The 2 AM alarm
**Prompt:** A bleary anime researcher bolts upright in bed in the dark; their phone glows with an urgent alert; moonlight through the window; they throw on a jacket with tired heroic resolve. Bittersweet, slightly funny. [STYLE SUFFIX]
**Duration:** 7s · **Caption:** *02:00 — the recording must go on.*

## SCENE 22 — End hero (optional anime version)
**Prompt:** A researcher silhouette stands before a glowing wall of mouse cages with data flowing smoothly through them; calm triumphant dawn light breaks; sense of a quest completed. [STYLE SUFFIX]
**Duration:** 6s · **Caption:** *THE HOME-CAGE SAGA — to be continued.*

---

## OPTIONAL: animate your REAL photos with image-to-video
Some tools (Runway, Kling) let you upload a still and add subtle motion. Try these with your real images
for extra life (keep motion SUBTLE so they don't warp):

- `01_hardware_wiring/wires_box_tangled.jpeg` → "slow push-in, faint electrical sparks, dust motes" (Scene 5)
- `03_cage_build/live_rig_with_mice.png` → "gentle parallax, soft LED glow pulse" (Scene 15)
- `05_salk/salk_courtyard_sunset.png` → "slow aerial push-in toward the sun" (Scene 1)
- `04_scale/full_cart_cage_arrays.png` → "slow vertical pan up the racks" (Scene 11)
