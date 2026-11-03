import {Composition} from 'remotion';
import {HelloStudio} from './HelloStudio';
import {InsyncHalloween, type InsyncProps} from './insync/InsyncHalloween';
import {DURATION, FPS} from './insync/timeline';

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
      // Empty clips = placeholder preview. Pass real clips with --props.
      defaultProps={{clips: [], music: 'music/beat.wav'} satisfies InsyncProps}
    />
  </>
);
