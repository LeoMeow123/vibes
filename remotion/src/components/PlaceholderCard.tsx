import React from "react";
import { useCurrentFrame, interpolate, Easing } from "remotion";
import { FONTS, COLORS } from "../styles";

export const PlaceholderCard: React.FC<{
  sceneNumber: number;
  title: string;
}> = ({ sceneNumber, title }) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        background: `radial-gradient(ellipse at 50% 40%, ${COLORS.line}, ${COLORS.bg})`,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        opacity,
      }}
    >
      <div
        style={{
          fontFamily: FONTS.mono,
          fontSize: 18,
          color: COLORS.muted,
          letterSpacing: 3,
          marginBottom: 16,
        }}
      >
        AI-GENERATED CLIP
      </div>
      <div
        style={{
          fontFamily: FONTS.display,
          fontSize: 48,
          fontWeight: 700,
          color: COLORS.ink,
          marginBottom: 12,
        }}
      >
        Scene {sceneNumber}
      </div>
      <div
        style={{
          fontFamily: FONTS.mono,
          fontSize: 22,
          color: COLORS.muted,
          maxWidth: 700,
          textAlign: "center",
          lineHeight: 1.5,
        }}
      >
        {title}
      </div>
      <div
        style={{
          marginTop: 40,
          width: 120,
          height: 120,
          borderRadius: "50%",
          border: `2px dashed ${COLORS.muted}`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontFamily: FONTS.mono,
          fontSize: 14,
          color: COLORS.muted,
        }}
      >
        DROP MP4
      </div>
    </div>
  );
};
