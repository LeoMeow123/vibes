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

export const ML07_AngleChanged: React.FC = () => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Camera tilts
  const cameraAngle = interpolate(frame, [30, 70], [0, 25], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  // Good state opacity
  const goodOpacity = interpolate(frame, [10, 20, 60, 80], [0, 1, 1, 0.3], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Failure image
  const failOpacity = interpolate(frame, [90, 110], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Red flash
  const redFlash = interpolate(frame, [70, 80, 95], [0, 0.3, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Shake when breaking
  const shakeX = frame > 65 && frame < 85
    ? Math.sin(frame * 2.5) * interpolate(frame, [65, 75, 85], [0, 8, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
    : 0;

  // Explanation text
  const explainOpacity = interpolate(frame, [130, 150], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // X mark
  const xScale = interpolate(frame, [110, 125], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.back(2)),
  });

  return (
    <AbsoluteFill style={{ background: COLORS.bg, transform: `translateX(${shakeX}px)` }}>
      {/* Red flash overlay */}
      <AbsoluteFill style={{ background: COLORS.danger, opacity: redFlash, zIndex: 5 }} />

      <div
        style={{
          position: "absolute",
          top: 50,
          left: "50%",
          transform: "translateX(-50%)",
          fontFamily: FONTS.display,
          fontWeight: 700,
          fontSize: 44,
          color: COLORS.danger,
          opacity: titleOpacity,
        }}
      >
        ⚠️ Camera angle changed
      </div>

      {/* Camera icon that tilts */}
      <div
        style={{
          position: "absolute",
          left: 300,
          top: "40%",
          transform: `rotate(${cameraAngle}deg)`,
          fontSize: 120,
          opacity: goodOpacity,
        }}
      >
        📷
      </div>

      {/* Arrow showing the tilt */}
      {cameraAngle > 5 && (
        <svg
          width={200}
          height={100}
          style={{ position: "absolute", left: 250, top: "32%" }}
        >
          <path
            d={`M 100 80 A 60 60 0 0 1 160 40`}
            fill="none"
            stroke={COLORS.danger}
            strokeWidth={3}
            strokeDasharray="6,4"
            opacity={interpolate(cameraAngle, [5, 25], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
          />
        </svg>
      )}

      {/* Angle label */}
      <div
        style={{
          position: "absolute",
          left: 310,
          top: "55%",
          fontFamily: FONTS.mono,
          fontSize: 22,
          color: cameraAngle > 10 ? COLORS.danger : COLORS.compute,
          opacity: goodOpacity,
        }}
      >
        {cameraAngle < 2 ? "✅ Original angle" : `❌ Tilted ${Math.round(cameraAngle)}°`}
      </div>

      {/* Good tracking → failure */}
      <div
        style={{
          position: "absolute",
          right: 200,
          top: "25%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 20,
        }}
      >
        {/* Good result (fades) */}
        <div
          style={{
            opacity: goodOpacity * (1 - failOpacity),
            borderRadius: 12,
            overflow: "hidden",
            border: `3px solid ${COLORS.compute}`,
          }}
        >
          <Img
            src={staticFile("images/ml_demo/slide10_Picture_4.png")}
            style={{ width: 320, height: "auto" }}
          />
        </div>

        {/* Bad result (appears) */}
        <div
          style={{
            position: "absolute",
            top: 0,
            opacity: failOpacity,
            borderRadius: 12,
            overflow: "hidden",
            border: `3px solid ${COLORS.danger}`,
            boxShadow: `0 0 20px ${COLORS.danger}`,
          }}
        >
          <Img
            src={staticFile("images/ml_demo/slide10_Picture_26.png")}
            style={{ width: 320, height: "auto" }}
          />
        </div>

        {/* X mark */}
        <div
          style={{
            position: "absolute",
            top: -20,
            right: -20,
            fontSize: 60,
            transform: `scale(${xScale})`,
            zIndex: 10,
          }}
        >
          ❌
        </div>
      </div>

      {/* Explanation */}
      <div
        style={{
          position: "absolute",
          bottom: 140,
          left: "50%",
          transform: "translateX(-50%)",
          fontFamily: FONTS.mono,
          fontSize: 26,
          color: COLORS.danger,
          opacity: explainOpacity,
          textAlign: "center",
          background: "rgba(255,107,107,0.1)",
          padding: "12px 30px",
          borderRadius: 16,
          border: `1px solid ${COLORS.danger}`,
          maxWidth: 800,
        }}
      >
        Same mouse, but every pixel shifted — the model's patterns don't match
      </div>

      <Caption text="Trained on angle A ≠ works on angle B" />
    </AbsoluteFill>
  );
};
