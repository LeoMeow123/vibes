import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  Easing,
  Img,
  staticFile,
} from "remotion";
import { FONTS, COLORS } from "../styles";

export const ML12_EndCard: React.FC = () => {
  const frame = useCurrentFrame();

  const logoScale = interpolate(frame, [10, 35], [0.5, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.back(1.3)),
  });
  const logoOpacity = interpolate(frame, [10, 25], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const titleOpacity = interpolate(frame, [30, 50], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const titleY = interpolate(frame, [30, 50], [20, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const subtitleOpacity = interpolate(frame, [55, 75], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const glowPulse = Math.sin(frame * 0.05) * 0.3 + 0.7;

  const docsOpacity = interpolate(frame, [85, 105], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      {/* Radial glow */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "42%",
          transform: "translate(-50%, -50%)",
          width: 500,
          height: 500,
          borderRadius: "50%",
          background: `radial-gradient(circle, rgba(123,232,138,${0.08 * glowPulse}) 0%, transparent 70%)`,
        }}
      />

      {/* SLEAP logo */}
      <div
        style={{
          position: "absolute",
          top: "30%",
          left: "50%",
          transform: `translate(-50%, -50%) scale(${logoScale})`,
          opacity: logoOpacity,
        }}
      >
        <Img
          src={staticFile("images/ml_demo/sleap_logo.png")}
          style={{ width: 160, height: 160, borderRadius: 24 }}
        />
      </div>

      {/* Main message */}
      <div
        style={{
          position: "absolute",
          top: "52%",
          left: "50%",
          transform: `translate(-50%, 0) translateY(${titleY}px)`,
          fontFamily: FONTS.display,
          fontWeight: 700,
          fontSize: 56,
          color: COLORS.compute,
          opacity: titleOpacity,
          textAlign: "center",
          textShadow: `0 0 30px rgba(123,232,138,${glowPulse * 0.5})`,
        }}
      >
        Keep it consistent!
      </div>

      {/* Subtitle */}
      <div
        style={{
          position: "absolute",
          top: "64%",
          left: "50%",
          transform: "translate(-50%, 0)",
          fontFamily: FONTS.mono,
          fontSize: 26,
          color: COLORS.muted,
          opacity: subtitleOpacity,
          textAlign: "center",
          letterSpacing: 2,
        }}
      >
        Same camera &bull; Same angle &bull; Same light
      </div>

      {/* Docs link */}
      <div
        style={{
          position: "absolute",
          bottom: 80,
          left: "50%",
          transform: "translate(-50%, 0)",
          fontFamily: FONTS.mono,
          fontSize: 22,
          color: COLORS.acquisition,
          opacity: docsOpacity,
        }}
      >
        sleap.ai &bull; talmolab
      </div>
    </AbsoluteFill>
  );
};
