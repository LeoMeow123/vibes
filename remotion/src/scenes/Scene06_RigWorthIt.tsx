import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  Easing,
  Img,
  staticFile,
  Sequence,
} from "remotion";
import { FONTS, COLORS } from "../styles";
import { Caption } from "../components/Caption";

const CHECKMARKS = [
  { text: "Consistent FOV", delay: 30 },
  { text: "High SNR", delay: 60 },
  { text: "Low blur", delay: 90 },
  { text: "Stable capture", delay: 120 },
  { text: "Consistent illumination", delay: 150 },
];

export const Scene06_RigWorthIt: React.FC = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>
        <Img
          src={staticFile("images/02_cameras/component_labels_checkmarks.png")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "contain",
            transform: `scale(${interpolate(frame, [0, 240], [1, 1.05], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })})`,
          }}
        />
      </div>

      <div
        style={{
          position: "absolute",
          right: 80,
          top: 200,
          display: "flex",
          flexDirection: "column",
          gap: 16,
          zIndex: 3,
        }}
      >
        {CHECKMARKS.map((ck) => {
          const localFrame = frame - ck.delay;
          const opacity = interpolate(localFrame, [0, 15], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.cubic),
          });
          const scale = interpolate(localFrame, [0, 12], [0.7, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.bezier(0.34, 1.56, 0.64, 1),
          });

          return (
            <div
              key={ck.text}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                opacity,
                transform: `scale(${scale})`,
              }}
            >
              <div
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: 8,
                  background: COLORS.compute,
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: 18,
                  fontWeight: 700,
                  color: COLORS.bg,
                  boxShadow: `0 0 12px ${COLORS.compute}`,
                }}
              >
                ✓
              </div>
              <span
                style={{
                  fontFamily: FONTS.mono,
                  fontSize: 20,
                  fontWeight: 700,
                  color: COLORS.ink,
                }}
              >
                {ck.text}
              </span>
            </div>
          );
        })}
      </div>

      <Sequence from={0} layout="none">
        <Caption text="Raw gear → real data." />
      </Sequence>
    </AbsoluteFill>
  );
};
