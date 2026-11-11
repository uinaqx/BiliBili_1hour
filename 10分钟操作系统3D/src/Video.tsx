import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import timeline from './timeline.json';
import {SceneCtx, SceneData} from './anim';
import {Header, SceneFade, Subtitle} from './ui';
import {C} from './theme';
import {Intro} from './scenes/Intro';
import {KernelScene} from './scenes/KernelScene';
import {ProcessScene} from './scenes/ProcessScene';
import {SchedScene} from './scenes/SchedScene';
import {SyncScene} from './scenes/SyncScene';
import {DeadlockScene} from './scenes/DeadlockScene';
import {MemoryScene} from './scenes/MemoryScene';
import {VmemScene} from './scenes/VmemScene';
import {FileScene} from './scenes/FileScene';
import {IoScene} from './scenes/IoScene';
import {Outro} from './scenes/Outro';

const SCENES: Record<string, React.FC> = {
  intro: Intro, kernel: KernelScene, process: ProcessScene, sched: SchedScene, sync: SyncScene,
  deadlock: DeadlockScene, memory: MemoryScene, vmem: VmemScene, file: FileScene, io: IoScene, outro: Outro,
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
