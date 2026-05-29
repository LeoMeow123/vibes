import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
  Img,
  staticFile,
  Sequence,
} from "remotion";
import { FONTS, COLORS } from "../styles";
import { Caption } from "../components/Caption";

const TEAM_ICONS = Array.from({ length: 15 }, (_, i) => ({
  x: 180 + (i % 5) * 120,
  y: 240 + Math.floor(i / 5) * 130,
  delay: i * 4 + 10,
  emoji: ["👩‍💻", "👨‍💻", "🧑‍💻", "👷", "🔧"][i % 5],
}));

export const Scene19_TeamVsMe: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const cutFrame = Math.floor(durationInFrames * 0.45);
  const showGithub = frame >= cutFrame;

  // Phase 1: split screen — big team vs lone researcher
  const splitOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const vsScale = interpolate(frame, [fps * 1, fps * 1.5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.34, 1.56, 0.64, 1),
  });

  // Phase 2: github reveal
  const githubOpacity = interpolate(
    frame,
    [cutFrame, cutFrame + 15],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const wipeProgress = interpolate(
    frame,
    [cutFrame + 20, cutFrame + 60],
    [0, 100],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.bezier(0.16, 1, 0.3, 1),
    },
  );

  const stampOpacity = interpolate(
    frame,
    [cutFrame + 50, cutFrame + 65],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const stampScale = interpolate(
    frame,
    [cutFrame + 50, cutFrame + 65],
    [1.5, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.cubic),
    },
  );

  if (!showGithub) {
    return (
      <AbsoluteFill
        style={{
          background: COLORS.bg,
        }}
      >
        {/* Divider line */}
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: 180,
            bottom: 120,
            width: 2,
            background: COLORS.line,
            opacity: splitOpacity,
            zIndex: 3,
          }}
        />

        {/* Left side: Big team */}
        <div
          style={{
            position: "absolute",
            top: 60,
            left: 280,
            fontFamily: FONTS.display,
            fontSize: 28,
            fontWeight: 700,
            color: COLORS.muted,
            opacity: splitOpacity,
          }}
        >
          THEM: A TEAM
        </div>
        {TEAM_ICONS.map((icon, i) => {
          const localFrame = frame - icon.delay;
          const opacity = interpolate(localFrame, [0, 12], [0, 0.85], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const popScale = interpolate(localFrame, [0, 10], [0.5, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.34, 1.56, 0.64, 1),
          });
          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left: icon.x,
                top: icon.y,
                fontSize: 50,
                opacity: localFrame < 0 ? 0 : opacity,
                transform: `scale(${localFrame < 0 ? 0.5 : popScale})`,
                zIndex: 2,
              }}
            >
              {icon.emoji}
            </div>
          );
        })}

        {/* Right side: lone researcher */}
        <div
          style={{
            position: "absolute",
            top: 60,
            right: 280,
            fontFamily: FONTS.display,
            fontSize: 28,
            fontWeight: 700,
            color: COLORS.training,
            opacity: splitOpacity,
          }}
        >
          ME: JUST ONE
        </div>
        <div
          style={{
            position: "absolute",
            right: 300,
            top: 380,
            fontSize: 120,
            opacity: interpolate(frame, [fps * 0.5, fps * 1], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            filter: "drop-shadow(0 4px 20px rgba(255,196,107,.4))",
            zIndex: 2,
          }}
        >
          🧑‍💻
        </div>
        {/* Glowing aura around lone researcher */}
        <div
          style={{
            position: "absolute",
            right: 250,
            top: 330,
            width: 200,
            height: 200,
            borderRadius: "50%",
            background: `radial-gradient(circle, rgba(255,196,107,.2), transparent 70%)`,
            opacity: 0.6 + Math.sin(frame * 0.1) * 0.3,
            zIndex: 1,
          }}
        />

        {/* VS badge */}
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: `translate(-50%, -50%) scale(${vsScale})`,
            fontFamily: FONTS.display,
            fontSize: 56,
            fontWeight: 700,
            color: COLORS.danger,
            textShadow: `0 0 30px ${COLORS.danger}`,
            zIndex: 5,
            opacity: vsScale > 0.1 ? 1 : 0,
          }}
        >
          VS
        </div>

        <Sequence from={0} layout="none">
          <Caption text="Them: a team. Me: 41 commits this month." />
        </Sequence>
      </AbsoluteFill>
    );
  }

  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          opacity: githubOpacity,
        }}
      >
        <div
          style={{
            position: "relative",
            overflow: "hidden",
            borderRadius: 20,
            border: `2px solid ${COLORS.line}`,
          }}
        >
          <Img
            src={staticFile("images/08_personal/github_41_commits.png")}
            style={{
              width: 1200,
              objectFit: "contain",
            }}
          />
          <div
            style={{
              position: "absolute",
              inset: 0,
              background: `linear-gradient(90deg, rgba(123,232,138,.15) 0%, transparent ${wipeProgress}%)`,
              pointerEvents: "none",
            }}
          />
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          top: 80,
          right: 120,
          fontFamily: FONTS.display,
          fontSize: 64,
          fontWeight: 700,
          color: COLORS.compute,
          opacity: stampOpacity,
          transform: `scale(${stampScale})`,
          textShadow: `0 0 30px ${COLORS.compute}`,
          zIndex: 5,
        }}
      >
        41 commits
      </div>

      <Sequence from={0} layout="none">
        <Caption text="Them: a team. Me: 41 commits this month." />
      </Sequence>
    </AbsoluteFill>
  );
};
