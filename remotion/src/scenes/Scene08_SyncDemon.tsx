import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  Easing,
  Sequence,
} from "remotion";
import { FONTS, COLORS } from "../styles";
import { Caption } from "../components/Caption";

interface WindowData {
  id: string;
  x: number;
  y: number;
  appearFrame: number;
  freezeFrame: number | null;
  fpsText: string;
  frozenFps?: string;
}

const WINDOWS: WindowData[] = [
  { id: "cam_01", x: 140, y: 200, appearFrame: 15, freezeFrame: null, fpsText: "50 fps" },
  { id: "cam_02", x: 580, y: 250, appearFrame: 36, freezeFrame: 138, fpsText: "50 fps", frozenFps: "38 fps" },
  { id: "cam_03", x: 340, y: 500, appearFrame: 57, freezeFrame: 99, fpsText: "— fps" },
  { id: "cam_04", x: 820, y: 520, appearFrame: 75, freezeFrame: 114, fpsText: "— fps" },
];

const RecorderWindow: React.FC<{
  data: WindowData;
  frame: number;
}> = ({ data, frame }) => {
  const localFrame = frame - data.appearFrame;
  const isFrozen = data.freezeFrame !== null && frame >= data.freezeFrame;

  const scale = interpolate(localFrame, [0, 12], [0.88, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.34, 1.56, 0.64, 1),
  });

  const opacity = interpolate(localFrame, [0, 8], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  if (localFrame < 0) return null;

  const displayFps = isFrozen && data.frozenFps ? data.frozenFps : data.fpsText;
  const fpsColor = isFrozen ? COLORS.danger : COLORS.compute;
  const borderColor = isFrozen ? "rgba(255,107,107,.5)" : COLORS.line;

  const glitchOffset = isFrozen
    ? Math.sin(frame * 2.7) * 1.5
    : 0;

  return (
    <div
      style={{
        position: "absolute",
        left: data.x,
        top: data.y,
        width: 420,
        height: 250,
        borderRadius: 14,
        background: "#141826",
        border: `1.5px solid ${borderColor}`,
        boxShadow: "0 14px 40px rgba(0,0,0,.55)",
        opacity,
        transform: `scale(${scale}) translateY(${glitchOffset}px)`,
        overflow: "hidden",
        filter: isFrozen ? "grayscale(.5) brightness(.75)" : "none",
      }}
    >
      <div
        style={{
          height: 40,
          background: "#1d2335",
          display: "flex",
          alignItems: "center",
          padding: "0 16px",
          gap: 8,
        }}
      >
        <div style={{ width: 13, height: 13, borderRadius: "50%", background: "#ff5f57" }} />
        <div style={{ width: 13, height: 13, borderRadius: "50%", background: "#febc2e" }} />
        <div style={{ width: 13, height: 13, borderRadius: "50%", background: "#28c840" }} />
        <span
          style={{
            marginLeft: 10,
            fontFamily: FONTS.mono,
            fontSize: 15,
            color: "#aab4d0",
          }}
        >
          recorder · {data.id}
        </span>
      </div>

      <div style={{ padding: 18 }}>
        <div style={{ fontFamily: FONTS.mono, fontSize: 15, color: COLORS.muted }}>
          capture rate
        </div>
        <div
          style={{
            fontFamily: FONTS.mono,
            fontSize: 42,
            fontWeight: 700,
            color: fpsColor,
            marginTop: 4,
          }}
        >
          {displayFps}
        </div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 9,
            marginTop: 16,
            fontFamily: FONTS.mono,
            fontSize: 16,
            color: COLORS.ink,
          }}
        >
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: "50%",
              background: isFrozen ? COLORS.danger : COLORS.compute,
            }}
          />
          REC 00:00:{localFrame < 30 ? "00" : "01"}
        </div>
      </div>

      {isFrozen && (
        <>
          <div
            style={{
              position: "absolute",
              inset: "40px 0 0 0",
              background:
                "repeating-linear-gradient(0deg, rgba(255,80,80,.08) 0px, rgba(255,80,80,.08) 2px, transparent 2px, transparent 5px)",
              pointerEvents: "none",
            }}
          />
          <div
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: "translate(-50%,-50%) rotate(-8deg)",
              fontFamily: FONTS.display,
              fontWeight: 700,
              fontSize: 30,
              color: COLORS.danger,
              border: `3px solid ${COLORS.danger}`,
              padding: "6px 18px",
              borderRadius: 8,
            }}
          >
            FROZEN
          </div>
        </>
      )}
    </div>
  );
};

export const Scene08_SyncDemon: React.FC = () => {
  const frame = useCurrentFrame();

  const demonOpacity = interpolate(frame, [156, 175], [0, 0.9], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(900px 550px at 70% 20%, rgba(180,60,90,.12), transparent 60%), ${COLORS.bg}`,
      }}
    >
      <div
        style={{
          position: "absolute",
          top: 50,
          left: 80,
          fontFamily: FONTS.display,
          fontSize: 38,
          fontWeight: 700,
          color: COLORS.ink,
          zIndex: 6,
        }}
      >
        Open them all at once…
      </div>
      <div
        style={{
          position: "absolute",
          top: 100,
          left: 80,
          fontFamily: FONTS.mono,
          fontSize: 16,
          color: COLORS.muted,
          letterSpacing: 3,
          zIndex: 6,
        }}
      >
        4 RECORDERS · 1 MACHINE
      </div>

      {WINDOWS.map((w) => (
        <RecorderWindow key={w.id} data={w} frame={frame} />
      ))}

      <div
        style={{
          position: "absolute",
          right: 80,
          bottom: 100,
          fontSize: 160,
          opacity: demonOpacity,
          filter: "drop-shadow(0 0 30px rgba(255,70,90,.6))",
          zIndex: 2,
        }}
      >
        👹
      </div>

      <Sequence from={0} layout="none">
        <Caption text="The Sync Demon appears." />
      </Sequence>
    </AbsoluteFill>
  );
};
