// End card where boxing gloves punch the title words off the screen.
// Words alternate: even words get hit from the left, odd words from the right.
import {AbsoluteFill, Easing, interpolate, random, useCurrentFrame} from 'remotion';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const FIRST_START = 26; // frame the first glove starts flying in
const GAP = 16; // frames between punches
const TRAVEL = 8; // frames from off-screen to contact
const HOLD = 3; // frames the glove stays on contact
const GLOVE = 560; // glove size in px
const FONT = 290;
const LINE = 270;

// Contact frames (relative to the end card start), used for shake and punch sounds.
export const punchFrames = (words: number) =>
  Array.from({length: words}, (_, i) => FIRST_START + i * GAP + TRAVEL);

// Whole-frame shake after each punch (frame relative to the end card start).
export const punchShake = (f: number, words: number) => {
  let x = 0;
  let y = 0;
  for (const hit of punchFrames(words)) {
    const d = f - hit;
    if (d < 0 || d >= 10) continue;
    const amp = 30 * (1 - d / 10);
    x += (random(`sx${hit}-${d}`) - 0.5) * 2 * amp;
    y += (random(`sy${hit}-${d}`) - 0.5) * 2 * amp;
  }
  return {x, y};
};

// Red glove pointing right; cuff on the left. viewBox 300x300, front edge at x=290.
const Glove: React.FC = () => (
  <svg viewBox="0 0 300 300" width={GLOVE} height={GLOVE} style={{overflow: 'visible'}}>
    <defs>
      <radialGradient id="gloveRed" cx="0.6" cy="0.3" r="0.8">
        <stop offset="0" stopColor="#ff4a3d" />
        <stop offset="0.55" stopColor="#d4141c" />
        <stop offset="1" stopColor="#7d0a0f" />
      </radialGradient>
    </defs>
    <g stroke="#000" strokeWidth={8} strokeLinejoin="round" strokeLinecap="round">
      {/* wrist cuff: white with red trim and laces */}
      <path d="M-40 128 L112 118 L112 218 L-40 212 Z" fill="#f2f2f2" />
      <path d="M86 120 L86 216" stroke="#d4141c" strokeWidth={14} />
      <path d="M86 120 L86 216" strokeWidth={4} fill="none" />
      <path d="M10 132 L40 160 M40 132 L10 160 M10 168 L40 196 M40 168 L10 196" strokeWidth={5} fill="none" />
      {/* hand: big rounded knuckles at the front */}
      <path
        d="M106 116 C110 70 160 40 214 42 C266 44 296 88 293 142 C290 192 262 224 222 232 L150 234 C124 234 106 220 102 200 Z"
        fill="url(#gloveRed)"
      />
      {/* finger creases on the front */}
      <path d="M236 56 C262 84 270 124 264 162" fill="none" strokeWidth={5} />
      <path d="M206 46 C230 74 238 112 232 150" fill="none" strokeWidth={4} opacity={0.6} />
      {/* thumb tucked along the side */}
      <path d="M126 192 C148 168 224 166 256 184 C276 198 266 228 234 228 L152 228 C126 228 114 208 126 192 Z" fill="#c0121a" />
    </g>
    <ellipse cx="190" cy="72" rx="58" ry="17" fill="#fff" opacity={0.4} transform="rotate(-10 190 72)" />
    <ellipse cx="200" cy="190" rx="34" ry="8" fill="#fff" opacity={0.25} />
  </svg>
);

// Radiating impact lines at the contact point.
const Burst: React.FC<{x: number; y: number; t: number}> = ({x, y, t}) => {
  if (t < 0 || t > 8) return null;
  const s = interpolate(t, [0, 8], [0.6, 1.7], {...clamp, easing: Easing.out(Easing.cubic)});
  const o = interpolate(t, [0, 2, 8], [1, 1, 0], clamp);
  return (
    <svg width={500} height={500} viewBox="-250 -250 500 500" style={{position: 'absolute', left: x - 250, top: y - 250, opacity: o, transform: `scale(${s})`}}>
      {Array.from({length: 12}, (_, i) => {
        const a = (i / 12) * Math.PI * 2 + 0.2;
        const r1 = 70 + (i % 2) * 20;
        const r2 = 150 + (i % 3) * 30;
        return (
          <line key={i} x1={Math.cos(a) * r1} y1={Math.sin(a) * r1} x2={Math.cos(a) * r2} y2={Math.sin(a) * r2}
            stroke="white" strokeWidth={16} strokeLinecap="round" style={{filter: 'drop-shadow(0 0 3px black)'}} />
        );
      })}
    </svg>
  );
};

