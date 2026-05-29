import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Sequence,
} from "remotion";
import { KenBurns } from "../components/KenBurns";
import { Caption } from "../components/Caption";

export const Scene15_LiveRig: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const glowOpacity = interpolate(
    frame,
    [fps * 2, fps * 3, fps * 5, fps * 6],
    [0, 0.4, 0.4, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const glowPulse = 0.3 + Math.sin(frame * 0.08) * 0.1;

  return (
    <AbsoluteFill>
      <KenBurns
        src="images/03_cage_build/live_rig_with_mice.png"
        startScale={1.02}
        endScale={1.1}
        translateX={[-10, 10]}
      />

      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(ellipse at 50% 50%, rgba(123,232,138,${glowPulse}) 0%, transparent 60%)`,
          opacity: glowOpacity,
          zIndex: 1,
          pointerEvents: "none",
          mixBlendMode: "screen",
        }}
      />

      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(transparent 60%, rgba(10,14,26,.8) 100%)",
          zIndex: 2,
        }}
      />

      <Sequence from={0} layout="none">
        <Caption text="Hand-built. And it's alive." />
      </Sequence>
    </AbsoluteFill>
  );
};
