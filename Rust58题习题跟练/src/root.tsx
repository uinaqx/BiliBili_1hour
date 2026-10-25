import React from 'react';
import {Composition} from 'remotion';
import {Course, Timeline} from './video';
export const Root: React.FC = () => <Composition id="RustPracticeCourse" component={Course} width={1920} height={1080} fps={30} durationInFrames={Timeline.totalFrames} defaultProps={{includeAudio:Timeline.scope==='complete-course',includeCaptions:false}} />;
