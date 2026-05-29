import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  Easing,
} from "remotion";
import { FONTS, COLORS } from "../styles";
import { Caption } from "../components/Caption";

const PIXEL_GRID = [
  [142, 156, 138, 145, 161],
  [147, 139, 155, 148, 137],
  [134, 162, 141, 153, 146],
  [159, 144, 136, 158, 140],
];

export const ML02_HumanVsComputer: React.FC = () => {
  const frame = useCurrentFrame();

  const dividerX = interpolate(frame, [0, 20], [960, 960], {
    extrapolateRight: "clamp",
  });
  const dividerOpacity = interpolate(frame, [5, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const leftOpacity = interpolate(frame, [20, 40], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const rightOpacity = interpolate(frame, [50, 70], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const mouseY = interpolate(frame, [30, 50], [20, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const bubbleOpacity = interpolate(frame, [55, 65], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const gridBubbleOpacity = interpolate(frame, [85, 95], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const vsOpacity = interpolate(frame, [100, 115], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const vsScale = interpolate(frame, [100, 115], [2, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.back(1.5)),
  });

  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      {/* Divider */}
      <div
        style={{
          position: "absolute",
          left: dividerX,
          top: 100,
          bottom: 140,
          width: 2,
          background: COLORS.line,
          opacity: dividerOpacity,
        }}
      />

      {/* Left: Human */}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: 960,
          height: 1080,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          opacity: leftOpacity,
        }}
      >
        <div style={{ fontSize: 48, fontFamily: FONTS.display, fontWeight: 700, color: COLORS.muted, marginBottom: 40 }}>
          You see...
        </div>
        <div style={{ fontSize: 120, transform: `translateY(${mouseY}px)` }}>
          🐭
        </div>
        <div
          style={{
            marginTop: 30,
            fontSize: 36,
            fontFamily: FONTS.display,
            fontWeight: 700,
            color: COLORS.ink,
            opacity: bubbleOpacity,
            background: "rgba(107,179,255,0.15)",
            padding: "12px 30px",
            borderRadius: 20,
            border: `1px solid ${COLORS.acquisition}`,
          }}
        >
          "A mouse running!"
        </div>
      </div>

      {/* Right: Computer */}
      <div
        style={{
          position: "absolute",
          right: 0,
          top: 0,
          width: 960,
          height: 1080,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          opacity: rightOpacity,
        }}
      >
        <div style={{ fontSize: 48, fontFamily: FONTS.display, fontWeight: 700, color: COLORS.muted, marginBottom: 40 }}>
          Computer sees...
        </div>

        {/* Pixel grid */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: 3,
            background: "rgba(255,255,255,0.05)",
            padding: 12,
            borderRadius: 12,
          }}
        >
          {PIXEL_GRID.map((row, ri) => (
            <div key={ri} style={{ display: "flex", gap: 3 }}>
              {row.map((val, ci) => {
                const cellDelay = 60 + (ri * 5 + ci) * 3;
                const cellOpacity = interpolate(frame, [cellDelay, cellDelay + 8], [0, 1], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                });
                const gray = val;
                return (
                  <div
                    key={ci}
                    style={{
                      width: 72,
                      height: 56,
                      background: `rgb(${gray},${gray},${gray})`,
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                      fontFamily: FONTS.mono,
                      fontSize: 18,
                      color: gray > 145 ? "#222" : "#ddd",
                      borderRadius: 4,
                      opacity: cellOpacity,
                    }}
                  >
                    {val}
                  </div>
                );
              })}
            </div>
          ))}
        </div>

        <div
          style={{
            marginTop: 30,
            fontSize: 32,
            fontFamily: FONTS.mono,
            color: COLORS.danger,
            opacity: gridBubbleOpacity,
            background: "rgba(255,107,107,0.12)",
            padding: "12px 30px",
            borderRadius: 20,
            border: `1px solid ${COLORS.danger}`,
          }}
        >
          "Just numbers."
        </div>
      </div>

      {/* VS badge */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          transform: `translate(-50%, -50%) scale(${vsScale})`,
          opacity: vsOpacity,
          fontFamily: FONTS.display,
          fontWeight: 700,
          fontSize: 42,
          color: COLORS.training,
          background: COLORS.bg,
          border: `3px solid ${COLORS.training}`,
          borderRadius: 50,
          width: 80,
          height: 80,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        VS
      </div>

      <Caption text="Computers don't see mice — they see numbers" />
    </AbsoluteFill>
  );
};
