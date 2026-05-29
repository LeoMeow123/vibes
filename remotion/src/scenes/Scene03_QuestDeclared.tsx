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
import { Caption } from "../components/Caption";

const GRID_COLS = 10;
const GRID_ROWS = 5;

export const Scene03_QuestDeclared: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const silhouetteOpacity = interpolate(frame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const fistRaise = interpolate(frame, [fps * 1.5, fps * 2.5], [0, -40], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.34, 1.56, 0.64, 1),
  });

  const auraScale = interpolate(frame, [fps * 2, fps * 3.5], [0, 3], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const auraOpacity = interpolate(frame, [fps * 2, fps * 3, fps * 3.5], [0, 0.6, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const bossTextOpacity = interpolate(frame, [fps * 3, fps * 4], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const bossTextScale = interpolate(frame, [fps * 3, fps * 4], [2, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at 50% 80%, rgba(109,179,255,.15), transparent 60%), ${COLORS.bg}`,
      }}
    >
      {Array.from({ length: GRID_COLS * GRID_ROWS }).map((_, i) => {
        const col = i % GRID_COLS;
        const row = Math.floor(i / GRID_COLS);
        const delay = (col + row) * 3 + 30;
        const cellOpacity = interpolate(frame, [delay, delay + 20], [0, 0.7], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.out(Easing.cubic),
        });

        const cellScale = interpolate(frame, [delay, delay + 15], [0.5, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.bezier(0.34, 1.56, 0.64, 1),
        });

        const glow = Math.sin(frame * 0.05 + i * 0.3) * 0.3 + 0.7;

        return (
          <div
            key={i}
            style={{
              position: "absolute",
              left: 650 + col * 100,
              top: 200 + row * 120,
              width: 80,
              height: 100,
              borderRadius: 8,
              border: `1.5px solid rgba(109,179,255,${glow * 0.5})`,
              background: `rgba(109,179,255,${glow * 0.08})`,
              boxShadow: `0 0 ${glow * 12}px rgba(109,179,255,${glow * 0.3})`,
              opacity: cellOpacity,
              transform: `scale(${cellScale})`,
            }}
          >
            <div
              style={{
                position: "absolute",
                top: 8,
                left: "50%",
                transform: "translateX(-50%)",
                width: 10,
                height: 10,
                borderRadius: "50%",
                background: `rgba(123,232,138,${glow})`,
                boxShadow: `0 0 6px rgba(123,232,138,${glow})`,
              }}
            />
          </div>
        );
      })}

      <div
        style={{
          position: "absolute",
          left: 300,
          bottom: 150,
          opacity: silhouetteOpacity,
          zIndex: 3,
        }}
      >
        <div
          style={{
            width: 60,
            height: 140,
            background: "linear-gradient(180deg, #2a3550, #0a0e1a)",
            borderRadius: "30px 30px 10px 10px",
            position: "relative",
          }}
        >
          <div
            style={{
              position: "absolute",
              top: -50,
              left: "50%",
              transform: "translateX(-50%)",
              width: 50,
              height: 50,
              borderRadius: "50%",
              background: "linear-gradient(180deg, #3a4a6a, #1a2540)",
            }}
          />
          <div
            style={{
              position: "absolute",
              top: -20 + fistRaise,
              right: -35,
              width: 25,
              height: 70,
              background: "#2a3550",
              borderRadius: 12,
              transformOrigin: "bottom center",
              transform: "rotate(-20deg)",
            }}
          />
          <div
            style={{
              position: "absolute",
              top: 40,
              left: -20,
              width: 25,
              height: 60,
              background: "#2a3550",
              borderRadius: 12,
              transform: "rotate(10deg)",
            }}
          />
        </div>
      </div>

      <div
        style={{
          position: "absolute",
          left: 330,
          bottom: 280,
          width: 100,
          height: 100,
          borderRadius: "50%",
          background: `radial-gradient(circle, rgba(255,196,107,.6), transparent 70%)`,
          transform: `scale(${auraScale})`,
          opacity: auraOpacity,
          pointerEvents: "none",
        }}
      />

      <div
        style={{
          position: "absolute",
          left: 150,
          top: 100,
          opacity: bossTextOpacity,
          transform: `scale(${bossTextScale})`,
          zIndex: 5,
        }}
      >
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: 72,
            fontWeight: 700,
            color: COLORS.training,
            textShadow: `0 0 40px ${COLORS.training}`,
          }}
        >
          BOSS BATTLES
        </div>
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: 120,
            fontWeight: 700,
            color: COLORS.danger,
            textShadow: `0 0 50px ${COLORS.danger}`,
            marginTop: -10,
          }}
        >
          5
        </div>
      </div>

      <Sequence from={0} layout="none">
        <Caption text="BOSS BATTLES: 5" />
      </Sequence>
    </AbsoluteFill>
  );
};
