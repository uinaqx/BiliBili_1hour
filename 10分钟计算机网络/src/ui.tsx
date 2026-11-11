import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, FONT} from './theme';
import {clamp, easeInOut, easeOut, ip, prog, useScene} from './anim';

export const ORDER = ['intro', 'layers', 'link', 'network', 'transport', 'app', 'journey', 'outro'];

/** Keynote-style chapter card that dissolves into a small header. */
export const Header: React.FC = () => {
  const {frame, s} = useScene();
  if (s.id === 'intro') return null;
  const n = String(ORDER.indexOf(s.id)).padStart(2, '0');
  const inT = ip(frame, 2, 20, easeOut);
  const outT = ip(frame, 40, 20, easeInOut);
  const cardO = inT * (1 - outT);
  const h = ip(frame, 50, 22, easeOut);
  return (
    <>
      {cardO > 0 && (
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: cardO, fontFamily: FONT,
          transform: `translateY(${(1 - inT) * 24}px) scale(${1 + 0.05 * outT})`, filter: `blur(${outT * 10}px)`}}>
          <div style={{textAlign: 'center'}}>
            <div style={{fontSize: 26, color: C.blue, fontWeight: 600, letterSpacing: 6}}>CHAPTER {n}</div>
            <div style={{fontSize: 124, fontWeight: 700, color: C.ink, letterSpacing: 4, marginTop: 8}}>{s.title}</div>
            <div style={{fontSize: 34, color: C.muted, marginTop: 10}}>{s.en}</div>
          </div>
        </AbsoluteFill>
      )}
      <div style={{position: 'absolute', left: 96, top: 62, opacity: h, transform: `translateY(${(1 - h) * -10}px)`, fontFamily: FONT,
        display: 'flex', alignItems: 'baseline', gap: 18}}>
        <span style={{fontSize: 22, fontWeight: 650, color: C.blue, letterSpacing: 2}}>{n}</span>
        <span style={{fontSize: 40, fontWeight: 700, color: C.ink, letterSpacing: 1}}>{s.title}</span>
        <span style={{fontSize: 21, color: C.muted}}>{s.en}</span>
      </div>
      <div style={{position: 'absolute', right: 96, top: 80, display: 'flex', gap: 8, opacity: h}}>
        {ORDER.slice(1).map((id, i) => (
          <div key={id} style={{width: id === s.id ? 34 : 14, height: 6, borderRadius: 3,
            background: i < ORDER.indexOf(s.id) ? (id === s.id ? C.blue : C.ink2) : C.line, opacity: id === s.id ? 1 : 0.55}} />
        ))}
      </div>
    </>
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
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 44, display: 'flex', justifyContent: 'center', opacity: o}}>
      <div style={{maxWidth: 1600, padding: '12px 32px', borderRadius: 20, background: 'rgba(28,28,31,0.82)',
        backdropFilter: 'blur(24px)', boxShadow: '0 10px 30px rgba(0,0,0,0.45)',
        border: '1px solid rgba(255,255,255,0.07)', fontFamily: FONT, fontSize: 30, lineHeight: '44px', color: C.ink, textAlign: 'center',
        fontWeight: 500, letterSpacing: 0.5}}>
        {beat.text}
      </div>
    </div>
  );
};

export const SceneFade: React.FC = () => {
  const {frame, dur} = useScene();
  const o = Math.max(1 - clamp(frame / 14), clamp((frame - (dur - 12)) / 12));
  if (o <= 0) return null;
  return <AbsoluteFill style={{background: C.bg, opacity: o}} />;
};

/** Soft, slowly drifting colour washes behind everything. */
export const Backdrop: React.FC = () => {
  const f = useCurrentFrame() / 30;
  const blob = (x: number, y: number, r: number, color: string) => (
    <div style={{position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: r,
      background: `radial-gradient(circle, ${color} 0%, transparent 70%)`}} />
  );
  return (
    <AbsoluteFill style={{background: C.bg, overflow: 'hidden'}}>
      {blob(300 + Math.sin(f * 0.07) * 120, 200 + Math.cos(f * 0.05) * 80, 700, 'rgba(10,132,255,0.10)')}
      {blob(1650 + Math.cos(f * 0.06) * 120, 900 + Math.sin(f * 0.08) * 80, 760, 'rgba(191,90,242,0.08)')}
    </AbsoluteFill>
  );
};
