import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import timeline from './timeline.json';
import {SceneCtx, SceneData} from './anim';
import {Backdrop, Header, Subtitle, Sweep, Transit} from './ui';
import {Intro} from './scenes/Intro';
import {LoopScene} from './scenes/LoopScene';
import {ToolsScene} from './scenes/ToolsScene';
import {ContextScene} from './scenes/ContextScene';
import {SafetyScene} from './scenes/SafetyScene';
import {PlanScene} from './scenes/PlanScene';
import {Outro} from './scenes/Outro';

const SCENES: Record<string, React.FC> = {
  intro: Intro, loop: LoopScene, tools: ToolsScene, context: ContextScene, safety: SafetyScene, plan: PlanScene, outro: Outro,
};

export const Video: React.FC<{subtitles: boolean}> = ({subtitles}) => (
  <AbsoluteFill>
    <Backdrop />
    {(timeline.scenes as SceneData[]).map((s) => {
      const Comp = SCENES[s.id];
      return (
        <Sequence key={s.id} from={s.from} durationInFrames={s.duration} name={s.title} premountFor={30}>
          <SceneCtx.Provider value={s}>
            <Transit>
              <Comp />
              <Header />
            </Transit>
            <Sweep />
            {subtitles && <Subtitle />}
            {s.beats.map((b, i) => b.audio && (
              <Sequence key={i} from={b.from} durationInFrames={b.dur + 15} layout="none">
                <Audio src={staticFile(b.audio)} />
              </Sequence>
            ))}
          </SceneCtx.Provider>
        </Sequence>
      );
    })}
  </AbsoluteFill>
);
