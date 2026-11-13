import {Composition} from 'remotion';
import {HelloStudio} from './HelloStudio';
import {InsyncHalloween, type InsyncProps} from './insync/InsyncHalloween';
import {DURATION, FPS, planDuration} from './insync/timeline';
import {BarberReel, type BarberProps} from './barber/BarberReel';
import barberPlaceholder from '../edits/barber-placeholder.json';

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
    <Composition
      id="BarberReel"
      component={BarberReel}
      durationInFrames={planDuration(barberPlaceholder.plan as BarberProps['plan'])}
      fps={FPS}
      width={1080}
      height={1920}
      // Placeholder footage and captions. Pass the real edit with --props=edits/barber-<name>.json.
      defaultProps={barberPlaceholder as unknown as BarberProps}
      calculateMetadata={({props}) => ({durationInFrames: planDuration(props.plan)})}
    />
  </>
);
