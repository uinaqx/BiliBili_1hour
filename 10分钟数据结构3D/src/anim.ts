import {createContext, useContext} from 'react';
import {useCurrentFrame} from 'remotion';

export type Beat = {text: string; audio: string | null; from: number; dur: number};
export type SceneData = {id: string; title: string; en: string; from: number; duration: number; beats: Beat[]};

export const SceneCtx = createContext<SceneData | null>(null);

export const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const easeInOut = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
export const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);
export const easeOutBack = (t: number) => {
  const c1 = 1.70158, c3 = c1 + 1;
  return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
};
export const bounce = (t: number) => {
  const n1 = 7.5625, d1 = 2.75;
  if (t < 1 / d1) return n1 * t * t;
  if (t < 2 / d1) return n1 * (t -= 1.5 / d1) * t + 0.75;
  if (t < 2.5 / d1) return n1 * (t -= 2.25 / d1) * t + 0.9375;
  return n1 * (t -= 2.625 / d1) * t + 0.984375;
};

/** Linear 0..1 progress of `frame` through [start, start+len]. */
export const prog = (frame: number, start: number, len: number) => clamp((frame - start) / Math.max(1, len));
export const ip = (frame: number, start: number, len: number, ease = easeInOut) => ease(prog(frame, start, len));

export const lerp3 = (a: number[], b: number[], t: number): [number, number, number] =>
  [lerp(a[0], b[0], t), lerp(a[1], b[1], t), lerp(a[2], b[2], t)];

/** Frame, scene info and beat helpers for the current scene. */
export const useScene = () => {
  const frame = useCurrentFrame();
  const s = useContext(SceneCtx)!;
  const b = (i: number) => s.beats[Math.min(i, s.beats.length - 1)].from;
  const bd = (i: number) => s.beats[Math.min(i, s.beats.length - 1)].dur;
  /** Absolute frame at fraction `f` through beat i. */
  const at = (i: number, f = 0) => b(i) + bd(i) * f;
  const beatIndex = s.beats.reduce((acc, x, i) => (frame >= x.from ? i : acc), -1);
  return {frame, s, b, bd, at, beatIndex, dur: s.duration};
};

type Key = [number, number[], number[]];
/** Smoothly interpolated camera path through [frame, position, target] keys. */
export const camPath = (frame: number, keys: Key[]) => {
  const ks = [...keys].sort((a, b) => a[0] - b[0]);
  if (frame <= ks[0][0]) return {pos: ks[0][1] as [number, number, number], target: ks[0][2] as [number, number, number]};
  for (let i = 0; i < ks.length - 1; i++) {
    const [f0, p0, t0] = ks[i], [f1, p1, t1] = ks[i + 1];
    if (frame <= f1) {
      const t = easeInOut(clamp((frame - f0) / Math.max(1, f1 - f0)));
      return {pos: lerp3(p0, p1, t), target: lerp3(t0, t1, t)};
    }
  }
  const last = ks[ks.length - 1];
  return {pos: last[1] as [number, number, number], target: last[2] as [number, number, number]};
};

/** Deterministic pseudo random in [0,1). */
export const rand = (seed: number) => {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
