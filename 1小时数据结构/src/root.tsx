import React from 'react';
import {Composition} from 'remotion';
import {Course, Timeline} from './video';
export const Root: React.FC = () => <Composition id="DataStructuresCourse" component={Course} width={1920} height={1080} fps={30} durationInFrames={Timeline.totalFrames} defaultProps={{includeAudio:Timeline.audioAvailable!==false,includeCaptions:true}} />;
