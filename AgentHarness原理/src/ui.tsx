import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {BORDER, C, FONT, GRAD, MONO, tint} from './theme';
import {clamp, easeInOut, easeOut, ip, pop, prog, rand, useScene} from './anim';

export const ORDER = ['intro', 'loop', 'tools', 'context', 'safety', 'plan', 'outro'];

const gradText: React.CSSProperties = {backgroundImage: GRAD, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent'};

/** Chapter card: giant outlined number, per-character title, light beam; then collapses into a corner header. */
export const Header: React.FC = () => {
  const {frame, s} = useScene();
  if (s.id === 'intro') return null;
  const n = String(ORDER.indexOf(s.id)).padStart(2, '0');
  const out = ip(frame, 44, 16, easeInOut);
  const cardO = ip(frame, 0, 10) * (1 - out);
  const beam = ip(frame, 2, 22, easeOut);
  const h = ip(frame, 52, 20, easeOut);
  const chars = Array.from(s.title);
  return (
    <>
      {cardO > 0 && (
        <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: cardO, fontFamily: FONT,
          transform: `scale(${1 + 0.35 * out})`, filter: out > 0 ? `blur(${out * 16}px)` : undefined}}>
          <div style={{position: 'absolute', fontSize: 560, fontWeight: 900, letterSpacing: -20, color: 'transparent',
            WebkitTextStroke: `2px ${tint(C.violet, 0.35)}`, transform: `translateX(${(1 - beam) * 120}px) scale(${1.15 - 0.15 * beam})`,
            fontFamily: FONT, lineHeight: 1}}>{n}</div>
          <div style={{position: 'absolute', top: 540, left: 960 - 900 * beam, width: 1800 * beam, height: 2,
            background: `linear-gradient(90deg, transparent, ${C.magenta}, ${C.cyan}, transparent)`, boxShadow: `0 0 24px ${C.magenta}`,
            transform: 'translateY(118px)'}} />
          <div style={{textAlign: 'center', position: 'relative'}}>
            <div style={{fontSize: 24, fontWeight: 700, letterSpacing: 12, color: C.cyan, fontFamily: MONO,
              opacity: ip(frame, 4, 10)}}>CHAPTER {n}</div>
            <div style={{display: 'flex', justifyContent: 'center', marginTop: 10}}>
              {chars.map((ch, i) => {
                const k = pop(frame, 4 + i * 2, 11);
                return (
                  <span key={i} style={{display: 'inline-block', fontSize: 132, fontWeight: 800, color: C.ink, whiteSpace: 'pre',
                    transform: `translateY(${(1 - k) * 90}px) scale(${0.6 + 0.4 * k})`, opacity: clamp(k * 1.6),
                    filter: k < 0.9 ? `blur(${(1 - k) * 12}px)` : undefined, textShadow: `0 0 40px ${tint(C.violet, 0.5)}`}}>{ch}</span>
                );
              })}
            </div>
            <div style={{fontSize: 34, fontWeight: 600, marginTop: 14, opacity: ip(frame, 14, 12), letterSpacing: 3, ...gradText}}>{s.en}</div>
          </div>
        </AbsoluteFill>
      )}
      <div style={{position: 'absolute', left: 96, top: 58, opacity: h, transform: `translateX(${(1 - h) * -40}px)`, fontFamily: FONT,
        display: 'flex', alignItems: 'baseline', gap: 18}}>
        <span style={{fontSize: 24, fontWeight: 800, fontFamily: MONO, ...gradText}}>{n}</span>
        <span style={{fontSize: 38, fontWeight: 800, color: C.ink}}>{s.title}</span>
        <span style={{fontSize: 20, color: C.muted, fontWeight: 600, letterSpacing: 1}}>{s.en}</span>
      </div>
      <div style={{position: 'absolute', right: 96, top: 76, display: 'flex', gap: 8, opacity: h}}>
        {ORDER.slice(1).map((id, i) => {
          const cur = id === s.id, done = i < ORDER.indexOf(s.id) - 1;
          return <div key={id} style={{width: cur ? 46 : 16, height: 6, borderRadius: 3,
            background: cur ? GRAD : done ? C.ink2 : C.line, boxShadow: cur ? `0 0 14px ${tint(C.magenta, 0.7)}` : 'none'}} />;
        })}
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
    <div style={{position: 'absolute', left: 0, right: 0, bottom: 42, display: 'flex', justifyContent: 'center', opacity: o,
      transform: `translateY(${(1 - o) * 10}px)`}}>
      <div style={{maxWidth: 1600, padding: '12px 34px', borderRadius: 18, background: 'rgba(14,14,20,0.78)', backdropFilter: 'blur(20px)',
        border: BORDER, boxShadow: '0 16px 40px rgba(0,0,0,0.5)', fontFamily: FONT, fontSize: 30, lineHeight: '44px', color: C.ink,
        textAlign: 'center', fontWeight: 600, letterSpacing: 0.5}}>
        {beat.text}
      </div>
    </div>
  );
};

