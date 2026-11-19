import React, {useEffect, useState} from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  OffthreadVideo,
  Sequence,
  continueRender,
  delayRender,
  interpolate,
  random,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  Easing,
} from 'remotion';

// ---------- palette (Vice-city neon) ----------
const PINK = '#ff2bd6';
const HOT = '#ff3d81';
const CYAN = '#21f3ff';
const PURPLE = '#7a2bff';
const SUN = '#ffcc33';
const NAVY = 'rgba(16, 6, 40, 0.82)';

// ---------- timeline (frames @30fps) ----------
export const GTA_FPS = 30;
export const GTA_DURATION = 780;
const T = {
  intro: [0, 120],
  card1: [120, 210],
  card2: [210, 300],
  card3: [300, 390],
  card4: [390, 480],
  selected: [480, 570],
  mission: [570, 675],
  end: [675, 780],
} as const;
const CUTS = [120, 210, 300, 390, 480, 570, 675];

// ---------- fonts ----------
const FONTS: [string, string][] = [
  ['Bungee', 'fonts/Bungee-Regular.ttf'],
  ['Russo', 'fonts/RussoOne-Regular.ttf'],
  ['Pixel', 'fonts/PressStart2P-Regular.ttf'],
  ['Brush', 'fonts/KaushanScript-Regular.ttf'],
];
const useFonts = () => {
  const [handle] = useState(() => delayRender('fonts'));
  useEffect(() => {
    Promise.all(
      FONTS.map(([name, file]) => {
        const f = new FontFace(name, `url(${staticFile(file)})`);
        return f.load().then((loaded) => document.fonts.add(loaded));
      }),
    ).then(() => continueRender(handle));
  }, [handle]);
};

// ---------- footage ----------
const GRADE = 'saturate(1.35) contrast(1.1) brightness(1.04)';
const Shot: React.FC<{src: string; rate?: number; zoom?: [number, number]; dur: number}> = ({
  src,
  rate = 1,
  zoom = [1, 1],
  dur,
}) => {
  const f = useCurrentFrame();
  const s = interpolate(f, [0, dur], zoom, {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{overflow: 'hidden', backgroundColor: '#000'}}>
      <OffthreadVideo
        src={staticFile(src)}
        playbackRate={rate}
        muted
        style={{width: '100%', height: '100%', objectFit: 'cover', filter: GRADE, transform: `scale(${s})`}}
      />
      {/* sunset tint: magenta sky, teal shadows */}
      <AbsoluteFill
        style={{
          background: 'linear-gradient(180deg, rgba(255,60,200,0.22) 0%, rgba(255,140,80,0.10) 40%, rgba(0,200,255,0.12) 100%)',
          mixBlendMode: 'soft-light',
        }}
      />
      <AbsoluteFill
        style={{background: 'radial-gradient(ellipse at 50% 45%, transparent 55%, rgba(20,0,40,0.55) 100%)'}}
      />
    </AbsoluteFill>
  );
};

// ---------- glitch helpers ----------
const glitchAmt = (frame: number) => {
  // spikes around every cut
  let a = 0;
  for (const c of CUTS) {
    const d = frame - c;
    if (d >= -3 && d <= 5) a = Math.max(a, 1 - Math.abs(d + (d < 0 ? 0 : 0)) / 6);
  }
  return a;
};

const CutGlitch: React.FC = () => {
  const frame = useCurrentFrame();
  const a = glitchAmt(frame);
  if (a <= 0) return null;
  const bars = new Array(7).fill(0).map((_, i) => {
    const y = random(`y${frame}${i}`) * 1920;
    const h = 20 + random(`h${frame}${i}`) * 120;
    const x = (random(`x${frame}${i}`) - 0.5) * 160 * a;
    const c = i % 2 ? PINK : CYAN;
    return (
      <div
        key={i}
        style={{position: 'absolute', left: x, top: y, width: 1080, height: h, background: c, opacity: 0.28 * a, mixBlendMode: 'screen'}}
      />
    );
  });
  const flash = CUTS.includes(frame) ? 0.55 : 0;
  return (
    <AbsoluteFill>
      {bars}
      <AbsoluteFill style={{background: '#fff', opacity: flash}} />
    </AbsoluteFill>
  );
};

