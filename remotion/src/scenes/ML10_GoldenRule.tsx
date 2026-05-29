import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  interpolate,
  Easing,
} from "remotion";
import { FONTS, COLORS } from "../styles";
import { Caption } from "../components/Caption";

const RULES = [
  { icon: "📷", text: "Same camera position", delay: 20 },
  { icon: "📐", text: "Same angle", delay: 50 },
  { icon: "💡", text: "Same lighting", delay: 80 },
  { icon: "🖼️", text: "Same background", delay: 110 },
];

export const ML10_GoldenRule: React.FC = () => {
  const frame = useCurrentFrame();

  const titleOpacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const titleScale = interpolate(frame, [0, 15], [0.9, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.back(1.3)),
  });

  const resultDelay = 145;
  const resultOpacity = interpolate(frame, [resultDelay, resultDelay + 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const resultScale = interpolate(frame, [resultDelay, resultDelay + 20], [0.5, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.back(1.5)),
  });

  const glowPulse = Math.sin(frame * 0.06) * 0.4 + 0.6;

  return (
    <AbsoluteFill style={{ background: COLORS.bg }}>
      <div
        style={{
          position: "absolute",
          top: 70,
          left: "50%",
          transform: `translateX(-50%) scale(${titleScale})`,
          fontFamily: FONTS.display,
          fontWeight: 700,
          fontSize: 52,
          color: COLORS.training,
          opacity: titleOpacity,
        }}
      >
        The Golden Rule
      </div>

      {/* Checklist */}
      <div
        style={{
          position: "absolute",
          top: "28%",
          left: "50%",
          transform: "translateX(-50%)",
          display: "flex",
          flexDirection: "column",
          gap: 24,
        }}
      >
        {RULES.map((rule, i) => {
          const checkOp = interpolate(frame, [rule.delay, rule.delay + 15], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const checkScale = interpolate(frame, [rule.delay, rule.delay + 15], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.back(2)),
          });
          const slideX = interpolate(frame, [rule.delay, rule.delay + 15], [30, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.cubic),
          });

          return (
            <div
              key={i}
              style={{
                display: "flex",
                alignItems: "center",
                gap: 20,
                opacity: checkOp,
                transform: `translateX(${slideX}px)`,
              }}
            >
              <div
                style={{
                  fontSize: 36,
                  transform: `scale(${checkScale})`,
                  width: 50,
                  textAlign: "center",
                }}
              >
                ✅
              </div>
              <div style={{ fontSize: 40, width: 50, textAlign: "center" }}>
                {rule.icon}
              </div>
              <div
                style={{
                  fontFamily: FONTS.display,
                  fontSize: 36,
                  fontWeight: 700,
                  color: COLORS.ink,
                }}
              >
                {rule.text}
              </div>
            </div>
          );
        })}
      </div>

      {/* = Happy Model result */}
      <div
        style={{
          position: "absolute",
          top: "72%",
          left: "50%",
          transform: `translateX(-50%) scale(${resultScale})`,
          opacity: resultOpacity,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 12,
        }}
      >
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: 28,
            color: COLORS.muted,
          }}
        >
          =
        </div>
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: 48,
            fontWeight: 700,
            color: COLORS.compute,
            background: `rgba(123,232,138,${0.1 + glowPulse * 0.1})`,
            padding: "16px 50px",
            borderRadius: 24,
            border: `3px solid ${COLORS.compute}`,
            boxShadow: `0 0 ${20 + glowPulse * 20}px rgba(123,232,138,0.3)`,
          }}
        >
          🎯 Happy Model
        </div>
      </div>

      <Caption text="Consistency is everything for pose tracking" />
    </AbsoluteFill>
  );
};
