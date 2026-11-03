import {AbsoluteFill, useCurrentFrame, useVideoConfig} from 'remotion';
import {ThreeCanvas} from '@remotion/three';
import gsap from 'gsap';

// Test scene: a spinning 3D cube (Three.js) plus a GSAP-eased headline.
export const HelloStudio: React.FC = () => {
  const frame = useCurrentFrame();
  const {width, height, fps} = useVideoConfig();
  const t = Math.min(frame / (fps * 1.2), 1);
  const ease = gsap.parseEase('back.out(1.7)')(t);

  return (
    <AbsoluteFill style={{background: '#0b0d12'}}>
      <ThreeCanvas width={width} height={height}>
        <ambientLight intensity={0.6} />
        <directionalLight position={[3, 4, 5]} intensity={1.4} />
        <mesh rotation={[frame * 0.02, frame * 0.03, 0]} position={[0, 0.6, 0]}>
          <boxGeometry args={[1.4, 1.4, 1.4]} />
          <meshStandardMaterial color="#e8734a" />
        </mesh>
      </ThreeCanvas>
      <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 380}}>
        <div
          style={{
            color: 'white',
            fontFamily: 'sans-serif',
            fontWeight: 800,
            fontSize: 110,
            transform: `translateY(${(1 - ease) * 300}px) scale(${0.6 + ease * 0.4})`,
            opacity: t,
          }}
        >
          Studio ready
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};
