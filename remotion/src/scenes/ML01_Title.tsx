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

export const ML01_Title: React.FC = () => {
  const frame = useCurrentFrame();

  const logoScale = interpolate(frame, [10, 40], [0.3, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.back(1.4)),
  });
  const logoOpacity = interpolate(frame, [10, 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const titleY = interpolate(frame, [35, 65], [40, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const titleOpacity = interpolate(frame, [35, 55], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const subOpacity = interpolate(frame, [70, 90], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: `translate(-50%, -60%) scale(${logoScale})`,
          opacity: logoOpacity,
        }}
      >
        <Img
          src={staticFile("images/ml_demo/sleap_logo.png")}
          style={{ width: 180, height: 180, borderRadius: 28 }}
        />
      </div>

      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: `translate(-50%, 60px) translateY(${titleY}px)`,
          opacity: titleOpacity,
          fontFamily: FONTS.display,
          fontSize: 52,
          fontWeight: 700,
          color: COLORS.ink,
          textAlign: "center",
          whiteSpace: "nowrap",
        }}
      >
        ML for Wet Lab
      </div>

      <div
        style={{
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, 130px)",
          opacity: subOpacity,
          fontFamily: FONTS.mono,
          fontSize: 26,
          color: COLORS.muted,
          textAlign: "center",
          whiteSpace: "nowrap",
        }}
      >
        Why camera consistency matters for pose tracking
      </div>
    </AbsoluteFill>
  );
};
