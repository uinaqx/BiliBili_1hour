import React from 'react';
import {C, FONT, MONO, SHADOW, tint} from './theme';
import {P, clamp, easeOut, ip, partial, pointAt, pop, prog, useScene, vis} from './anim';

export const Svg: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute', left: 0, top: 0, overflow: 'visible', ...style}}>
    {children}
  </svg>
);

type Anchor = 'center' | 'left' | 'right' | 'top' | 'topleft';
const ANCHOR: Record<Anchor, string> = {
  center: 'translate(-50%, -50%)', left: 'translate(0, -50%)', right: 'translate(-100%, -50%)', top: 'translate(-50%, 0)', topleft: 'none',
};

/** Springs in at `from` (rise + scale), fades out at `to`. */
export const Pop: React.FC<{from: number; to?: number; x: number; y: number; anchor?: Anchor; rise?: number; style?: React.CSSProperties; children: React.ReactNode}> =
  ({from, to = 1e9, x, y, anchor = 'center', rise = 22, style, children}) => {
    const {frame} = useScene();
    const s = pop(frame, from);
    const o = Math.min(clamp(s * 1.5), 1 - prog(frame, to, 12));
    if (o <= 0.002) return null;
    const base = ANCHOR[anchor] === 'none' ? '' : ANCHOR[anchor];
    return (
      <div style={{position: 'absolute', left: x, top: y, opacity: o, fontFamily: FONT,
        transform: `${base} translateY(${(1 - s) * rise}px) scale(${0.94 + 0.06 * s})`, ...style}}>
        {children}
      </div>
    );
  };

export const card = (extra: React.CSSProperties = {}): React.CSSProperties => ({
  background: C.card, borderRadius: 24, boxShadow: SHADOW, ...extra,
});

/** White rounded block for diagrams; `hl` 0..1 tints it with `color`. */
export const Block: React.FC<{x: number; y: number; w?: number; h?: number; from: number; to?: number; title: React.ReactNode; sub?: React.ReactNode;
  color?: string; hl?: number; size?: number; mono?: boolean; children?: React.ReactNode; radius?: number}> =
  ({x, y, w = 200, h = 100, from, to, title, sub, color = C.blue, hl = 0, size = 30, mono, children, radius = 22}) => (
    <Pop from={from} to={to} x={x} y={y}>
      <div style={{width: w, height: h, borderRadius: radius, boxSizing: 'border-box', display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center', backgroundColor: C.card,
        backgroundImage: `linear-gradient(${tint(color, 0.18 * hl)}, ${tint(color, 0.18 * hl)})`,
        border: `2px solid ${hl > 0.01 ? tint(color, 0.35 + 0.65 * hl) : 'rgba(255,255,255,0.07)'}`,
        boxShadow: `${SHADOW}${hl > 0.01 ? `, 0 0 0 ${8 * hl}px ${tint(color, 0.1)}` : ''}`}}>
        <div style={{fontSize: size, fontWeight: 650, color: C.ink, fontFamily: mono ? MONO : FONT, lineHeight: 1.15}}>{title}</div>
        {sub && <div style={{fontSize: 19, color: C.muted, marginTop: 6, fontFamily: FONT}}>{sub}</div>}
        {children}
      </div>
    </Pop>
  );

export const Pill: React.FC<{children: React.ReactNode; color?: string; solid?: boolean; size?: number; style?: React.CSSProperties}> =
  ({children, color = C.blue, solid, size = 24, style}) => (
    <span style={{display: 'inline-flex', alignItems: 'center', gap: 8, padding: `${size * 0.32}px ${size * 0.8}px`, borderRadius: 999,
      background: solid ? color : tint(color, 0.16), color: solid ? '#fff' : color, fontSize: size, fontWeight: 600, fontFamily: FONT,
      whiteSpace: 'nowrap', ...style}}>
      {children}
    </span>
  );

