import '@fontsource/anton/400.css';
import '@fontsource/space-mono/700.css';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {Shot} from '../insync/Shot';
import {Caption} from './Captions';
import {PunchEndCard, punchFrames, punchShake} from './PunchOut';
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
  endFx?: 'punch'; // boxing gloves punch the end title words off the screen
  punchSound?: string; // path inside public/, played on each punch
};

export const BarberReel: React.FC<BarberProps> = ({plan, music, title, subtitle, endTitle, endSubtitle, look: lookIn, endFx, punchSound}) => {
  const frame = useCurrentFrame();
  const look = {...DEFAULT_LOOK, ...lookIn};
  const tl = buildBarberTimeline(plan);
  const [introStart, introEnd] = tl.intro;
  const [endStart, endEnd] = tl.endCard;
  const punchWords = endFx === 'punch' ? endTitle.split(' ').length : 0;
  const shake = punchWords ? punchShake(frame - endStart, punchWords) : {x: 0, y: 0};

  return (
    <AbsoluteFill style={{background: 'black'}}>
      <AbsoluteFill style={{transform: `translate(${shake.x}px, ${shake.y}px) scale(${shake.x || shake.y ? 1.04 : 1})`}}>
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
        {endFx === 'punch' ? (
          <PunchEndCard title={endTitle} duration={endEnd - endStart} />
        ) : (
          <EndCard title={endTitle} subtitle={endSubtitle} duration={endEnd - endStart} look={look} />
        )}
      </Sequence>
      </AbsoluteFill>

      {punchSound &&
        punchFrames(punchWords).map((hit) => (
          <Sequence key={`punch${hit}`} from={endStart + hit - 1} durationInFrames={20}>
            <Audio src={staticFile(punchSound)} />
          </Sequence>
        ))}

      {music && <Audio src={staticFile(music)} volume={(f) => musicVolume(f, tl.audioWindows, endEnd)} />}
    </AbsoluteFill>
  );
};
