import '@fontsource/anton/400.css';
import '@fontsource/space-mono/700.css';
import {AbsoluteFill, Audio, Sequence, staticFile} from 'remotion';
import {Shot} from '../insync/Shot';
import {Caption} from './Captions';
import {DEFAULT_LOOK, EndCard, Grade, TitleCard, type Look} from './Overlays';
import {buildBarberTimeline, musicVolume, type BarberPlan} from './timeline';

export type BarberProps = {
  plan: BarberPlan;
  music: string; // path inside public/
  title: string;
  subtitle?: string;
  endTitle: string;
  endSubtitle?: string;
  look?: Partial<Look>;
};

export const BarberReel: React.FC<BarberProps> = ({plan, music, title, subtitle, endTitle, endSubtitle, look: lookIn}) => {
  const look = {...DEFAULT_LOOK, ...lookIn};
  const tl = buildBarberTimeline(plan);
  const [introStart, introEnd] = tl.intro;
  const [endStart, endEnd] = tl.endCard;

  return (
    <AbsoluteFill style={{background: 'black'}}>
      {tl.shots.map((shot) => (
        <Sequence key={shot.index} from={shot.from} durationInFrames={shot.duration}>
          <Shot shot={shot} clip={tl.clips[shot.clip]} dim={shot.from === introStart && introEnd > introStart ? 0.4 : 1} />
        </Sequence>
      ))}

      <Grade look={look} />

      {introEnd > introStart && (
        <Sequence from={introStart} durationInFrames={introEnd - introStart}>
          <TitleCard title={title} subtitle={subtitle} look={look} />
        </Sequence>
      )}
      {tl.captions.map((c, i) => (
        <Sequence key={`cap${i}`} from={c.from} durationInFrames={Math.max(1, c.to - c.from)}>
          <Caption text={c.text} duration={c.to - c.from} accent={look.accent} />
        </Sequence>
      ))}
      <Sequence from={endStart} durationInFrames={endEnd - endStart}>
        <EndCard title={endTitle} subtitle={endSubtitle} duration={endEnd - endStart} look={look} />
      </Sequence>

      {music && <Audio src={staticFile(music)} volume={(f) => musicVolume(f, tl.audioWindows, endEnd)} />}
    </AbsoluteFill>
  );
};
