import React from "react";
import { AbsoluteFill, Sequence } from "remotion";
import { PlaceholderCard } from "../components/PlaceholderCard";
import { Caption } from "../components/Caption";

const makePlaceholder = (
  sceneNumber: number,
  title: string,
  caption: string,
) => {
  const Component: React.FC = () => (
    <AbsoluteFill>
      <PlaceholderCard sceneNumber={sceneNumber} title={title} />
      <Sequence from={0} layout="none">
        <Caption text={caption} />
      </Sequence>
    </AbsoluteFill>
  );
  Component.displayName = `Scene${String(sceneNumber).padStart(2, "0")}`;
  return Component;
};

export const Scene03_QuestDeclared = makePlaceholder(
  3,
  "Researcher raises fist, cages multiply into glowing grid",
  "BOSS BATTLES: 5",
);

export const Scene04_PhoneMelts = makePlaceholder(
  4,
  "Smartphone taped to cage overheats with comic smoke",
  "Consumer cameras: melt.",
);

export const Scene07_FourPhones = makePlaceholder(
  7,
  "Four phones floating above cages, clocks out of sync",
  "4 phones ≠ synced.",
);

export const Scene09_Orchestrated = makePlaceholder(
  9,
  "Frozen windows snap into synchronized glowing grid",
  "Sync Demon: defeated.",
);

export const Scene10_Encoder = makePlaceholder(
  10,
  "Raw video streams pour into glowing encoder engine",
  "Encode at the source.",
);

export const Scene12_LocalDrives = makePlaceholder(
  12,
  "Hard drive shatters; snail carries drive across campus",
  "Local drive = single point of failure.",
);

export const Scene14_SalkFlourish = makePlaceholder(
  14,
  "Salk twin buildings as anime landmark, mascot mice waving",
  "Salk Institute, but make it anime.",
);

export const Scene18_ArmyOfBugs = makePlaceholder(
  18,
  "Swarms of cute bug creatures crawling over software windows",
  "Every system runs on bugs.",
);