// chromatic neon text: two offset copies + gradient face
const NeonText: React.FC<{
  text: string;
  size: number;
  font?: string;
  jitter?: number;
  grad?: string;
  style?: React.CSSProperties;
  seed?: string;
}> = ({text, size, font = 'Bungee', jitter = 0, grad, style, seed = 'n'}) => {
  const frame = useCurrentFrame();
  const jx = (random(`${seed}x${frame}`) - 0.5) * jitter;
  const jy = (random(`${seed}y${frame}`) - 0.5) * jitter * 0.4;
  const base: React.CSSProperties = {
    fontFamily: font,
    fontSize: size,
    lineHeight: 1,
    whiteSpace: 'nowrap',
    position: 'absolute',
    left: 0,
    top: 0,
  };
  const g = grad ?? `linear-gradient(180deg, ${CYAN} 0%, #b9fbff 35%, ${PINK} 62%, ${PURPLE} 100%)`;
  return (
    <div style={{position: 'relative', ...style}}>
      <div style={{...base, position: 'relative', visibility: 'hidden'}}>{text}</div>
      <div style={{...base, color: CYAN, opacity: 0.85, transform: `translate(${-6 - jx}px, ${jy}px)`, filter: 'blur(1px)'}}>{text}</div>
      <div style={{...base, color: PINK, opacity: 0.85, transform: `translate(${6 + jx}px, ${-jy}px)`, filter: 'blur(1px)'}}>{text}</div>
      <div
        style={{
          ...base,
          backgroundImage: g,
          WebkitBackgroundClip: 'text',
          backgroundClip: 'text',
          color: 'transparent',
          transform: `translate(${jx * 0.3}px, 0)`,
          filter: `drop-shadow(0 0 ${size * 0.12}px rgba(255,43,214,0.75)) drop-shadow(0 0 ${size * 0.05}px rgba(33,243,255,0.9))`,
        }}
      >
        {text}
      </div>
    </div>
  );
};

// ---------- sunset / palm / San Antonio skyline badge ----------
const SunsetBadge: React.FC<{w: number}> = ({w}) => (
  <svg width={w} height={w * 0.75} viewBox="0 0 200 150">
    <defs>
      <linearGradient id="sun" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stopColor={SUN} />
        <stop offset="0.55" stopColor={HOT} />
        <stop offset="1" stopColor={PURPLE} />
      </linearGradient>
      <clipPath id="sunclip">
        <rect x="0" y="0" width="200" height="82" />
        <rect x="0" y="86" width="200" height="6" />
        <rect x="0" y="96" width="200" height="5" />
        <rect x="0" y="105" width="200" height="4" />
      </clipPath>
    </defs>
    <circle cx="110" cy="78" r="56" fill="url(#sun)" clipPath="url(#sunclip)" />
    {/* skyline with Tower of the Americas */}
    <g fill="#14062a">
      <rect x="40" y="96" width="16" height="34" />
      <rect x="58" y="84" width="12" height="46" />
      <rect x="72" y="100" width="18" height="30" />
      <rect x="128" y="90" width="14" height="40" />
      <rect x="144" y="102" width="20" height="28" />
      <rect x="104" y="40" width="5" height="90" />
      <ellipse cx="106.5" cy="40" rx="13" ry="6" />
      <rect x="101" y="30" width="11" height="6" />
      <rect x="20" y="126" width="170" height="10" />
    </g>
    <g stroke={CYAN} strokeWidth="1.5" fill="none" opacity="0.9">
      <path d="M40 96 h16 M58 84 h12 M128 90 h14 M144 102 h20" />
    </g>
    {/* palm */}
    <g fill="#14062a">
      <path d="M172 136 C170 110 166 88 160 62 L163 61 C170 88 175 110 177 136 Z" />
      <path d="M161 62 C150 50 132 50 120 58 C136 54 150 56 161 64 Z" />
      <path d="M161 62 C158 46 146 36 132 34 C146 42 154 52 160 64 Z" />
      <path d="M162 62 C170 46 184 40 198 44 C184 46 172 54 163 64 Z" />
      <path d="M162 62 C176 56 192 62 198 74 C188 66 174 62 162 65 Z" />
      <path d="M161 62 C162 48 168 36 176 30 C170 42 166 52 163 64 Z" />
    </g>
  </svg>
);

const Wings: React.FC<{w: number; style?: React.CSSProperties}> = ({w, style}) => (
  <Img src={staticFile('ccc/wings.png')} style={{width: w, ...style}} />
);