/** Floating text label. */
export const Label: React.FC<{x: number; y: number; from: number; to?: number; children: React.ReactNode; color?: string; size?: number;
  weight?: number; anchor?: Anchor; mono?: boolean}> =
  ({x, y, from, to, children, color = C.muted, size = 22, weight = 500, anchor = 'center', mono}) => (
    <Pop from={from} to={to} x={x} y={y} anchor={anchor} rise={10}>
      <div style={{color, fontSize: size, fontWeight: weight, whiteSpace: 'nowrap', fontFamily: mono ? MONO : FONT}}>{children}</div>
    </Pop>
  );

/** Polyline that draws itself from `from` over `len` frames, with an optional arrow head. */
export const Wire: React.FC<{pts: P[]; from: number; len?: number; to?: number; color?: string; w?: number; dash?: string; head?: boolean; opacity?: number}> =
  ({pts, from, len = 18, to = 1e9, color = C.faint, w = 3, dash, head = true, opacity = 1}) => {
    const {frame} = useScene();
    const p = ip(frame, from, len);
    const o = (1 - prog(frame, to, 12)) * opacity;
    if (p <= 0 || o <= 0) return null;
    const q = partial(pts, p);
    const {p: end, angle} = pointAt(pts, p);
    const hs = 4 + w * 2.2;
    return (
      <g opacity={o}>
        <polyline points={q.map((v) => v.join(',')).join(' ')} fill="none" stroke={color} strokeWidth={w} strokeLinecap="round"
          strokeLinejoin="round" strokeDasharray={dash} />
        {head && p > 0.02 && <path d={`M0,0 L${-hs},${-hs * 0.55} L${-hs},${hs * 0.55} Z`} fill={color}
          transform={`translate(${end[0]},${end[1]}) rotate(${angle})`} />}
      </g>
    );
  };

/** Glowing dot (optionally with a text tag) moving along a polyline between `from` and `from+len`. */
export const Packet: React.FC<{pts: P[]; from: number; len: number; color?: string; r?: number; tag?: React.ReactNode; hold?: number}> =
  ({pts, from, len, color = C.blue, r = 10, tag, hold = 0}) => {
    const {frame} = useScene();
    if (frame < from || frame > from + len + hold) return null;
    const {p} = pointAt(pts, ip(frame, from, len));
    const o = Math.min(prog(frame, from, 5), 1 - prog(frame, from + len + hold - 5, 5));
    return (
      <div style={{position: 'absolute', left: p[0], top: p[1], transform: 'translate(-50%,-50%)', opacity: o, fontFamily: FONT}}>
        {tag ? (
          <div style={{padding: '6px 16px', borderRadius: 999, background: color, color: '#fff', fontSize: 22, fontWeight: 650,
            whiteSpace: 'nowrap', boxShadow: `0 6px 20px ${tint(color, 0.45)}`, fontFamily: MONO}}>{tag}</div>
        ) : (
          <div style={{width: r * 2, height: r * 2, borderRadius: r, background: color, boxShadow: `0 0 0 6px ${tint(color, 0.18)}, 0 0 24px ${tint(color, 0.6)}`}} />
        )}
      </div>
    );
  };

/** One binary digit tile. `lit` 0..1 fills it with color. */
export const Bit: React.FC<{v: string; size?: number; lit?: number; color?: string; ring?: string; dim?: number}> =
  ({v, size = 80, lit = 0, color = C.blue, ring, dim = 0}) => (
    <div style={{width: size, height: size, borderRadius: size * 0.24, display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontFamily: MONO, fontSize: size * 0.52, fontWeight: 600, boxSizing: 'border-box',
      backgroundColor: C.card, backgroundImage: `linear-gradient(${tint(color, lit)}, ${tint(color, lit)})`,
      color: lit > 0.5 ? '#fff' : C.ink, opacity: 1 - dim * 0.7,
      border: ring ? `3px solid ${ring}` : '1px solid rgba(255,255,255,0.08)', boxShadow: SHADOW}}>
      {v}
    </div>
  );

