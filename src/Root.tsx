import {Composition} from 'remotion';
import {HelloStudio} from './HelloStudio';
import {TurkeyReel, turkeyDuration} from './turkey/TurkeyReel';

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
    {/* Thanksgiving Turkey Giveaway thank-you reel. Media lives in public/turkey (not committed). */}
    <Composition
      id="TurkeyThankYou"
      component={TurkeyReel}
      durationInFrames={turkeyDuration}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{minimal: false, bare: false}}
    />
    <Composition
      id="TurkeyThankYouClean"
      component={TurkeyReel}
      durationInFrames={turkeyDuration}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{minimal: true, bare: false}}
    />
    <Composition
      id="TurkeyBase"
      component={TurkeyReel}
      durationInFrames={turkeyDuration}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{minimal: false, bare: true}}
    />
  </>
);