export const PunchEndCard: React.FC<{title: string; duration: number}> = ({title, duration}) => {
  const f = useCurrentFrame();
  const words = title.split(' ');
  const hits = punchFrames(words.length);
  const lastGone = hits[hits.length - 1] + 12;
  const scrim = interpolate(f, [0, 8, lastGone, lastGone + 12], [0, 0.5, 0.5, 0.15], clamp);
  const out = interpolate(f, [duration - 12, duration], [1, 0], clamp);
  const flash = Math.max(...hits.map((h) => interpolate(f - h, [-1, 0, 4], [0, 0.35, 0], clamp)));
  const top = 960 - ((words.length - 1) * LINE) / 2;

  return (
    <AbsoluteFill style={{opacity: out}}>
      <AbsoluteFill style={{background: `rgba(0,0,0,${scrim})`}} />
      {words.map((w, i) => {
        const fromLeft = i % 2 === 0;
        const dir = fromLeft ? 1 : -1; // direction the punch travels
        const hit = hits[i];
        const y = top + i * LINE;
        const textW = w.length * FONT * 0.47; // rough Anton width
        const contactX = 540 - dir * textW * 0.04; // glove lands a little into the word

        // Word: pops in, squashes on contact, then flies off in the punch direction.
        const pop = interpolate(f, [i * 3, i * 3 + 8], [1.5, 1], {...clamp, easing: Easing.out(Easing.back(2))});
        const inO = interpolate(f, [i * 3, i * 3 + 3], [0, 1], clamp);
        const squash = f >= hit && f < hit + 2 ? 0.85 : 1;
        const fly = interpolate(f, [hit, hit + 12], [0, 1], {...clamp, easing: Easing.out(Easing.cubic)});
        const wx = dir * fly * 1500;
        const wy = -fly * 260;
        const rot = dir * fly * 35;

        // Glove: accelerates in, holds on contact, pulls back out.
        const inT = interpolate(f, [hit - TRAVEL, hit], [0, 1], {...clamp, easing: Easing.in(Easing.quad)});
        const backT = interpolate(f, [hit + HOLD, hit + HOLD + 9], [0, 1], {...clamp, easing: Easing.in(Easing.quad)});
        const offscreen = -GLOVE - 80;
        const gx = fromLeft
          ? interpolate(inT - backT, [0, 1], [offscreen, contactX - GLOVE * 0.97])
          : interpolate(inT - backT, [0, 1], [1080 + 80, contactX - GLOVE * 0.03]);
        const moving = (f >= hit - TRAVEL && f < hit) || (f > hit + HOLD && f <= hit + HOLD + 9);
        const showGlove = f >= hit - TRAVEL && f <= hit + HOLD + 9;

        return (
          <div key={i}>
            <div
              style={{
                position: 'absolute',
                left: 0,
                width: 1080,
                top: y - FONT * 0.62,
                textAlign: 'center',
                fontFamily: 'Anton',
                fontSize: FONT,
                lineHeight: 1.2,
                color: 'white',
                WebkitTextStroke: '22px black',
                paintOrder: 'stroke fill',
                textShadow: '0 12px 30px rgba(0,0,0,0.55)',
                opacity: inO,
                transform: `translate(${wx}px, ${wy}px) rotate(${rot}deg) scale(${pop * (fly > 0 ? 1 - fly * 0.15 : 1)}) scaleX(${squash})`,
                filter: fly > 0 && fly < 0.9 ? `blur(${4 * (1 - fly)}px)` : undefined,
              }}
            >
              {w}
            </div>
            {showGlove && (
              <div
                style={{
                  position: 'absolute',
                  left: gx,
                  top: y - GLOVE / 2,
                  transform: `scaleX(${fromLeft ? 1 : -1}) rotate(${-6}deg) scaleX(${moving ? 1.12 : 1})`,
                  transformOrigin: 'center',
                  filter: `drop-shadow(0 18px 24px rgba(0,0,0,0.6))${moving ? ' blur(2px)' : ''}`,
                }}
              >
                <Glove />
              </div>
            )}
            <Burst x={contactX} y={y} t={f - hit} />
          </div>
        );
      })}
      <AbsoluteFill style={{background: 'white', opacity: flash}} />
    </AbsoluteFill>
  );
};
