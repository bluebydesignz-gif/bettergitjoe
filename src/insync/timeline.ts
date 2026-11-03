// Beat-locked edit plan for the INSYNC Halloween reel.
// Every cut lands on a beat (or half beat in the bursts) of a 124 BPM track.

export const FPS = 30;
export const BPM = 124;
export const FRAMES_PER_BEAT = (FPS * 60) / BPM; // ~14.5
export const b2f = (beat: number) => Math.round(beat * FRAMES_PER_BEAT);

export const TOTAL_BEATS = 36;
export const DURATION = b2f(TOTAL_BEATS) + 15; // short tail for the final hit

export type Fx = 'flash' | 'glitch' | 'zoom' | 'whip';

export type ClipInput = {
  // Path inside public/, e.g. "clips/clip01.mp4". Leave clips empty for a placeholder preview.
  src: string;
  // Start times (seconds) of the best moments in this clip.
  moments: number[];
};

export type Shot = {
  index: number;
  from: number; // frame
  duration: number; // frames
  clip: number; // index into clips
  moment: number; // index into clip.moments
  fx: Fx;
  bw: boolean;
  stutter: boolean;
};

// Cut points in beats.
const cutBeats: number[] = [
  0, // intro shot under the title
  ...range(4, 12, 1), // drop: one cut per beat
  ...range(12, 16, 0.5), // burst: half-beat cuts
  16, // mid title hit (one shot, 2 beats)
  ...range(18, 28, 1), // groove
  ...range(28, 30, 0.5), // burst into the outro
  30, // end card shot
  TOTAL_BEATS,
];

function range(start: number, end: number, step: number) {
  const out: number[] = [];
  for (let b = start; b < end - 1e-9; b += step) out.push(b);
  return out;
}

const FX_CYCLE: Fx[] = ['flash', 'whip', 'zoom', 'glitch'];
const STUTTER_SHOTS = new Set([6, 14, 22]);

export const buildShots = (clipCount: number): Shot[] => {
  const n = Math.max(clipCount, 1);
  const shots: Shot[] = [];
  for (let i = 0; i < cutBeats.length - 1; i++) {
    const startBeat = cutBeats[i];
    const from = b2f(startBeat);
    const inBurst = (startBeat >= 12 && startBeat < 16) || (startBeat >= 28 && startBeat < 30);
    shots.push({
      index: i,
      from,
      duration: b2f(cutBeats[i + 1]) - from + (i === cutBeats.length - 2 ? 15 : 0),
      clip: i % n,
      moment: Math.floor(i / n),
      fx: inBurst ? (i % 2 ? 'glitch' : 'flash') : startBeat === 16 || startBeat === 30 ? 'flash' : FX_CYCLE[i % 4],
      bw: inBurst ? i % 2 === 1 : i % 7 === 3,
      stutter: STUTTER_SHOTS.has(i),
    });
  }
  return shots;
};

export const SECTIONS = {
  intro: [0, b2f(4)],
  midTitle: [b2f(16), b2f(18)],
  endCard: [b2f(30), DURATION],
} as const;
