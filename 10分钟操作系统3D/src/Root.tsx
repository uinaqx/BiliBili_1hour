import React from 'react';
import {Composition} from 'remotion';
import {Video} from './Video';
import timeline from './timeline.json';

export const Root: React.FC = () => (
  <>
    <Composition id="OS3D" component={Video} durationInFrames={timeline.total} fps={timeline.fps} width={1920} height={1080}
      defaultProps={{subtitles: true}} />
  </>
);
