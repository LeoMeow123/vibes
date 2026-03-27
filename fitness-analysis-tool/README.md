# Fitness Form Analyzer

Browser-based AI-powered exercise form analysis tool using MediaPipe pose estimation with personalized biomechanical calculations.

**Solves**: Generic fitness advice doesn't account for individual body proportions. This tool analyzes exercise form using your height, weight, arm span, and leg length to calculate personalized joint torques, detect asymmetry, and assess injury risk.

## Live Demo

[Launch Fitness Form Analyzer](https://leomeow123.github.io/vibes/fitness-analysis-tool/)

Click **Try Demo** to see the full analysis with an animated skeleton — no video upload needed.

## How It Works

### Input
- **Personal measurements**: height, weight, arm span, leg length, gender
- **Exercise setup**: exercise type (squat, deadlift, overhead press, bench press), weight used
- **Video**: upload an exercise recording (or use the built-in demo)

### Analysis Pipeline
1. **Pose estimation** — MediaPipe Pose Landmarker runs in-browser, extracting 33 body landmarks per frame
2. **Joint angles** — knee, hip, elbow, and torso lean calculated per frame
3. **Rep detection** — automatically finds repetitions via hip position peaks
4. **Biomechanical analysis** — personalized torque calculations using De Leva (1996) anthropometric segment data
5. **Asymmetry detection** — compares left vs right joint angles across reps
6. **Form assessment** — exercise-specific checks (depth, knee valgus, forward lean, consistency)

### Output
- **Overall score** (0–100) with rating (Excellent / Good / Fair / Poor)
- **Key metrics**: depth, symmetry, stability, knee tracking
- **Detailed findings** with severity levels, injury risk explanations, and specific correction suggestions
- **Joint torque analysis** — knee torque, hip torque, lumbar shear force with personalized safe thresholds
- **Left-right asymmetry** breakdown per joint with visual bars
- **Injury risk assessment** — knee (ACL/MCL), lower back, hip, ankle
- **Numbered recommendations** — actionable exercises and form cues
- **Skeleton overlay** — video playback with real-time skeleton and angle HUD

## Demo Mode

Click **Try Demo** to see:
- Animated skeleton performing 5 squat reps with realistic kinematics
- Built-in asymmetry (left knee valgus, slight left-side weakness)
- Barbell with weight plates
- Real-time angle arcs at knee and hip joints
- Timeline bar with looping playback
- Full analysis results personalized to your entered body measurements

## Biomechanics

### Torque Calculations
```
τ_knee = (upper_body_mass + barbell_mass) × g × horizontal_lever_arm
τ_hip  = (trunk_mass + barbell_mass) × g × horizontal_lever_arm
F_lumbar = (trunk_mass + barbell_mass) × g × sin(lean_angle)
```

Body segment masses from De Leva (1996) anthropometric data, differentiated by gender.

### Asymmetry Detection
```
asymmetry = |left_angle - right_angle|
```
- < 3°: symmetric (good)
- 3–8°: mild asymmetry
- \> 8°: significant asymmetry

### Form Checks (Squat)
| Check | Good | Warning | Danger |
|-------|------|---------|--------|
| Depth (knee angle) | ≤ 90° | 90–110° | > 130° |
| Forward lean | < 25° | 25–45° | > 45° |
| Knee valgus | Score > 75% | 50–75% | < 50% |
| Depth consistency | σ < 8° | — | σ > 8° |

## Technical Details

- **Pose estimation**: [MediaPipe Tasks Vision](https://developers.google.com/mediapipe/solutions/vision/pose_landmarker) (loaded from CDN)
- **Model**: `pose_landmarker_full` (float16) — balanced accuracy/speed
- **Processing**: samples video at 10fps, processes each frame sequentially
- **Rendering**: HTML5 Canvas for skeleton overlay and demo animation
- **No server required** — runs entirely in browser

## Limitations

- Requires internet connection (MediaPipe model loaded from CDN)
- Best with side-view or front-view camera angle
- Single-person analysis only
- Squat analysis is most detailed; other exercises use simplified checks
- Torque calculations are simplified biomechanical estimates, not clinical-grade

## Local Development

```bash
python3 -m http.server 8000
# Open http://localhost:8000/fitness-analysis-tool/
```
