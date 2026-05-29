import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
  Sequence,
} from "remotion";
import { FONTS, COLORS } from "../styles";
import { KenBurns } from "../components/KenBurns";
import { Caption } from "../components/Caption";

const MICE = [
  { x: 600, y: 720, delay: 20, emoji: "🐭" },
  { x: 900, y: 750, delay: 35, emoji: "🐭" },
  { x: 1200, y: 710, delay: 50, emoji: "🐭" },
  { x: 750, y: 780, delay: 65, emoji: "🐁" },
  { x: 1050, y: 760, delay: 45, emoji: "🐁" },
];

export const Scene14_SalkFlourish: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const tintOpacity = interpolate(frame, [0, fps * 2], [0, 0.25], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <KenBurns
        src="images/05_salk/salk_courtyard_sunset.png"
        startScale={1.05}
        endScale={1.0}
        translateY={[5, -5]}
      />

      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `linear-gradient(
            transparent 50%,
            rgba(255,196,107,${tintOpacity}) 70%,
            rgba(255,138,60,${tintOpacity * 0.8}) 100%
          )`,
          zIndex: 1,
          pointerEvents: "none",
        }}
      />

      {MICE.map((mouse, i) => {
        const localFrame = frame - mouse.delay;
        const opacity = interpolate(localFrame, [0, 15], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const bounce = localFrame > 15
          ? Math.sin(localFrame * 0.15 + i) * 6
          : 0;
        const popScale = interpolate(localFrame, [0, 10], [0.3, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.bezier(0.34, 1.56, 0.64, 1),
        });

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: mouse.x,
              top: mouse.y + bounce,
              fontSize: 40,
              opacity,
              transform: `scale(${popScale})`,
              zIndex: 2,
              filter: "drop-shadow(0 2px 8px rgba(0,0,0,.4))",
            }}
          >
            {mouse.emoji}
          </div>
        );
      })}

      <div
        style={{
          position: "absolute",
          top: 80,
          left: "50%",
          transform: "translateX(-50%)",
          textAlign: "center",
          zIndex: 3,
          opacity: interpolate(frame, [fps * 1, fps * 2], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: 44,
            fontWeight: 700,
            color: COLORS.ink,
            textShadow: "0 3px 20px rgba(0,0,0,.6)",
          }}
        >
          Salk Institute
        </div>
        <div
          style={{
            fontFamily: FONTS.mono,
            fontSize: 20,
            color: COLORS.training,
            marginTop: 8,
            textShadow: "0 2px 10px rgba(0,0,0,.5)",
          }}
        >
          but make it anime ✨
        </div>
      </div>

      <Sequence from={0} layout="none">
        <Caption text="Salk Institute, but make it anime." />
      </Sequence>
    </AbsoluteFill>
  );
};
