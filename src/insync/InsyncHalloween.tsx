import '@fontsource/anton/400.css';
import '@fontsource/space-mono/700.css';
import {AbsoluteFill, Audio, interpolate, Sequence, staticFile} from 'remotion';
import {EndCard, Grade, Hud, IntroTitle, MidTitle} from './Overlays';
import {Shot} from './Shot';
import {buildShots, SECTIONS, type ClipInput} from './timeline';

export type InsyncProps = {
  clips: ClipInput[];
  music: string; // path inside public/
};

export const InsyncHalloween: React.FC<InsyncProps> = ({clips, music}) => {
  const shots = buildShots(clips.length);
  const [introStart, introEnd] = SECTIONS.intro;
  const [midStart, midEnd] = SECTIONS.midTitle;
  const [endStart, endEnd] = SECTIONS.endCard;

  return (
    <AbsoluteFill style={{background: 'black'}}>
      {shots.map((shot) => {
        const isIntro = shot.from === introStart;
        const isEnd = shot.from === endStart;
        return (
          <Sequence key={shot.index} from={shot.from} durationInFrames={shot.duration}>
            <Shot shot={shot} clip={clips[shot.clip]} dim={isIntro ? 0.35 : isEnd ? 0.45 : 1} />
          </Sequence>
        );
      })}

      <Grade />

      <Sequence from={introEnd} durationInFrames={endStart - introEnd}>
        <Hud />
      </Sequence>
      <Sequence from={introStart} durationInFrames={introEnd - introStart}>
        <IntroTitle />
      </Sequence>
      <Sequence from={midStart} durationInFrames={midEnd - midStart}>
        <MidTitle />
      </Sequence>
      <Sequence from={endStart} durationInFrames={endEnd - endStart}>
        <EndCard />
      </Sequence>

      {music && (
        <Audio
          src={staticFile(music)}
          volume={(f) => interpolate(f, [endEnd - 20, endEnd], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})}
        />
      )}
    </AbsoluteFill>
  );
};
