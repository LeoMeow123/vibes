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

interface SlackMsg {
  time: string;
  hour: number;
  bot: string;
  emoji: string;
  text: string;
  severity: "ok" | "warn" | "danger";
  appearFrame: number;
}

const MESSAGES: SlackMsg[] = [
  {
    time: "10:02 PM",
    hour: 22,
    bot: "hcm-bot",
    emoji: "🤖",
    text: "📹 Recording started on all 4 cameras. Nightly session active.",
    severity: "ok",
    appearFrame: 15,
  },
  {
    time: "11:47 PM",
    hour: 23.78,
    bot: "hcm-bot",
    emoji: "🤖",
    text: "⚠️ cam_03 frame drop detected — buffer overflow. Restarting stream…",
    severity: "warn",
    appearFrame: 40,
  },
  {
    time: "2:03 AM",
    hour: 2.05,
    bot: "hcm-bot",
    emoji: "🤖",
    text: "🚨 Transfer delayed! VAST mount timeout. 47 GB queued. Retrying…",
    severity: "danger",
    appearFrame: 70,
  },
  {
    time: "2:15 AM",
    hour: 2.25,
    bot: "hcm-bot",
    emoji: "🤖",
    text: "✅ Transfer recovered. Queue cleared. 47 GB written to /vast/hcm/",
    severity: "ok",
    appearFrame: 100,
  },
  {
    time: "3:00 AM",
    hour: 3,
    bot: "hcm-bot",
    emoji: "🤖",
    text: "🔥 Nightly inference batch complete — 1,247 videos processed on Triton.",
    severity: "ok",
    appearFrame: 125,
  },
  {
    time: "9:14 AM",
    hour: 9.23,
    bot: "hcm-bot",
    emoji: "🤖",
    text: "🚨 Acq PC 2 unresponsive — no heartbeat for 12 min. Camera offline!",
    severity: "danger",
    appearFrame: 150,
  },
  {
    time: "9:16 AM",
    hour: 9.27,
    bot: "hcm-bot",
    emoji: "🤖",
    text: "📱 @leo — Acq PC 2 down. Recordings paused. Manual restart needed.",
    severity: "danger",
    appearFrame: 170,
  },
];

const severityColor = (s: SlackMsg["severity"]) =>
  s === "danger" ? COLORS.danger : s === "warn" ? COLORS.training : COLORS.compute;

const severityBorder = (s: SlackMsg["severity"]) =>
  s === "danger"
    ? "rgba(255,107,107,.5)"
    : s === "warn"
      ? "rgba(255,196,107,.4)"
      : "rgba(123,232,138,.25)";

