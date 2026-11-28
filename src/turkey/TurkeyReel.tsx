import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Easing,
  Img,
  OffthreadVideo,
  Sequence,
  continueRender,
  delayRender,
  interpolate,
  staticFile,
  useCurrentFrame,
} from 'remotion';
import timeline from './timeline.json';

// ---- brand -----------------------------------------------------------------
const RED = '#E01B22';
const INK = '#0B0B0C';
const SERIF = 'InstrumentSerif';
const SANS = 'Barlow';
const COND = 'BarlowCondensed';

const FONT_FILES: Array<[string, string, string, string]> = [
  [SANS, '500', 'normal', 'Barlow-Medium.ttf'],
  [SANS, '600', 'normal', 'Barlow-SemiBold.ttf'],
  [SANS, '700', 'normal', 'Barlow-Bold.ttf'],
  [SANS, '800', 'normal', 'Barlow-ExtraBold.ttf'],
  [COND, '800', 'normal', 'BarlowCondensed-ExtraBold.ttf'],
  [SERIF, '400', 'italic', 'InstrumentSerif-Italic.ttf'],
];
if (typeof document !== 'undefined') {
  const handle = delayRender('Loading brand fonts');
  Promise.all(
    FONT_FILES.map(([family, weight, style, file]) => {
      const face = new FontFace(family, `url(${staticFile('turkey/fonts/' + file)})`, {weight, style});
      return face.load().then((f) => document.fonts.add(f));
    }),
  )
    .then(() => continueRender(handle))
    .catch((err) => {
      console.error(err);
      continueRender(handle);
    });
}

// ---- motion ----------------------------------------------------------------
// One soft "fly in": rise, un-blur and fade up on a long ease-out. No bounce.
const EASE_OUT = Easing.bezier(0.16, 1, 0.3, 1);
const EASE_IN = Easing.bezier(0.5, 0, 0.75, 0);

const Reveal: React.FC<{
  dur: number; // frames this element lives for (local to its Sequence)
  delay?: number;
  rise?: number;
  slideX?: number;
  inDur?: number;
  outDur?: number;
  hold?: boolean; // no exit (stays to the end)
  style?: React.CSSProperties;
  children: React.ReactNode;
}> = ({dur, delay = 0, rise = 34, slideX = 0, inDur = 26, outDur = 14, hold = false, style, children}) => {
  const f = useCurrentFrame();
  const p = interpolate(f, [delay, delay + inDur], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: EASE_OUT});
  const q = hold ? 0 : interpolate(f, [dur - outDur, dur], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: EASE_IN});
  return (
    <div
      style={{
        opacity: p * (1 - q),
        transform: `translate(${(1 - p) * slideX}px, ${(1 - p) * rise - q * 12}px)`,
        filter: `blur(${(1 - p) * 9 + q * 3}px)`,
        willChange: 'transform, opacity, filter',
        ...style,
      }}
    >
      {children}
    </div>
  );
};

const shadow = '0 2px 18px rgba(0,0,0,0.55), 0 1px 3px rgba(0,0,0,0.5)';
const strongShadow = '0 2px 22px rgba(0,0,0,0.85), 0 0 46px rgba(0,0,0,0.55), 0 1px 3px rgba(0,0,0,0.7)';
const lines = (t?: string) => (t ?? '').split('|');

// Soft dark veil behind text so it stays readable without a hard box.
const Veil: React.FC<{dur: number; from: 'top' | 'bottom'; strength?: number; size?: number}> = ({dur, from, strength = 0.5, size = 46}) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 18, dur - 14, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill
      style={{
        opacity: o,
        background: `linear-gradient(${from === 'top' ? 180 : 0}deg, rgba(11,11,12,${strength}) 0%, rgba(11,11,12,${strength * 0.55}) ${size * 0.55}%, rgba(11,11,12,0) ${size}%)`,
      }}
    />
  );
};

// ---- overlays --------------------------------------------------------------
type Ov = (typeof timeline.overlays)[number] & Record<string, any>;

