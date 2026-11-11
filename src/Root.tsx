import {Composition} from 'remotion';
import {HelloStudio} from './HelloStudio';
import {InsyncHalloween, type InsyncProps} from './insync/InsyncHalloween';
import {DURATION, FPS, planDuration} from './insync/timeline';

export const Root: React.FC = () => (
  <>
    <Composition
      id="HelloStudio"
      component={HelloStudio}
      durationInFrames={120}
      fps={30}
      width={1080}
      height={1920}
    />
    <Composition
      id="InsyncHalloween"
      component={InsyncHalloween}
      durationInFrames={DURATION}
      fps={FPS}
      width={1080}
      height={1920}
      // Empty clips = placeholder preview. Pass real clips or a plan with --props.
      defaultProps={{clips: [], music: 'music/beat.wav'} as InsyncProps}
      calculateMetadata={({props}) => ({durationInFrames: props.plan ? planDuration(props.plan) : DURATION})}
    />
  </>
);
