# ML for Wet Lab — Remotion Video

A ~1.3 min animated explainer teaching wet lab researchers why camera consistency
matters for ML-based pose tracking (SLEAP). Built entirely in **Remotion** —
all 12 scenes are coded motion graphics with embedded images from existing slides.

## Quick start

```bash
cd /home/exx/vast/leo/remotion
npm install
npx remotion studio          # preview in browser (select "MLDemo" composition)
npx remotion render MLDemo out/ml_demo.mp4 --codec h264   # render MP4
```

## How this was built

1. **Extracted assets** from `Demo Machine learning.pptx` using `python-pptx`:
   - SLEAP logo, pipeline diagram, failure mode images (motion blur, low contrast, occlusion, rearing)
   - Localization error chart, sample efficiency curve, before/after cage photos
   - Saved to `public/images/ml_demo/`
2. **Designed 12 scenes** around the core message: "computers see pixels, not mice"
   - Part 1 (Scenes 1–5): What the computer sees + how SLEAP works
   - Part 2 (Scenes 6–9): What works vs what breaks it (angle, lights, position)
   - Part 3 (Scenes 10–12): The golden rule + retraining + end card
3. **Coded each scene** as a React component using `useCurrentFrame()` + `interpolate()` + `Easing`
4. **Wired** all 12 scenes into a `TransitionSeries` with 12-frame fade/slide transitions
5. **Added** as a second composition (`MLDemo`) alongside the existing `Saga` in `Root.tsx`
6. **Rendered** final MP4 at 1920x1080, 30fps

## Scene list (12 scenes, ~77s)

| # | Scene | Duration | Type | Teaching point |
|---|-------|----------|------|----------------|
| 1 | Title | 5s | Coded | SLEAP logo + "ML for Wet Lab" |
| 2 | Human vs Computer | 7s | Coded | Split: you see a mouse — computer sees a number grid |
| 3 | Pixel Zoom | 7s | Coded | Mouse emoji pixelates into brightness values 0–255 |
| 4 | Labeling | 8s | Coded | Keypoints placed on mouse skeleton — "like flashcards" |
| 5 | Neural Network | 7s | Coded | Image → conv layers → heatmaps → keypoints diagram |
| 6 | It Works! | 6s | Photo+Coded | Good tracking image + green confidence bar + pipeline |
| 7 | Camera Angle | 8s | Photo+Coded | Camera tilts → failure image with scattered keypoints |
| 8 | Lights Off | 7s | Coded | Brightness slider → pixel values collapse to ~0 |
| 9 | Camera Moved | 7s | Photo+Coded | Position shifts → different background → confused model |
| 10 | Golden Rule | 7s | Coded | Animated checklist: same camera, angle, lighting, background |
| 11 | Retrain | 7s | Photo+Coded | Retraining cycle + accuracy charts from slides |
| 12 | End Card | 5s | Coded | "Keep it consistent!" + SLEAP logo |

## Key concepts taught

1. **Computers see pixels, not mice** — every frame is a grid of brightness values
2. **Neural networks are pattern matchers** — they memorize "this pixel pattern = nose"
3. **Three things that break it:**
   - Changing the camera angle → all pixel positions shift
   - Turning off lights → pixel values collapse to near-zero
   - Moving the camera → background changes completely
4. **The golden rule:** same camera + same angle + same lighting = happy model
5. **If you must change:** retrain with new labeled data from the new setup

## Images used from slides

| File | Source slide | Content |
|------|-------------|---------|
| `sleap_logo.png` | — | SLEAP app icon |
| `slide02_Picture_7.png` | Slide 2 | SLEAP pipeline: Videos → Labeling → NN → Pose → Tracking |
| `slide10_Picture_4.png` | Slide 10 | Good tracking — mouse with clean keypoints |
| `slide10_Picture_25.png` | Slide 10 | Failure — two mice, scattered keypoints (motion blur) |
| `slide10_Picture_26.png` | Slide 10 | Failure — single mouse, messy keypoints (low contrast) |
| `slide10_Picture_28.png` | Slide 10 | Failure — rearing mouse with stretched skeleton |
| `slide08_Content_Placeholder_4.png` | Slide 8 | Sample efficiency curve (accuracy vs # labels) |
| `slide11_Content_Placeholder_22.png` | Slide 11 | Localization error improvement with more labels |
| `slide12_Content_Placeholder_4.png` | Slide 12 | Cage view — position A |
| `slide12_Picture_6.png` | Slide 12 | Cage view — position B |

## File structure

```
remotion/
  src/
    Root.tsx              # Both compositions: Saga + MLDemo
    MLDemo.tsx            # TransitionSeries wiring 12 ML scenes
    styles.ts             # Shared fonts + color palette
    scenes/
      ML01_Title.tsx      # SLEAP logo + title
      ML02_HumanVsComputer.tsx  # Split-screen pixel grid vs mouse
      ML03_PixelZoom.tsx  # Progressive pixelation
      ML04_Labeling.tsx   # Keypoint placement on skeleton
      ML05_NeuralNet.tsx  # Network layer diagram with data flow
      ML06_ItWorks.tsx    # Good tracking + confidence bar
      ML07_AngleChanged.tsx  # Camera tilt → failure
      ML08_LightsOff.tsx  # Brightness collapse
      ML09_CameraMoved.tsx  # Position shift → different background
      ML10_GoldenRule.tsx # Consistency checklist
      ML11_Retrain.tsx    # Retraining cycle + accuracy charts
      ML12_EndCard.tsx    # "Keep it consistent!"
  public/
    images/
      ml_demo/            # 23 images extracted from PPTX
  out/
    ml_demo.mp4           # Rendered output (8.4 MB, ~77s)
```

## Technical details

- **Framework:** Remotion 4.0.468, React, TypeScript
- **Resolution:** 1920x1080 @ 30fps
- **Source slides:** `Demo Machine learning.pptx` (12 slides, extracted via python-pptx)
- **Animation:** All via `useCurrentFrame()` + `interpolate()` + `Easing` (NO CSS animations)
- **Transitions:** `TransitionSeries` with `fade()` and `slide()`, 12-frame overlap
- **Shared:** Same `styles.ts` color palette and fonts as the HCM Saga video
