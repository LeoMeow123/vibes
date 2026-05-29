import React from "react";
import {
  AbsoluteFill,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  Easing,
  Img,
  staticFile,
} from "remotion";
import { FONTS, COLORS } from "../styles";

const IMG_ASPECT = 836 / 1266;
const IMG_W = 1080 * IMG_ASPECT;
const IMG_LEFT = (1920 - IMG_W) / 2;

const pct = (xPct: number, yPct: number) => ({
  x: IMG_LEFT + xPct * IMG_W,
  y: yPct * 1080,
});

const BLDG1 = pct(0.24, 0.88);
const BLDG5_LEE = pct(0.33, 0.15);
const BLDG5_TALMO = pct(0.28, 0.23);

const NORTH_TOP = pct(0.75, 0.18);
const NORTH_MID = pct(0.80, 0.42);
const NORTH_BOT = pct(0.72, 0.65);
const SOUTH_MID = pct(0.30, 0.50);
const CENTER_POOL = pct(0.52, 0.12);
const BLDG9 = pct(0.68, 0.92);

const TALMO_PCS = [
  { label: "Acq PC 1", offset: { x: -140, y: -20 } },
  { label: "Acq PC 2", offset: { x: -150, y: 40 } },
  { label: "VAST NAS", offset: { x: -80, y: 80 } },
  { label: "Triton 1", offset: { x: 50, y: 85 } },
  { label: "Triton 2", offset: { x: 140, y: 45 } },
  { label: "Curation", offset: { x: 140, y: -15 } },
  { label: "Dashboard", offset: { x: 50, y: -55 } },
];

const NUM_FREEWAY_CARS = 70;
const NUM_LANES = 6;

const SALK_ROUTES: { from: { x: number; y: number }; to: { x: number; y: number }; particles: number }[] = [
  { from: NORTH_TOP, to: NORTH_MID, particles: 3 },
  { from: NORTH_MID, to: NORTH_BOT, particles: 2 },
  { from: NORTH_MID, to: CENTER_POOL, particles: 2 },
  { from: NORTH_BOT, to: BLDG9, particles: 2 },
  { from: SOUTH_MID, to: NORTH_MID, particles: 1 },
  { from: CENTER_POOL, to: NORTH_TOP, particles: 2 },
];

// Explosion routes: data floods EVERY underground cable across campus
const EXPLOSION_ROUTES: { from: { x: number; y: number }; to: { x: number; y: number } }[] = [
  // From freeway midpoint outward to all corners
  { from: pct(0.26, 0.55), to: pct(0.10, 0.20) },
  { from: pct(0.26, 0.55), to: pct(0.15, 0.80) },
  { from: pct(0.26, 0.55), to: pct(0.50, 0.95) },
  { from: pct(0.26, 0.55), to: pct(0.85, 0.30) },
  { from: pct(0.26, 0.55), to: pct(0.90, 0.70) },
  { from: pct(0.26, 0.55), to: pct(0.65, 0.10) },
  { from: pct(0.26, 0.55), to: pct(0.45, 0.40) },
  // Cross-campus underground lines
  { from: BLDG1, to: BLDG9 },
  { from: BLDG5_TALMO, to: NORTH_TOP },
  { from: BLDG5_TALMO, to: NORTH_BOT },
  { from: BLDG1, to: pct(0.60, 0.75) },
  { from: BLDG5_LEE, to: pct(0.70, 0.10) },
  { from: pct(0.50, 0.50), to: pct(0.80, 0.85) },
  { from: pct(0.40, 0.70), to: pct(0.10, 0.50) },
  { from: pct(0.55, 0.30), to: pct(0.90, 0.50) },
];

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

const bezierPoint = (
  p0: { x: number; y: number },
  cp: { x: number; y: number },
  p1: { x: number; y: number },
  t: number,
) => ({
  x: (1 - t) * (1 - t) * p0.x + 2 * (1 - t) * t * cp.x + t * t * p1.x,
  y: (1 - t) * (1 - t) * p0.y + 2 * (1 - t) * t * cp.y + t * t * p1.y,
});

