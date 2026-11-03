import {Composition} from 'remotion';
import {HelloStudio} from './HelloStudio';

export const Root: React.FC = () => (
  <Composition
    id="HelloStudio"
    component={HelloStudio}
    durationInFrames={120}
    fps={30}
    width={1080}
    height={1920}
  />
);