/** Wraps a scene: zooms through with blur on entry, pulls back on exit. */
export const Transit: React.FC<{children: React.ReactNode}> = ({children}) => {
  const {frame, dur} = useScene();
  const a = ip(frame, 0, 20, easeOut);
  const b = ip(frame, dur - 16, 16, easeInOut);
  const blur = (1 - a) * 22 + b * 18;
  return (
    <AbsoluteFill style={{opacity: Math.min(a * 1.4, 1 - b), transform: `scale(${1.22 - 0.22 * a - 0.12 * b})`,
      filter: blur > 0.3 ? `blur(${blur}px)` : undefined}}>
      {children}
    </AbsoluteFill>
  );
};

/** Diagonal light sweep that crosses the frame at the start of each scene. */
export const Sweep: React.FC = () => {
  const {frame} = useScene();
  const t = prog(frame, 0, 22);
  if (t <= 0 || t >= 1) return null;
  return (
    <AbsoluteFill style={{pointerEvents: 'none', mixBlendMode: 'screen'}}>
      <div style={{position: 'absolute', top: -300, left: -800 + t * 3600, width: 380, height: 1700, transform: 'rotate(18deg)',
        background: `linear-gradient(90deg, transparent, ${tint(C.magenta, 0.16)}, ${tint(C.cyan, 0.28)}, transparent)`}} />
    </AbsoluteFill>
  );
};

const STARS = Array.from({length: 70}, (_, i) => ({x: rand(i + 1) * 1920, y: rand(i + 101) * 1080, r: 0.6 + rand(i + 201) * 1.6,
  sp: 0.15 + rand(i + 301) * 0.5, ph: rand(i + 401) * 6.28}));

/** Aurora washes, a receding perspective grid and drifting stars. */
export const Backdrop: React.FC = () => {
  const frame = useCurrentFrame();
  const f = frame / 30;
  const blob = (x: number, y: number, r: number, color: string, a: number) => (
    <div style={{position: 'absolute', left: x - r, top: y - r, width: r * 2, height: r * 2, borderRadius: '50%',
      background: `radial-gradient(circle, ${tint(color, a)} 0%, transparent 68%)`}} />
  );
  return (
    <AbsoluteFill style={{background: C.bg, overflow: 'hidden'}}>
      {blob(260 + Math.sin(f * 0.11) * 160, 160 + Math.cos(f * 0.08) * 90, 760, C.violet, 0.2)}
      {blob(1700 + Math.cos(f * 0.09) * 150, 260 + Math.sin(f * 0.12) * 120, 620, C.magenta, 0.11)}
      {blob(1300 + Math.sin(f * 0.07) * 200, 1050 + Math.cos(f * 0.1) * 60, 820, C.cyan, 0.1)}
      <div style={{position: 'absolute', left: -960, right: -960, top: 640, height: 900, transformOrigin: '50% 0%',
        transform: 'perspective(700px) rotateX(72deg)', opacity: 0.55,
        backgroundImage: `linear-gradient(${tint(C.violet, 0.5)} 1.5px, transparent 1.5px), linear-gradient(90deg, ${tint(C.violet, 0.5)} 1.5px, transparent 1.5px)`,
        backgroundSize: '90px 90px', backgroundPosition: `0px ${(frame * 1.6) % 90}px`,
        WebkitMaskImage: 'linear-gradient(to bottom, transparent 0%, #000 30%, #000 60%, transparent 100%)'}} />
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0}}>
        {STARS.map((s, i) => {
          const y = (s.y - frame * s.sp + 1080) % 1080;
          return <circle key={i} cx={s.x} cy={y} r={s.r} fill="#fff" opacity={0.2 + 0.5 * (0.5 + 0.5 * Math.sin(f * 2 + s.ph))} />;
        })}
      </svg>
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at center, transparent 45%, rgba(0,0,0,0.65) 100%)'}} />
    </AbsoluteFill>
  );
};
