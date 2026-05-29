import React from "react";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";

import { Scene01_Establishing } from "./scenes/Scene01_Establishing";
import { Scene02_Timeline } from "./scenes/Scene02_Timeline";
import { Scene03_QuestDeclared } from "./scenes/Scene03_QuestDeclared";
import { Scene04_PhoneMelts } from "./scenes/Scene04_PhoneMelts";
import { Scene07_FourPhones } from "./scenes/Scene07_FourPhones";
import { Scene09_Orchestrated } from "./scenes/Scene09_Orchestrated";
import { Scene10_Encoder } from "./scenes/Scene10_Encoder";
import { Scene12_LocalDrives } from "./scenes/Scene12_LocalDrives";
import { Scene18_ArmyOfBugs } from "./scenes/Scene18_ArmyOfBugs";
import { Scene05_BareWires } from "./scenes/Scene05_BareWires";
import { Scene06_RigWorthIt } from "./scenes/Scene06_RigWorthIt";
import { Scene08_SyncDemon } from "./scenes/Scene08_SyncDemon";
import { Scene11_ScaleReveal } from "./scenes/Scene11_ScaleReveal";
import { Scene13_Freeway } from "./scenes/Scene13_Freeway";
import { Scene15_LiveRig } from "./scenes/Scene15_LiveRig";
import { Scene16_SAAPS } from "./scenes/Scene16_SAAPS";
import { Scene17_MathMontage } from "./scenes/Scene17_MathMontage";
import { Scene19_TeamVsMe } from "./scenes/Scene19_TeamVsMe";
import { Scene20_Watchtower } from "./scenes/Scene20_Watchtower";
import { Scene21_TwoAM } from "./scenes/Scene21_TwoAM";
import { Scene22_EndCard } from "./scenes/Scene22_EndCard";

const FPS = 30;

interface SceneEntry {
  component: React.FC;
  durationSeconds: number;
  transitionType?: "fade" | "slide-up";
}

const SCENES: SceneEntry[] = [
  { component: Scene01_Establishing, durationSeconds: 8 },
  { component: Scene02_Timeline, durationSeconds: 9 },
  { component: Scene03_QuestDeclared, durationSeconds: 6, transitionType: "slide-up" },
  { component: Scene04_PhoneMelts, durationSeconds: 5 },
  { component: Scene05_BareWires, durationSeconds: 7 },
  { component: Scene06_RigWorthIt, durationSeconds: 8 },
  { component: Scene07_FourPhones, durationSeconds: 6 },
  { component: Scene08_SyncDemon, durationSeconds: 7 },
  { component: Scene09_Orchestrated, durationSeconds: 5 },
  { component: Scene10_Encoder, durationSeconds: 6 },
  { component: Scene11_ScaleReveal, durationSeconds: 7 },
  { component: Scene12_LocalDrives, durationSeconds: 8 },
  { component: Scene13_Freeway, durationSeconds: 15 },
  { component: Scene15_LiveRig, durationSeconds: 8 },
  { component: Scene16_SAAPS, durationSeconds: 9 },
  { component: Scene17_MathMontage, durationSeconds: 6 },
  { component: Scene18_ArmyOfBugs, durationSeconds: 6, transitionType: "slide-up" },
  { component: Scene19_TeamVsMe, durationSeconds: 8 },
  { component: Scene20_Watchtower, durationSeconds: 9 },
  { component: Scene21_TwoAM, durationSeconds: 7 },
  { component: Scene22_EndCard, durationSeconds: 7 },
];

const FADE_FRAMES = 12;

export const Saga: React.FC = () => {
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
