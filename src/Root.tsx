import {Composition} from 'remotion';
import {HelloStudio} from './HelloStudio';
import {CertifiedGTA, GTA_DURATION, GTA_FPS} from './CertifiedGTA';

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
    id="CertifiedGTA"
    component={CertifiedGTA}
    durationInFrames={GTA_DURATION}
    fps={GTA_FPS}
    width={1080}
    height={1920}
  />
  </>
);
