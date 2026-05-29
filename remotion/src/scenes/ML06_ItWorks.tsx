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
import { Caption } from "../components/Caption";

export const ML06_ItWorks: React.FC = () => {
  const frame = useCurrentFrame();

  const imgScale = interpolate(frame, [0, 30], [1.1, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const imgOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const greenGlow = interpolate(frame, [30, 50], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const glowPulse = Math.sin(frame * 0.08) * 0.3 + 0.7;

  const barProgress = interpolate(frame, [40, 80], [0, 0.95], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const checkScale = interpolate(frame, [85, 100], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.back(2)),
  });

  const pipelineOpacity = interpolate(frame, [100, 120], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      {/* Good tracking image */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "45%",
          transform: `translate(-50%, -50%) scale(${imgScale})`,
          opacity: imgOpacity,
          borderRadius: 16,
          overflow: "hidden",
          border: `3px solid ${COLORS.compute}`,
          boxShadow: `0 0 ${30 * greenGlow * glowPulse}px ${COLORS.compute}`,
        }}
      >
        <Img
          src={staticFile("images/ml_demo/slide10_Picture_4.png")}
          style={{ width: 400, height: "auto" }}
        />
      </div>

      {/* Confidence bar */}
      <div
        style={{
          position: "absolute",
          left: "50%",
          top: "72%",
          transform: "translateX(-50%)",
          width: 400,
        }}
      >
        <div
          style={{
            fontFamily: FONTS.mono,
            fontSize: 18,
            color: COLORS.muted,
            marginBottom: 8,
          }}
        >
          Tracking confidence
        </div>
        <div
          style={{
            width: "100%",
            height: 28,
            background: COLORS.line,
            borderRadius: 14,
            overflow: "hidden",
          }}
        >
          <div
            style={{
              width: `${barProgress * 100}%`,
              height: "100%",
              background: `linear-gradient(90deg, ${COLORS.compute}, #4ade80)`,
              borderRadius: 14,
              display: "flex",
              alignItems: "center",
              justifyContent: "flex-end",
              paddingRight: 12,
              fontFamily: FONTS.mono,
              fontSize: 14,
              fontWeight: 700,
              color: "#0a0e1a",
            }}
          >
            {barProgress > 0.3 ? `${Math.round(barProgress * 100)}%` : ""}
          </div>
        </div>
      </div>

      {/* Checkmark */}
      <div
        style={{
          position: "absolute",
          right: 280,
          top: "40%",
          transform: `scale(${checkScale})`,
          fontSize: 80,
        }}
      >
        ✅
      </div>

      {/* SLEAP pipeline image */}
      <div
        style={{
          position: "absolute",
          bottom: 140,
          left: "50%",
          transform: "translateX(-50%)",
          opacity: pipelineOpacity,
          borderRadius: 12,
          overflow: "hidden",
        }}
      >
        <Img
          src={staticFile("images/ml_demo/slide02_Picture_7.png")}
          style={{ width: 700, height: "auto" }}
        />
      </div>

      {/* Title */}
      <div
        style={{
          position: "absolute",
          top: 50,
          left: "50%",
          transform: "translateX(-50%)",
          fontFamily: FONTS.display,
          fontWeight: 700,
          fontSize: 48,
          color: COLORS.compute,
          opacity: interpolate(frame, [0, 15], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        It works!
      </div>

      <Caption text="Consistent setup → accurate, reliable tracking" />
    </AbsoluteFill>
  );
};
