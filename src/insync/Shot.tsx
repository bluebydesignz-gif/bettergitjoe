import {
  AbsoluteFill,
  Easing,
  interpolate,
  OffthreadVideo,
  random,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import type {ClipInput, Shot as ShotT} from './timeline';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// Stand-in footage until the real clips arrive: moving party lights in Halloween colors.
const Placeholder: React.FC<{index: number; offset: number}> = ({index, offset}) => {
  const f = useCurrentFrame() + offset;
  const colors = ['#ff6a13', '#8b2cff', '#39ff88', '#ff2d55', '#ffb000'];
  return (
    <AbsoluteFill style={{background: '#07060a', overflow: 'hidden'}}>
      {Array.from({length: 7}).map((_, k) => {
        const s = index * 13 + k;
        const x = 50 + 40 * Math.sin(f * 0.03 * (1 + random(s) * 2) + random(s + 1) * 6);
        const y = 45 + 35 * Math.cos(f * 0.025 * (1 + random(s + 2)) + random(s + 3) * 6);
        const size = 300 + random(s + 4) * 600;
        return (
          <div
            key={k}
            style={{
              position: 'absolute',
              left: `${x}%`,
              top: `${y}%`,
              width: size,
              height: size,
              marginLeft: -size / 2,
              marginTop: -size / 2,
              borderRadius: '50%',
              background: `radial-gradient(circle, ${colors[(index + k) % colors.length]}cc 0%, transparent 65%)`,
            }}
          />
        );
      })}
      <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center'}}>
        <div style={{fontFamily: 'Space Mono', fontSize: 44, color: 'rgba(255,255,255,0.35)', letterSpacing: '0.3em'}}>
          RAW CLIP {String(index + 1).padStart(2, '0')}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

const Media: React.FC<{clip?: ClipInput; startSec: number; index: number; offsetFrames: number}> = ({
  clip,
  startSec,
  index,
  offsetFrames,
}) => {
  const {fps} = useVideoConfig();
  if (!clip) return <Placeholder index={index} offset={offsetFrames} />;
  return (
    <OffthreadVideo
      src={staticFile(clip.src)}
      startFrom={Math.round(startSec * fps) + offsetFrames}
      muted
      style={{width: '100%', height: '100%', objectFit: 'cover'}}
    />
  );
};

export const Shot: React.FC<{shot: ShotT; clip?: ClipInput; dim?: number}> = ({shot, clip, dim = 1}) => {
  const f = useCurrentFrame();
  const startSec = clip ? clip.moments[shot.moment % clip.moments.length] ?? 0 : 0;
  const id = `s${shot.index}-${f}`;

  // Slow push-in on every shot keeps the frame alive.
  let scale = interpolate(f, [0, shot.duration], [1.08, 1.0], clamp);
  let tx = 0;
  if (shot.fx === 'zoom') scale *= interpolate(f, [0, 7], [1.35, 1], {...clamp, easing: Easing.out(Easing.cubic)});
  if (shot.fx === 'whip') tx = interpolate(f, [0, 6], [70, 0], {...clamp, easing: Easing.out(Easing.cubic)});
  if (f < 3) tx += (random(`${id}x`) - 0.5) * 4; // impact shake

  const glitching = shot.fx === 'glitch' && f < Math.min(5, Math.floor(shot.duration / 2));
  const whipping = shot.fx === 'whip' && f < 5;
  const filters = [
    shot.bw ? 'grayscale(1) contrast(1.45) brightness(0.95)' : 'contrast(1.15) saturate(1.2) brightness(0.95)',
    glitching ? `url(#glitch-${id})` : '',
    whipping ? `url(#whip-${id})` : '',
    dim !== 1 ? `brightness(${dim})` : '',
  ].join(' ');

  const flash = shot.fx === 'flash' ? interpolate(f, [0, 4], [1, 0], clamp) : 0;

  // Stutter: repeat the first 3 frames three times, then play on.
  const media = shot.stutter ? (
    <>
      {[0, 3, 6].map((at) => (
        <Sequence key={at} from={at} durationInFrames={3} layout="none">
          <Media clip={clip} startSec={startSec} index={clip ? shot.clip : shot.index} offsetFrames={0} />
        </Sequence>
      ))}
      <Sequence from={9} layout="none">
        <Media clip={clip} startSec={startSec} index={clip ? shot.clip : shot.index} offsetFrames={3} />
      </Sequence>
    </>
  ) : (
    <Media clip={clip} startSec={startSec} index={clip ? shot.clip : shot.index} offsetFrames={0} />
  );

  return (
    <AbsoluteFill style={{overflow: 'hidden', background: 'black'}}>
      <svg width="0" height="0" style={{position: 'absolute'}}>
        <filter id={`glitch-${id}`} x="-10%" y="-10%" width="120%" height="120%">
          <feTurbulence type="fractalNoise" baseFrequency="0.00001 0.05" numOctaves="1" seed={(shot.index * 31 + f) % 997} result="noise" />
          <feDisplacementMap in="SourceGraphic" in2="noise" scale="120" xChannelSelector="R" yChannelSelector="B" result="disp" />
          <feColorMatrix in="disp" type="matrix" values="1 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 1 0" result="r" />
          <feOffset in="r" dx="18" result="r2" />
          <feColorMatrix in="disp" type="matrix" values="0 0 0 0 0  0 1 0 0 0  0 0 0 0 0  0 0 0 1 0" result="g" />
          <feColorMatrix in="disp" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 1 0 0  0 0 0 1 0" result="b" />
          <feOffset in="b" dx="-18" result="b2" />
          <feBlend in="r2" in2="g" mode="screen" result="rg" />
          <feBlend in="rg" in2="b2" mode="screen" />
        </filter>
        <filter id={`whip-${id}`} x="-20%" y="0" width="140%" height="100%">
          <feGaussianBlur stdDeviation="60 0" />
        </filter>
      </svg>
      <AbsoluteFill style={{transform: `translateX(${tx}%) scale(${scale})`, filter: filters}}>{media}</AbsoluteFill>
      {flash > 0 && <AbsoluteFill style={{background: 'white', opacity: flash}} />}
    </AbsoluteFill>
  );
};
