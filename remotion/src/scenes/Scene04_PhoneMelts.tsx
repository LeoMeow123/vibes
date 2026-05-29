import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
  Sequence,
} from "remotion";
import { FONTS, COLORS } from "../styles";
import { Caption } from "../components/Caption";

export const Scene04_PhoneMelts: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const phoneOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const heatProgress = interpolate(frame, [fps * 1, fps * 3], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const heatColor = `rgba(255, ${Math.floor(107 - heatProgress * 80)}, ${Math.floor(107 - heatProgress * 107)}, ${heatProgress * 0.8})`;

  const phoneShake = heatProgress > 0.3
    ? Math.sin(frame * 1.5) * heatProgress * 8
    : 0;

  const xOpacity = interpolate(frame, [fps * 3.5, fps * 4], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const xScale = interpolate(frame, [fps * 3.5, fps * 4], [3, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at 50% 60%, rgba(255,107,107,.08), transparent 50%), ${COLORS.bg}`,
      }}
    >
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "50%",
          transform: `translate(-50%, -50%) translateX(${phoneShake}px)`,
          opacity: phoneOpacity,
          zIndex: 2,
        }}
      >
        <div
          style={{
            width: 220,
            height: 380,
            borderRadius: 24,
            background: `linear-gradient(180deg, #2a3244, #1a2030)`,
            border: `2px solid ${heatProgress > 0.5 ? COLORS.danger : COLORS.line}`,
            boxShadow: `0 0 ${heatProgress * 50}px ${heatColor}, 0 20px 40px rgba(0,0,0,.5)`,
            position: "relative",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              position: "absolute",
              top: 16,
              left: "50%",
              transform: "translateX(-50%)",
              width: 60,
              height: 8,
              borderRadius: 4,
              background: "#3a4a6a",
            }}
          />
          <div
            style={{
              position: "absolute",
              top: 40,
              left: 12,
              right: 12,
              bottom: 50,
              borderRadius: 4,
              background: `rgba(255, ${Math.floor(200 - heatProgress * 150)}, ${Math.floor(200 - heatProgress * 200)}, 0.15)`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <div style={{ fontSize: 64 }}>📱</div>
          </div>
          <div
            style={{
              position: "absolute",
              inset: 0,
              background: `linear-gradient(transparent, ${heatColor})`,
              opacity: heatProgress,
            }}
          />
        </div>

        <div
          style={{
            position: "absolute",
            bottom: -40,
            left: -50,
            right: -50,
            height: 80,
            background: `linear-gradient(transparent, rgba(10,14,26,.9))`,
            borderRadius: "0 0 20px 20px",
          }}
        />
      </div>

      <div
        style={{
          position: "absolute",
          bottom: 260,
          left: "50%",
          transform: "translateX(-50%)",
          width: 240,
          height: 130,
          borderRadius: 8,
          border: `1px solid ${COLORS.line}`,
          background: "rgba(42,53,80,.3)",
          zIndex: 1,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: FONTS.mono,
          fontSize: 18,
          color: COLORS.muted,
        }}
      >
        🐭 cage
      </div>

      {[...Array(5)].map((_, i) => {
        const smokeY = interpolate(
          frame,
          [fps * 2.5 + i * 5, fps * 4 + i * 5],
          [0, -150 - i * 30],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
        );
        const smokeIndivOpacity = interpolate(
          frame,
          [fps * 2.5 + i * 5, fps * 3 + i * 5, fps * 4 + i * 5],
          [0, 0.5, 0],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
        );
        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: `calc(50% + ${(i - 2) * 25}px)`,
              top: `calc(50% - 130px)`,
              transform: `translateY(${smokeY}px)`,
              width: 40 + i * 10,
              height: 40 + i * 10,
              borderRadius: "50%",
              background: "rgba(180,180,200,.2)",
              filter: "blur(8px)",
              opacity: smokeIndivOpacity,
              zIndex: 4,
            }}
          />
        );
      })}

      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: `translate(-50%, -50%) scale(${xScale})`,
          fontFamily: FONTS.display,
          fontSize: 200,
          fontWeight: 700,
          color: COLORS.danger,
          opacity: xOpacity,
          textShadow: `0 0 60px ${COLORS.danger}`,
          zIndex: 5,
        }}
      >
        ✕
      </div>

      <Sequence from={0} layout="none">
        <Caption text="Consumer cameras: melt." />
      </Sequence>
    </AbsoluteFill>
  );
};
