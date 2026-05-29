import "./index.css";
import { Composition } from "remotion";
import { Saga } from "./Saga";
import { MLDemo } from "./MLDemo";

const FPS = 30;

const SAGA_DURATIONS = [8, 9, 6, 5, 7, 8, 6, 7, 5, 6, 7, 8, 15, 8, 9, 6, 6, 8, 9, 7, 7];
const FADE_FRAMES = 12;
const SAGA_FRAMES =
  SAGA_DURATIONS.reduce((sum, s) => sum + s * FPS, 0) -
  (SAGA_DURATIONS.length - 1) * FADE_FRAMES;

const ML_DURATIONS = [5, 7, 7, 8, 7, 6, 8, 7, 7, 7, 7, 5];
const ML_FRAMES =
  ML_DURATIONS.reduce((sum, s) => sum + s * FPS, 0) -
  (ML_DURATIONS.length - 1) * FADE_FRAMES;

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="Saga"
        component={Saga}
        durationInFrames={SAGA_FRAMES}
        fps={FPS}
        width={1920}
        height={1080}
      />
      <Composition
        id="MLDemo"
        component={MLDemo}
        durationInFrames={ML_FRAMES}
        fps={FPS}
        width={1920}
        height={1080}
      />
    </>
  );
};
