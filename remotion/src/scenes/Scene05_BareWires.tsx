import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
  Img,
  staticFile,
  Sequence,
} from "remotion";
import { COLORS } from "../styles";
import { Caption } from "../components/Caption";

export const Scene05_BareWires: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();

  const cutFrame = Math.floor(durationInFrames * 0.55);
  const showSecond = frame >= cutFrame;

  const brightness1 = interpolate(frame, [0, fps * 1.5], [0.15, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const scale1 = interpolate(frame, [0, durationInFrames], [1, 1.08], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const img2Opacity = interpolate(
    frame,
    [cutFrame, cutFrame + 12],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>
        <Img
          src={staticFile("images/01_hardware_wiring/wires_box_tangled.jpeg")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            filter: `brightness(${brightness1})`,
            transform: `scale(${scale1})`,
          }}
        />
      </div>

      {showSecond && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            overflow: "hidden",
            opacity: img2Opacity,
          }}
        >
          <Img
            src={staticFile("images/01_hardware_wiring/wires_box_soldered.jpeg")}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              transform: `scale(${interpolate(frame - cutFrame, [0, durationInFrames - cutFrame], [1, 1.06], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })})`,
            }}
          />
        </div>
      )}

      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "radial-gradient(ellipse at 50% 50%, transparent 30%, rgba(10,14,26,.6) 100%)",
          pointerEvents: "none",
        }}
      />

      <Sequence from={0} layout="none">
        <Caption text={'"These cameras expect an EE. I am becoming one."'} />
      </Sequence>
    </AbsoluteFill>
  );
};