const Title: React.FC<{o: Ov}> = ({o}) => {
  const f = useCurrentFrame();
  const rule = interpolate(f, [16, 46], [0, 150], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: EASE_OUT});
  const ruleOut = interpolate(f, [o.dur - 14, o.dur], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill>
      <Veil dur={o.dur} from="top" strength={0.62} size={52} />
      <AbsoluteFill style={{top: 300, alignItems: 'center', color: 'white', textAlign: 'center'}}>
        <Reveal dur={o.dur} delay={0} rise={22}>
          <div style={{fontFamily: SANS, fontWeight: 600, fontSize: 31, letterSpacing: '0.34em', textTransform: 'uppercase', textShadow: shadow, marginRight: '-0.34em'}}>
            {o.eyebrow}
          </div>
        </Reveal>
        <Reveal dur={o.dur} delay={6} rise={40} style={{marginTop: 6}}>
          <div style={{fontFamily: SERIF, fontStyle: 'italic', fontSize: 164, lineHeight: 1.08, textShadow: shadow}}>{o.line1}</div>
        </Reveal>
        <div style={{height: 4, width: rule, background: RED, opacity: ruleOut, marginTop: 18, borderRadius: 2}} />
        <Reveal dur={o.dur} delay={14} rise={30} style={{marginTop: 26}}>
          <div style={{fontFamily: COND, fontWeight: 800, fontSize: 86, letterSpacing: '0.1em', lineHeight: 1, textShadow: shadow, marginRight: '-0.1em'}}>
            {o.line2}
          </div>
        </Reveal>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Tagline: React.FC<{o: Ov}> = ({o}) => (
  <AbsoluteFill>
    <Veil dur={o.dur} from="top" strength={0.58} size={48} />
    <AbsoluteFill style={{top: 318, alignItems: 'center', color: 'white', textAlign: 'center'}}>
      {lines(o.text).map((l, i) => (
        <Reveal key={i} dur={o.dur} delay={i * 16} rise={36}>
          <div style={{fontFamily: SERIF, fontStyle: 'italic', fontSize: 124, lineHeight: 1.12, textShadow: shadow}}>{l}</div>
        </Reveal>
      ))}
    </AbsoluteFill>
  </AbsoluteFill>
);

const Caption: React.FC<{o: Ov}> = ({o}) => (
  <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 470}}>
    <Reveal dur={o.dur} rise={16} inDur={12} outDur={8}>
      <div
        style={{
          fontFamily: SANS,
          fontWeight: 700,
          fontSize: 50,
          lineHeight: 1.22,
          color: 'white',
          textAlign: 'center',
          padding: '16px 34px 18px',
          borderRadius: 22,
          background: 'rgba(11,11,12,0.46)',
          textShadow: '0 1px 6px rgba(0,0,0,0.45)',
          maxWidth: 880,
        }}
      >
        {lines(o.text).map((l, i) => (
          <div key={i}>{l}</div>
        ))}
      </div>
    </Reveal>
  </AbsoluteFill>
);

const NameSuper: React.FC<{o: Ov}> = ({o}) => {
  const f = useCurrentFrame();
  const bar = interpolate(f, [0, 20], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: EASE_OUT});
  const out = interpolate(f, [o.dur - 12, o.dur], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill>
      <Veil dur={o.dur} from="bottom" strength={0.5} size={50} />
      <div style={{position: 'absolute', left: 84, top: 1108, display: 'flex', gap: 22, alignItems: 'stretch'}}>
        <div style={{width: 6, background: RED, borderRadius: 3, transform: `scaleY(${bar})`, transformOrigin: 'top', opacity: out}} />
        <div style={{color: 'white'}}>
          <Reveal dur={o.dur} delay={4} rise={0} slideX={-26} inDur={22}>
            <div style={{fontFamily: SANS, fontWeight: 800, fontSize: 46, letterSpacing: '0.05em', textTransform: 'uppercase', lineHeight: 1.1, textShadow: shadow}}>{o.name}</div>
          </Reveal>
          <Reveal dur={o.dur} delay={10} rise={0} slideX={-26} inDur={22}>
            <div style={{fontFamily: SANS, fontWeight: 600, fontSize: 34, marginTop: 6, textShadow: shadow}}>{o.role}</div>
          </Reveal>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const Label: React.FC<{o: Ov}> = ({o}) => (
  <AbsoluteFill>
    <Veil dur={o.dur} from="bottom" strength={0.8} size={50} />
    <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 432}}>
      <Reveal dur={o.dur} rise={30}>
        <div style={{fontFamily: SERIF, fontStyle: 'italic', fontSize: 84, color: 'white', textShadow: strongShadow, textAlign: 'center'}}>{o.text}</div>
      </Reveal>
    </AbsoluteFill>
  </AbsoluteFill>
);

