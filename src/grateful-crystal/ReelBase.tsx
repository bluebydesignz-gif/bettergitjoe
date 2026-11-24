// Picture cut and natural-sound mix for a Certified Red reel. No text: the text layer is
// composited later in HyperFrames (scripts/build_text.py). Copy to src/<slug>/ReelBase.tsx,
// put assemble.py's timeline.json next to it, and register it in src/Root.tsx.
import React from 'react';
import {AbsoluteFill, Audio, Easing, OffthreadVideo, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import timeline from './timeline.json';

const INK = '#0B0B0C';
type Seg = (typeof timeline.segments)[number];

const Shot: React.FC<{seg: Seg}> = ({seg}) => {
  const f = useCurrentFrame();
  const scale = interpolate(f, [0, seg.dur], seg.push as [number, number]);
  const opacity = seg.xfade > 0 ? interpolate(f, [0, seg.xfade], [0, 1], {extrapolateRight: 'clamp', easing: Easing.inOut(Easing.quad)}) : 1;
  return (
    <AbsoluteFill style={{opacity}}>
      <OffthreadVideo muted src={staticFile(seg.file)} style={{width: '100%', height: '100%', transform: `scale(${scale})`}} />
    </AbsoluteFill>
  );
};

export const ReelBase: React.FC = () => {
  const frame = useCurrentFrame();
  const fadeIn = interpolate(frame, [0, 6], [1, 0], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{background: INK}}>
      {timeline.segments.map((seg) => (
        <Sequence key={seg.id} from={seg.from} durationInFrames={seg.dur} name={seg.id}>
          <Shot seg={seg} />
        </Sequence>
      ))}
      {/* light vignette; kept subtle so skin tones stay natural */}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 46%, rgba(0,0,0,0) 62%, rgba(0,0,0,0.12) 100%)'}} />
      <AbsoluteFill style={{background: INK, opacity: fadeIn}} />
      <Audio src={staticFile(`${timeline.slug}/mix.wav`)} />
    </AbsoluteFill>
  );
};

export const reelDuration = timeline.durationInFrames;

/* In src/Root.tsx:
import {ReelBase, reelDuration} from './<slug>/ReelBase';
<Composition id="<Slug>Base" component={ReelBase} durationInFrames={reelDuration} fps={30} width={1080} height={1920} />
*/
