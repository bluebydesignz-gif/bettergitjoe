import '@fontsource/anton/400.css';
import '@fontsource/space-mono/700.css';
import {AbsoluteFill, Audio, interpolate, Sequence, staticFile} from 'remotion';
import {EndCard, Grade, Hud, IntroTitle, MidTitle} from './Overlays';
import {Shot} from './Shot';
import {buildTimeline, type ClipInput, type Plan} from './timeline';

export type InsyncProps = {
  clips: ClipInput[];
  music: string; // path inside public/
  plan?: Plan; // explicit shot list; overrides clips when present
};

export const InsyncHalloween: React.FC<InsyncProps> = ({clips, music, plan}) => {
  const tl = buildTimeline(clips, plan);
  const [introStart, introEnd] = tl.intro;
  const [midStart, midEnd] = tl.midTitle;
  const [endStart, endEnd] = tl.endCard;

  return (
    <AbsoluteFill style={{background: 'black'}}>
      {tl.shots.map((shot) => (
        <Sequence key={shot.index} from={shot.from} durationInFrames={shot.duration}>
          <Shot shot={shot} clip={tl.clips[shot.clip]} dim={shot.from === introStart && introEnd > introStart ? 0.35 : 1} />
        </Sequence>
      ))}

      <Grade />

      <Sequence from={introEnd} durationInFrames={Math.max(1, endStart - introEnd)}>
        <Hud />
      </Sequence>
      {introEnd > introStart && (
        <Sequence from={introStart} durationInFrames={introEnd - introStart}>
          <IntroTitle />
        </Sequence>
      )}
      {midEnd > midStart && (
        <Sequence from={midStart} durationInFrames={midEnd - midStart}>
          <MidTitle />
        </Sequence>
      )}
      <Sequence from={endStart} durationInFrames={endEnd - endStart}>
        <EndCard duration={endEnd - endStart} />
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