// ---------- intro: loading screen ----------
const Intro: React.FC = () => {
  const frame = useCurrentFrame();
  const inA = spring({frame: frame - 8, fps: GTA_FPS, config: {damping: 12, stiffness: 120}});
  const flick = frame < 26 ? (random(`fl${frame}`) > 0.45 ? 1 : 0.15) : 1;
  const dots = '.'.repeat(1 + (Math.floor(frame / 8) % 3));
  const prog = interpolate(frame, [20, 112], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.quad)});
  const tagIn = spring({frame: frame - 26, fps: GTA_FPS, config: {damping: 9}});
  const jitter = frame < 30 ? 30 : 4 + 10 * Math.max(0, Math.sin(frame * 0.9)) * (random(`j${Math.floor(frame / 6)}`) > 0.7 ? 1 : 0);
  return (
    <AbsoluteFill>
      <Shot src="ccc/intro.mp4" dur={120} zoom={[1.0, 1.06]} />
      <AbsoluteFill style={{alignItems: 'center', top: 560, opacity: flick, transform: `scale(${0.6 + 0.4 * inA})`}}>
        <NeonText text="CERTIFIED" size={136} jitter={jitter} seed="t1" />
        <div style={{height: 10}} />
        <NeonText text="COLLISION" size={136} jitter={jitter} seed="t2" />
        <div
          style={{
            position: 'absolute',
            top: 128,
            transform: `rotate(-4deg) scale(${tagIn})`,
            fontFamily: 'Russo',
            fontSize: 64,
            color: '#fff',
            letterSpacing: 1,
            WebkitTextStroke: '3px #14062a',
            textShadow: `0 0 18px ${CYAN}, 4px 4px 0 ${PURPLE}`,
            padding: '2px 22px',
          }}
        >
          gta edition
        </div>
      </AbsoluteFill>
      {/* LOADING + bar */}
      <AbsoluteFill style={{top: 1060, alignItems: 'center'}}>
        <div style={{fontFamily: 'Pixel', fontSize: 50, color: '#fff', textShadow: `0 0 12px ${PINK}, 3px 3px 0 #000`, width: 520}}>
          LOADING{dots}
        </div>
        <div style={{marginTop: 34, width: 640, height: 18, border: `3px solid ${CYAN}`, boxShadow: `0 0 16px ${CYAN}`, background: 'rgba(0,0,0,0.45)'}}>
          <div style={{width: `${prog * 100}%`, height: '100%', background: `linear-gradient(90deg, ${CYAN}, ${PINK})`}} />
        </div>
        <div style={{marginTop: 22, fontFamily: 'Russo', fontSize: 30, color: '#fff', textShadow: '2px 2px 0 #000', letterSpacing: 2}}>
          8880 OAKLAND RD · SAN ANTONIO, TX
        </div>
      </AbsoluteFill>
      {/* GTA-like spinner bottom right */}
      <div style={{position: 'absolute', right: 70, top: 1480, width: 70, height: 70}}>
        <svg width="70" height="70" viewBox="0 0 70 70" style={{transform: `rotate(${frame * 12}deg)`}}>
          <circle cx="35" cy="35" r="26" stroke="rgba(255,255,255,0.25)" strokeWidth="8" fill="none" />
          <path d="M35 9 A26 26 0 0 1 61 35" stroke="#fff" strokeWidth="8" fill="none" strokeLinecap="round" />
        </svg>
      </div>
    </AbsoluteFill>
  );
};

