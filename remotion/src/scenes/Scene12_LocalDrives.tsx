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

const TUNNEL_X = 1300;
const TUNNEL_Y = 340;
const TUNNEL_W = 220;
const TUNNEL_H = 260;
const ROAD_Y = 540;

const TB_BLOCKS = [
  { label: "cam_01", delay: 0 },
  { label: "cam_02", delay: 4 },
  { label: "cam_03", delay: 8 },
  { label: "cam_04", delay: 12 },
  { label: ".mp4", delay: 16 },
  { label: ".mp4", delay: 18 },
  { label: ".mp4", delay: 20 },
  { label: ".mp4", delay: 22 },
];

export const Scene12_LocalDrives: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Phase 1 (0-2s):   Small bus drives in, data loads on
  // Phase 2 (2-3.2s): Bus overflows, "TOO SMALL!"
  // Phase 3 (3.2-4.8s): Get BIGGER bus
  // Phase 4 (4.8-6s): Big bus hits the tunnel — CRASH
  // Phase 5 (6-8s):   Fix the tunnel → "REAL-TIME STREAMING" solution

  const p1End = fps * 2;
  const p2End = fps * 3.2;
  const p3End = fps * 4.8;
  const p4End = fps * 6;

  // Phase 1: small bus drives in from left
  const smallBusX = interpolate(frame, [0, fps * 1.2], [-200, 400], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  // TB blocks loading onto bus
  const loadedBlocks = Math.min(
    TB_BLOCKS.length,
    Math.floor(interpolate(frame, [fps * 0.6, p1End], [0, TB_BLOCKS.length], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    })),
  );

  // Phase 2: overflowing, blocks falling off
  const overflowShake = frame >= p1End && frame < p2End
    ? Math.sin(frame * 2) * 4
    : 0;
  const tooSmallOpacity = interpolate(frame, [p1End + 5, p1End + 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Phase 3: big bus scales up from center
  const bigBusActive = frame >= p2End;
  const bigBusScale = interpolate(frame, [p2End, p2End + 15], [0.3, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.34, 1.56, 0.64, 1),
  });
  const bigBusX = interpolate(frame, [p3End - 15, p3End + 20], [400, TUNNEL_X - 200], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  // Phase 4: crash into tunnel
  const crashActive = frame >= p3End + 15;
  const crashShake = crashActive && frame < p4End
    ? Math.sin((frame - p3End) * 3) * 12 * interpolate(frame, [p3End + 15, p3End + 20], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 0;
  const crashFlashOpacity = interpolate(frame, [p3End + 18, p3End + 22, p3End + 30], [0, 0.6, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Phase 5: tunnel widens, real-time streaming replaces bus
  const fixActive = frame >= p4End;
  const tunnelExpand = interpolate(frame, [p4End, p4End + 20], [1, 2.2], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const solutionOpacity = interpolate(frame, [p4End + 15, p4End + 30], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const streamParticleCount = fixActive ? 20 : 0;

  const phase = frame < p1End ? 1 : frame < p2End ? 2 : frame < p3End ? 3 : frame < p4End ? 4 : 5;

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at 50% 80%, rgba(255,107,107,.05), transparent 50%), ${COLORS.bg}`,
      }}
    >
      {/* Road */}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: ROAD_Y,
          width: "100%",
          height: 6,
          background: COLORS.line,
          zIndex: 1,
        }}
      />
      <div
        style={{
          position: "absolute",
          left: 0,
          top: ROAD_Y + 3,
          width: "100%",
          height: 2,
          background: "rgba(255,255,255,.08)",
          zIndex: 1,
        }}
      />

      {/* Tunnel */}
      <div
        style={{
          position: "absolute",
          left: TUNNEL_X,
          top: TUNNEL_Y,
          width: TUNNEL_W * (fixActive ? tunnelExpand : 1),
          height: TUNNEL_H * (fixActive ? tunnelExpand : 1),
          borderRadius: `${TUNNEL_W / 2}px ${TUNNEL_W / 2}px 0 0`,
          border: `4px solid ${fixActive ? COLORS.compute : crashActive ? COLORS.danger : COLORS.muted}`,
          borderBottom: "none",
          background: "rgba(20,24,38,.6)",
          zIndex: 2,
          transform: fixActive
            ? `translate(${-(TUNNEL_W * (tunnelExpand - 1)) / 2}px, ${-(TUNNEL_H * (tunnelExpand - 1))}px)`
            : "none",
          boxShadow: crashActive && !fixActive
            ? `0 0 30px ${COLORS.danger}`
            : fixActive ? `0 0 30px ${COLORS.compute}` : "none",
        }}
      >
        <div
          style={{
            position: "absolute",
            bottom: 0,
            left: "50%",
            transform: "translateX(-50%)",
            fontFamily: FONTS.mono,
            fontSize: fixActive ? 16 : 14,
            color: fixActive ? COLORS.compute : COLORS.muted,
            whiteSpace: "nowrap",
          }}
        >
          {fixActive ? "NETWORK" : "tunnel"}
        </div>
      </div>

      {/* Title */}
      <div
        style={{
          position: "absolute",
          top: 50,
          left: "50%",
          transform: "translateX(-50%)",
          fontFamily: FONTS.display,
          fontSize: 44,
          fontWeight: 700,
          color: COLORS.ink,
          textAlign: "center",
          opacity: interpolate(frame, [0, 20], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          zIndex: 10,
        }}
      >
        {phase <= 2
          ? "Local drive: load up the data bus"
          : phase === 3
            ? "Get a BIGGER bus!"
            : phase === 4
              ? "It doesn't fit the tunnel!"
              : "→ Real-time streaming. No bus needed."}
      </div>

      {/* Phase 1-2: Small bus */}
      {phase <= 2 && (
        <div
          style={{
            position: "absolute",
            left: smallBusX,
            top: ROAD_Y - 90,
            transform: `translateX(${overflowShake}px)`,
            zIndex: 5,
          }}
        >
          {/* Bus body */}
          <div
            style={{
              width: 200,
              height: 80,
              borderRadius: 12,
              background: "linear-gradient(180deg, #3a5a8a, #2a3a5a)",
              border: `2px solid ${phase === 2 ? COLORS.danger : COLORS.acquisition}`,
              boxShadow: phase === 2
                ? `0 0 20px ${COLORS.danger}`
                : `0 4px 16px rgba(0,0,0,.5)`,
              position: "relative",
              overflow: "hidden",
            }}
          >
            {/* Windows */}
            {[0, 1, 2].map((w) => (
              <div
                key={w}
                style={{
                  position: "absolute",
                  left: 15 + w * 55,
                  top: 10,
                  width: 40,
                  height: 28,
                  borderRadius: 4,
                  background: "rgba(109,179,255,.15)",
                  border: "1px solid rgba(109,179,255,.3)",
                }}
              />
            ))}
            {/* Wheels */}
            {[0, 1].map((w) => (
              <div
                key={`wheel-${w}`}
                style={{
                  position: "absolute",
                  bottom: -14,
                  left: 25 + w * 120,
                  width: 28,
                  height: 28,
                  borderRadius: "50%",
                  background: "#1a1a2a",
                  border: "3px solid #4a4a6a",
                }}
              />
            ))}
            <div
              style={{
                position: "absolute",
                bottom: 8,
                left: "50%",
                transform: "translateX(-50%)",
                fontFamily: FONTS.mono,
                fontSize: 11,
                color: COLORS.ink,
                fontWeight: 700,
              }}
            >
              LOCAL DRIVE
            </div>
          </div>

          {/* Data blocks stacked on top */}
          {Array.from({ length: loadedBlocks }).map((_, i) => {
            const col = i % 4;
            const row = Math.floor(i / 4);
            const isFalling = phase === 2 && row >= 1;
            const fallOffset = isFalling
              ? interpolate(frame - p1End, [0, 15 + i * 3], [0, 120 + i * 20], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                  easing: Easing.in(Easing.cubic),
                })
              : 0;
            const fallRotate = isFalling
              ? interpolate(frame - p1End, [0, 20], [0, (i % 2 === 0 ? 1 : -1) * 35], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                })
              : 0;

            return (
              <div
                key={`block-${i}`}
                style={{
                  position: "absolute",
                  left: 10 + col * 48,
                  top: -35 - row * 35 + fallOffset,
                  width: 44,
                  height: 28,
                  borderRadius: 5,
                  background: `linear-gradient(135deg, ${COLORS.training}, rgba(255,196,107,.6))`,
                  border: "1px solid rgba(255,196,107,.5)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontFamily: FONTS.mono,
                  fontSize: 9,
                  color: COLORS.bg,
                  fontWeight: 700,
                  zIndex: 6,
                  transform: `rotate(${fallRotate}deg)`,
                  opacity: fallOffset > 100 ? 0 : 1,
                }}
              >
                {TB_BLOCKS[i].label}
              </div>
            );
          })}

          {/* TB counter */}
          <div
            style={{
              position: "absolute",
              left: 210,
              top: 10,
              fontFamily: FONTS.mono,
              fontSize: 22,
              fontWeight: 700,
              color: loadedBlocks > 5 ? COLORS.danger : COLORS.training,
              whiteSpace: "nowrap",
            }}
          >
            {loadedBlocks > 0 && `${loadedBlocks * 5} TB`}
          </div>
        </div>
      )}

      {/* Phase 2: TOO SMALL */}
      {phase === 2 && (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: ROAD_Y + 60,
            transform: "translateX(-50%)",
            fontFamily: FONTS.display,
            fontSize: 52,
            fontWeight: 700,
            color: COLORS.danger,
            textShadow: `0 0 25px ${COLORS.danger}`,
            opacity: tooSmallOpacity,
            zIndex: 10,
          }}
        >
          TOO SMALL! 🚫
        </div>
      )}

      {/* Phase 3-4: Big bus */}
      {bigBusActive && phase <= 4 && (
        <div
          style={{
            position: "absolute",
            left: bigBusX,
            top: ROAD_Y - 160,
            transform: `scale(${bigBusScale}) translateX(${crashShake}px)`,
            transformOrigin: "bottom left",
            zIndex: 5,
          }}
        >
          {/* Big bus body */}
          <div
            style={{
              width: 380,
              height: 150,
              borderRadius: 16,
              background: "linear-gradient(180deg, #5a3a2a, #3a2a1a)",
              border: `3px solid ${phase === 4 ? COLORS.danger : COLORS.training}`,
              boxShadow: phase === 4
                ? `0 0 40px ${COLORS.danger}`
                : `0 6px 24px rgba(0,0,0,.6)`,
              position: "relative",
              overflow: "hidden",
            }}
          >
            {/* Windows */}
            {[0, 1, 2, 3, 4].map((w) => (
              <div
                key={w}
                style={{
                  position: "absolute",
                  left: 15 + w * 70,
                  top: 15,
                  width: 55,
                  height: 40,
                  borderRadius: 6,
                  background: "rgba(255,196,107,.12)",
                  border: "1px solid rgba(255,196,107,.25)",
                }}
              />
            ))}
            {/* Wheels */}
            {[0, 1, 2].map((w) => (
              <div
                key={`bigwheel-${w}`}
                style={{
                  position: "absolute",
                  bottom: -20,
                  left: 30 + w * 140,
                  width: 40,
                  height: 40,
                  borderRadius: "50%",
                  background: "#1a1a2a",
                  border: "4px solid #5a5a7a",
                }}
              />
            ))}
            <div
              style={{
                position: "absolute",
                bottom: 12,
                left: "50%",
                transform: "translateX(-50%)",
                fontFamily: FONTS.mono,
                fontSize: 16,
                color: COLORS.ink,
                fontWeight: 700,
              }}
            >
              BIG LOCAL DRIVE
            </div>
            {/* Stacked data on big bus */}
            {Array.from({ length: 12 }).map((_, i) => (
              <div
                key={`bigblock-${i}`}
                style={{
                  position: "absolute",
                  left: 10 + (i % 6) * 60,
                  top: -28 - Math.floor(i / 6) * 30,
                  width: 52,
                  height: 24,
                  borderRadius: 4,
                  background: `linear-gradient(135deg, ${COLORS.training}, rgba(255,196,107,.6))`,
                  border: "1px solid rgba(255,196,107,.4)",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontFamily: FONTS.mono,
                  fontSize: 8,
                  color: COLORS.bg,
                  fontWeight: 700,
                }}
              >
                {i < 4 ? `cam_0${i + 1}` : ".mp4"}
              </div>
            ))}
          </div>

          {phase === 3 && (
            <div
              style={{
                position: "absolute",
                left: 400,
                top: 20,
                fontFamily: FONTS.display,
                fontSize: 36,
                fontWeight: 700,
                color: COLORS.training,
                whiteSpace: "nowrap",
                opacity: interpolate(frame - p2End, [5, 20], [0, 1], {
                  extrapolateLeft: "clamp",
                  extrapolateRight: "clamp",
                }),
              }}
            >
              300 TB loaded! 💪
            </div>
          )}
        </div>
      )}

      {/* Phase 4: crash flash */}
      {crashFlashOpacity > 0 && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: `rgba(255,107,107,${crashFlashOpacity})`,
            zIndex: 8,
            pointerEvents: "none",
          }}
        />
      )}

      {/* Phase 4: CRASH text */}
      {phase === 4 && (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: ROAD_Y + 60,
            transform: `translateX(-50%) scale(${interpolate(frame - p3End, [18, 28], [2.5, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.out(Easing.cubic),
            })})`,
            fontFamily: FONTS.display,
            fontSize: 60,
            fontWeight: 700,
            color: COLORS.danger,
            textShadow: `0 0 30px ${COLORS.danger}`,
            opacity: interpolate(frame - p3End, [15, 22], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            zIndex: 10,
          }}
        >
          💥 DOESN'T FIT!
        </div>
      )}

      {/* Phase 5: streaming particles instead of bus */}
      {fixActive && (
        <svg
          style={{
            position: "absolute",
            inset: 0,
            width: "100%",
            height: "100%",
            zIndex: 5,
            pointerEvents: "none",
          }}
          viewBox="0 0 1920 1080"
        >
          {/* Streaming line */}
          <line
            x1={200}
            y1={ROAD_Y}
            x2={1700}
            y2={ROAD_Y}
            stroke={COLORS.compute}
            strokeWidth={3}
            opacity={solutionOpacity * 0.4}
            strokeDasharray="8 12"
            strokeDashoffset={-frame * 2}
          />
          {/* Streaming particles */}
          {Array.from({ length: streamParticleCount }).map((_, i) => {
            const speed = 5 + (i % 5) * 1.5;
            const rawX = ((frame - p4End) * speed + i * 80) % 1600 + 200;
            const pOpacity = solutionOpacity * (0.5 + (i % 3) * 0.2);
            const colors = [COLORS.acquisition, COLORS.compute, COLORS.training, COLORS.source];
            return (
              <circle
                key={`stream-${i}`}
                cx={rawX}
                cy={ROAD_Y + Math.sin(frame * 0.1 + i) * 8}
                r={5 + (i % 3) * 2}
                fill={colors[i % 4]}
                opacity={rawX > 1650 ? 0 : pOpacity}
                filter={`drop-shadow(0 0 6px ${colors[i % 4]})`}
              />
            );
          })}
        </svg>
      )}

      {/* Phase 5: Solution text */}
      {fixActive && (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: ROAD_Y + 50,
            transform: "translateX(-50%)",
            fontFamily: FONTS.display,
            fontSize: 40,
            fontWeight: 700,
            color: COLORS.compute,
            textShadow: `0 0 20px ${COLORS.compute}`,
            opacity: solutionOpacity,
            zIndex: 10,
          }}
        >
          ✓ Stream directly to VAST — no bus
        </div>
      )}

      {/* Subtitle explaining the gag */}
      <div
        style={{
          position: "absolute",
          top: 110,
          left: "50%",
          transform: "translateX(-50%)",
          fontFamily: FONTS.mono,
          fontSize: 18,
          color: COLORS.muted,
          opacity: interpolate(frame, [15, 30], [0, 0.8], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          }),
          zIndex: 10,
        }}
      >
        {phase <= 2
          ? "small drive → small bus"
          : phase <= 4
            ? "big drive → big bus → 💥"
            : "real-time network transfer → no drives needed"}
      </div>

      <Sequence from={0} layout="none">
        <Caption text="Local drive = single point of failure." />
      </Sequence>
    </AbsoluteFill>
  );
};