const ThanksGlow: React.FC<{dur: number}> = ({dur}) => {
  const f = useCurrentFrame();
  const o = interpolate(f, [0, 20, dur - 14, dur], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{opacity: o, background: 'radial-gradient(ellipse 62% 24% at 50% 56%, rgba(11,11,12,0.62) 0%, rgba(11,11,12,0) 100%)'}} />;
};

const Thanks: React.FC<{o: Ov}> = ({o}) => {
  const f = useCurrentFrame();
  const dimTo = Number(o.dim ?? 0);
  const dim = dimTo ? interpolate(f, [0, 18], [0, dimTo], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 0;
  const head = o.headSize ?? 196;
  return (
    <AbsoluteFill>
      {o.dim ? (
        <>
          <AbsoluteFill style={{background: INK, opacity: dim}} />
          {o.veil ? <Veil dur={o.dur + 30} from="bottom" strength={0.78} size={46} /> : null}
        </>
      ) : (
        <>
          <Veil dur={o.dur} from="bottom" strength={0.8} size={78} />
          <ThanksGlow dur={o.dur} />
        </>
      )}
      <AbsoluteFill style={{top: o.top ?? 850, alignItems: 'center', color: 'white', textAlign: 'center'}}>
        <Reveal dur={o.dur} delay={o.dim ? 12 : 0} rise={44}>
          <div style={{fontFamily: SERIF, fontStyle: 'italic', fontSize: head, lineHeight: 1.05, textShadow: strongShadow}}>{o.head}</div>
        </Reveal>
        <div style={{marginTop: 22}}>
          {(o.lines as string[]).map((l, i) => (
            <Reveal key={i} dur={o.dur} delay={(o.dim ? 26 : 14) + i * 8} rise={22}>
              <div
                style={{
                  fontFamily: SANS,
                  fontWeight: 600,
                  fontSize: o.lineSize ?? 36,
                  letterSpacing: '0.16em',
                  textTransform: 'uppercase',
                  lineHeight: 1.7,
                  textShadow: strongShadow,
                  marginRight: '-0.16em',
                }}
              >
                {l}
              </div>
            </Reveal>
          ))}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const EndCard: React.FC<{o: Ov; minimal: boolean}> = ({o, minimal}) => {
  const f = useCurrentFrame();
  const scrimFrom = minimal ? 0 : Number(o.scrimFrom ?? 0);
  const scrim = interpolate(f, [0, 22], [scrimFrom, 0.9], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const solid = interpolate(f, [Number(o.dur) - 60, Number(o.dur) - 30], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const rule = interpolate(f, [48, 78], [0, 120], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: EASE_OUT});
  const [s1, s2] = (o.slogan as string).split('. ').map((s, i) => (i === 0 ? s + '.' : s));
  const sloganDelay = minimal ? 26 : 58;
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{background: INK, opacity: Math.max(scrim, solid)}} />
      <AbsoluteFill style={{alignItems: 'center', color: 'white', textAlign: 'center', top: minimal ? 660 : 500}}>
        <Reveal dur={o.dur} delay={6} rise={30} hold>
          <Img src={staticFile('turkey/logo.png')} style={{width: 760}} />
        </Reveal>
        {minimal ? null : (
          <div style={{marginTop: 56}}>
            {lines(o.proud).map((l, i) => (
              <Reveal key={i} dur={o.dur} delay={20 + i * 8} rise={26} hold>
                <div style={{fontFamily: SERIF, fontStyle: 'italic', fontSize: 66, lineHeight: 1.2}}>{l}</div>
              </Reveal>
            ))}
          </div>
        )}
        {minimal ? <div style={{height: 40}} /> : <div style={{height: 3, width: rule, background: RED, borderRadius: 2, marginTop: 50, marginBottom: 46}} />}
        <Reveal dur={o.dur} delay={sloganDelay} rise={24} hold>
          <div style={{fontFamily: SANS, fontWeight: 800, fontSize: 60, lineHeight: 1.2, letterSpacing: '0.01em'}}>{s1}</div>
        </Reveal>
        <Reveal dur={o.dur} delay={sloganDelay + 9} rise={24} hold>
          <div style={{fontFamily: SANS, fontWeight: 800, fontSize: 60, lineHeight: 1.2, letterSpacing: '0.01em', color: RED}}>{s2}</div>
        </Reveal>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const renderOverlay = (o: Ov, minimal: boolean) => {
  switch (o.type) {
    case 'title':
      return <Title o={o} />;
    case 'tagline':
      return <Tagline o={o} />;
    case 'caption':
      return <Caption o={o} />;
    case 'name':
      return <NameSuper o={o} />;
    case 'label':
      return <Label o={o} />;
    case 'thanks':
      return <Thanks o={o} />;
    case 'endcard':
      return <EndCard o={o} minimal={minimal} />;
    default:
      return null;
  }
};

// ---- picture ---------------------------------------------------------------
const Shot: React.FC<{seg: (typeof timeline.segments)[number]}> = ({seg}) => {
  const f = useCurrentFrame();
  const scale = interpolate(f, [0, seg.dur], seg.push as [number, number]);
  const opacity = seg.xfade > 0 ? interpolate(f, [0, seg.xfade], [0, 1], {extrapolateRight: 'clamp', easing: Easing.inOut(Easing.quad)}) : 1;
  return (
    <AbsoluteFill style={{opacity}}>
      <OffthreadVideo muted src={staticFile(seg.file)} style={{width: '100%', height: '100%', transform: `scale(${scale})`}} />
    </AbsoluteFill>
  );
};

export const TurkeyReel: React.FC<{minimal?: boolean; bare?: boolean}> = ({minimal = false, bare = false}) => {
  const frame = useCurrentFrame();
  const fadeIn = interpolate(frame, [0, 6], [1, 0], {extrapolateRight: 'clamp'});
  // bare = picture and sound only; the text layer is composited in HyperFrames (edits/turkey-giveaway/hf)
  const overlays = bare ? [] : (timeline.overlays as Ov[]).filter((o) => !minimal || o.keepInMinimal);
  return (
    <AbsoluteFill style={{background: INK}}>
      {timeline.segments.map((seg) => (
        <Sequence key={seg.id} from={seg.from} durationInFrames={seg.dur} name={seg.id}>
          <Shot seg={seg} />
        </Sequence>
      ))}
      {/* gentle vignette to focus the eye; kept subtle so skin tones stay natural */}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 46%, rgba(0,0,0,0) 62%, rgba(0,0,0,0.12) 100%)'}} />
      {overlays.map((o, i) => (
        <Sequence key={i} from={o.from} durationInFrames={o.dur} name={o.type}>
          {renderOverlay(o, minimal)}
        </Sequence>
      ))}
      <AbsoluteFill style={{background: INK, opacity: fadeIn}} />
      <Audio src={staticFile('turkey/mix.wav')} />
    </AbsoluteFill>
  );
};

export const turkeyDuration = timeline.durationInFrames;