export const Scene21_TwoAM: React.FC = () => {
  const frame = useCurrentFrame();

  const currentMsg = MESSAGES.filter((m) => frame >= m.appearFrame);
  const latestMsg = currentMsg.length > 0 ? currentMsg[currentMsg.length - 1] : null;

  const clockHour = latestMsg ? latestMsg.hour : 22;
  const isNight = clockHour >= 20 || clockHour < 7;

  const bgPulse = latestMsg?.severity === "danger"
    ? 0.03 + Math.sin(frame * 0.15) * 0.02
    : 0;

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at 50% 50%, rgba(255,107,107,${bgPulse}), transparent 50%), ${COLORS.bg}`,
      }}
    >
      {/* Slack-style sidebar hint */}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          bottom: 0,
          width: 60,
          background: "#1a1d23",
          borderRight: `1px solid ${COLORS.line}`,
          zIndex: 1,
        }}
      >
        <div
          style={{
            width: 36,
            height: 36,
            borderRadius: 8,
            background: "#3e1d6d",
            margin: "16px auto",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: 18,
          }}
        >
          S
        </div>
      </div>

      {/* Channel header */}
      <div
        style={{
          position: "absolute",
          left: 60,
          top: 0,
          right: 0,
          height: 56,
          background: "#1a1d23",
          borderBottom: `1px solid ${COLORS.line}`,
          display: "flex",
          alignItems: "center",
          padding: "0 24px",
          zIndex: 3,
        }}
      >
        <span style={{ fontFamily: FONTS.mono, fontSize: 16, color: COLORS.muted }}>
          # hcm-alerts
        </span>
        <span style={{ fontFamily: FONTS.mono, fontSize: 12, color: COLORS.muted, marginLeft: 16 }}>
          24/7 monitoring · automated
        </span>
      </div>

      {/* Clock display */}
      <div
        style={{
          position: "absolute",
          top: 16,
          right: 30,
          fontFamily: FONTS.mono,
          fontSize: 32,
          fontWeight: 700,
          color: isNight ? "#3a5a8a" : COLORS.muted,
          textShadow: isNight ? "0 0 15px rgba(58,90,138,.5)" : "none",
          zIndex: 5,
          letterSpacing: 2,
        }}
      >
        {latestMsg ? latestMsg.time : "10:02 PM"}
      </div>
      {isNight && (
        <div
          style={{
            position: "absolute",
            top: 52,
            right: 48,
            fontSize: 20,
            zIndex: 5,
          }}
        >
          🌙
        </div>
      )}

      {/* Messages feed */}
      <div
        style={{
          position: "absolute",
          left: 80,
          top: 70,
          right: 20,
          bottom: 100,
          overflow: "hidden",
          zIndex: 2,
        }}
      >
        {MESSAGES.map((msg, i) => {
          const localFrame = frame - msg.appearFrame;
          if (localFrame < 0) return null;

          const slideUp = interpolate(localFrame, [0, 12], [40, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.cubic),
          });
          const opacity = interpolate(localFrame, [0, 10], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });

          const shake = msg.severity === "danger" && localFrame < 30
            ? Math.sin(localFrame * 1.5) * 3 * interpolate(localFrame, [0, 8, 30], [0, 1, 0], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              })
            : 0;

          const isLatest = i === currentMsg.length - 1;
          const glow = isLatest && msg.severity === "danger"
            ? 0.2 + Math.sin(frame * 0.2) * 0.1
            : 0;

          return (
            <div
              key={i}
              style={{
                marginBottom: 12,
                padding: "12px 16px",
                borderRadius: 8,
                background: "rgba(26,29,35,.9)",
                borderLeft: `4px solid ${severityBorder(msg.severity)}`,
                boxShadow: glow > 0
                  ? `0 0 20px rgba(255,107,107,${glow})`
                  : "none",
                opacity,
                transform: `translateY(${slideUp}px) translateX(${shake}px)`,
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 10,
                  marginBottom: 6,
                }}
              >
                <div
                  style={{
                    width: 28,
                    height: 28,
                    borderRadius: 6,
                    background: "#2a3550",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 16,
                  }}
                >
                  {msg.emoji}
                </div>
                <span
                  style={{
                    fontFamily: FONTS.mono,
                    fontSize: 14,
                    fontWeight: 700,
                    color: COLORS.ink,
                  }}
                >
                  {msg.bot}
                </span>
                <span
                  style={{
                    fontFamily: FONTS.mono,
                    fontSize: 12,
                    color: COLORS.muted,
                    marginLeft: "auto",
                  }}
                >
                  {msg.time}
                </span>
              </div>
              <div
                style={{
                  fontFamily: FONTS.mono,
                  fontSize: 15,
                  color: severityColor(msg.severity),
                  lineHeight: 1.5,
                  paddingLeft: 38,
                }}
              >
                {msg.text}
              </div>
            </div>
          );
        })}
      </div>

      {/* Phone vibration indicator when danger messages appear */}
      {latestMsg?.severity === "danger" && (
        <div
          style={{
            position: "absolute",
            left: "50%",
            top: "50%",
            transform: "translate(-50%, -50%)",
            width: 200,
            height: 200,
            borderRadius: "50%",
            background: `radial-gradient(circle, rgba(255,107,107,.08), transparent 70%)`,
            zIndex: 1,
            opacity: 0.5 + Math.sin(frame * 0.3) * 0.3,
            pointerEvents: "none",
          }}
        />
      )}

      {/* Notification count badge */}
      {currentMsg.length > 0 && (
        <div
          style={{
            position: "absolute",
            left: 44,
            top: 12,
            width: 20,
            height: 20,
            borderRadius: "50%",
            background: COLORS.danger,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontFamily: FONTS.mono,
            fontSize: 11,
            fontWeight: 700,
            color: "#fff",
            zIndex: 4,
            opacity: interpolate(
              Math.sin(frame * 0.2),
              [-1, 1],
              [0.7, 1],
            ),
          }}
        >
          {currentMsg.filter((m) => m.severity !== "ok").length || ""}
        </div>
      )}

      <Sequence from={0} layout="none">
        <Caption text="The watchtower never sleeps. Neither do you." />
      </Sequence>
    </AbsoluteFill>
  );
};
