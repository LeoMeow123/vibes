import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  Easing,
} from "remotion";
import { FONTS, COLORS } from "../styles";
import { Caption } from "../components/Caption";

const LAYERS = [
  { x: 200, label: "Input\nImage", nodes: 6, color: COLORS.muted },
  { x: 480, label: "Conv\nLayer 1", nodes: 8, color: COLORS.acquisition },
  { x: 720, label: "Conv\nLayer 2", nodes: 8, color: COLORS.acquisition },
  { x: 960, label: "Conv\nLayer 3", nodes: 6, color: COLORS.compute },
  { x: 1200, label: "Heatmaps", nodes: 5, color: COLORS.training },
  { x: 1440, label: "Keypoints", nodes: 4, color: COLORS.danger },
];

export const ML05_NeuralNet: React.FC = () => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      <div
        style={{
          position: "absolute",
          top: 50,
          left: "50%",
          transform: "translateX(-50%)",
          fontFamily: FONTS.display,
          fontWeight: 700,
          fontSize: 42,
          color: COLORS.ink,
          opacity: titleOpacity,
        }}
      >
        Inside the neural network
      </div>

      <svg width={1920} height={1080} style={{ position: "absolute" }}>
        {/* Connections between layers */}
        {LAYERS.map((layer, li) => {
          if (li === 0) return null;
          const prev = LAYERS[li - 1];
          const connDelay = 15 + li * 20;
          const connOp = interpolate(frame, [connDelay, connDelay + 15], [0, 0.15], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const lines: React.ReactNode[] = [];
          for (let pi = 0; pi < prev.nodes; pi++) {
            for (let ci = 0; ci < layer.nodes; ci++) {
              const py = 300 + (pi / (prev.nodes - 1)) * 400;
              const cy = 300 + (ci / (layer.nodes - 1)) * 400;
              lines.push(
                <line
                  key={`${li}-${pi}-${ci}`}
                  x1={prev.x + 240}
                  y1={py}
                  x2={layer.x}
                  y2={cy}
                  stroke={layer.color}
                  strokeWidth={1}
                  opacity={connOp}
                />
              );
            }
          }
          return <g key={`conn-${li}`}>{lines}</g>;
        })}

        {/* Nodes */}
        {LAYERS.map((layer, li) => {
          const layerDelay = 10 + li * 20;
          const layerOp = interpolate(frame, [layerDelay, layerDelay + 15], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.cubic),
          });

          const nodes: React.ReactNode[] = [];
          for (let ni = 0; ni < layer.nodes; ni++) {
            const y = 300 + (ni / (layer.nodes - 1)) * 400;
            const pulsePhase = (frame * 0.05 + ni * 0.3 + li * 0.5) % 1;
            const pulse = 1 + Math.sin(pulsePhase * Math.PI * 2) * 0.15;

            const dataFlowDelay = 80 + li * 15 + ni * 3;
            const dataGlow = interpolate(frame, [dataFlowDelay, dataFlowDelay + 10, dataFlowDelay + 20, dataFlowDelay + 30], [0, 1, 1, 0.3], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });

            nodes.push(
              <circle
                key={`node-${li}-${ni}`}
                cx={layer.x + 120}
                cy={y}
                r={14 * pulse}
                fill={layer.color}
                opacity={layerOp * (0.4 + dataGlow * 0.6)}
                stroke="white"
                strokeWidth={dataGlow > 0.5 ? 2 : 0}
              />
            );
          }

          return (
            <g key={`layer-${li}`}>
              {nodes}
              <text
                x={layer.x + 120}
                y={760}
                fill={COLORS.muted}
                fontFamily={FONTS.mono}
                fontSize={16}
                textAnchor="middle"
                opacity={layerOp}
              >
                {layer.label.split("\n").map((line, i) => (
                  <tspan key={i} x={layer.x + 120} dy={i === 0 ? 0 : 18}>
                    {line}
                  </tspan>
                ))}
              </text>
            </g>
          );
        })}

        {/* Data flow arrow */}
        {(() => {
          const arrowOp = interpolate(frame, [60, 75], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const arrowX = interpolate(frame, [80, 160], [200, 1550], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.inOut(Easing.cubic),
          });
          return (
            <circle
              cx={arrowX}
              cy={240}
              r={8}
              fill={COLORS.compute}
              opacity={arrowOp * 0.8}
              filter="url(#glow)"
            />
          );
        })()}

        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="6" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
      </svg>

      {/* Input/Output labels */}
      <div
        style={{
          position: "absolute",
          left: 100,
          top: 250,
          fontFamily: FONTS.mono,
          fontSize: 20,
          color: COLORS.muted,
          opacity: interpolate(frame, [10, 25], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        📷 Frame
      </div>
      <div
        style={{
          position: "absolute",
          right: 140,
          top: 250,
          fontFamily: FONTS.mono,
          fontSize: 20,
          color: COLORS.danger,
          opacity: interpolate(frame, [120, 140], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
        }}
      >
        📍 Keypoints
      </div>

      {/* Key insight */}
      <div
        style={{
          position: "absolute",
          bottom: 140,
          left: "50%",
          transform: "translateX(-50%)",
          fontFamily: FONTS.mono,
          fontSize: 26,
          color: COLORS.acquisition,
          opacity: interpolate(frame, [150, 170], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          textAlign: "center",
        }}
      >
        It learns: "this pixel pattern = nose" — pure pattern matching
      </div>

      <Caption text="The network memorizes pixel patterns, not concepts" />
    </AbsoluteFill>
  );
};
