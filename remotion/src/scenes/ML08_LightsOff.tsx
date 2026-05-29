import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  Easing,
} from "remotion";
import { FONTS, COLORS } from "../styles";
import { Caption } from "../components/Caption";

const BRIGHT_VALUES = [180, 195, 172, 165, 188, 175, 190, 168, 182, 177, 185, 170];
const DARK_VALUES = [12, 8, 15, 5, 11, 7, 14, 3, 9, 6, 13, 4];

export const ML08_LightsOff: React.FC = () => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const brightness = interpolate(frame, [30, 80], [1, 0.05], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  const sliderX = interpolate(frame, [30, 80], [280, 20], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  const valuesTransition = interpolate(frame, [30, 80], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const garbageOpacity = interpolate(frame, [100, 120], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const shakeX = frame > 85 && frame < 105
    ? Math.sin(frame * 3) * interpolate(frame, [85, 95, 105], [0, 6, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
    : 0;

  const explainOpacity = interpolate(frame, [130, 150], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: COLORS.bg, transform: `translateX(${shakeX}px)` }}>
      <div
        style={{
          position: "absolute",
          top: 50,
          left: "50%",
          transform: "translateX(-50%)",
          fontFamily: FONTS.display,
          fontWeight: 700,
          fontSize: 44,
          color: COLORS.danger,
          opacity: titleOpacity,
        }}
      >
        ⚠️ Lights turned off
      </div>

      {/* Brightness dimmer visualization */}
      <div
        style={{
          position: "absolute",
          left: 200,
          top: "35%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 15,
        }}
      >
        <div style={{ fontFamily: FONTS.mono, fontSize: 20, color: COLORS.muted }}>
          Brightness
        </div>
        <div
          style={{
            width: 300,
            height: 24,
            background: COLORS.line,
            borderRadius: 12,
            position: "relative",
          }}
        >
          <div
            style={{
              position: "absolute",
              left: 0,
              top: 0,
              width: sliderX,
              height: "100%",
              background: `linear-gradient(90deg, ${COLORS.danger}, ${COLORS.training})`,
              borderRadius: 12,
            }}
          />
          <div
            style={{
              position: "absolute",
              left: sliderX - 10,
              top: -4,
              width: 20,
              height: 32,
              background: "white",
              borderRadius: 10,
              boxShadow: "0 2px 8px rgba(0,0,0,0.3)",
            }}
          />
        </div>
        <div style={{ fontFamily: FONTS.mono, fontSize: 28, fontWeight: 700, color: brightness > 0.5 ? COLORS.compute : COLORS.danger }}>
          {Math.round(brightness * 100)}%
        </div>
      </div>

      {/* "Camera view" that dims */}
      <div
        style={{
          position: "absolute",
          left: 200,
          top: "58%",
          width: 300,
          height: 200,
          background: `rgba(${Math.round(180 * brightness)}, ${Math.round(195 * brightness)}, ${Math.round(172 * brightness)}, 1)`,
          borderRadius: 12,
          border: `2px solid ${COLORS.line}`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: brightness > 0.3 ? 80 : 40,
          transition: "none",
        }}
      >
        {brightness > 0.3 ? "🐭" : "⬛"}
      </div>

      {/* Pixel values panel */}
      <div
        style={{
          position: "absolute",
          right: 200,
          top: "30%",
          display: "flex",
          flexDirection: "column",
          gap: 8,
        }}
      >
        <div style={{ fontFamily: FONTS.mono, fontSize: 20, color: COLORS.muted, marginBottom: 10 }}>
          Pixel values:
        </div>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, 80px)",
            gap: 6,
          }}
        >
          {BRIGHT_VALUES.map((bv, i) => {
            const dv = DARK_VALUES[i];
            const currentVal = Math.round(bv + (dv - bv) * valuesTransition);
            const gray = currentVal;
            return (
              <div
                key={i}
                style={{
                  width: 80,
                  height: 50,
                  background: `rgb(${gray},${gray},${gray})`,
                  borderRadius: 6,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontFamily: FONTS.mono,
                  fontSize: 18,
                  fontWeight: 700,
                  color: gray > 100 ? "#222" : "#aaa",
                  border: `1px solid rgba(255,255,255,0.1)`,
                }}
              >
                {currentVal}
              </div>
            );
          })}
        </div>

        {/* Arrow showing collapse */}
        <div
          style={{
            fontFamily: FONTS.mono,
            fontSize: 22,
            color: COLORS.danger,
            marginTop: 15,
            opacity: garbageOpacity,
            textAlign: "center",
          }}
        >
          All values → ~0
        </div>
      </div>

      {/* Scattered keypoints visualization */}
      <div
        style={{
          position: "absolute",
          right: 250,
          top: "68%",
          opacity: garbageOpacity,
        }}
      >
        <svg width={280} height={180}>
          {Array.from({ length: 10 }).map((_, i) => {
            const angle = (i / 10) * Math.PI * 2 + frame * 0.02;
            const r = 40 + Math.sin(i * 1.7) * 30;
            const cx = 140 + Math.cos(angle) * r;
            const cy = 90 + Math.sin(angle) * r;
            return (
              <circle
                key={i}
                cx={cx}
                cy={cy}
                r={6}
                fill={COLORS.danger}
                opacity={0.7}
              />
            );
          })}
          <text
            x={140}
            y={170}
            fill={COLORS.danger}
            fontFamily={FONTS.mono}
            fontSize={16}
            textAnchor="middle"
          >
            Keypoints: garbage
          </text>
        </svg>
      </div>

      {/* Explanation */}
      <div
        style={{
          position: "absolute",
          bottom: 140,
          left: "50%",
          transform: "translateX(-50%)",
          fontFamily: FONTS.mono,
          fontSize: 24,
          color: COLORS.danger,
          opacity: explainOpacity,
          textAlign: "center",
          background: "rgba(255,107,107,0.1)",
          padding: "12px 30px",
          borderRadius: 16,
          border: `1px solid ${COLORS.danger}`,
          maxWidth: 700,
        }}
      >
        "I learned patterns in bright pixels — dark pixels are a foreign language"
      </div>

      <Caption text="Lights off → pixel values collapse → model outputs garbage" />
    </AbsoluteFill>
  );
};
