import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  Easing,
  Img,
  staticFile,
} from "remotion";
import { FONTS, COLORS } from "../styles";
import { Caption } from "../components/Caption";

const CYCLE_STEPS = [
  { label: "Change\nsetup", icon: "🔧", angle: -90 },
  { label: "Label new\nexamples", icon: "🏷️", angle: -18 },
  { label: "Retrain\nmodel", icon: "🧠", angle: 54 },
  { label: "Test\naccuracy", icon: "📊", angle: 126 },
  { label: "Deploy", icon: "🚀", angle: 198 },
];

export const ML11_Retrain: React.FC = () => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const cx = 580;
  const cy = 480;
  const radius = 200;

  const chartOpacity = interpolate(frame, [120, 145], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const chartScale = interpolate(frame, [120, 145], [0.9, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const moreLabelsOpacity = interpolate(frame, [155, 175], [0, 1], {
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
          fontSize: 44,
          color: COLORS.training,
          opacity: titleOpacity,
        }}
      >
        If you MUST change the setup...
      </div>

      {/* Circular retraining cycle */}
      <svg width={1200} height={900} style={{ position: "absolute", left: 0, top: 100 }}>
        {/* Circle path */}
        <circle
          cx={cx}
          cy={cy}
          r={radius}
          fill="none"
          stroke={COLORS.line}
          strokeWidth={3}
          strokeDasharray="8,6"
          opacity={interpolate(frame, [15, 30], [0, 0.5], { extrapolateLeft: "clamp", extrapolateRight: "clamp" })}
        />

        {/* Animated arrow traveling the circle */}
        {(() => {
          const arrowProgress = interpolate(frame, [30, 150], [0, 2], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const arrowAngle = (-90 + arrowProgress * 360) * (Math.PI / 180);
          const ax = cx + Math.cos(arrowAngle) * radius;
          const ay = cy + Math.sin(arrowAngle) * radius;
          const arrowOp = interpolate(frame, [30, 40], [0, 0.8], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          return (
            <circle
              cx={ax}
              cy={ay}
              r={8}
              fill={COLORS.training}
              opacity={arrowOp}
            />
          );
        })()}

        {/* Steps */}
        {CYCLE_STEPS.map((step, i) => {
          const stepDelay = 20 + i * 22;
          const stepOp = interpolate(frame, [stepDelay, stepDelay + 15], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const stepScale = interpolate(frame, [stepDelay, stepDelay + 15], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.back(1.5)),
          });
          const rad = step.angle * (Math.PI / 180);
          const sx = cx + Math.cos(rad) * radius;
          const sy = cy + Math.sin(rad) * radius;
          const lx = cx + Math.cos(rad) * (radius + 70);
          const ly = cy + Math.sin(rad) * (radius + 70);

          return (
            <g key={i} opacity={stepOp}>
              <circle
                cx={sx}
                cy={sy}
                r={28 * stepScale}
                fill={COLORS.bg}
                stroke={COLORS.training}
                strokeWidth={3}
              />
              <text
                x={sx}
                y={sy + 6}
                textAnchor="middle"
                fontSize={24}
              >
                {step.icon}
              </text>
              {step.label.split("\n").map((line, li) => (
                <text
                  key={li}
                  x={lx}
                  y={ly + li * 18 - 6}
                  textAnchor="middle"
                  fill={COLORS.ink}
                  fontFamily={FONTS.mono}
                  fontSize={14}
                >
                  {line}
                </text>
              ))}
            </g>
          );
        })}
      </svg>

      {/* Accuracy chart from slides */}
      <div
        style={{
          position: "absolute",
          right: 140,
          top: "25%",
          transform: `scale(${chartScale})`,
          opacity: chartOpacity,
          borderRadius: 12,
          overflow: "hidden",
          border: `2px solid ${COLORS.line}`,
          background: "white",
        }}
      >
        <Img
          src={staticFile("images/ml_demo/slide11_Content_Placeholder_22.png")}
          style={{ width: 420, height: "auto" }}
        />
      </div>

      {/* More labels text */}
      <div
        style={{
          position: "absolute",
          right: 160,
          top: "62%",
          fontFamily: FONTS.mono,
          fontSize: 22,
          color: COLORS.compute,
          opacity: moreLabelsOpacity,
          textAlign: "center",
          maxWidth: 380,
          lineHeight: 1.5,
        }}
      >
        More labeled frames from the <span style={{ color: COLORS.training, fontWeight: 700 }}>new setup</span>
        {" "}→ model adapts
      </div>

      {/* Sample efficiency chart */}
      <div
        style={{
          position: "absolute",
          right: 160,
          top: "72%",
          transform: `scale(${chartScale})`,
          opacity: moreLabelsOpacity,
          borderRadius: 12,
          overflow: "hidden",
          border: `2px solid ${COLORS.line}`,
          background: "white",
        }}
      >
        <Img
          src={staticFile("images/ml_demo/slide08_Content_Placeholder_4.png")}
          style={{ width: 300, height: "auto" }}
        />
      </div>

      <Caption text="Retraining with new data fixes the distribution shift" />
    </AbsoluteFill>
  );
};
