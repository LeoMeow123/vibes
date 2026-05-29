import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Sequence,
} from "remotion";
import { FONTS, COLORS } from "../styles";
import { Caption } from "../components/Caption";

const STREAM_COLORS = [COLORS.acquisition, COLORS.compute, COLORS.training, COLORS.source];

export const Scene10_Encoder: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const engineGlow = 0.4 + Math.sin(frame * 0.1) * 0.3;

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at 60% 50%, rgba(255,138,60,.06), transparent 50%), ${COLORS.bg}`,
      }}
    >
      {STREAM_COLORS.map((color, i) => {
        const yBase = 250 + i * 160;
        const streamLen = 12;
        return (
          <React.Fragment key={i}>
            {Array.from({ length: streamLen }).map((_, j) => {
              const speed = 8 + i * 1.5;
              const xPos = ((frame * speed + j * 60) % 800) + 100;
              const opacity = xPos > 700 ? interpolate(xPos, [700, 800], [1, 0], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              }) : xPos < 200 ? interpolate(xPos, [100, 200], [0, 1], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              }) : 0.7;

              return (
                <div
                  key={j}
                  style={{
                    position: "absolute",
                    left: xPos,
                    top: yBase + Math.sin(frame * 0.05 + j) * 8,
                    width: 30,
                    height: 8,
                    borderRadius: 4,
                    background: color,
                    opacity,
                    boxShadow: `0 0 8px ${color}`,
                  }}
                />
              );
            })}

            <div
              style={{
                position: "absolute",
                left: 50,
                top: yBase - 8,
                fontFamily: FONTS.mono,
                fontSize: 13,
                color: COLORS.muted,
              }}
            >
              cam_{i + 1}
            </div>
          </React.Fragment>
        );
      })}

      <div
        style={{
          position: "absolute",
          left: 850,
          top: 180,
          width: 280,
          height: 720,
          zIndex: 3,
        }}
      >
        <div
          style={{
            width: "100%",
            height: "100%",
            borderRadius: 20,
            background: `linear-gradient(180deg, rgba(42,53,80,.8), rgba(26,32,48,.9))`,
            border: `2px solid rgba(255,138,60,${engineGlow})`,
            boxShadow: `0 0 ${engineGlow * 40}px rgba(255,138,60,.3), inset 0 0 30px rgba(255,138,60,.05)`,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            gap: 20,
          }}
        >
          <div style={{ fontSize: 50 }}>⚡</div>
          <div
            style={{
              fontFamily: FONTS.display,
              fontSize: 24,
              fontWeight: 700,
              color: COLORS.ink,
              textAlign: "center",
            }}
          >
            ENCODER
          </div>
          <div
            style={{
              fontFamily: FONTS.mono,
              fontSize: 14,
              color: COLORS.source,
              textAlign: "center",
            }}
          >
            CPU + GPU
          </div>

          <div
            style={{
              width: 200,
              height: 6,
              background: "rgba(255,255,255,.1)",
              borderRadius: 3,
              overflow: "hidden",
            }}
          >
            <div
              style={{
                width: `${50 + Math.sin(frame * 0.08) * 30}%`,
                height: "100%",
                background: `linear-gradient(90deg, ${COLORS.source}, ${COLORS.training})`,
                borderRadius: 3,
              }}
            />
          </div>

          <div
            style={{
              fontFamily: FONTS.mono,
              fontSize: 12,
              color: COLORS.muted,
            }}
          >
            H.264 / NVENC
          </div>

          <div
            style={{
              position: "absolute",
              bottom: -40,
              left: "50%",
              transform: "translateX(-50%)",
              width: 200,
              height: 20,
              background: `radial-gradient(ellipse, rgba(255,138,60,${engineGlow * 0.3}), transparent)`,
              filter: "blur(10px)",
            }}
          />
        </div>
      </div>

      {Array.from({ length: 8 }).map((_, i) => {
        const speed = 6 + i * 0.8;
        const xPos = 1180 + ((frame * speed + i * 70) % 600);
        const yBase = 280 + i * 80;
        const opacity = interpolate(frame, [20, 40], [0, 0.8], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

        return (
          <div
            key={`packet-${i}`}
            style={{
              position: "absolute",
              left: xPos,
              top: yBase + Math.sin(frame * 0.04 + i) * 5,
              width: 50,
              height: 30,
              borderRadius: 6,
              background: `linear-gradient(135deg, ${COLORS.compute}, rgba(123,232,138,.3))`,
              border: `1px solid rgba(123,232,138,.4)`,
              opacity: xPos > 1700 ? 0 : opacity,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontFamily: FONTS.mono,
              fontSize: 9,
              color: COLORS.bg,
              fontWeight: 700,
              boxShadow: `0 0 8px rgba(123,232,138,.3)`,
            }}
          >
            .mp4
          </div>
        );
      })}

      <div
        style={{
          position: "absolute",
          right: 60,
          top: "50%",
          transform: "translateY(-50%)",
          fontFamily: FONTS.mono,
          fontSize: 14,
          color: COLORS.compute,
          opacity: interpolate(frame, [fps * 2, fps * 3], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
        }}
      >
        compressed →
      </div>

      <Sequence from={0} layout="none">
        <Caption text="Encode at the source." />
      </Sequence>
    </AbsoluteFill>
  );
};
