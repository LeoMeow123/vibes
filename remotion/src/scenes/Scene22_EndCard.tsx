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

export const Scene22_EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const titleOpacity = interpolate(frame, [fps * 2, fps * 3], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const subtitleOpacity = interpolate(frame, [fps * 3.5, fps * 4.5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <KenBurns
        src="images/07_monitoring/dashboard_filmstrip.png"
        startScale={1.15}
        endScale={1.0}
        translateY={[10, 0]}
      />

      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(transparent 30%, rgba(10,14,26,.7) 60%, rgba(10,14,26,.95) 100%)",
          zIndex: 1,
        }}
      />

      <div
        style={{
          position: "absolute",
          bottom: 120,
          left: 0,
          right: 0,
          textAlign: "center",
          zIndex: 2,
        }}
      >
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: 72,
            fontWeight: 700,
            color: COLORS.ink,
            opacity: titleOpacity,
            letterSpacing: 2,
            textShadow: "0 4px 30px rgba(0,0,0,.6)",
          }}
        >
          THE HOME-CAGE SAGA
        </div>
        <div
          style={{
            fontFamily: FONTS.mono,
            fontSize: 26,
            color: COLORS.training,
            opacity: subtitleOpacity,
            letterSpacing: 4,
            marginTop: 20,
          }}
        >
          — to be continued.
        </div>
      </div>
    </AbsoluteFill>
  );
};
