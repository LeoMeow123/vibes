import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from "remotion";
import { FONTS, COLORS } from "../styles";

interface PipelineNode {
  icon: string;
  label: string;
  meta: string;
  group: "acq" | "train" | "infra";
  x: number;
  y: number;
}

const PIPELINE_NODES: PipelineNode[] = [
  { icon: "🏠", label: "Home cage", meta: "behavioral assay", group: "acq", x: 200, y: 235 },
  { icon: "🎥", label: "Camera(s)", meta: "industrial · IR", group: "acq", x: 200, y: 370 },
  { icon: "💻", label: "Acquisition PC", meta: "encode · 4 cages:1", group: "acq", x: 195, y: 505 },
  { icon: "🗄️", label: "VAST storage", meta: "network · shared", group: "acq", x: 570, y: 505 },
  { icon: "🧹", label: "Dataset curation", meta: "→ model dev", group: "train", x: 940, y: 505 },
  { icon: "🧠", label: "Train & evaluate", meta: "pose · tracking", group: "train", x: 940, y: 650 },
  { icon: "📦", label: "Models", meta: "SLEAP · behaviors", group: "train", x: 680, y: 650 },
  { icon: "⚡", label: "Triton Inference", meta: "NVIDIA · run:ai", group: "infra", x: 410, y: 650 },
  { icon: "🟩", label: "GPU nodes", meta: "Blackwell ×N", group: "infra", x: 400, y: 810 },
];

const EDGES: [number, number][] = [
  [0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 2], [7, 8],
];

const GROUP_LABELS = [
  { text: "DATA ACQUISITION", color: COLORS.acquisition, x: 380, y: 200, showAt: 0 },
  { text: "MODEL TRAINING", color: COLORS.training, x: 1100, y: 555, showAt: 4 },
  { text: "COMPUTE INFRASTRUCTURE", color: COLORS.compute, x: 170, y: 770, showAt: 7 },
];

const GROUP_COLORS = {
  acq: { border: "rgba(91,155,213,.5)", glow: "rgba(109,179,255,.55)" },
  train: { border: "rgba(232,168,87,.5)", glow: "rgba(255,196,107,.5)" },
  infra: { border: "rgba(123,196,127,.5)", glow: "rgba(123,232,138,.5)" },
};

const STEP_DURATION = 27;

