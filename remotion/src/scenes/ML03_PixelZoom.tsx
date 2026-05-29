import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  Easing,
} from "remotion";
import { FONTS, COLORS } from "../styles";
import { Caption } from "../components/Caption";

const GRID_VALUES = [
  [45, 52, 48, 180, 175, 168, 50, 47],
  [47, 50, 165, 172, 178, 170, 55, 48],
  [44, 160, 170, 185, 190, 175, 162, 46],
  [48, 155, 175, 195, 200, 185, 160, 50],
  [46, 158, 168, 188, 192, 180, 155, 47],
  [45, 50, 162, 170, 175, 165, 52, 49],
  [47, 48, 50, 165, 168, 52, 48, 46],
  [44, 46, 48, 50, 52, 49, 47, 45],
];

export const ML03_PixelZoom: React.FC = () => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const gridProgress = interpolate(frame, [20, 80], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  const numbersOpacity = interpolate(frame, [90, 120], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const gridOpacity = interpolate(frame, [20, 35], [0, 0.6], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const cellSize = 68;
  const gap = 3;
  const totalW = GRID_VALUES[0].length * (cellSize + gap) - gap;
  const totalH = GRID_VALUES.length * (cellSize + gap) - gap;

  const mouseOpacity = interpolate(frame, [60, 90], [1, 0.15], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const labelOpacity = interpolate(frame, [130, 150], [0, 1], {
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
        What does a video frame look like to a computer?
      </div>

      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -45%)",
        }}
      >
        {/* Mouse silhouette behind the grid */}
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: "translate(-50%, -50%)",
            fontSize: 280,
            opacity: mouseOpacity,
            filter: `blur(${interpolate(frame, [40, 80], [0, 8], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}px)`,
          }}
        >
          🐭
        </div>

        {/* Pixel grid overlay */}
        <div
          style={{
            position: "relative",
            width: totalW,
            height: totalH,
            opacity: gridOpacity,
          }}
        >
          {GRID_VALUES.map((row, ri) =>
            row.map((val, ci) => {
              const idx = ri * row.length + ci;
              const totalCells = GRID_VALUES.length * row.length;
              const cellProgress = interpolate(
                gridProgress,
                [idx / totalCells, Math.min(1, (idx + 8) / totalCells)],
                [0, 1],
                { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
              );
              const gray = val;
              return (
                <div
                  key={`${ri}-${ci}`}
                  style={{
                    position: "absolute",
                    left: ci * (cellSize + gap),
                    top: ri * (cellSize + gap),
                    width: cellSize,
                    height: cellSize,
                    background: `rgba(${gray},${gray},${gray},${cellProgress * 0.9})`,
                    borderRadius: 4,
                    border: `1px solid rgba(255,255,255,${cellProgress * 0.3})`,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontFamily: FONTS.mono,
                    fontSize: 16,
                    fontWeight: 700,
                    color: gray > 140 ? "rgba(0,0,0,0.8)" : `rgba(255,255,255,${numbersOpacity})`,
                  }}
                >
                  {numbersOpacity > 0.1 ? val : ""}
                </div>
              );
            })
          )}
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          bottom: 140,
          left: "50%",
          transform: "translateX(-50%)",
          fontFamily: FONTS.mono,
          fontSize: 28,
          color: COLORS.training,
          opacity: labelOpacity,
          textAlign: "center",
          background: "rgba(255,196,107,0.1)",
          padding: "10px 28px",
          borderRadius: 16,
          border: `1px solid ${COLORS.training}`,
        }}
      >
        Each pixel = one number (brightness 0–255)
      </div>

      <Caption text="Every frame is just a grid of pixel values" />
    </AbsoluteFill>
  );
};
