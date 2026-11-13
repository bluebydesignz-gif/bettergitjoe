import {AbsoluteFill, Easing, interpolate, random, useCurrentFrame} from 'remotion';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

export type Look = {
  accent: string; // title color
  top: string; // grade tint, top of frame
  bottom: string; // grade tint, bottom of frame
  grain: number; // 0-0.3
};

// Placeholder look until the reference videos set the real palette.
export const DEFAULT_LOOK: Look = {
  accent: '#e8b04a',
  top: 'rgba(20,40,90,0.45)',
  bottom: 'rgba(230,140,40,0.40)',
  grain: 0.14,
};

export const Grade: React.FC<{look: Look}> = ({look}) => {
  const f = useCurrentFrame();
  return (
    <>
      <AbsoluteFill
        style={{
          background: `linear-gradient(180deg, ${look.top} 0%, rgba(0,0,0,0) 45%, rgba(0,0,0,0) 60%, ${look.bottom} 100%)`,
          mixBlendMode: 'soft-light',
        }}
      />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, transparent 50%, rgba(0,0,0,0.65) 100%)'}} />
      <AbsoluteFill style={{opacity: look.grain, mixBlendMode: 'overlay'}}>
        <svg width="100%" height="100%">
          <filter id={`bgrain-${f}`}>
            <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed={f % 500} />
            <feColorMatrix type="saturate" values="0" />
          </filter>
          <rect width="100%" height="100%" filter={`url(#bgrain-${f})`} />
        </svg>
      </AbsoluteFill>
    </>
  );
};

const chroma = (f: number, strength: number) => {
  const d = (random(`bc${f}`) - 0.5) * strength;
  return `${d}px 0 0 rgba(0,229,255,0.8), ${-d}px 0 0 rgba(255,0,64,0.8)`;
};

export const TitleCard: React.FC<{title: string; subtitle?: string; look: Look}> = ({title, subtitle, look}) => {
  const f = useCurrentFrame();
  const spacing = interpolate(f, [3, 40], [0.3, 0.03], {...clamp, easing: Easing.out(Easing.cubic)});
  const subO = interpolate(f, [10, 18], [0, 1], clamp);
  const subY = interpolate(f, [10, 22], [40, 0], {...clamp, easing: Easing.out(Easing.back(2))});
  const size = title.length > 8 ? 190 : 250;
  return (
    <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', flexDirection: 'column', padding: 60}}>
      <div
        style={{
          fontFamily: 'Anton',
          fontSize: size,
          lineHeight: 1,
          color: look.accent,
          textAlign: 'center',
          letterSpacing: `${spacing}em`,
          marginRight: `-${spacing}em`,
          opacity: f >= 3 ? 1 : 0,
          textShadow: chroma(f, f < 15 ? 20 : 6),
        }}
      >
        {title}
      </div>
      {subtitle && (
        <div
          style={{
            fontFamily: 'Space Mono',
            fontWeight: 700,
            fontSize: 52,
            color: 'white',
            letterSpacing: '0.4em',
            marginRight: '-0.4em',
            marginTop: 20,
            textAlign: 'center',
            opacity: subO,
            transform: `translateY(${subY}px)`,
          }}
        >
          {subtitle}
        </div>
      )}
    </AbsoluteFill>
  );
};

export const EndCard: React.FC<{title: string; subtitle?: string; duration: number; look: Look}> = ({
  title,
  subtitle,
  duration,
  look,
}) => {
  const f = useCurrentFrame();
  const scrim = interpolate(f, [0, 8], [0, 0.5], clamp);
  const out = interpolate(f, [duration - 12, duration], [1, 0], clamp);
  return (
    <AbsoluteFill style={{opacity: out}}>
      <AbsoluteFill style={{background: `rgba(0,0,0,${scrim})`}} />
      <TitleCard title={title} subtitle={subtitle} look={look} />
    </AbsoluteFill>
  );
};
