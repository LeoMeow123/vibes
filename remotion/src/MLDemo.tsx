import React from "react";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";

import { ML01_Title } from "./scenes/ML01_Title";
import { ML02_HumanVsComputer } from "./scenes/ML02_HumanVsComputer";
import { ML03_PixelZoom } from "./scenes/ML03_PixelZoom";
import { ML04_Labeling } from "./scenes/ML04_Labeling";
import { ML05_NeuralNet } from "./scenes/ML05_NeuralNet";
import { ML06_ItWorks } from "./scenes/ML06_ItWorks";
import { ML07_AngleChanged } from "./scenes/ML07_AngleChanged";
import { ML08_LightsOff } from "./scenes/ML08_LightsOff";
import { ML09_CameraMoved } from "./scenes/ML09_CameraMoved";
import { ML10_GoldenRule } from "./scenes/ML10_GoldenRule";
import { ML11_Retrain } from "./scenes/ML11_Retrain";
import { ML12_EndCard } from "./scenes/ML12_EndCard";

const FPS = 30;

interface SceneEntry {
  component: React.FC;
  durationSeconds: number;
  transitionType?: "fade" | "slide-up";
}

const SCENES: SceneEntry[] = [
  { component: ML01_Title, durationSeconds: 5 },
  { component: ML02_HumanVsComputer, durationSeconds: 7 },
  { component: ML03_PixelZoom, durationSeconds: 7 },
  { component: ML04_Labeling, durationSeconds: 8 },
  { component: ML05_NeuralNet, durationSeconds: 7 },
  { component: ML06_ItWorks, durationSeconds: 6 },
  { component: ML07_AngleChanged, durationSeconds: 8, transitionType: "slide-up" },
  { component: ML08_LightsOff, durationSeconds: 7 },
  { component: ML09_CameraMoved, durationSeconds: 7 },
  { component: ML10_GoldenRule, durationSeconds: 7 },
  { component: ML11_Retrain, durationSeconds: 7 },
  { component: ML12_EndCard, durationSeconds: 5 },
];

const FADE_FRAMES = 12;

export const MLDemo: React.FC = () => {
  const elements: React.ReactNode[] = [];

  SCENES.forEach((scene, i) => {
    if (i > 0) {
      const tType = scene.transitionType || "fade";
      const presentation =
        tType === "slide-up"
          ? slide({ direction: "from-bottom" })
          : fade();

      elements.push(
        <TransitionSeries.Transition
          key={`t-${i}`}
          presentation={presentation}
          timing={linearTiming({ durationInFrames: FADE_FRAMES })}
        />,
      );
    }

    const SceneComponent = scene.component;
    elements.push(
      <TransitionSeries.Sequence
        key={`s-${i}`}
        durationInFrames={scene.durationSeconds * FPS}
      >
        <SceneComponent />
      </TransitionSeries.Sequence>,
    );
  });

  return <TransitionSeries>{elements}</TransitionSeries>;
};
