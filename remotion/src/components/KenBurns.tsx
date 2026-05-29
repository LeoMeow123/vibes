import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, Easing, Img, staticFile } from "remotion";

export const KenBurns: React.FC<{
  src: string;
  startScale?: number;
  endScale?: number;
  translateX?: [number, number];
  translateY?: [number, number];
  brightness?: number;
}> = ({
  src,
  startScale = 1.0,
  endScale = 1.08,
  translateX = [0, 0],
  translateY = [0, 0],
  brightness = 1,
}) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const progress = interpolate(frame, [0, durationInFrames], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  const scale = interpolate(progress, [0, 1], [startScale, endScale]);
  const tx = interpolate(progress, [0, 1], translateX);
  const ty = interpolate(progress, [0, 1], translateY);

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        overflow: "hidden",
      }}
    >
      <Img
        src={staticFile(src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale}) translate(${tx}px, ${ty}px)`,
          filter: `brightness(${brightness})`,
        }}
      />
    </div>
  );
};