export const Scene13_Freeway: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Extended 15s timeline:
  // 0-4s:   Daytime — Lee Lab GPU heat source glowing
  // 4-6s:   Night transition, 3AM clock
  // 6-8s:   Freeway ramps up from Bldg 1 to Talmo Lab
  // 8-11s:  PC nodes reveal, Salk traffic appears
  // 11-12.5s: Contrast label
  // 12.5-15s: 300 TB EXPLOSION — data floods entire campus

  const nightProgress = interpolate(frame, [fps * 4, fps * 6], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.cubic),
  });

  const mapBrightness = lerp(0.9, 0.2, nightProgress);

  const heatIntensity = interpolate(frame, [fps * 0.5, fps * 3], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const heatFade = interpolate(nightProgress, [0, 0.5], [1, 0.12], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const heatPulse = 0.7 + Math.sin(frame * 0.12) * 0.3;

  const freewayStart = fps * 6;
  const freewayActive = frame >= freewayStart;
  const freewayRamp = interpolate(frame, [freewayStart, freewayStart + fps * 2], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });

  const clockOpacity = interpolate(frame, [fps * 4.5, fps * 5, fps * 7, fps * 7.5], [0, 1, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const pcRevealStart = fps * 8;

  const contrastLabelOpacity = interpolate(frame, [fps * 11, fps * 12], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const salkTrafficOpacity = interpolate(frame, [fps * 8, fps * 9], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Explosion phase: 300 TB overwhelms the entire campus
  const explosionStart = fps * 12.5;
  const explosionActive = frame >= explosionStart;
  const explosionRamp = interpolate(frame, [explosionStart, explosionStart + fps * 1], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const explosionShake = explosionActive
    ? Math.sin(frame * 1.5) * 4 * interpolate(frame, [explosionStart, explosionStart + 15], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 0;
  const explosionFlash = interpolate(frame, [explosionStart, explosionStart + 8, explosionStart + 20], [0, 0.4, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const captionTexts = [
    { text: "Lee Lab · 5th floor · 8× Blackwell GPUs 🔥", start: 0, end: fps * 4 },
    { text: "3:00 AM — the data transfer begins", start: fps * 4.5, end: fps * 7 },
    { text: "Building 1 (EBS) → Talmo Lab — like a freeway at night", start: fps * 7, end: fps * 11 },
    { text: "Our project alone ≫ entire Salk data transfer", start: fps * 11, end: fps * 12.5 },
    { text: "300 TB → the entire Salk underground explodes 💥", start: fps * 12.5, end: fps * 15 },
  ];

  const currentCaption = captionTexts.find(
    (c) => frame >= c.start && frame < c.end,
  );

  const captionOpacity = currentCaption
    ? Math.min(
        interpolate(frame, [currentCaption.start, currentCaption.start + 12], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        }),
        interpolate(frame, [currentCaption.end - 10, currentCaption.end], [1, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        }),
      )
    : 0;

  return (
    <AbsoluteFill style={{ background: "#020510", transform: `translate(${explosionShake}px, ${explosionShake * 0.6}px)` }}>
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          justifyContent: "center",
          overflow: "hidden",
        }}
      >
        <Img
          src={staticFile("images/05_salk/salk_aerial_map.png")}
          style={{
            height: "100%",
            objectFit: "cover",
            filter: `brightness(${mapBrightness}) saturate(${lerp(0.9, 0.4, nightProgress)}) contrast(1.05)`,
          }}
        />
      </div>

      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(120% 80% at 50% 40%, transparent 30%, rgba(2,5,12,${lerp(0.4, 0.92, nightProgress)}) 100%)`,
          zIndex: 2,
          pointerEvents: "none",
        }}
      />

      {nightProgress > 0.5 && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: `linear-gradient(rgba(2,5,16,${nightProgress * 0.5}), rgba(2,5,16,${nightProgress * 0.65}))`,
            zIndex: 2,
            pointerEvents: "none",
          }}
        />
      )}

      <div
        style={{
          position: "absolute",
          left: BLDG5_LEE.x - 100,
          top: BLDG5_LEE.y - 100,
          width: 200,
          height: 200,
          borderRadius: "50%",
          background: `radial-gradient(circle, rgba(255,60,20,${heatIntensity * heatFade * heatPulse * 0.8}), rgba(255,120,40,${heatIntensity * heatFade * 0.4}), transparent 70%)`,
          boxShadow: `0 0 ${heatIntensity * heatFade * 100}px rgba(255,80,30,${heatIntensity * heatFade * 0.7})`,
          zIndex: 3,
          pointerEvents: "none",
          transform: `scale(${1 + heatPulse * 0.4})`,
        }}
      />

      {heatIntensity > 0.3 && heatFade > 0.3 && (
        <div
          style={{
            position: "absolute",
            left: BLDG5_LEE.x + 40,
            top: BLDG5_LEE.y - 30,
            zIndex: 5,
            opacity: heatFade,
          }}
        >
          <div
            style={{
              fontFamily: FONTS.mono,
              fontSize: 16,
              fontWeight: 700,
              color: "#ff8833",
              textShadow: "0 0 12px rgba(255,100,40,.9)",
              whiteSpace: "nowrap",
            }}
          >
            Lee Lab · 5th floor
          </div>
          <div
            style={{
              fontFamily: FONTS.mono,
              fontSize: 14,
              color: "#ffbb66",
              textShadow: "0 0 10px rgba(255,150,60,.7)",
              marginTop: 4,
            }}
          >
            8× Blackwell GPU 🔥
          </div>
        </div>
      )}

      {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => {
        const angle = (i / 8) * Math.PI * 2 + frame * 0.025;
        const radius = 35 + Math.sin(frame * 0.06 + i) * 10;
        const shimmerOpacity = heatIntensity * heatFade * (0.4 + Math.sin(frame * 0.15 + i * 1.5) * 0.25);
        return (
          <div
            key={`gpu-${i}`}
            style={{
              position: "absolute",
              left: BLDG5_LEE.x + Math.cos(angle) * radius - 7,
              top: BLDG5_LEE.y + Math.sin(angle) * radius - 7,
              width: 14,
              height: 14,
              borderRadius: 3,
              background: `rgba(255,${80 + i * 18},20,${shimmerOpacity})`,
              boxShadow: `0 0 10px rgba(255,80,30,${shimmerOpacity})`,
              zIndex: 4,
            }}
          />
        );
      })}

      {freewayActive && (
        <div
          style={{
            position: "absolute",
            left: BLDG1.x - 10,
            top: BLDG1.y - 10,
            width: 20,
            height: 20,
            borderRadius: "50%",
            background: `radial-gradient(circle, #fff, ${COLORS.source})`,
            boxShadow: `0 0 25px ${COLORS.source}, 0 0 60px rgba(255,138,60,.7)`,
            zIndex: 5,
            opacity: interpolate(frame, [freewayStart, freewayStart + 15], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        />
      )}

      {freewayActive && (
        <div
          style={{
            position: "absolute",
            left: BLDG1.x - 90,
            top: BLDG1.y + 18,
            fontFamily: FONTS.mono,
            fontSize: 15,
            fontWeight: 700,
            color: COLORS.source,
            textShadow: `0 0 10px rgba(255,138,60,.7)`,
            zIndex: 5,
            opacity: interpolate(frame, [freewayStart, freewayStart + 15], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            whiteSpace: "nowrap",
          }}
        >
          Bldg 1 · EBS 🐭
        </div>
      )}

      {freewayActive && (
        <div
          style={{
            position: "absolute",
            left: Math.min(BLDG1.x, BLDG5_TALMO.x) - 60,
            top: Math.min(BLDG5_TALMO.y, BLDG5_LEE.y) - 20,
            width: Math.abs(BLDG1.x - BLDG5_TALMO.x) + 200,
            height: BLDG1.y - BLDG5_TALMO.y + 80,
            background: `radial-gradient(ellipse at 50% 60%, rgba(109,179,255,${freewayRamp * 0.06}), transparent 70%)`,
            zIndex: 3,
            pointerEvents: "none",
            filter: "blur(30px)",
          }}
        />
      )}

      <svg
        style={{ position: "absolute", inset: 0, width: "100%", height: "100%", zIndex: 4, pointerEvents: "none" }}
        viewBox="0 0 1920 1080"
      >
        {freewayActive &&
          Array.from({ length: NUM_LANES }).map((_, i) => {
            const laneSpread = (i - (NUM_LANES - 1) / 2) * 18;
            const trailOpacity = interpolate(
              frame,
              [freewayStart + 10, freewayStart + 35],
              [0, 0.25 + (i === 2 || i === 3 ? 0.1 : 0)],
              { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
            );
            const cpX = (BLDG1.x + BLDG5_TALMO.x) / 2 - 50 + laneSpread * 0.5;
            const cpY = (BLDG1.y + BLDG5_TALMO.y) / 2 + laneSpread;
            return (
              <path
                key={`lane-${i}`}
                d={`M ${BLDG1.x + laneSpread * 0.3} ${BLDG1.y} Q ${cpX} ${cpY} ${BLDG5_TALMO.x + laneSpread * 0.3} ${BLDG5_TALMO.y}`}
                fill="none"
                stroke={COLORS.acquisition}
                strokeWidth={1.2}
                opacity={trailOpacity * freewayRamp}
                strokeDasharray="4 10"
              />
            );
          })}

        {freewayActive &&
          Array.from({ length: NUM_FREEWAY_CARS }).map((_, i) => {
            const localFrame = frame - freewayStart - i * 1.8;
            if (localFrame < 0) return null;

            const speed = 0.006 + (i % 9) * 0.0015;
            const rawT = (localFrame * speed) % 1;

            const lane = i % NUM_LANES;
            const laneSpread = (lane - (NUM_LANES - 1) / 2) * 18;

            const cpX = (BLDG1.x + BLDG5_TALMO.x) / 2 - 50 + laneSpread * 0.5 + ((i * 13) % 20 - 10);
            const cpY = (BLDG1.y + BLDG5_TALMO.y) / 2 + laneSpread;

            const fromPt = { x: BLDG1.x + laneSpread * 0.3, y: BLDG1.y };
            const toPt = { x: BLDG5_TALMO.x + laneSpread * 0.3, y: BLDG5_TALMO.y };

            const pt = bezierPoint(fromPt, { x: cpX, y: cpY }, toPt, rawT);

            const colorIdx = i % 4;
            const color = colorIdx === 0 ? COLORS.acquisition
              : colorIdx === 1 ? COLORS.compute
              : colorIdx === 2 ? COLORS.source
              : "#b088ff";
            const brightness = 0.6 + (i % 4) * 0.1;
            const size = 4 + (i % 4) * 1.5;

            const trailLen = 0.08;
            const trailPts: { x: number; y: number }[] = [];
            for (let s = 0; s <= 1; s += 0.015) {
              const tt = rawT - trailLen * s;
              if (tt < 0) break;
              trailPts.push(bezierPoint(fromPt, { x: cpX, y: cpY }, toPt, tt));
            }

            return (
              <React.Fragment key={`car-${i}`}>
                {trailPts.length > 1 && (
                  <polyline
                    points={trailPts.map((p) => `${p.x},${p.y}`).join(" ")}
                    fill="none"
                    stroke={color}
                    strokeWidth={2}
                    opacity={brightness * 0.35 * freewayRamp}
                  />
                )}
                <circle
                  cx={pt.x}
                  cy={pt.y}
                  r={size / 2}
                  fill={color}
                  opacity={brightness * freewayRamp}
                  filter={`drop-shadow(0 0 ${size + 2}px ${color})`}
                />
              </React.Fragment>
            );
          })}

        {frame >= pcRevealStart &&
          TALMO_PCS.map((pc, i) => {
            const pcFrame = frame - pcRevealStart - i * 7;
            const pcOpacity = interpolate(pcFrame, [0, 15], [0, 0.85], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.out(Easing.cubic),
            });
            if (pcFrame < 0) return null;

            const px = BLDG5_TALMO.x + pc.offset.x;
            const py = BLDG5_TALMO.y + pc.offset.y;
            const pulse = 0.6 + Math.sin(frame * 0.1 + i * 1.2) * 0.4;

            return (
              <React.Fragment key={`pc-${i}`}>
                <line
                  x1={BLDG5_TALMO.x}
                  y1={BLDG5_TALMO.y}
                  x2={px}
                  y2={py}
                  stroke={COLORS.compute}
                  strokeWidth={2}
                  opacity={pcOpacity * 0.5}
                  filter={`drop-shadow(0 0 5px ${COLORS.compute})`}
                />
                <circle cx={px} cy={py} r={9} fill={COLORS.bg} stroke={COLORS.compute} strokeWidth={1.5} opacity={pcOpacity}
                  filter={`drop-shadow(0 0 8px rgba(123,232,138,${pulse}))`}
                />
                <circle cx={px} cy={py} r={3.5} fill={COLORS.compute} opacity={pcOpacity * pulse} />
              </React.Fragment>
            );
          })}

        {salkTrafficOpacity > 0 &&
          SALK_ROUTES.map((route, ri) => {
            const dashAnim = frame * 0.3 + ri * 10;
            return (
              <React.Fragment key={`salk-route-${ri}`}>
                <line
                  x1={route.from.x}
                  y1={route.from.y}
                  x2={route.to.x}
                  y2={route.to.y}
                  stroke="#ffffff"
                  strokeWidth={1.5}
                  opacity={0.2 * salkTrafficOpacity}
                />
                <line
                  x1={route.from.x}
                  y1={route.from.y}
                  x2={route.to.x}
                  y2={route.to.y}
                  stroke="#ffffff"
                  strokeWidth={2}
                  opacity={0.35 * salkTrafficOpacity}
                  strokeDasharray="4 18"
                  strokeDashoffset={-dashAnim}
                />
                {Array.from({ length: route.particles }).map((_, pi) => {
                  const speed = 0.004 + pi * 0.002;
                  const dimFrame = frame - fps * 5 - ri * 8 - pi * 15;
                  if (dimFrame < 0) return null;
                  const rawT = (dimFrame * speed) % 1;
                  return (
                    <circle
                      key={`salk-p-${ri}-${pi}`}
                      cx={lerp(route.from.x, route.to.x, rawT)}
                      cy={lerp(route.from.y, route.to.y, rawT)}
                      r={2.5}
                      fill="#ffffff"
                      opacity={0.4 * salkTrafficOpacity}
                    />
                  );
                })}
              </React.Fragment>
            );
          })}

        {/* EXPLOSION: data floods every underground cable */}
        {explosionActive &&
          EXPLOSION_ROUTES.map((route, ri) => {
            const routeDelay = ri * 2;
            const localFrame = (frame - explosionStart - routeDelay);
            if (localFrame < 0) return null;
            const lineOpacity = interpolate(localFrame, [0, 12], [0, 0.6], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            const dashAnim = localFrame * 3 + ri * 20;
            const colors = [COLORS.acquisition, COLORS.compute, COLORS.source, "#b088ff", COLORS.training];
            const color = colors[ri % colors.length];

            return (
              <React.Fragment key={`exp-route-${ri}`}>
                <line
                  x1={route.from.x}
                  y1={route.from.y}
                  x2={route.to.x}
                  y2={route.to.y}
                  stroke={color}
                  strokeWidth={2.5}
                  opacity={lineOpacity * 0.4}
                  filter={`drop-shadow(0 0 8px ${color})`}
                />
                <line
                  x1={route.from.x}
                  y1={route.from.y}
                  x2={route.to.x}
                  y2={route.to.y}
                  stroke={color}
                  strokeWidth={3}
                  opacity={lineOpacity * 0.7}
                  strokeDasharray="6 10"
                  strokeDashoffset={-dashAnim}
                  filter={`drop-shadow(0 0 12px ${color})`}
                />
                {/* Particles racing along explosion routes */}
                {Array.from({ length: 4 }).map((_, pi) => {
                  const pSpeed = 0.008 + pi * 0.003;
                  const pFrame = localFrame - pi * 6;
                  if (pFrame < 0) return null;
                  const pT = (pFrame * pSpeed) % 1;
                  return (
                    <circle
                      key={`exp-p-${ri}-${pi}`}
                      cx={lerp(route.from.x, route.to.x, pT)}
                      cy={lerp(route.from.y, route.to.y, pT)}
                      r={4 + (pi % 2) * 2}
                      fill={color}
                      opacity={lineOpacity * 0.8}
                      filter={`drop-shadow(0 0 8px ${color})`}
                    />
                  );
                })}
              </React.Fragment>
            );
          })}

        {/* Explosion burst rings radiating from freeway midpoint */}
        {explosionActive &&
          [0, 1, 2].map((ring) => {
            const ringFrame = frame - explosionStart - ring * 10;
            if (ringFrame < 0) return null;
            const ringRadius = interpolate(ringFrame, [0, 40], [20, 500], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.out(Easing.cubic),
            });
            const ringOpacity = interpolate(ringFrame, [0, 10, 40], [0, 0.5, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            const midX = (BLDG1.x + BLDG5_TALMO.x) / 2;
            const midY = (BLDG1.y + BLDG5_TALMO.y) / 2;
            return (
              <circle
                key={`burst-${ring}`}
                cx={midX}
                cy={midY}
                r={ringRadius}
                fill="none"
                stroke={COLORS.acquisition}
                strokeWidth={2}
                opacity={ringOpacity}
                filter={`drop-shadow(0 0 15px ${COLORS.acquisition})`}
              />
            );
          })}
      </svg>

      {frame >= pcRevealStart &&
        TALMO_PCS.map((pc, i) => {
          const pcFrame = frame - pcRevealStart - i * 7;
          const pcOpacity = interpolate(pcFrame, [0, 15], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          if (pcFrame < 0) return null;

          return (
            <div
              key={`pc-label-${i}`}
              style={{
                position: "absolute",
                left: BLDG5_TALMO.x + pc.offset.x - 35,
                top: BLDG5_TALMO.y + pc.offset.y + 14,
                fontFamily: FONTS.mono,
                fontSize: 11,
                color: COLORS.compute,
                opacity: pcOpacity * 0.85,
                whiteSpace: "nowrap",
                textShadow: `0 0 8px rgba(123,232,138,.6)`,
                zIndex: 6,
              }}
            >
              {pc.label}
            </div>
          );
        })}

      {nightProgress > 0.3 && (
        <div
          style={{
            position: "absolute",
            left: BLDG5_TALMO.x + 40,
            top: BLDG5_TALMO.y - 12,
            fontFamily: FONTS.mono,
            fontSize: 15,
            fontWeight: 700,
            color: COLORS.compute,
            textShadow: `0 0 12px ${COLORS.compute}`,
            opacity: interpolate(nightProgress, [0.3, 0.7], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            zIndex: 6,
            whiteSpace: "nowrap",
          }}
        >
          Talmo Lab · 3rd floor
        </div>
      )}

      {salkTrafficOpacity > 0 && (
        <div
          style={{
            position: "absolute",
            right: IMG_LEFT + IMG_W * 0.05,
            top: NORTH_MID.y - 30,
            fontFamily: FONTS.mono,
            fontSize: 12,
            color: "rgba(255,255,255,.35)",
            opacity: salkTrafficOpacity,
            zIndex: 6,
            whiteSpace: "nowrap",
            textAlign: "right",
          }}
        >
          normal Salk traffic
        </div>
      )}

      <div
        style={{
          position: "absolute",
          top: 30,
          right: 60,
          fontFamily: FONTS.mono,
          fontSize: 52,
          fontWeight: 700,
          color: nightProgress > 0.5 ? "#3a5a8a" : COLORS.ink,
          textShadow: nightProgress > 0.5 ? "0 0 25px rgba(58,90,138,.5)" : "none",
          opacity: clockOpacity,
          zIndex: 8,
          letterSpacing: 3,
        }}
      >
        3:00 AM
      </div>

      {contrastLabelOpacity > 0 && (
        <div
          style={{
            position: "absolute",
            right: 60,
            bottom: 110,
            textAlign: "right",
            zIndex: 8,
            opacity: contrastLabelOpacity,
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 12, marginBottom: 14 }}>
            <div
              style={{
                width: 260,
                height: 10,
                borderRadius: 5,
                background: `linear-gradient(90deg, ${COLORS.source}, ${COLORS.acquisition}, ${COLORS.compute}, #b088ff)`,
                boxShadow: `0 0 16px ${COLORS.acquisition}, 0 0 30px rgba(109,179,255,.3)`,
              }}
            />
            <span
              style={{
                fontFamily: FONTS.mono,
                fontSize: 18,
                fontWeight: 700,
                color: COLORS.compute,
                textShadow: `0 0 8px rgba(123,232,138,.4)`,
              }}
            >
              HCM project
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "flex-end", gap: 12 }}>
            <div
              style={{
                width: 20,
                height: 2,
                borderRadius: 1,
                background: "#ffffff",
                opacity: 0.3,
              }}
            />
            <span
              style={{
                fontFamily: FONTS.mono,
                fontSize: 14,
                color: "rgba(255,255,255,.35)",
              }}
            >
              rest of Salk
            </span>
          </div>
        </div>
      )}

      {freewayActive && (
        <div
          style={{
            position: "absolute",
            left: (BLDG1.x + BLDG5_TALMO.x) / 2 - 170,
            top: (BLDG1.y + BLDG5_TALMO.y) / 2 - 20,
            zIndex: 7,
            opacity: interpolate(frame, [freewayStart + 25, freewayStart + 50], [0, 0.75], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          <div
            style={{
              fontFamily: FONTS.display,
              fontSize: 20,
              fontWeight: 700,
              color: COLORS.acquisition,
              textShadow: `0 0 14px rgba(109,179,255,.6)`,
              transform: "rotate(-60deg)",
              whiteSpace: "nowrap",
            }}
          >
            ≈ 300 TB data freeway 🚗
          </div>
        </div>
      )}

      {/* Explosion flash overlay */}
      {explosionFlash > 0 && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: `rgba(109,179,255,${explosionFlash})`,
            zIndex: 9,
            pointerEvents: "none",
          }}
        />
      )}

      {/* Explosion: campus-wide glow */}
      {explosionActive && (
        <div
          style={{
            position: "absolute",
            inset: 0,
            background: `radial-gradient(ellipse at 40% 50%, rgba(109,179,255,${explosionRamp * 0.12}), rgba(123,232,138,${explosionRamp * 0.06}), transparent 70%)`,
            zIndex: 3,
            pointerEvents: "none",
          }}
        />
      )}

      {/* "300 TB" dramatic text */}
      {explosionActive && (
        <div
          style={{
            position: "absolute",
            top: 30,
            left: 60,
            zIndex: 10,
            opacity: interpolate(frame, [explosionStart + 10, explosionStart + 25], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          <div
            style={{
              fontFamily: FONTS.display,
              fontSize: 64,
              fontWeight: 700,
              color: COLORS.danger,
              textShadow: `0 0 40px ${COLORS.danger}, 0 0 80px rgba(255,107,107,.4)`,
            }}
          >
            300 TB
          </div>
          <div
            style={{
              fontFamily: FONTS.mono,
              fontSize: 18,
              color: COLORS.training,
              marginTop: 4,
              textShadow: `0 0 12px rgba(255,196,107,.5)`,
            }}
          >
            overwhelms Salk underground
          </div>
        </div>
      )}

      {currentCaption && (
        <div
          style={{
            position: "absolute",
            bottom: 40,
            left: "50%",
            transform: "translateX(-50%)",
            fontFamily: FONTS.mono,
            fontSize: 22,
            color: COLORS.ink,
            background: COLORS.captionBg,
            border: `1px solid ${COLORS.line}`,
            padding: "12px 28px",
            borderRadius: 40,
            letterSpacing: 0.5,
            opacity: captionOpacity,
            whiteSpace: "nowrap",
            zIndex: 10,
          }}
        >
          {currentCaption.text}
        </div>
      )}
    </AbsoluteFill>
  );
};
