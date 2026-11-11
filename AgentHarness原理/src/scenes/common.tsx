import React from 'react';
import {C, FONT, MONO, glow, tint} from '../theme';
import {ip, pop, prog, useScene, easeOut, clamp} from '../anim';
import {Orb, Pop, Shock, Svg} from '../kit';

export type Sat = {label: string; color: string; at: number};

/** The model orb wrapped in a Harness ring, with capability satellites sitting on the ring. */
export const HarnessRing: React.FC<{cx: number; cy: number; R?: number; orbR?: number; orbFrom: number; ringFrom: number; sats?: Sat[];
  to?: number; id: string; hl?: (i: number) => number; dim?: number; label?: string; orbLabel?: string; energy?: number; start?: number}> =
  ({cx, cy, R = 250, orbR = 110, orbFrom, ringFrom, sats = [], to = 1e9, id, hl, dim = 0, label = 'HARNESS', orbLabel = 'LLM', energy = 0, start = -90}) => {
    const {frame} = useScene();
    const draw = ip(frame, ringFrom, 36, easeOut);
    const out = prog(frame, to, 14);
    const o = (1 - out) * (1 - dim * 0.65);
    const circ = 2 * Math.PI * R;
    const tag = pop(frame, ringFrom + 26, 12);
    return (
      <>
        <Orb x={cx} y={cy} r={orbR} from={orbFrom} to={to} label={orbLabel} energy={energy} />
        {draw > 0 && o > 0 && (
          <Svg style={{opacity: o}}>
            <defs>
              <linearGradient id={`hr-${id}`} x1="0" y1="0" x2="1" y2="1">
                <stop offset="0" stopColor={C.violet} />
                <stop offset="0.5" stopColor={C.magenta} />
                <stop offset="1" stopColor={C.cyan} />
              </linearGradient>
            </defs>
            <circle cx={cx} cy={cy} r={R} fill="none" stroke={`url(#hr-${id})`} strokeOpacity={0.22} strokeWidth={26}
              strokeDasharray={`${circ * draw} ${circ}`} transform={`rotate(-90 ${cx} ${cy})`} />
            <circle cx={cx} cy={cy} r={R} fill="none" stroke={`url(#hr-${id})`} strokeWidth={3}
              strokeDasharray={`${circ * draw} ${circ}`} transform={`rotate(-90 ${cx} ${cy})`} />
            <circle cx={cx} cy={cy} r={R + 30} fill="none" stroke={C.violet} strokeOpacity={0.35 * draw} strokeWidth={1.5}
              strokeDasharray="3 16" transform={`rotate(${frame * 0.4} ${cx} ${cy})`} />
            <circle cx={cx} cy={cy} r={R - 26} fill="none" stroke={C.cyan} strokeOpacity={0.25 * draw} strokeWidth={1}
              strokeDasharray="40 30" transform={`rotate(${-frame * 0.7} ${cx} ${cy})`} />
            <Shock x={cx} y={cy} at={ringFrom + 34} r0={R} r1={R + 260} color={C.magenta} len={34} />
          </Svg>
        )}
        {tag > 0.01 && o > 0 && (
          <div style={{position: 'absolute', left: cx, top: cy + R, opacity: clamp(tag * 1.5) * o,
            transform: `translate(-50%,-50%) scale(${0.5 + 0.5 * tag})`}}>
            <div style={{padding: '6px 20px', borderRadius: 999, background: C.bg, border: `1.5px solid ${tint(C.magenta, 0.7)}`,
              fontFamily: MONO, fontSize: 20, fontWeight: 800, letterSpacing: 6, color: C.ink, boxShadow: glow(C.magenta, 0.5)}}>{label}</div>
          </div>
        )}
        {sats.map((s, i) => {
          const a = ((start + (360 / sats.length) * i) * Math.PI) / 180;
          const x = cx + R * Math.cos(a), y = cy + R * Math.sin(a);
          const h = hl ? hl(i) : 0;
          return (
            <Pop key={s.label} from={s.at} to={to} x={x} y={y} fx="zoom">
              <div style={{display: 'flex', alignItems: 'center', gap: 10, padding: '11px 22px', borderRadius: 16, fontFamily: FONT,
                background: `linear-gradient(160deg, ${tint(s.color, 0.22 + 0.25 * h)}, ${C.card})`, opacity: 1 - dim * 0.6,
                border: `1.5px solid ${tint(s.color, 0.55 + 0.45 * h)}`, boxShadow: glow(s.color, 0.45 + 0.8 * h),
                transform: `scale(${1 + 0.12 * h})`, whiteSpace: 'nowrap'}}>
                <div style={{width: 10, height: 10, borderRadius: 5, background: s.color, boxShadow: `0 0 12px ${s.color}`}} />
                <span style={{fontSize: 26, fontWeight: 800, color: C.ink}}>{s.label}</span>
              </div>
            </Pop>
          );
        })}
      </>
    );
  };

/** "Agent = Model + Harness", each term slamming in. */
export const Equation: React.FC<{x: number; y: number; from: number; to?: number; size?: number}> = ({x, y, from, to, size = 66}) => {
  const terms: [string, React.CSSProperties][] = [
    ['Agent', {backgroundImage: `linear-gradient(90deg, ${C.violet}, ${C.magenta}, ${C.cyan})`, WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent'}],
    ['=', {color: C.faint}], ['模型', {color: C.ink}], ['+', {color: C.faint}], ['Harness', {color: C.cyan, textShadow: `0 0 30px ${tint(C.cyan, 0.6)}`}],
  ];
  return (
    <Pop from={from} to={to} x={x} y={y} fx="rise">
      <div style={{display: 'flex', gap: size * 0.32, alignItems: 'baseline', fontFamily: FONT, fontWeight: 800, fontSize: size}}>
        {terms.map(([t, st], i) => (
          <Pop key={i} from={from + i * 5} x={0} y={0} anchor="topleft" fx="slam" style={{position: 'relative'}}>
            <span style={{whiteSpace: 'nowrap', ...st}}>{t}</span>
          </Pop>
        ))}
      </div>
    </Pop>
  );
};
