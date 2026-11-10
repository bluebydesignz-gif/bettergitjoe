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

// Explicit edit: one entry per shot, each with its own length in beats.
// Used when an edit needs held shots, slow motion or a custom ending.
export type PlanShot = {
  src: string; // path inside public/
  start: number; // seconds into the clip
  beats: number; // shot length in beats
  fx?: Fx;
  bw?: boolean;
  stutter?: boolean;
  section?: 'intro' | 'mid';
};

export type Plan = {
  shots: PlanShot[];
  endCardBeats: number; // end card overlays the last N beats
};

export type Timeline = {
  shots: Shot[];
  clips: ClipInput[];
  duration: number;
  intro: [number, number];
  midTitle: [number, number];
  endCard: [number, number];
};

const TAIL = 15;

export const planBeats = (plan: Plan) => plan.shots.reduce((sum, s) => sum + s.beats, 0);
export const planDuration = (plan: Plan) => b2f(planBeats(plan)) + TAIL;

export const buildTimeline = (clips: ClipInput[], plan?: Plan): Timeline => {
  if (!plan) {
    return {
      shots: buildShots(clips.length),
      clips,
      duration: DURATION,
      intro: [...SECTIONS.intro],
      midTitle: [...SECTIONS.midTitle],
      endCard: [...SECTIONS.endCard],
    };
  }
  const shots: Shot[] = [];
  const planClips: ClipInput[] = [];
  let intro: [number, number] = [0, 0];
  let midTitle: [number, number] = [0, 0];
  let beat = 0;
  plan.shots.forEach((s, i) => {
    const from = b2f(beat);
    const last = i === plan.shots.length - 1;
    const duration = b2f(beat + s.beats) - from + (last ? TAIL : 0);
    planClips.push({src: s.src, moments: [s.start]});
    shots.push({
      index: i,
      from,
      duration,
      clip: i,
      moment: 0,
      fx: s.fx ?? FX_CYCLE[i % 4],
      bw: s.bw ?? false,
      stutter: s.stutter ?? false,
    });
    if (s.section === 'intro') intro = [from, from + duration];
    if (s.section === 'mid') midTitle = [from, from + duration];
    beat += s.beats;
  });
  const duration = b2f(beat) + TAIL;
  return {shots, clips: planClips, duration, intro, midTitle, endCard: [b2f(beat - plan.endCardBeats), duration]};
};
