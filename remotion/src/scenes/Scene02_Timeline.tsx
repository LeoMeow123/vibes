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

const BAR_DATA = [
  {
    name: "Fast-mutating models",
    sub: "e.g. acute / inducible",
    widthPct: 10,
    label: "weeks",
    gradient: `linear-gradient(90deg, #4a90d9, ${COLORS.acquisition})`,
    delay: 0,
  },
  {
    name: "Prior home-cage studies",
    sub: "published norm",
    widthPct: 17,
    label: "1–2 mo",
    gradient: "linear-gradient(90deg, #5aa0c0, #8fd0e8)",
    delay: 30,
  },
  {
    name: "Alzheimer's disease",
    sub: "what we need",
    widthPct: 100,
    label: "up to 24 months",
    gradient: `linear-gradient(90deg, ${COLORS.danger}, ${COLORS.training})`,
    delay: 63,
  },
];

const AXIS = ["0", "6 mo", "12 mo", "18 mo", "24 mo"];

const Bar: React.FC<{
  data: (typeof BAR_DATA)[number];
  frame: number;
}> = ({ data, frame }) => {
  const localFrame = frame - data.delay;

  const rowOpacity = interpolate(localFrame, [0, 18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const rowSlide = interpolate(localFrame, [0, 18], [-30, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const barWidth = interpolate(localFrame, [5, 38], [0, data.widthPct], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.2, 0.8, 0.2, 1),
  });

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        marginBottom: 40,
        opacity: rowOpacity,
        transform: `translateX(${rowSlide}px)`,
      }}
    >
      <div
        style={{
          width: 320,
          textAlign: "right",
          paddingRight: 30,
        }}
      >
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: 24,
            fontWeight: 600,
            color: COLORS.ink,
          }}
        >
          {data.name}
        </div>
        <div
          style={{
            fontFamily: FONTS.mono,
            fontSize: 16,
            color: COLORS.muted,
            marginTop: 2,
          }}
        >
          {data.sub}
        </div>
      </div>
      <div
        style={{
          flex: 1,
          height: 48,
          background: "rgba(255,255,255,.04)",
          borderRadius: 10,
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${barWidth}%`,
            background: data.gradient,
            borderRadius: 10,
            display: "flex",
            alignItems: "center",
            justifyContent: "flex-end",
            paddingRight: 16,
            fontFamily: FONTS.mono,
            fontSize: 18,
            fontWeight: 700,
            color: COLORS.bg,
          }}
        >
          {barWidth > 5 ? data.label : ""}
        </div>
      </div>
    </div>
  );
};

export const Scene02_Timeline: React.FC = () => {
  const frame = useCurrentFrame();

  const punchOpacity = interpolate(frame, [130, 148], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(1100px 600px at 30% 0%, rgba(232,90,90,.10), transparent 60%), ${COLORS.bg}`,
        padding: "80px 120px",
        fontFamily: FONTS.display,
      }}
    >
      <div
        style={{
          fontSize: 44,
          fontWeight: 700,
          color: COLORS.ink,
          marginBottom: 8,
        }}
      >
        Why long-term home-cage monitoring is rare
      </div>
      <div
        style={{
          fontFamily: FONTS.mono,
          color: COLORS.muted,
          fontSize: 17,
          letterSpacing: 3,
          marginBottom: 70,
        }}
      >
        DISEASE TIMELINE vs. TYPICAL STUDY LENGTH
      </div>

      {BAR_DATA.map((d) => (
        <Bar key={d.name} data={d} frame={frame} />
      ))}

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginTop: 12,
          marginLeft: 320,
          fontFamily: FONTS.mono,
          fontSize: 15,
          color: "#6b769a",
        }}
      >
        {AXIS.map((a) => (
          <span key={a}>{a}</span>
        ))}
      </div>

      <div
        style={{
          position: "absolute",
          bottom: 120,
          left: 120,
          fontSize: 32,
          fontWeight: 700,
          color: COLORS.training,
          opacity: punchOpacity,
        }}
      >
        One cage, 24 months → a single n. Not enough.
      </div>

      <Sequence from={0} layout="none">
        <Caption text="AD ≈ 24 months · prior studies ≈ 1–2 mo" />
      </Sequence>
    </AbsoluteFill>
  );
};
