import { loadFont as loadSpaceGrotesk } from "@remotion/google-fonts/SpaceGrotesk";
import { loadFont as loadJetBrainsMono } from "@remotion/google-fonts/JetBrainsMono";

const { fontFamily: spaceGrotesk } = loadSpaceGrotesk("normal", {
  weights: ["500", "700"],
  subsets: ["latin"],
});

const { fontFamily: jetBrainsMono } = loadJetBrainsMono("normal", {
  weights: ["400", "700"],
  subsets: ["latin"],
});

export const FONTS = {
  display: spaceGrotesk,
  mono: jetBrainsMono,
} as const;

export const COLORS = {
  bg: "#0a0e1a",
  acquisition: "#6db3ff",
  compute: "#7be88a",
  training: "#ffc46b",
  danger: "#ff6b6b",
  source: "#ff8a3c",
  ink: "#eef1f8",
  muted: "#8c97b8",
  line: "#2a3550",
  captionBg: "rgba(10,14,28,.85)",
} as const;

export const FPS = 30;
