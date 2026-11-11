import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT, MONO} from './theme';
import {clamp, easeOut, ip, prog, useScene} from './anim';

const ORDER = ['intro', 'array', 'linked', 'stack', 'queue', 'hash', 'tree', 'heap', 'graph', 'complexity', 'outro'];

export const Header: React.FC = () => {
  const {frame, s} = useScene();
  if (s.id === 'intro') return null;
  const t = ip(frame, 4, 26, easeOut);
  const n = ORDER.indexOf(s.id);
  const chapter = n >= 1 && n <= 9 ? String(n).padStart(2, '0') : null;
  return (
    <div style={{position: 'absolute', left: 72, top: 54, fontFamily: FONT, opacity: t, transform: `translateX(${(1 - t) * -40}px)`}}>
      <div style={{display: 'flex', alignItems: 'baseline', gap: 22}}>
        {chapter && <span style={{fontFamily: MONO, fontSize: 30, color: C.orange, letterSpacing: 2}}>{chapter}</span>}
        <span style={{fontSize: 54, fontWeight: 700, color: C.text, letterSpacing: 4}}>{s.title}</span>
        {s.en && <span style={{fontFamily: MONO, fontSize: 26, color: C.muted}}>{s.en}</span>}
      </div>
      <div style={{marginTop: 12, height: 3, width: 260 * t, background: `linear-gradient(90deg, ${C.orange}, transparent)`}} />
    </div>
  );
};

export const Subtitle: React.FC = () => {
  const {frame, s} = useScene();
  const i = s.beats.reduce((acc, b, k) => (frame >= b.from - 4 ? k : acc), -1);
  if (i < 0) return null;
  const beat = s.beats[i];
  const next = s.beats[i + 1]?.from ?? s.duration;
  const end = Math.min(next - 2, beat.from + beat.dur + 10);
  const o = Math.min(prog(frame, beat.from - 4, 8), 1 - prog(frame, end - 6, 6));
  if (o <= 0) return null;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 52, display: 'flex', justifyContent: 'center', opacity: o}}>
      <div style={{maxWidth: 1720, padding: '12px 30px', borderRadius: 14, background: 'rgba(11,20,34,0.72)',
        border: `1px solid ${C.border}`, fontFamily: FONT, fontSize: 32, lineHeight: '46px', color: C.text, textAlign: 'center',
        letterSpacing: 1}}>
        {beat.text}
      </div>
    </div>
  );
};

/** Pill badge, fades/slides in at `from` and optionally out at `to`. */
export const Badge: React.FC<{from: number; to?: number; x: number; y: number; children: React.ReactNode; color?: string; size?: number; align?: 'left' | 'right' | 'center'}> =
  ({from, to = 1e9, x, y, children, color = C.orange, size = 30, align = 'left'}) => {
    const {frame} = useScene();
    const o = Math.min(ip(frame, from, 14, easeOut), 1 - prog(frame, to, 12));
    if (o <= 0) return null;
    const shift = align === 'right' ? '-100%' : align === 'center' ? '-50%' : '0';
    return (
      <div style={{position: 'absolute', left: x, top: y, transform: `translate(${shift}, ${(1 - o) * 16}px)`, opacity: o,
        padding: '10px 22px', borderRadius: 999, background: 'rgba(18,32,51,0.86)', border: `2px solid ${color}`,
        boxShadow: `0 0 28px ${color}44`, fontFamily: FONT, fontSize: size, color: C.text, whiteSpace: 'nowrap'}}>
        {children}
      </div>
    );
  };

/** Floating HTML card for formulas or code. */
export const Card: React.FC<{from: number; to?: number; x: number; y: number; w?: number; children: React.ReactNode; accent?: string}> =
  ({from, to = 1e9, x, y, w, children, accent = C.orange}) => {
    const {frame} = useScene();
    const o = Math.min(ip(frame, from, 16, easeOut), 1 - prog(frame, to, 12));
    if (o <= 0) return null;
    return (
      <div style={{position: 'absolute', left: x, top: y, width: w, opacity: o, transform: `scale(${0.94 + 0.06 * o})`,
        transformOrigin: 'left top', padding: '20px 28px', borderRadius: 16, background: 'rgba(18,32,51,0.9)',
        border: `1px solid ${C.border}`, borderLeft: `4px solid ${accent}`, fontFamily: FONT, fontSize: 30, color: C.text,
        lineHeight: 1.5}}>
        {children}
      </div>
    );
  };

export const Mono: React.FC<{children: React.ReactNode; color?: string}> = ({children, color = C.orange}) =>
  <span style={{fontFamily: MONO, color}}>{children}</span>;

export const SceneFade: React.FC = () => {
  const {frame, dur} = useScene();
  const o = Math.max(1 - clamp(frame / 16), clamp((frame - (dur - 12)) / 12));
  if (o <= 0) return null;
  return <AbsoluteFill style={{background: C.bg, opacity: o}} />;
};