export const Scene16_SAAPS: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  const captions = [
    "Home cage — the behavior happens here",
    "Industrial cameras capture 24/7",
    "Acquisition PC encodes at the source",
    "→ straight to VAST network storage",
    "Curate the dataset",
    "Train & evaluate the models",
    "Trained models ready to deploy",
    "Triton Inference Server runs them",
    "Powered by GPU nodes",
    "Home cage → PC → VAST → Triton → GPU nodes",
  ];

  const activeStep = Math.min(
    Math.floor((frame - 18) / STEP_DURATION),
    PIPELINE_NODES.length,
  );

  const currentCaption =
    activeStep >= 0 && activeStep < captions.length
      ? captions[activeStep]
      : activeStep >= captions.length - 1
        ? captions[captions.length - 1]
        : "";

  const captionOpacity = interpolate(
    frame,
    [0, 18, durationInFrames - 12, durationInFrames],
    [0, 1, 1, 0],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  return (
    <AbsoluteFill
      style={{
        background: `
          radial-gradient(1400px 700px at 50% -10%, rgba(91,155,213,.10), transparent 60%),
          radial-gradient(1000px 550px at 80% 110%, rgba(123,196,127,.08), transparent 60%),
          ${COLORS.bg}`,
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundImage:
            "linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px)",
          backgroundSize: "40px 40px",
          pointerEvents: "none",
        }}
      />

      <div
        style={{
          position: "absolute",
          top: 35,
          left: "50%",
          transform: "translateX(-50%)",
          textAlign: "center",
          zIndex: 5,
        }}
      >
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: 40,
            fontWeight: 700,
            color: COLORS.ink,
          }}
        >
          <span style={{ textDecoration: "underline", textUnderlineOffset: 5 }}>S</span>alk{" "}
          <span style={{ textDecoration: "underline", textUnderlineOffset: 5 }}>A</span>I{" "}
          <span style={{ textDecoration: "underline", textUnderlineOffset: 5 }}>A</span>nimal{" "}
          <span style={{ textDecoration: "underline", textUnderlineOffset: 5 }}>P</span>henotyping{" "}
          <span style={{ textDecoration: "underline", textUnderlineOffset: 5 }}>S</span>ystem
        </div>
        <div
          style={{
            fontFamily: FONTS.mono,
            fontSize: 15,
            color: COLORS.muted,
            letterSpacing: 3,
            marginTop: 6,
          }}
        >
          S A A P S — DATA FLOW
        </div>
      </div>

      <svg
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          zIndex: 1,
        }}
        viewBox="0 0 1920 1080"
      >
        <defs>
          <linearGradient id="saapsGrad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor={COLORS.acquisition} />
            <stop offset="100%" stopColor={COLORS.compute} />
          </linearGradient>
        </defs>
        {EDGES.map(([from, to], i) => {
          const edgeStep = from === 7 && to === 2 ? 9 : i;
          const isLit = activeStep >= edgeStep + 1;
          const fromNode = PIPELINE_NODES[from];
          const toNode = PIPELINE_NODES[to];
          return (
            <line
              key={`${from}-${to}`}
              x1={fromNode.x + 80}
              y1={fromNode.y + 40}
              x2={toNode.x + 80}
              y2={toNode.y + 40}
              stroke={isLit ? "url(#saapsGrad)" : COLORS.line}
              strokeWidth={isLit ? 3.5 : 2.5}
              filter={
                isLit
                  ? "drop-shadow(0 0 6px rgba(109,179,255,.6))"
                  : "none"
              }
            />
          );
        })}
      </svg>

      {PIPELINE_NODES.map((node, i) => {
        const isOn = activeStep >= i;
        const nodeFrame = 18 + i * STEP_DURATION;
        const localFrame = frame - nodeFrame;
        const popScale =
          isOn && localFrame >= 0 && localFrame < 15
            ? interpolate(localFrame, [0, 7, 15], [1, 1.08, 1], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              })
            : 1;

        const gc = GROUP_COLORS[node.group];

        return (
          <div
            key={node.label}
            style={{
              position: "absolute",
              left: node.x,
              top: node.y,
              zIndex: 3,
              borderRadius: 16,
              padding: "16px 20px",
              background: "rgba(18,24,40,.92)",
              border: `1.5px solid ${isOn ? gc.border : COLORS.line}`,
              textAlign: "center",
              minWidth: 160,
              boxShadow: isOn
                ? `0 0 0 1.5px ${gc.border}, 0 0 30px ${gc.glow}, 0 6px 22px rgba(0,0,0,.45)`
                : "0 6px 22px rgba(0,0,0,.45)",
              opacity: isOn ? 1 : 0.35,
              transform: `scale(${popScale})`,
            }}
          >
            <div style={{ fontSize: 26, marginBottom: 4 }}>{node.icon}</div>
            <div
              style={{
                fontFamily: FONTS.display,
                fontSize: 18,
                fontWeight: 600,
                color: COLORS.ink,
                lineHeight: 1.2,
              }}
            >
              {node.label}
            </div>
            <div
              style={{
                fontFamily: FONTS.mono,
                fontSize: 13,
                color: COLORS.muted,
                marginTop: 5,
              }}
            >
              {node.meta}
            </div>
          </div>
        );
      })}

      {GROUP_LABELS.map((gl) => {
        const visible = activeStep >= gl.showAt;
        const opacity = visible
          ? interpolate(
              frame - (18 + gl.showAt * STEP_DURATION),
              [0, 15],
              [0, 0.9],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
            )
          : 0;
        return (
          <div
            key={gl.text}
            style={{
              position: "absolute",
              left: gl.x,
              top: gl.y,
              zIndex: 2,
              fontFamily: FONTS.display,
              fontWeight: 700,
              fontSize: 17,
              letterSpacing: 1.5,
              color: gl.color,
              opacity,
            }}
          >
            {gl.text}
          </div>
        );
      })}

      {currentCaption && (
        <div
          style={{
            position: "absolute",
            bottom: 30,
            left: "50%",
            transform: "translateX(-50%)",
            fontFamily: FONTS.mono,
            fontSize: 20,
            color: "#aeb9d6",
            background: "rgba(12,16,28,.8)",
            border: `1px solid ${COLORS.line}`,
            padding: "10px 24px",
            borderRadius: 30,
            zIndex: 5,
            letterSpacing: 0.5,
            opacity: captionOpacity,
            whiteSpace: "nowrap",
          }}
        >
          {currentCaption}
        </div>
      )}
    </AbsoluteFill>
  );
};
