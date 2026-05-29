import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  Easing,
} from "remotion";
import { FONTS, COLORS } from "../styles";
import { Caption } from "../components/Caption";

const KEYPOINTS = [
  { name: "nose", x: 960, y: 300, color: "#ff6b6b" },
  { name: "L ear", x: 890, y: 260, color: "#6db3ff" },
  { name: "R ear", x: 1030, y: 260, color: "#6db3ff" },
  { name: "spine", x: 960, y: 440, color: "#7be88a" },
  { name: "L paw", x: 870, y: 520, color: "#ffc46b" },
  { name: "R paw", x: 1050, y: 520, color: "#ffc46b" },
  { name: "hip", x: 960, y: 580, color: "#7be88a" },
  { name: "L hind", x: 880, y: 680, color: "#ff8a3c" },
  { name: "R hind", x: 1040, y: 680, color: "#ff8a3c" },
  { name: "tail", x: 960, y: 780, color: "#c084fc" },
];

const BONES: [number, number][] = [
  [0, 1], [0, 2], [0, 3], [3, 4], [3, 5], [3, 6], [6, 7], [6, 8], [6, 9],
];

export const ML04_Labeling: React.FC = () => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const mouseOpacity = interpolate(frame, [10, 25], [0, 0.25], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const bonesProgress = interpolate(frame, [120, 160], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const flashcardOpacity = interpolate(frame, [170, 190], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      <div
        style={{
          position: "absolute",
          top: 60,
          left: "50%",
          transform: "translateX(-50%)",
          fontFamily: FONTS.display,
          fontWeight: 700,
          fontSize: 44,
          color: COLORS.ink,
          opacity: titleOpacity,
        }}
      >
        Teaching the model: Label keypoints
      </div>

      {/* Mouse silhouette */}
      <div
        style={{
          position: "absolute",
          left: 960,
          top: 500,
          transform: "translate(-50%, -50%)",
          fontSize: 360,
          opacity: mouseOpacity,
        }}
      >
        🐭
      </div>

      {/* SVG for bones and keypoints */}
      <svg
        width={1920}
        height={1080}
        style={{ position: "absolute", left: 0, top: 0 }}
      >
        {/* Bones */}
        {BONES.map(([a, b], idx) => {
          const kpA = KEYPOINTS[a];
          const kpB = KEYPOINTS[b];
          return (
            <line
              key={`bone-${idx}`}
              x1={kpA.x}
              y1={kpA.y}
              x2={kpA.x + (kpB.x - kpA.x) * bonesProgress}
              y2={kpA.y + (kpB.y - kpA.y) * bonesProgress}
              stroke="rgba(255,255,255,0.4)"
              strokeWidth={3}
              opacity={bonesProgress}
            />
          );
        })}

        {/* Keypoints */}
        {KEYPOINTS.map((kp, idx) => {
          const delay = 25 + idx * 10;
          const scale = interpolate(frame, [delay, delay + 12], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.back(2)),
          });
          const labelOp = interpolate(frame, [delay + 5, delay + 15], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          return (
            <g key={idx}>
              <circle
                cx={kp.x}
                cy={kp.y}
                r={10 * scale}
                fill={kp.color}
                stroke="white"
                strokeWidth={2}
              />
              <text
                x={kp.x + 18}
                y={kp.y + 5}
                fill={COLORS.ink}
                fontFamily={FONTS.mono}
                fontSize={16}
                opacity={labelOp}
              >
                {kp.name}
              </text>
            </g>
          );
        })}
      </svg>

      {/* Flashcard analogy */}
      <div
        style={{
          position: "absolute",
          bottom: 140,
          left: "50%",
          transform: "translateX(-50%)",
          fontFamily: FONTS.mono,
          fontSize: 26,
          color: COLORS.compute,
          opacity: flashcardOpacity,
          background: "rgba(123,232,138,0.1)",
          padding: "12px 30px",
          borderRadius: 16,
          border: `1px solid ${COLORS.compute}`,
        }}
      >
        Like flashcards — you show the model where each body part is
      </div>

      <Caption text="Label a few dozen frames → model learns the pattern" />
    </AbsoluteFill>
  );
};
