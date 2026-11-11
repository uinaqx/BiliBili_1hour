import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import timeline from './timeline.json';
import {SceneCtx, SceneData} from './anim';
import {Header, SceneFade, Subtitle} from './ui';
import {C} from './theme';
import {Intro} from './scenes/Intro';
import {ArrayScene} from './scenes/ArrayScene';
import {Linked} from './scenes/Linked';
import {StackScene} from './scenes/StackScene';
import {QueueScene} from './scenes/QueueScene';
import {HashScene} from './scenes/HashScene';
import {TreeScene} from './scenes/TreeScene';
import {HeapScene} from './scenes/HeapScene';
import {GraphScene} from './scenes/GraphScene';
import {Complexity} from './scenes/Complexity';
import {Outro} from './scenes/Outro';

const SCENES: Record<string, React.FC> = {
  intro: Intro, array: ArrayScene, linked: Linked, stack: StackScene, queue: QueueScene, hash: HashScene,
  tree: TreeScene, heap: HeapScene, graph: GraphScene, complexity: Complexity, outro: Outro,
};

export const Video: React.FC<{subtitles: boolean}> = ({subtitles}) => (
  <AbsoluteFill style={{background: C.bg}}>
    {(timeline.scenes as SceneData[]).map((s) => {
      const Comp = SCENES[s.id];
      return (
        <Sequence key={s.id} from={s.from} durationInFrames={s.duration} name={s.title} premountFor={30}>
          <SceneCtx.Provider value={s}>
            <Comp />
            <Header />
            {subtitles && <Subtitle />}
            <SceneFade />
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
