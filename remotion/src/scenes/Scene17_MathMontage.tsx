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
import { FONTS, COLORS } from "../styles";
import { Caption } from "../components/Caption";

const EQUATIONS = [
  { text: "BW = fps × res² × bpp", x: 200, y: 250, delay: 20 },
  { text: "Δt_sync < 1/fps", x: 900, y: 300, delay: 45 },
  { text: "naming = cam_{id}_{ts}.mp4", x: 300, y: 450, delay: 70 },
  { text: "bitrate ≤ NIC / n_cams", x: 800, y: 500, delay: 95 },
  { text: "f_transfer = ceil(dur / slot)", x: 500, y: 650, delay: 120 },
];

export const Scene17_MathMontage: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const imgOpacity = interpolate(frame, [fps * 2, fps * 3, fps * 4, fps * 4.5], [0, 0.6, 0.6, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(800px at 50% 50%, rgba(109,179,255,.06), transparent), ${COLORS.bg}`,
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage:
            "linear-gradient(rgba(255,255,255,.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.02) 1px, transparent 1px)",
          backgroundSize: "30px 30px",
        }}
      />

      {EQUATIONS.map((eq) => {
        const localFrame = frame - eq.delay;
        const opacity = interpolate(localFrame, [0, 20], [0, 0.85], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.out(Easing.cubic),
        });
        const drift = Math.sin(frame * 0.02 + eq.delay) * 8;

        return (
          <div
            key={eq.text}
            style={{
              position: "absolute",
              left: eq.x,
              top: eq.y + drift,
              fontFamily: FONTS.mono,
              fontSize: 24,
              color: COLORS.acquisition,
              opacity,
              textShadow: `0 0 20px rgba(109,179,255,.4)`,
            }}
          >
            {eq.text}
          </div>
        );
      })}

      <div
        style={{
          position: "absolute",
          right: 100,
          bottom: 180,
          width: 500,
          height: 350,
          overflow: "hidden",
          borderRadius: 16,
          border: `1px solid ${COLORS.line}`,
          opacity: imgOpacity,
        }}
      >
        <Img
          src={staticFile("images/01_hardware_wiring/parts_boxes_donottake.jpeg")}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
        />
      </div>

      <Sequence from={0} layout="none">
        <Caption text="bandwidth · sync · auto-naming · encoding" />
      </Sequence>
    </AbsoluteFill>
  );
};
