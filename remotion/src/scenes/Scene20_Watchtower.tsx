import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Img,
  staticFile,
  Sequence,
} from "remotion";
import { COLORS } from "../styles";
import { Caption } from "../components/Caption";

export const Scene20_Watchtower: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const cutFrame = Math.floor(durationInFrames * 0.6);
  const showSlack = frame >= cutFrame;

  const dashScale = interpolate(frame, [0, durationInFrames], [1, 1.06], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const slackOpacity = interpolate(frame, [cutFrame, cutFrame + 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const alertPulse = showSlack
    ? 0.5 + Math.sin((frame - cutFrame) * 0.2) * 0.5
    : 0;

  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          overflow: "hidden",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <Img
          src={staticFile("images/07_monitoring/dashboard_full.png")}
          style={{
            width: "95%",
            objectFit: "contain",
            transform: `scale(${dashScale})`,
            borderRadius: 16,
          }}
        />
      </div>

      {showSlack && (
        <div
          style={{
            position: "absolute",
            right: 60,
            top: 80,
            width: 500,
            overflow: "hidden",
            borderRadius: 16,
            border: `2px solid ${COLORS.danger}`,
            boxShadow: `0 0 ${30 * alertPulse}px ${COLORS.danger}`,
            opacity: slackOpacity,
          }}
        >
          <Img
            src={staticFile("images/07_monitoring/slack_gpu_status.png")}
            style={{
              width: "100%",
              objectFit: "contain",
            }}
          />
        </div>
      )}

      <div
        style={{
          position: "absolute",
          inset: 0,
          background: "linear-gradient(transparent 80%, rgba(10,14,26,.9) 100%)",
          pointerEvents: "none",
        }}
      />

      <Sequence from={0} layout="none">
        <Caption text="510 days · 63,897 videos · 25,381 crashes caught" />
      </Sequence>
    </AbsoluteFill>
  );
};
