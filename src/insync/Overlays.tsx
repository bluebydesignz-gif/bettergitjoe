import {AbsoluteFill, Easing, interpolate, random, useCurrentFrame} from 'remotion';
import {FPS} from './timeline';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const ORANGE = '#ff6a13';

// Halloween grade, vignette and film grain over the whole reel.
export const Grade: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <>
      <AbsoluteFill
        style={{
          background:
            'linear-gradient(180deg, rgba(110,30,170,0.55) 0%, rgba(0,0,0,0) 45%, rgba(0,0,0,0) 60%, rgba(255,100,20,0.5) 100%)',
          mixBlendMode: 'soft-light',
        }}
      />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, transparent 45%, rgba(0,0,0,0.7) 100%)'}} />
      <AbsoluteFill style={{opacity: 0.16, mixBlendMode: 'overlay'}}>
        <svg width="100%" height="100%">
          <filter id={`grain-${f}`}>
            <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={f % 500} />
            <feColorMatrix type="saturate" values="0" />
          </filter>
          <rect width="100%" height="100%" filter={`url(#grain-${f})`} />
        </svg>
      </AbsoluteFill>
    </>
  );
};

// Spooky flicker: mostly on, with random dropouts.
const flicker = (f: number, seed: string, rate = 0.18) => (random(`${seed}${f}`) < rate ? 0.15 : 1);

const chroma = (f: number, strength: number) => {
  const d = (random(`c${f}`) - 0.5) * strength;
  return `${d}px 0 0 rgba(0,229,255,0.85), ${-d}px 0 0 rgba(255,0,64,0.85)`;
};

export const IntroTitle: React.FC = () => {
  const f = useCurrentFrame();
  const show = f >= 5;
  const spacing = interpolate(f, [5, 50], [0.35, 0.04], {...clamp, easing: Easing.out(Easing.cubic)});
  const subY = interpolate(f, [12, 24], [40, 0], {...clamp, easing: Easing.out(Easing.back(2))});
  const subO = interpolate(f, [12, 20], [0, 1], clamp);
  const op = show ? flicker(f, 'intro', f < 20 ? 0.35 : 0.1) : 0;
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', flexDirection: 'column'}}>
      <div
        style={{
          fontFamily: 'Anton',
          fontSize: 250,
          lineHeight: 1,
          color: ORANGE,
          letterSpacing: `${spacing}em`,
          marginRight: `-${spacing}em`,
          opacity: op,
          textShadow: chroma(f, f < 20 ? 24 : 8),
        }}
      >
        INSYNC
      </div>
      <div
        style={{
          fontFamily: 'Space Mono',
          fontWeight: 700,
          fontSize: 58,
          color: 'white',
          letterSpacing: '0.55em',
          marginRight: '-0.55em',
          marginTop: 18,
          transform: `translateY(${subY}px)`,
          opacity: subO * op,
        }}
      >
        HALLOWEEN
      </div>
    </AbsoluteFill>
  );
};

export const MidTitle: React.FC = () => {
  const f = useCurrentFrame();
  const scale = interpolate(f, [0, 6], [1.4, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  const strobe = f < 8 ? (f % 2 === 0 ? 1 : 0.2) : 1;
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
      <div
        style={{
          fontFamily: 'Anton',
          fontSize: 330,
          color: 'white',
          mixBlendMode: 'difference',
          transform: `scale(${scale}) rotate(-4deg)`,
          opacity: strobe,
          lineHeight: 1,
        }}
      >
        INSYNC
      </div>
    </AbsoluteFill>
  );
};

export const EndCard: React.FC<{duration: number}> = ({duration}) => {
  const f = useCurrentFrame();
  const letters = 'INSYNC'.split('');
  const sub = interpolate(f, [18, 30], [0, 1], clamp);
  const out = interpolate(f, [duration - 15, duration], [1, 0], clamp);
  const scrim = interpolate(f, [0, 8], [0, 0.45], clamp);
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', flexDirection: 'column', opacity: out}}>
      <AbsoluteFill style={{background: `rgba(0,0,0,${scrim})`}} />
      <div style={{display: 'flex', fontFamily: 'Anton', fontSize: 250, lineHeight: 1, color: ORANGE}}>
        {letters.map((l, i) => {
          const on = f > 3 + i * 2;
          return (
            <span key={i} style={{opacity: on ? flicker(f, `e${i}`, 0.08) : 0, textShadow: chroma(f + i, 6)}}>
              {l}
            </span>
          );
        })}
      </div>
      <div
        style={{
          fontFamily: 'Space Mono',
          fontWeight: 700,
          fontSize: 58,
          color: 'white',
          letterSpacing: '0.55em',
          marginRight: '-0.55em',
          marginTop: 18,
          opacity: sub,
        }}
      >
        HALLOWEEN
      </div>
    </AbsoluteFill>
  );
};

// Camcorder-style HUD in the top safe zone during the montage.
export const Hud: React.FC = () => {
  const f = useCurrentFrame();
  const secs = f / FPS;
  const tc = `00:${String(Math.floor(secs)).padStart(2, '0')}:${String(f % FPS).padStart(2, '0')}`;
  const style: React.CSSProperties = {fontFamily: 'Space Mono', fontSize: 30, color: 'rgba(255,255,255,0.85)', letterSpacing: '0.12em'};
  return (
    <AbsoluteFill style={{padding: '170px 70px', flexDirection: 'row', justifyContent: 'space-between'}}>
      <div style={style}>
        <span style={{color: '#ff2d2d', opacity: Math.floor(f / 15) % 2 ? 1 : 0.2}}>●</span> REC
      </div>
      <div style={style}>{tc}</div>
    </AbsoluteFill>
  );
};