/** A row of bits with a wider gap every four bits. Each tile springs in staggered from `from`. */
export const BitRow: React.FC<{bits: string; x: number; y: number; from: number; to?: number; size?: number; gap?: number;
  lit?: (i: number) => number; color?: (i: number) => string; ring?: (i: number) => string | undefined; stagger?: number}> =
  ({bits, x, y, from, to, size = 64, gap = 10, lit, color, ring, stagger = 2}) => {
    const {frame} = useScene();
    const o = vis(frame, from, to);
    if (o <= 0) return null;
    return (
      <div style={{position: 'absolute', left: x, top: y, transform: 'translateY(-50%)', display: 'flex', opacity: o}}>
        {bits.split('').map((v, i) => {
          const s = pop(frame, from + i * stagger);
          return (
            <div key={i} style={{marginLeft: i === 0 ? 0 : i % 4 === 0 ? gap * 3 : gap, transform: `translateY(${(1 - s) * 16}px)`, opacity: clamp(s * 1.5)}}>
              <Bit v={v} size={size} lit={lit?.(i) ?? 0} color={color?.(i) ?? C.blue} ring={ring?.(i)} />
            </div>
          );
        })}
      </div>
    );
  };

export const bitRowWidth = (n: number, size = 64, gap = 10) => n * size + (n - 1) * gap + Math.floor((n - 1) / 4) * gap * 2;

/** Animated number between a and b. */
export const useCount = (from: number, len: number, a: number, b: number) => {
  const {frame} = useScene();
  return Math.round(a + (b - a) * ip(frame, from, len, easeOut));
};

/** Stylized processor chip. */
export const Chip: React.FC<{x: number; y: number; size?: number; label?: string; glow?: number}> = ({x, y, size = 260, label = 'CPU', glow = 0}) => {
  const pins = 7, s = size, inner = s * 0.62, pinLen = s * 0.09, pinW = s * 0.035;
  const span = s * 0.7;
  const pinPos = Array.from({length: pins}, (_, i) => -span / 2 + (span * i) / (pins - 1));
  return (
    <g transform={`translate(${x},${y})`}>
      <defs>
        <linearGradient id="die" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0" stopColor="#0a84ff" />
          <stop offset="1" stopColor="#bf5af2" />
        </linearGradient>
        <filter id="chipShadow" x="-50%" y="-50%" width="200%" height="200%">
          <feDropShadow dx="0" dy="14" stdDeviation="20" floodColor="#000" floodOpacity="0.5" />
        </filter>
      </defs>
      {pinPos.map((p, i) => (
        <g key={i} fill="#48484c">
          <rect x={p - pinW / 2} y={-s / 2 - pinLen} width={pinW} height={pinLen} rx={pinW / 2} />
          <rect x={p - pinW / 2} y={s / 2} width={pinW} height={pinLen} rx={pinW / 2} />
          <rect x={-s / 2 - pinLen} y={p - pinW / 2} width={pinLen} height={pinW} rx={pinW / 2} />
          <rect x={s / 2} y={p - pinW / 2} width={pinLen} height={pinW} rx={pinW / 2} />
        </g>
      ))}
      <rect x={-s / 2} y={-s / 2} width={s} height={s} rx={s * 0.14} fill="#2c2c30" filter="url(#chipShadow)" />
      <rect x={-inner / 2} y={-inner / 2} width={inner} height={inner} rx={s * 0.08} fill="url(#die)" />
      {glow > 0 && <rect x={-inner / 2 - 8} y={-inner / 2 - 8} width={inner + 16} height={inner + 16} rx={s * 0.1} fill="none"
        stroke="#2997ff" strokeOpacity={0.35 * glow} strokeWidth={6} />}
      <text x={0} y={s * 0.065} textAnchor="middle" fontFamily={FONT} fontWeight={700} fontSize={s * 0.17} fill="#fff" letterSpacing={2}>{label}</text>
    </g>
  );
};

/** Opacity of an element living in [from, to). */
export const useVis = (from: number, to = 1e9, len = 14) => {
  const {frame} = useScene();
  return vis(frame, from, to, len);
};
