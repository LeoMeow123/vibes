import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
} from "remotion";
import { FONTS, COLORS } from "../styles";
import { KenBurns } from "../components/KenBurns";

export const Scene01_Establishing: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = interpolate(frame, [fps * 3, fps * 4], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const titleScale = interpolate(frame, [fps * 3, fps * 4], [0.9, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.16, 1, 0.3, 1),
  });

  const subtitleOpacity = interpolate(frame, [fps * 4.5, fps * 5.5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <KenBurns
        src="images/05_salk/salk_courtyard_sunset.png"
        startScale={1.0}
        endScale={1.12}
        translateY={[0, -15]}
      />

      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(transparent 40%, rgba(10,14,26,.7) 80%, rgba(10,14,26,.95) 100%)",
          zIndex: 1,
        }}
      />

      <div
        style={{
          position: "absolute",
          bottom: 140,
          left: 0,
          right: 0,
          textAlign: "center",
          zIndex: 2,
        }}
      >
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: 80,
            fontWeight: 700,
            color: COLORS.ink,
            opacity: titleOpacity,
            transform: `scale(${titleScale})`,
            letterSpacing: 2,
            textShadow: "0 4px 30px rgba(0,0,0,.6)",
          }}
        >
          THE HOME-CAGE SAGA
        </div>
        <div
          style={{
            fontFamily: FONTS.mono,
            fontSize: 22,
            color: COLORS.muted,
            opacity: subtitleOpacity,
            letterSpacing: 4,
            marginTop: 16,
          }}
        >
          A LONG-TERM MONITORING ODYSSEY
        </div>
      </div>
    </AbsoluteFill>
  );
};
