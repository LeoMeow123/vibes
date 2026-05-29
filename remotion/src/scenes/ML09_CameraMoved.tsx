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

export const ML09_CameraMoved: React.FC = () => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Camera slides from position A to B
  const cameraX = interpolate(frame, [25, 65], [0, 200], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  const failOpacity = interpolate(frame, [80, 100], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const shakeX = frame > 65 && frame < 85
    ? Math.sin(frame * 3) * interpolate(frame, [65, 75, 85], [0, 6, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })
    : 0;

  const redFlash = interpolate(frame, [65, 72, 82], [0, 0.2, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const comparisonOpacity = interpolate(frame, [110, 130], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const explainOpacity = interpolate(frame, [140, 160], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: COLORS.bg, transform: `translateX(${shakeX}px)` }}>
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
        ⚠️ Camera position changed
      </div>

      {/* Camera sliding */}
      <div
        style={{
          position: "absolute",
          left: 250 + cameraX,
          top: "30%",
        }}
      >
        <div style={{ fontSize: 100 }}>📷</div>
        <div
          style={{
            fontFamily: FONTS.mono,
            fontSize: 18,
            color: cameraX < 50 ? COLORS.compute : COLORS.danger,
            marginTop: 8,
            whiteSpace: "nowrap",
          }}
        >
          {cameraX < 50 ? "📍 Position A" : "📍 Position B"}
        </div>
      </div>

      {/* Dotted line showing movement */}
      {cameraX > 10 && (
        <svg
          width={300}
          height={20}
          style={{ position: "absolute", left: 290, top: "35%", marginTop: 50 }}
        >
          <line
            x1={0}
            y1={10}
            x2={cameraX}
            y2={10}
            stroke={COLORS.danger}
            strokeWidth={3}
            strokeDasharray="8,6"
          />
          <polygon
            points={`${cameraX - 8},2 ${cameraX},10 ${cameraX - 8},18`}
            fill={COLORS.danger}
            opacity={interpolate(cameraX, [10, 200], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
          />
        </svg>
      )}

      {/* Two "camera views" showing different backgrounds */}
      <div
        style={{
          position: "absolute",
          right: 150,
          top: "22%",
          display: "flex",
          flexDirection: "column",
          gap: 20,
          opacity: comparisonOpacity,
        }}
      >
        {/* View A */}
        <div style={{ display: "flex", alignItems: "center", gap: 15 }}>
          <div
            style={{
              width: 220,
              height: 150,
              borderRadius: 10,
              border: `2px solid ${COLORS.compute}`,
              overflow: "hidden",
              position: "relative",
            }}
          >
            <Img
              src={staticFile("images/ml_demo/slide12_Content_Placeholder_4.png")}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
            <div
              style={{
                position: "absolute",
                top: 6,
                left: 6,
                fontFamily: FONTS.mono,
                fontSize: 14,
                color: COLORS.compute,
                background: "rgba(10,14,28,0.8)",
                padding: "2px 8px",
                borderRadius: 6,
              }}
            >
              Position A ✅
            </div>
          </div>
        </div>

        {/* Arrow */}
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: 32,
            color: COLORS.muted,
            textAlign: "center",
          }}
        >
          ↓ moved camera
        </div>

        {/* View B */}
        <div style={{ display: "flex", alignItems: "center", gap: 15 }}>
          <div
            style={{
              width: 220,
              height: 150,
              borderRadius: 10,
              border: `2px solid ${COLORS.danger}`,
              overflow: "hidden",
              boxShadow: `0 0 15px ${COLORS.danger}`,
              position: "relative",
            }}
          >
            <Img
              src={staticFile("images/ml_demo/slide12_Picture_6.png")}
              style={{ width: "100%", height: "100%", objectFit: "cover" }}
            />
            <div
              style={{
                position: "absolute",
                top: 6,
                left: 6,
                fontFamily: FONTS.mono,
                fontSize: 14,
                color: COLORS.danger,
                background: "rgba(10,14,28,0.8)",
                padding: "2px 8px",
                borderRadius: 6,
              }}
            >
              Position B ❌
            </div>
          </div>
        </div>
      </div>

      {/* Failure images from slides */}
      <div
        style={{
          position: "absolute",
          left: 200,
          top: "55%",
          opacity: failOpacity,
          display: "flex",
          gap: 20,
        }}
      >
        <div
          style={{
            borderRadius: 10,
            overflow: "hidden",
            border: `2px solid ${COLORS.danger}`,
          }}
        >
          <Img
            src={staticFile("images/ml_demo/slide10_Picture_25.png")}
            style={{ width: 200, height: "auto" }}
          />
        </div>
        <div
          style={{
            borderRadius: 10,
            overflow: "hidden",
            border: `2px solid ${COLORS.danger}`,
          }}
        >
          <Img
            src={staticFile("images/ml_demo/slide10_Picture_28.png")}
            style={{ width: 160, height: "auto" }}
          />
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
          fontSize: 24,
          color: COLORS.danger,
          opacity: explainOpacity,
          textAlign: "center",
          background: "rgba(255,107,107,0.1)",
          padding: "12px 30px",
          borderRadius: 16,
          border: `1px solid ${COLORS.danger}`,
          maxWidth: 700,
        }}
      >
        Different background = completely different pixel values = confused model
      </div>

      <Caption text="Moving the camera rewrites the entire input" />
    </AbsoluteFill>
  );
};
