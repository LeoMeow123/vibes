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
import { KenBurns } from "../components/KenBurns";
import { Caption } from "../components/Caption";

export const Scene11_ScaleReveal: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const textOpacity = interpolate(frame, [fps * 2.5, fps * 3.5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const tbScale = interpolate(frame, [fps * 3, fps * 4], [0.6, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.bezier(0.34, 1.56, 0.64, 1),
  });

  const tbOpacity = interpolate(frame, [fps * 3, fps * 3.5], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill>
      <KenBurns
        src="images/04_scale/full_cart_cage_arrays.png"
        startScale={1}
        endScale={1.1}
        translateY={[20, -20]}
      />

      <div
        style={{
          position: "absolute",
          inset: 0,
          background:
            "linear-gradient(90deg, rgba(10,14,26,.85) 0%, transparent 50%, rgba(10,14,26,.85) 100%)",
          zIndex: 1,
        }}
      />

      <div
        style={{
          position: "absolute",
          left: 100,
          top: "50%",
          transform: "translateY(-50%)",
          zIndex: 2,
        }}
      >
        <div
          style={{
            fontFamily: FONTS.mono,
            fontSize: 20,
            color: COLORS.acquisition,
            letterSpacing: 2,
            marginBottom: 12,
            opacity: textOpacity,
          }}
        >
          TODAY
        </div>
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: 52,
            fontWeight: 700,
            color: COLORS.ink,
            opacity: textOpacity,
          }}
        >
          4 cameras
        </div>

        <div
          style={{
            marginTop: 50,
            fontFamily: FONTS.mono,
            fontSize: 20,
            color: COLORS.training,
            letterSpacing: 2,
            opacity: tbOpacity,
          }}
        >
          THE DREAM
        </div>
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: 52,
            fontWeight: 700,
            color: COLORS.ink,
            opacity: tbOpacity,
          }}
        >
          40 cages
        </div>
        <div
          style={{
            fontFamily: FONTS.display,
            fontSize: 80,
            fontWeight: 700,
            color: COLORS.danger,
            opacity: tbOpacity,
            transform: `scale(${tbScale})`,
            transformOrigin: "left center",
            marginTop: 8,
            textShadow: `0 0 40px ${COLORS.danger}`,
          }}
        >
          ≈ 300 TB
        </div>
      </div>

      <Sequence from={0} layout="none">
        <Caption text="Today: 4 cams · The dream: 40 cages ≈ 300 TB" />
      </Sequence>
    </AbsoluteFill>
  );
};
