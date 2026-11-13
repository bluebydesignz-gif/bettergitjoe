import {AbsoluteFill, Easing, interpolate, useCurrentFrame} from 'remotion';

const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// Burned-in caption for spoken lines. Sits above Instagram's bottom UI.
export const Caption: React.FC<{text: string; duration: number; accent: string}> = ({text, duration, accent}) => {
  const f = useCurrentFrame();
  const pop = interpolate(f, [0, 5], [0.85, 1], {...clamp, easing: Easing.out(Easing.back(2.5))});
  const op = interpolate(f, [0, 3, duration - 3, duration], [0, 1, 1, 0], clamp);
  const words = text.split(' ');
  // Reveal words across the first 60% of the caption's time, karaoke style.
  const shown = Math.ceil(interpolate(f, [0, Math.max(1, duration * 0.6)], [1, words.length], clamp));
  return (
    <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 520, paddingLeft: 70, paddingRight: 70}}>
      <div
        style={{
          fontFamily: 'Anton',
          fontSize: 92,
          lineHeight: 1.08,
          textAlign: 'center',
          textTransform: 'uppercase',
          color: 'white',
          WebkitTextStroke: '10px black',
          paintOrder: 'stroke fill',
          textShadow: '0 6px 18px rgba(0,0,0,0.6)',
          transform: `scale(${pop})`,
          opacity: op,
        }}
      >
        {words.map((w, i) => (
          <span key={i} style={{color: i === shown - 1 ? accent : 'white', opacity: i < shown ? 1 : 0}}>
            {w}
            {i < words.length - 1 ? ' ' : ''}
          </span>
        ))}
      </div>
    </AbsoluteFill>
  );
};