// ---------- service select card ----------
type CardProps = {
  index: number;
  title: string;
  stats: [string, number][];
  chip?: string;
  y: number;
};
const ServiceCard: React.FC<CardProps> = ({index, title, stats, chip, y}) => {
  const frame = useCurrentFrame();
  const inS = spring({frame, fps: GTA_FPS, config: {damping: 13, stiffness: 160}});
  const out = interpolate(frame, [82, 90], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const flick = frame < 6 ? (frame % 2 ? 0.3 : 1) : 1;
  const W = 940;
  return (
    <div
      style={{
        position: 'absolute',
        left: 70,
        top: y,
        width: W,
        opacity: flick * (1 - out),
        transform: `translateX(${(1 - inS) * -700 + out * 500}px) skewX(-9deg) scale(${0.84 + 0.08 * inS})`,
        transformOrigin: 'left center',
      }}
    >
      {/* header */}
      <div
        style={{
          position: 'relative',
          height: 128,
          background: NAVY,
          border: `4px solid ${CYAN}`,
          borderRadius: 22,
          boxShadow: `0 0 24px ${CYAN}, inset 0 0 18px rgba(33,243,255,0.35)`,
          display: 'flex',
          alignItems: 'center',
          paddingLeft: 26,
          width: W - 120,
        }}
      >
        <Wings w={120} style={{transform: 'skewX(9deg)', marginRight: 14}} />
        <div
          style={{
            fontFamily: 'Russo',
            fontSize: title.length > 18 ? 38 : title.length > 14 ? 42 : 52,
            color: '#fff',
            letterSpacing: 1,
            textShadow: `0 0 10px ${PINK}, 3px 3px 0 ${PURPLE}`,
            whiteSpace: 'nowrap',
          }}
        >
          {title}
        </div>
        <div style={{position: 'absolute', right: -150, top: -88, transform: 'skewX(9deg)'}}>
          <SunsetBadge w={230} />
        </div>
      </div>
      {/* stats panel */}
      <div
        style={{
          marginTop: 14,
          height: 300,
          background: NAVY,
          border: `4px solid ${PINK}`,
          borderRadius: 22,
          boxShadow: `0 0 26px ${PINK}, inset 0 0 18px rgba(255,43,214,0.35)`,
          display: 'flex',
          padding: '26px 30px',
          gap: 28,
        }}
      >
        <div style={{flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'space-between'}}>
          {stats.map(([label, v], i) => {
            const fill = interpolate(frame, [8 + i * 4, 30 + i * 4], [0, v], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
              easing: Easing.out(Easing.cubic),
            });
            return (
              <div key={label} style={{display: 'flex', alignItems: 'center', gap: 20}}>
                <div style={{width: 280, fontFamily: 'Russo', fontStyle: 'italic', fontSize: 34, color: '#fff', textShadow: '2px 2px 0 #000'}}>
                  {label}
                </div>
                <div style={{flex: 1, height: 26, background: 'rgba(255,255,255,0.12)', borderRadius: 4, overflow: 'hidden'}}>
                  <div
                    style={{
                      width: `${fill * 100}%`,
                      height: '100%',
                      background: `linear-gradient(90deg, ${CYAN}, ${PINK})`,
                      boxShadow: `0 0 12px ${PINK}`,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
        <div style={{width: 190, display: 'flex', flexDirection: 'column', alignItems: 'center', borderLeft: `3px solid ${CYAN}`, paddingLeft: 20}}>
          <div style={{fontFamily: 'Russo', fontSize: 36, color: '#fff', letterSpacing: 2}}>CLASS</div>
          <div
            style={{
              marginTop: 12,
              width: 150,
              height: 150,
              border: `5px solid ${PINK}`,
              borderRadius: 18,
              boxShadow: `0 0 22px ${PINK}, inset 0 0 22px ${PINK}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <NeonText text="S" size={110} seed={`c${index}`} jitter={frame < 12 ? 18 : 0} grad={`linear-gradient(180deg, #fff, ${PINK})`} />
          </div>
        </div>
      </div>
      {/* footer: chip + selector */}
      <div style={{marginTop: 18, display: 'flex', alignItems: 'center', gap: 22}}>
        <div style={{fontFamily: 'Pixel', fontSize: 30, color: '#fff', textShadow: `0 0 10px ${CYAN}, 3px 3px 0 #000`}}>
          {'◀'} {index}/4 {'▶'}
        </div>
        {chip ? (
          <div
            style={{
              fontFamily: 'Russo',
              fontSize: 30,
              color: '#14062a',
              background: `linear-gradient(90deg, ${CYAN}, #b9fbff)`,
              padding: '8px 20px',
              borderRadius: 10,
              boxShadow: `0 0 16px ${CYAN}`,
            }}
          >
            {chip}
          </div>
        ) : null}
      </div>
    </div>
  );
};

const STATS = (a: number, b: number, c: number, d: number): [string, number][] => [
  ['QUALITY', a],
  ['PAINT MATCH', b],
  ['PRECISION', c],
  ['CARE', d],
];

// ---------- shop selected ----------
const Selected: React.FC = () => {
  const frame = useCurrentFrame();
  const s = spring({frame: frame - 4, fps: GTA_FPS, config: {damping: 8, stiffness: 140}});
  const check = interpolate(frame, [10, 22], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const out = interpolate(frame, [82, 90], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div
      style={{
        position: 'absolute',
        left: 60,
        top: 1080,
        width: 960,
        height: 330,
        opacity: 1 - out,
        transform: `scale(${0.4 + 0.6 * s}) skewX(-8deg)`,
        background: NAVY,
        border: `5px solid ${CYAN}`,
        borderRadius: 30,
        boxShadow: `0 0 30px ${CYAN}, 0 0 60px rgba(255,43,214,0.6)`,
        display: 'flex',
        alignItems: 'center',
        padding: '0 40px',
        gap: 36,
      }}
    >
      <div
        style={{
          width: 190,
          height: 190,
          border: `7px solid ${PINK}`,
          borderRadius: 26,
          boxShadow: `0 0 26px ${PINK}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <svg width="150" height="150" viewBox="0 0 100 100">
          <path
            d="M18 52 L42 76 L84 26"
            stroke={CYAN}
            strokeWidth="14"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeDasharray="120"
            strokeDashoffset={120 * (1 - check)}
            style={{filter: `drop-shadow(0 0 8px ${CYAN})`}}
          />
        </svg>
      </div>
      <div style={{display: 'flex', flexDirection: 'column'}}>
        <NeonText text="SHOP" size={120} font="Russo" seed="sh" grad={`linear-gradient(180deg, #fff 0%, ${CYAN} 100%)`} />
        <div
          style={{
            fontFamily: 'Brush',
            fontSize: 118,
            marginTop: -6,
            color: HOT,
            textShadow: `0 0 18px ${PINK}, 4px 4px 0 ${PURPLE}`,
          }}
        >
          Selected
        </div>
      </div>
      <div style={{position: 'absolute', right: -40, top: -120}}>
        <SunsetBadge w={260} />
      </div>
    </div>
  );
};

// ---------- mission: minimap + subtitle + law ----------
const Minimap: React.FC = () => {
  const frame = useCurrentFrame();
  const route = interpolate(frame, [6, 50], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const pulse = 1 + 0.18 * Math.sin(frame * 0.35);
  return (
    <div
      style={{
        position: 'absolute',
        left: 60,
        top: 1150,
        width: 360,
        height: 360,
        borderRadius: '50%',
        overflow: 'hidden',
        border: '6px solid rgba(255,255,255,0.85)',
        boxShadow: `0 0 24px ${CYAN}`,
        background: 'rgba(30, 40, 60, 0.85)',
      }}
    >
      <svg width="360" height="360" viewBox="0 0 360 360">
        <rect width="360" height="360" fill="#3a4a3a" opacity="0.5" />
        <g stroke="#cfd6e2" strokeWidth="16" opacity="0.8" fill="none">
          <path d="M-20 250 L380 120" />
          <path d="M120 -20 L180 380" />
          <path d="M260 -20 L230 380" />
        </g>
        <g stroke="#9aa4b4" strokeWidth="7" opacity="0.6" fill="none">
          <path d="M-20 60 L380 40" />
          <path d="M40 -20 L70 380" />
          <path d="M-20 330 L380 300" />
        </g>
        <path
          d="M175 300 L160 205 L245 172 L240 95"
          stroke={PINK}
          strokeWidth="9"
          fill="none"
          strokeLinejoin="round"
          strokeDasharray="400"
          strokeDashoffset={400 * (1 - route)}
          style={{filter: `drop-shadow(0 0 6px ${PINK})`}}
        />
        <g transform={`translate(240 95) scale(${pulse})`}>
          <circle r="22" fill={SUN} stroke="#000" strokeWidth="3" />
          <text y="9" textAnchor="middle" fontFamily="Russo" fontSize="26" fill="#000">
            C
          </text>
        </g>
        <path d="M175 285 l-16 30 l16 -9 l16 9 z" fill="#fff" stroke="#000" strokeWidth="2" />
        <text x="270" y="150" fontFamily="Russo" fontSize="20" fill="#fff" transform="rotate(-18 270 150)">
          OAKLAND RD
        </text>
      </svg>
    </div>
  );
};

const Mission: React.FC = () => {
  const frame = useCurrentFrame();
  const a = interpolate(frame, [0, 8], [0, 1], {extrapolateRight: 'clamp'});
  const b = interpolate(frame, [24, 34], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const lawS = spring({frame: frame - 40, fps: GTA_FPS, config: {damping: 11}});
  return (
    <AbsoluteFill>
      {/* mission title, GTA-style top */}
      <div style={{position: 'absolute', top: 250, width: '100%', textAlign: 'center', opacity: a}}>
        <div style={{fontFamily: 'Brush', fontSize: 92, color: SUN, textShadow: `0 0 16px ${HOT}, 4px 4px 0 #000`}}>New Mission</div>
        <div style={{fontFamily: 'Russo', fontSize: 58, color: '#fff', marginTop: 4, textShadow: '4px 4px 0 #000', letterSpacing: 1}}>
          CHOOSE YOUR BODY SHOP
        </div>
      </div>
      {/* law banner */}
      <div
        style={{
          position: 'absolute',
          top: 520,
          left: 70,
          width: 940,
          transform: `scale(${lawS}) skewX(-8deg)`,
          background: NAVY,
          border: `4px solid ${PINK}`,
          borderRadius: 20,
          boxShadow: `0 0 24px ${PINK}`,
          padding: '22px 30px',
          textAlign: 'center',
        }}
      >
        <div style={{fontFamily: 'Pixel', fontSize: 26, color: CYAN, letterSpacing: 2}}>TEXAS LAW</div>
        <div style={{fontFamily: 'Russo', fontSize: 50, color: '#fff', marginTop: 12, lineHeight: 1.15, textShadow: `3px 3px 0 ${PURPLE}`}}>
          YOU HAVE THE RIGHT TO CHOOSE YOUR BODY SHOP
        </div>
      </div>
      <Minimap />
      {/* subtitle with GTA colour-coded keywords */}
      <div
        style={{
          position: 'absolute',
          left: 460,
          top: 1220,
          width: 560,
          opacity: b,
          fontFamily: 'Russo',
          fontSize: 44,
          lineHeight: 1.25,
          color: '#fff',
          textShadow: '3px 3px 0 #000, 0 0 10px #000',
        }}
      >
        Head to <span style={{color: SUN}}>Certified Collision</span> on <span style={{color: CYAN}}>Oakland Rd</span>.
      </div>
    </AbsoluteFill>
  );
};

// ---------- end card ----------
const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const s = spring({frame: frame - 2, fps: GTA_FPS, config: {damping: 10, stiffness: 110}});
  const passed = spring({frame: frame - 14, fps: GTA_FPS, config: {damping: 9}});
  const info = interpolate(frame, [30, 42], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const fade = interpolate(frame, [92, 105], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const gridY = (frame * 6) % 80;
  return (
    <AbsoluteFill style={{background: `linear-gradient(180deg, #12002e 0%, #3b0a5e 45%, #ff3d81 72%, #ffb347 100%)`, opacity: fade}}>
      {/* retro sun + grid floor */}
      <svg width="1080" height="1920" style={{position: 'absolute'}}>
        <defs>
          <linearGradient id="bigsun" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor={SUN} />
            <stop offset="1" stopColor={HOT} />
          </linearGradient>
        </defs>
        <circle cx="540" cy="1260" r="330" fill="url(#bigsun)" opacity="0.85" />
        {[0, 1, 2, 3, 4, 5].map((i) => (
          <rect key={i} x="0" y={1180 + i * 34} width="1080" height={6 + i * 3} fill="#3b0a5e" opacity="0.9" />
        ))}
        <rect x="0" y="1380" width="1080" height="540" fill="#14062a" />
        <g stroke={PINK} strokeWidth="3" opacity="0.8">
          {new Array(9).fill(0).map((_, i) => (
            <line key={`h${i}`} x1="0" x2="1080" y1={1400 + ((i * 80 + gridY) % 560)} y2={1400 + ((i * 80 + gridY) % 560)} />
          ))}
          {new Array(15).fill(0).map((_, i) => (
            <line key={`v${i}`} x1={540 + (i - 7) * 60} y1="1380" x2={540 + (i - 7) * 320} y2="1920" />
          ))}
        </g>
      </svg>
      <AbsoluteFill style={{alignItems: 'center', top: 230}}>
        <div style={{transform: `scale(${s})`, filter: `drop-shadow(0 0 30px ${CYAN})`}}>
          <Wings w={760} />
        </div>
        <Img src={staticFile('ccc/script.png')} style={{width: 900, marginTop: 30, transform: `scale(${s})`, filter: 'drop-shadow(0 0 14px rgba(255,255,255,0.7)) brightness(1.15)'}} />
        <div style={{marginTop: 40, transform: `scale(${passed}) rotate(-3deg)`}}>
          <div style={{fontFamily: 'Brush', fontSize: 120, color: SUN, textShadow: `0 0 20px ${HOT}, 5px 5px 0 #000`, textAlign: 'center'}}>
            Mission Passed
          </div>
        </div>
        <div style={{opacity: info, marginTop: 30, textAlign: 'center'}}>
          <div style={{fontFamily: 'Russo', fontSize: 50, color: '#fff', textShadow: '3px 3px 0 #000'}}>8880 OAKLAND RD</div>
          <div style={{fontFamily: 'Russo', fontSize: 40, color: '#fff', textShadow: '3px 3px 0 #000', marginTop: 6}}>SAN ANTONIO, TX 78240</div>
          <div style={{fontFamily: 'Bungee', fontSize: 86, color: CYAN, marginTop: 24, WebkitTextStroke: '4px #14062a', paintOrder: 'stroke fill', textShadow: `0 0 18px ${CYAN}, 5px 5px 0 #14062a`}}>
            210-663-6577
          </div>
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

// ---------- persistent HUD bits ----------
const Hud: React.FC = () => {
  return (
    <div style={{position: 'absolute', top: 230, right: 60, textAlign: 'right'}}>
      <div style={{fontFamily: 'Pixel', fontSize: 22, color: '#fff', textShadow: `0 0 8px ${PINK}, 2px 2px 0 #000`}}>SAN ANTONIO</div>
      <div style={{fontFamily: 'Russo', fontSize: 30, color: CYAN, textShadow: '2px 2px 0 #000', marginTop: 8}}>NORTHWEST SIDE</div>
    </div>
  );
};

const len = (r: readonly [number, number]) => r[1] - r[0];

export const CertifiedGTA: React.FC = () => {
  useFonts();
  const {fps} = useVideoConfig();
  return (
    <AbsoluteFill style={{backgroundColor: '#000'}}>
      <Sequence from={T.intro[0]} durationInFrames={len(T.intro)}>
        <Intro />
      </Sequence>

      <Sequence from={T.card1[0]} durationInFrames={len(T.card1)}>
        <Shot src="ccc/sign.mp4" dur={90} zoom={[1.0, 1.08]} />
        <ServiceCard index={1} title="COLLISION REPAIR" stats={STATS(0.96, 0.92, 0.95, 0.98)} chip="INSURANCE APPROVED" y={1090} />
        <Hud />
      </Sequence>

      <Sequence from={T.card2[0]} durationInFrames={len(T.card2)}>
        <Shot src="ccc/roof.mp4" dur={90} rate={2.8} />
        <ServiceCard index={2} title="HAIL DAMAGE REPAIR" stats={STATS(0.95, 0.9, 0.94, 0.97)} y={1090} />
        <Hud />
      </Sequence>

      <Sequence from={T.card3[0]} durationInFrames={len(T.card3)}>
        <Shot src="ccc/door.mp4" dur={90} zoom={[1.0, 1.05]} />
        <ServiceCard index={3} title="PAINTLESS DENT REPAIR" stats={STATS(0.94, 0.97, 0.96, 0.95)} y={300} />
      </Sequence>

      <Sequence from={T.card4[0]} durationInFrames={len(T.card4)}>
        <Shot src="ccc/pole.mp4" dur={90} />
        <ServiceCard index={4} title="AUTO REPAIR" stats={STATS(0.95, 0.91, 0.93, 0.98)} chip="LIMITED LIFETIME WARRANTY" y={330} />
      </Sequence>

      <Sequence from={T.selected[0]} durationInFrames={len(T.selected)}>
        <Shot src="ccc/front.mp4" dur={90} zoom={[1.0, 1.1]} />
        <Selected />
        <Hud />
      </Sequence>

      <Sequence from={T.mission[0]} durationInFrames={len(T.mission)}>
        <Shot src="ccc/reveal.mp4" dur={105} rate={0.97} />
        <Mission />
      </Sequence>

      <Sequence from={T.end[0]} durationInFrames={len(T.end)}>
        <EndCard />
      </Sequence>

      <CutGlitch />
      <Audio src={staticFile('ccc/music.wav')} />
      {fps !== GTA_FPS ? null : null}
    </AbsoluteFill>
  );
};
