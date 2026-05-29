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

const BUGS = Array.from({ length: 30 }, (_, i) => ({
  x: 100 + (i % 10) * 180 + ((i * 47) % 60),
  y: 150 + Math.floor(i / 10) * 280 + ((i * 31) % 80),
  delay: i * 4 + 10,
  size: 22 + (i % 5) * 6,
  emoji: ["🐛", "🪲", "🐜", "🦗"][i % 4],
  speed: 0.03 + (i % 7) * 0.01,
  amplitude: 10 + (i % 5) * 5,
}));

const WINDOWS = [
  { x: 200, y: 200, w: 400, h: 280, label: "recording.exe" },
  { x: 700, y: 160, w: 450, h: 300, label: "transfer_daemon" },
  { x: 1200, y: 220, w: 380, h: 260, label: "inference_server" },
  { x: 350, y: 550, w: 420, h: 260, label: "curation_pipeline" },
  { x: 900, y: 520, w: 440, h: 280, label: "dashboard_api" },
];

export const Scene18_ArmyOfBugs: React.FC = () => {
  const frame = useCurrentFrame();
  useVideoConfig();

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at 50% 50%, rgba(255,107,107,.06), transparent 50%), ${COLORS.bg}`,
      }}
    >
      {WINDOWS.map((win, i) => {
        const opacity = interpolate(frame, [i * 8, i * 8 + 15], [0, 0.8], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

        const bugCount = BUGS.filter(
          (b) =>
            b.x > win.x - 50 &&
            b.x < win.x + win.w + 50 &&
            b.y > win.y - 50 &&
            b.y < win.y + win.h + 50 &&
            frame > b.delay + 30,
        ).length;

        const infestLevel = Math.min(bugCount / 4, 1);

        return (
          <div
            key={win.label}
            style={{
              position: "absolute",
              left: win.x,
              top: win.y,
              width: win.w,
              height: win.h,
              borderRadius: 12,
              background: "rgba(20,24,38,.8)",
              border: `1.5px solid ${infestLevel > 0.5 ? `rgba(255,107,107,${infestLevel})` : COLORS.line}`,
              boxShadow: infestLevel > 0.5
                ? `0 0 ${infestLevel * 20}px rgba(255,107,107,.2)`
                : "0 8px 24px rgba(0,0,0,.3)",
              opacity,
              zIndex: 1,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                height: 32,
                background: "#1d2335",
                display: "flex",
                alignItems: "center",
                padding: "0 12px",
                gap: 6,
              }}
            >
              <div style={{ width: 10, height: 10, borderRadius: "50%", background: infestLevel > 0.5 ? COLORS.danger : "#28c840" }} />
              <div style={{ width: 10, height: 10, borderRadius: "50%", background: "#febc2e" }} />
              <span style={{ fontFamily: FONTS.mono, fontSize: 12, color: "#8c97b8", marginLeft: 6 }}>
                {win.label}
              </span>
            </div>
            <div style={{ padding: "12px 14px" }}>
              {[0, 1, 2, 3].map((line) => (
                <div
                  key={line}
                  style={{
                    height: 10,
                    width: `${60 + line * 10}%`,
                    background: "rgba(255,255,255,.04)",
                    borderRadius: 5,
                    marginBottom: 8,
                  }}
                />
              ))}
            </div>
          </div>
        );
      })}

      {BUGS.map((bug, i) => {
        const localFrame = frame - bug.delay;
        const opacity = interpolate(localFrame, [0, 15], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.out(Easing.cubic),
        });

        const wobbleX = Math.sin(frame * bug.speed * 3 + i) * bug.amplitude;
        const wobbleY = Math.cos(frame * bug.speed * 2 + i * 1.7) * (bug.amplitude * 0.7);

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: bug.x + wobbleX,
              top: bug.y + wobbleY,
              fontSize: bug.size,
              opacity: localFrame < 0 ? 0 : opacity,
              zIndex: 3,
              transform: `rotate(${Math.sin(frame * 0.05 + i) * 30}deg)`,
            }}
          >
            {bug.emoji}
          </div>
        );
      })}

      <div
        style={{
          position: "absolute",
          top: 40,
          left: "50%",
          transform: "translateX(-50%)",
          fontFamily: FONTS.display,
          fontSize: 36,
          fontWeight: 700,
          color: COLORS.ink,
          zIndex: 5,
          opacity: interpolate(frame, [0, 20], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        Every system runs on bugs.
      </div>

      <Sequence from={0} layout="none">
        <Caption text="Every system runs on bugs." />
      </Sequence>
    </AbsoluteFill>
  );
};
