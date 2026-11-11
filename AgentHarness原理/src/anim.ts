import {createContext, useContext} from 'react';
import {spring, useCurrentFrame} from 'remotion';

export type Beat = {text: string; audio: string | null; from: number; dur: number};
export type SceneData = {id: string; title: string; en: string; from: number; duration: number; beats: Beat[]};

export const SceneCtx = createContext<SceneData | null>(null);

export const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const easeInOut = (t: number) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);
export const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);

/** Linear 0..1 progress of `frame` through [start, start+len]. */
export const prog = (frame: number, start: number, len: number) => clamp((frame - start) / Math.max(1, len));
export const ip = (frame: number, start: number, len: number, ease = easeInOut) => ease(prog(frame, start, len));
/** Soft spring, 0 before `from`. */
export const pop = (frame: number, from: number, damping = 15) =>
  spring({frame: frame - from, fps: 30, config: {damping, stiffness: 120, mass: 0.9}});
/** Fade in at `from`, fade out at `to`. */
export const vis = (frame: number, from: number, to = 1e9, len = 14) =>
  Math.min(ip(frame, from, len, easeOut), 1 - prog(frame, to, len));

/** Frame, scene info and beat helpers for the current scene. */
export const useScene = () => {
  const frame = useCurrentFrame();
  const s = useContext(SceneCtx)!;
  const b = (i: number) => s.beats[Math.min(i, s.beats.length - 1)].from;
  const bd = (i: number) => s.beats[Math.min(i, s.beats.length - 1)].dur;
  /** Frame at fraction `f` through beat i. */
  const at = (i: number, f = 0) => Math.round(b(i) + bd(i) * f);
  return {frame, s, b, bd, at, dur: s.duration};
};

export type P = [number, number];

const segs = (pts: P[]) => pts.slice(1).map((p, i) => Math.hypot(p[0] - pts[i][0], p[1] - pts[i][1]));

/** Point and heading (degrees) at fraction t along a polyline. */
export const pointAt = (pts: P[], t: number): {p: P; angle: number} => {
  const L = segs(pts), total = L.reduce((a, b) => a + b, 0);
  let d = clamp(t) * total;
  for (let i = 0; i < L.length; i++) {
    if (d <= L[i] || i === L.length - 1) {
      const k = L[i] ? Math.min(1, d / L[i]) : 0, a = pts[i], b = pts[i + 1];
      return {p: [lerp(a[0], b[0], k), lerp(a[1], b[1], k)], angle: (Math.atan2(b[1] - a[1], b[0] - a[0]) * 180) / Math.PI};
    }
    d -= L[i];
  }
  return {p: pts[pts.length - 1], angle: 0};
};

/** The part of a polyline from its start to fraction t. */
export const partial = (pts: P[], t: number): P[] => {
  const L = segs(pts), total = L.reduce((a, b) => a + b, 0);
  let d = clamp(t) * total;
  const out: P[] = [pts[0]];
  for (let i = 0; i < L.length; i++) {
    if (d >= L[i]) { out.push(pts[i + 1]); d -= L[i]; continue; }
    const k = L[i] ? d / L[i] : 0;
    out.push([lerp(pts[i][0], pts[i + 1][0], k), lerp(pts[i][1], pts[i + 1][1], k)]);
    break;
  }
  return out;
};

/** Sampled quadratic curve from a to b, bulging by `bend` pixels to the left of travel. */
export const curve = (a: P, b: P, bend: number, n = 28): P[] => {
  const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
  const dx = b[0] - a[0], dy = b[1] - a[1], len = Math.hypot(dx, dy) || 1;
  const c: P = [mx + (dy / len) * bend, my - (dx / len) * bend];
  return Array.from({length: n + 1}, (_, i) => {
    const t = i / n, u = 1 - t;
    return [u * u * a[0] + 2 * u * t * c[0] + t * t * b[0], u * u * a[1] + 2 * u * t * c[1] + t * t * b[1]] as P;
  });
};

/** Points along a circular arc, angles in degrees (0 = right, 90 = down). */
export const arc = (cx: number, cy: number, r: number, a0: number, a1: number, n = 40): P[] =>
  Array.from({length: n + 1}, (_, i) => {
    const a = ((a0 + ((a1 - a0) * i) / n) * Math.PI) / 180;
    return [cx + r * Math.cos(a), cy + r * Math.sin(a)] as P;
  });

export const rand = (seed: number) => {
  const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
