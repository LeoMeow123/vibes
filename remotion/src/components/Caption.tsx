import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, Easing } from "remotion";
import { FONTS, COLORS } from "../styles";

export const Caption: React.FC<{ text: string }> = ({ text }) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const fadeIn = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const fadeOut = interpolate(
    frame,
    [durationInFrames - 12, durationInFrames],
    [1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const opacity = Math.min(fadeIn, fadeOut);

  return (
    <div
      style={{
        position: "absolute",
        bottom: 60,
        left: "50%",
        transform: "translateX(-50%)",
        fontFamily: FONTS.mono,
        fontSize: 28,
        color: COLORS.ink,
        background: COLORS.captionBg,
        border: `1px solid ${COLORS.line}`,
        padding: "14px 32px",
        borderRadius: 40,
        letterSpacing: 0.5,
        opacity,
        whiteSpace: "nowrap",
        zIndex: 10,
      }}
    >
      {text}
    </div>
  );
};
