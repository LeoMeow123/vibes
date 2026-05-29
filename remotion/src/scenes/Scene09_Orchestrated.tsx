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

const GRID = Array.from({ length: 4 }, (_, i) => ({
  label: `cam_0${i + 1}`,
  x: 300 + i * 340,
  y: 320,
}));

export const Scene09_Orchestrated: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const snapFrame = fps * 1.5;
  const progress = interpolate(frame, [snapFrame, snapFrame + 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

  const pulsePhase = Math.sin(frame * 0.15) * 0.5 + 0.5;

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at 50% 50%, rgba(123,232,138,.08), transparent 50%), ${COLORS.bg}`,
      }}
    >
      {GRID.map((node, i) => {
        const chaosX = (1 - progress) * (Math.sin(frame * 0.5 + i * 2) * 60);
        const chaosY = (1 - progress) * (Math.cos(frame * 0.7 + i * 3) * 40);
        const chaosRotate = (1 - progress) * (Math.sin(frame * 0.3 + i) * 15);

        const targetX = node.x;
        const targetY = node.y;

        const borderColor =
          progress > 0.8
            ? `rgba(123,232,138,${0.5 + pulsePhase * 0.5})`
            : progress > 0.5
              ? "rgba(255,196,107,.5)"
              : "rgba(255,107,107,.5)";

        return (
          <div
            key={node.label}
            style={{
              position: "absolute",
              left: targetX + chaosX,
              top: targetY + chaosY,
              transform: `rotate(${chaosRotate}deg)`,
              width: 260,
              height: 200,
              borderRadius: 14,
              background: "#141826",
              border: `2px solid ${borderColor}`,
              boxShadow: progress > 0.8
                ? `0 0 20px rgba(123,232,138,${pulsePhase * 0.4})`
                : "0 10px 30px rgba(0,0,0,.4)",
              overflow: "hidden",
              zIndex: 2,
            }}
          >
            <div
              style={{
                height: 34,
                background: "#1d2335",
                display: "flex",
                alignItems: "center",
                padding: "0 14px",
                gap: 7,
              }}
            >
              <div style={{ width: 10, height: 10, borderRadius: "50%", background: progress > 0.8 ? "#28c840" : "#ff5f57" }} />
              <span style={{ fontFamily: FONTS.mono, fontSize: 13, color: "#aab4d0" }}>
                {node.label}
              </span>
            </div>
            <div style={{ padding: 16, textAlign: "center" }}>
              <div style={{ fontFamily: FONTS.mono, fontSize: 13, color: COLORS.muted }}>
                capture rate
              </div>
              <div
                style={{
                  fontFamily: FONTS.mono,
                  fontSize: 36,
                  fontWeight: 700,
                  color: progress > 0.8 ? COLORS.compute : COLORS.danger,
                  marginTop: 4,
                }}
              >
                50 fps
              </div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: 8,
                  marginTop: 14,
                  fontFamily: FONTS.mono,
                  fontSize: 14,
                  color: COLORS.ink,
                }}
              >
                <div
                  style={{
                    width: 10,
                    height: 10,
                    borderRadius: "50%",
                    background: progress > 0.8 ? COLORS.compute : COLORS.danger,
                  }}
                />
                {progress > 0.8 ? "SYNCED" : "DRIFTING"}
              </div>
            </div>
          </div>
        );
      })}

      {progress > 0.8 &&
        GRID.slice(0, -1).map((node, i) => {
          const next = GRID[i + 1];
          const lineOpacity = interpolate(
            frame,
            [snapFrame + 25 + i * 5, snapFrame + 35 + i * 5],
            [0, 0.6 + pulsePhase * 0.4],
            { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
          );
          return (
            <svg
              key={`line-${i}`}
              style={{ position: "absolute", inset: 0, width: "100%", height: "100%", zIndex: 1 }}
              viewBox="0 0 1920 1080"
            >
              <line
                x1={node.x + 260}
                y1={node.y + 100}
                x2={next.x}
                y2={next.y + 100}
                stroke={COLORS.compute}
                strokeWidth={2.5}
                opacity={lineOpacity}
                filter={`drop-shadow(0 0 6px ${COLORS.compute})`}
              />
            </svg>
          );
        })}

      <div
        style={{
          position: "absolute",
          top: 80,
          left: "50%",
          transform: "translateX(-50%)",
          textAlign: "center",
          zIndex: 5,
        }}
      >
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: 40,
            fontWeight: 700,
            color: progress > 0.8 ? COLORS.compute : COLORS.ink,
            opacity: interpolate(frame, [0, 20], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          {progress > 0.8 ? "✓ Orchestrated & Synchronized" : "Chaotic startup…"}
        </div>
      </div>

      <Sequence from={0} layout="none">
        <Caption text="Sync Demon: defeated." />
      </Sequence>
    </AbsoluteFill>
  );
};
