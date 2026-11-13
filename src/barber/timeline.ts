// Beat-locked plan for the barber reel. Reuses the INSYNC plan format and adds
// per-shot real audio (with music ducking) and burned-in captions.
import {buildTimeline, FPS, type Plan, type PlanShot, type Timeline} from '../insync/timeline';

export type Caption = {
  text: string;
  at: number; // seconds from the start of the shot
  end: number; // seconds from the start of the shot
};

export type BarberShot = PlanShot & {
  audio?: number; // play the clip's own sound at this volume (0-1), music ducks under it
  captions?: Caption[];
};

export type BarberPlan = Omit<Plan, 'shots'> & {shots: BarberShot[]};

export type AudioWindow = {from: number; to: number};

export type BarberTimeline = Timeline & {
  captions: {from: number; to: number; text: string}[];
  audioWindows: AudioWindow[];
};

export const buildBarberTimeline = (plan: BarberPlan): BarberTimeline => {
  const tl = buildTimeline([], plan);
  const captions: BarberTimeline['captions'] = [];
  const audioWindows: AudioWindow[] = [];
  plan.shots.forEach((s, i) => {
    const shot = tl.shots[i];
    if (s.audio) {
      shot.audio = s.audio;
      audioWindows.push({from: shot.from, to: shot.from + shot.duration});
    }
    for (const c of s.captions ?? []) {
      captions.push({
        from: shot.from + Math.round(c.at * FPS),
        to: Math.min(shot.from + shot.duration, shot.from + Math.round(c.end * FPS)),
        text: c.text,
      });
    }
  });
  return {...tl, captions, audioWindows};
};

// Music level: full, dipping to `duck` around shots that play real audio.
export const musicVolume = (f: number, windows: AudioWindow[], end: number, duck = 0.12, ramp = 8) => {
  let v = 1;
  for (const w of windows) {
    if (f < w.from - ramp || f > w.to + ramp) continue;
    const into = f < w.from ? (w.from - f) / ramp : f > w.to ? (f - w.to) / ramp : 0;
    v = Math.min(v, duck + (1 - duck) * into);
  }
  const fadeOut = Math.max(0, Math.min(1, (end - f) / 20));
  return v * fadeOut;
};
