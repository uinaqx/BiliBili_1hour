import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import timeline from './timeline.json';
import {SceneCtx, SceneData} from './anim';
import {Backdrop, Header, SceneFade, Subtitle} from './ui';
import {Intro} from './scenes/Intro';
import {LayersScene} from './scenes/LayersScene';
import {LinkScene} from './scenes/LinkScene';
import {NetworkScene} from './scenes/NetworkScene';
import {TransportScene} from './scenes/TransportScene';
import {AppScene} from './scenes/AppScene';
import {JourneyScene} from './scenes/JourneyScene';
import {Outro} from './scenes/Outro';

const SCENES: Record<string, React.FC> = {
  intro: Intro, layers: LayersScene, link: LinkScene, network: NetworkScene, transport: TransportScene,
  app: AppScene, journey: JourneyScene, outro: Outro,
};

export const Video: React.FC<{subtitles: boolean}> = ({subtitles}) => (
  <AbsoluteFill>
    <Backdrop />
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
