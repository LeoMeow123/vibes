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

const PHONE_DATA = [
  { label: "Cam 1", driftRate: 1.0, color: COLORS.acquisition },
  { label: "Cam 2", driftRate: 0.87, color: COLORS.compute },
  { label: "Cam 3", driftRate: 1.13, color: COLORS.training },
  { label: "Cam 4", driftRate: 0.72, color: COLORS.source },
];

export const Scene07_FourPhones: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at 50% 40%, rgba(255,107,107,.06), transparent 50%), ${COLORS.bg}`,
      }}
    >
      <div
        style={{
          position: "absolute",
          top: 60,
          left: "50%",
          transform: "translateX(-50%)",
          fontFamily: FONTS.display,
          fontSize: 36,
          fontWeight: 700,
          color: COLORS.ink,
          textAlign: "center",
        }}
      >
        Four cameras, four different clocks
      </div>

      {PHONE_DATA.map((phone, i) => {
        const x = 240 + i * 380;
        const appearDelay = i * 10;
        const opacity = interpolate(frame, [appearDelay, appearDelay + 15], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

        const clock = frame * phone.driftRate;
        const seconds = Math.floor(clock / fps);
        const subFrames = Math.floor(clock % fps);
        const timeStr = `00:${String(seconds).padStart(2, "0")}:${String(subFrames).padStart(2, "0")}`;

        const frameCount = Math.floor(clock * 1.67);

        const drift = Math.abs(1 - phone.driftRate) * frame * 0.5;
        const glitchIntensity = interpolate(frame, [fps * 2, fps * 5], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });

        const glitchX = glitchIntensity > 0.3
          ? Math.sin(frame * phone.driftRate * 3) * drift * 0.5
          : 0;

        return (
          <div
            key={phone.label}
            style={{
              position: "absolute",
              left: x,
              top: 200,
              opacity,
              transform: `translateX(${glitchX}px)`,
              zIndex: 2,
            }}
          >
            <div
              style={{
                width: 160,
                height: 280,
                borderRadius: 20,
                background: "#1a2030",
                border: `2px solid ${drift > 15 ? COLORS.danger : phone.color}`,
                boxShadow: `0 0 ${drift > 15 ? 20 : 0}px rgba(255,107,107,.3), 0 10px 30px rgba(0,0,0,.4)`,
                overflow: "hidden",
                position: "relative",
              }}
            >
              <div
                style={{
                  height: 30,
                  background: "#141826",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontFamily: FONTS.mono,
                  fontSize: 11,
                  color: phone.color,
                }}
              >
                {phone.label}
              </div>

              <div style={{ padding: "12px 10px", textAlign: "center" }}>
                <div
                  style={{
                    fontFamily: FONTS.mono,
                    fontSize: 11,
                    color: COLORS.muted,
                    marginBottom: 4,
                  }}
                >
                  TIMECODE
                </div>
                <div
                  style={{
                    fontFamily: FONTS.mono,
                    fontSize: 22,
                    fontWeight: 700,
                    color: COLORS.ink,
                  }}
                >
                  {timeStr}
                </div>

                <div
                  style={{
                    fontFamily: FONTS.mono,
                    fontSize: 11,
                    color: COLORS.muted,
                    marginTop: 16,
                    marginBottom: 4,
                  }}
                >
                  FRAMES
                </div>
                <div
                  style={{
                    fontFamily: FONTS.mono,
                    fontSize: 20,
                    fontWeight: 700,
                    color: drift > 15 ? COLORS.danger : COLORS.ink,
                  }}
                >
                  {frameCount}
                </div>

                <div
                  style={{
                    marginTop: 20,
                    height: 4,
                    background: "rgba(255,255,255,.05)",
                    borderRadius: 2,
                    overflow: "hidden",
                  }}
                >
                  <div
                    style={{
                      width: `${(clock % 30) / 30 * 100}%`,
                      height: "100%",
                      background: phone.color,
                      borderRadius: 2,
                    }}
                  />
                </div>
              </div>

              {drift > 20 && (
                <div
                  style={{
                    position: "absolute",
                    inset: "30px 0 0 0",
                    background:
                      "repeating-linear-gradient(0deg, rgba(255,107,107,.04) 0px, rgba(255,107,107,.04) 1px, transparent 1px, transparent 4px)",
                    pointerEvents: "none",
                  }}
                />
              )}
            </div>

            <div
              style={{
                marginTop: 12,
                textAlign: "center",
                fontFamily: FONTS.mono,
                fontSize: 13,
                color: COLORS.muted,
              }}
            >
              ×{phone.driftRate.toFixed(2)} speed
            </div>
          </div>
        );
      })}

      {frame > fps * 3 && (
        <div
          style={{
            position: "absolute",
            top: 160,
            left: "50%",
            transform: "translateX(-50%)",
            fontFamily: FONTS.display,
            fontSize: 28,
            fontWeight: 700,
            color: COLORS.danger,
            opacity: interpolate(frame, [fps * 3, fps * 4], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          ⚠ DRIFT DETECTED
        </div>
      )}

      <Sequence from={0} layout="none">
        <Caption text="4 phones ≠ synced." />
      </Sequence>
    </AbsoluteFill>
  );
};
