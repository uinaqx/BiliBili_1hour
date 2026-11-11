import React from 'react';
import {AbsoluteFill} from 'remotion';
import {BORDER, C, FONT, MONO, SHADOW, glow, tint} from './theme';
import {P, clamp, easeInOut, easeOut, ip, lerp, partial, pointAt, pop, prog, rand, useScene, vis} from './anim';

export const Svg: React.FC<{children: React.ReactNode; style?: React.CSSProperties}> = ({children, style}) => (
  <svg width={1920} height={1080} viewBox="0 0 1920 1080" style={{position: 'absolute', left: 0, top: 0, overflow: 'visible', ...style}}>
    {children}
  </svg>
);

type Anchor = 'center' | 'left' | 'right' | 'top' | 'topleft';
const ANCHOR: Record<Anchor, string> = {
  center: 'translate(-50%, -50%)', left: 'translate(0, -50%)', right: 'translate(-100%, -50%)', top: 'translate(-50%, 0)', topleft: '',
};
export type Fx = 'rise' | 'zoom' | 'slam' | 'drop' | 'left' | 'right';

/** Springs in at `from` with a motion-blurred entrance, fades out at `to`. */
export const Pop: React.FC<{from: number; to?: number; x: number; y: number; anchor?: Anchor; fx?: Fx; style?: React.CSSProperties;
  children: React.ReactNode}> = ({from, to = 1e9, x, y, anchor = 'center', fx = 'rise', style, children}) => {
  const {frame} = useScene();
  const s = pop(frame, from, fx === 'slam' ? 11 : 13);
  const out = prog(frame, to, 12);
  const o = Math.min(clamp(s * 1.6), 1 - out);
  if (o <= 0.002) return null;
  const k = 1 - s;
  const move = {
    rise: `translateY(${k * 60}px) scale(${0.9 + 0.1 * s})`,
    zoom: `scale(${0.3 + 0.7 * s})`,
    slam: `scale(${1 + 1.4 * k})`,
    drop: `translateY(${-k * 120}px) rotate(${k * -6}deg)`,
    left: `translateX(${-k * 160}px)`,
    right: `translateX(${k * 160}px)`,
  }[fx];
  const blur = Math.abs(k) * (fx === 'slam' ? 18 : 10) + out * 10;
  return (
    <div style={{position: 'absolute', left: x, top: y, opacity: o, fontFamily: FONT, filter: blur > 0.3 ? `blur(${blur}px)` : undefined,
      transform: `${ANCHOR[anchor]} ${move} scale(${1 - 0.08 * out})`, ...style}}>
      {children}
    </div>
  );
};

export const card = (extra: React.CSSProperties = {}): React.CSSProperties => ({
  background: `linear-gradient(160deg, ${C.card2}, ${C.card})`, borderRadius: 26, border: BORDER, boxShadow: SHADOW, ...extra,
});

/** Dark diagram block; `hl` 0..1 lights it up in `color`. */
export const Block: React.FC<{x: number; y: number; w?: number; h?: number; from: number; to?: number; title: React.ReactNode; sub?: React.ReactNode;
  color?: string; hl?: number; size?: number; mono?: boolean; fx?: Fx; children?: React.ReactNode}> =
  ({x, y, w = 220, h = 110, from, to, title, sub, color = C.violet, hl = 0, size = 30, mono, fx, children}) => (
    <Pop from={from} to={to} x={x} y={y} fx={fx}>
      <div style={{...card({borderRadius: 22}), width: w, height: h, boxSizing: 'border-box', display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center', transform: `scale(${1 + 0.06 * hl})`,
        background: hl > 0.01 ? `linear-gradient(160deg, ${tint(color, 0.28 * hl)}, ${C.card})` : card().background,
        border: `1.5px solid ${hl > 0.01 ? tint(color, 0.3 + 0.7 * hl) : 'rgba(255,255,255,0.09)'}`,
        boxShadow: hl > 0.01 ? `${SHADOW}, ${glow(color, hl)}` : SHADOW}}>
        <div style={{fontSize: size, fontWeight: 700, color: C.ink, fontFamily: mono ? MONO : FONT, lineHeight: 1.15}}>{title}</div>
        {sub && <div style={{fontSize: 19, color: hl > 0.5 ? C.ink2 : C.muted, marginTop: 6}}>{sub}</div>}
        {children}
      </div>
    </Pop>
  );

export const Pill: React.FC<{children: React.ReactNode; color?: string; solid?: boolean; size?: number; style?: React.CSSProperties}> =
  ({children, color = C.violet, solid, size = 24, style}) => (
    <span style={{display: 'inline-flex', alignItems: 'center', gap: 8, padding: `${size * 0.34}px ${size * 0.85}px`, borderRadius: 999,
      background: solid ? color : tint(color, 0.13), color: solid ? C.dark : color, fontSize: size, fontWeight: 700, fontFamily: FONT,
      border: `1px solid ${tint(color, solid ? 1 : 0.4)}`, boxShadow: solid ? glow(color, 0.6) : 'none', whiteSpace: 'nowrap', ...style}}>
      {children}
    </span>
  );

export const Label: React.FC<{x: number; y: number; from: number; to?: number; children: React.ReactNode; color?: string; size?: number;
  weight?: number; anchor?: Anchor; mono?: boolean; fx?: Fx}> =
  ({x, y, from, to, children, color = C.muted, size = 22, weight = 600, anchor = 'center', mono, fx}) => (
    <Pop from={from} to={to} x={x} y={y} anchor={anchor} fx={fx}>
      <div style={{color, fontSize: size, fontWeight: weight, whiteSpace: 'nowrap', fontFamily: mono ? MONO : FONT}}>{children}</div>
    </Pop>
  );

/** Neon polyline that draws itself; `flow` animates dashes along it to show data moving. */
export const Wire: React.FC<{pts: P[]; from: number; len?: number; to?: number; color?: string; w?: number; head?: boolean;
  flow?: boolean; opacity?: number; dash?: string}> =
  ({pts, from, len = 18, to = 1e9, color = C.faint, w = 3, head = true, flow, opacity = 1, dash}) => {
    const {frame} = useScene();
    const p = ip(frame, from, len);
    const o = (1 - prog(frame, to, 12)) * opacity;
    if (p <= 0 || o <= 0) return null;
    const d = partial(pts, p).map((v) => v.join(',')).join(' ');
    const {p: end, angle} = pointAt(pts, p);
    const hs = 5 + w * 2.2;
    return (
      <g opacity={o}>
        <polyline points={d} fill="none" stroke={color} strokeOpacity={0.18} strokeWidth={w * 5} strokeLinecap="round" strokeLinejoin="round" />
        <polyline points={d} fill="none" stroke={color} strokeWidth={w} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={dash} />
        {flow && <polyline points={d} fill="none" stroke="#fff" strokeOpacity={0.85} strokeWidth={w * 0.9} strokeLinecap="round"
          strokeDasharray="2 26" strokeDashoffset={-frame * 3} />}
        {head && p > 0.02 && <path d={`M0,0 L${-hs},${-hs * 0.6} L${-hs},${hs * 0.6} Z`} fill={color}
          transform={`translate(${end[0]},${end[1]}) rotate(${angle})`} />}
      </g>
    );
  };

/** Glowing comet that travels a path in SVG, leaving a fading tail. */
export const Comet: React.FC<{pts: P[]; from: number; len: number; color?: string; r?: number; tail?: number}> =
  ({pts, from, len, color = C.cyan, r = 9, tail = 0.16}) => {
    const {frame} = useScene();
    if (frame < from || frame > from + len + 8) return null;
    const t = ip(frame, from, len, easeInOut);
    const fade = 1 - prog(frame, from + len, 8);
    const n = 14;
    return (
      <g opacity={fade}>
        {Array.from({length: n}, (_, i) => {
          const q = pointAt(pts, t - (tail * i) / n).p;
          const k = 1 - i / n;
          return <circle key={i} cx={q[0]} cy={q[1]} r={r * (0.35 + 0.65 * k)} fill={color} opacity={0.65 * k * k} />;
        })}
        <circle cx={pointAt(pts, t).p[0]} cy={pointAt(pts, t).p[1]} r={r * 2.6} fill={color} opacity={0.22} />
        <circle cx={pointAt(pts, t).p[0]} cy={pointAt(pts, t).p[1]} r={r * 0.7} fill="#fff" />
      </g>
    );
  };

/** HTML tag that rides along a path (for labelled packets). */
export const Packet: React.FC<{pts: P[]; from: number; len: number; color?: string; tag: React.ReactNode; hold?: number}> =
  ({pts, from, len, color = C.violet, tag, hold = 0}) => {
    const {frame} = useScene();
    if (frame < from || frame > from + len + hold) return null;
    const t = ip(frame, from, len);
    const {p} = pointAt(pts, t);
    const o = Math.min(prog(frame, from, 5), 1 - prog(frame, from + len + hold - 6, 6));
    const speed = Math.abs(ip(frame + 1, from, len) - t) * 60;
    return (
      <div style={{position: 'absolute', left: p[0], top: p[1], transform: `translate(-50%,-50%) scale(${1 + speed * 0.15})`, opacity: o,
        filter: speed > 0.4 ? `blur(${Math.min(3, speed * 1.2)}px)` : undefined}}>
        <div style={{padding: '7px 18px', borderRadius: 999, background: color, color: C.dark, fontSize: 22, fontWeight: 700,
          whiteSpace: 'nowrap', boxShadow: glow(color, 0.8), fontFamily: MONO}}>{tag}</div>
      </div>
    );
  };

/** Particle explosion at `at`. */
export const Burst: React.FC<{x: number; y: number; at: number; color?: string; n?: number; dist?: number; len?: number; seed?: number}> =
  ({x, y, at, color = C.magenta, n = 26, dist = 220, len = 34, seed = 1}) => {
    const {frame} = useScene();
    const t = prog(frame, at, len);
    if (t <= 0 || t >= 1) return null;
    const e = easeOut(t);
    return (
      <g>
        {Array.from({length: n}, (_, i) => {
          const a = (i / n) * Math.PI * 2 + rand(seed * 31 + i) * 0.6;
          const d = dist * (0.45 + 0.55 * rand(seed * 17 + i)) * e;
          const px = x + Math.cos(a) * d, py = y + Math.sin(a) * d;
          const tx = x + Math.cos(a) * d * 0.72, ty = y + Math.sin(a) * d * 0.72;
          return <line key={i} x1={tx} y1={ty} x2={px} y2={py} stroke={i % 3 === 0 ? '#fff' : color} strokeWidth={3 * (1 - t) + 1}
            strokeLinecap="round" opacity={1 - t} />;
        })}
      </g>
    );
  };

/** Expanding shockwave ring at `at`. */
export const Shock: React.FC<{x: number; y: number; at: number; color?: string; r0?: number; r1?: number; len?: number; w?: number}> =
  ({x, y, at, color = C.cyan, r0 = 40, r1 = 420, len = 30, w = 4}) => {
    const {frame} = useScene();
    const t = prog(frame, at, len);
    if (t <= 0 || t >= 1) return null;
    const r = lerp(r0, r1, easeOut(t));
    return (
      <g>
        <circle cx={x} cy={y} r={r} fill="none" stroke={color} strokeWidth={w * 6 * (1 - t)} opacity={0.15 * (1 - t)} />
        <circle cx={x} cy={y} r={r} fill="none" stroke={color} strokeWidth={w * (1 - t) + 0.5} opacity={1 - t} />
      </g>
    );
  };

/** The model: a glowing sphere with a spinning conic halo. */
export const Orb: React.FC<{x: number; y: number; r?: number; from: number; to?: number; label?: string; colors?: [string, string, string];
  energy?: number}> = ({x, y, r = 110, from, to = 1e9, label = 'LLM', colors = [C.violet, C.magenta, C.cyan], energy = 0}) => {
  const {frame} = useScene();
  const s = pop(frame, from, 10);
  const o = Math.min(clamp(s * 1.5), 1 - prog(frame, to, 14));
  if (o <= 0.002) return null;
  const breathe = 1 + 0.025 * Math.sin(frame / 9) + 0.08 * energy;
  const [a, b, c] = colors;
  const ring = (rr: number, w: number, speed: number, alpha: number) => (
    <div style={{position: 'absolute', left: -rr, top: -rr, width: rr * 2, height: rr * 2, borderRadius: '50%', opacity: alpha,
      background: `conic-gradient(from ${frame * speed}deg, ${a}, ${b}, ${c}, transparent 70%, ${a})`,
      WebkitMaskImage: `radial-gradient(farthest-side, transparent calc(100% - ${w + 1}px), #000 calc(100% - ${w}px))`}} />
  );
  return (
    <div style={{position: 'absolute', left: x, top: y, opacity: o, transform: `scale(${(0.2 + 0.8 * s) * breathe})`}}>
      <div style={{position: 'absolute', left: -r * 2.2, top: -r * 2.2, width: r * 4.4, height: r * 4.4, borderRadius: '50%',
        background: `radial-gradient(circle, ${tint(a, 0.35 + 0.25 * energy)} 0%, ${tint(b, 0.12)} 35%, transparent 65%)`}} />
      {ring(r * 1.32, 3, 2.2, 0.9)}
      {ring(r * 1.55, 2, -1.4, 0.5)}
      <div style={{position: 'absolute', left: -r, top: -r, width: r * 2, height: r * 2, borderRadius: '50%',
        background: `radial-gradient(circle at 34% 28%, #ffffff 0%, ${tint(c, 0.9)} 12%, ${a} 48%, #1a0b3d 100%)`,
        boxShadow: `0 0 ${60 + 60 * energy}px ${tint(a, 0.7)}, inset -${r * 0.25}px -${r * 0.3}px ${r * 0.6}px rgba(0,0,0,0.55)`,
        display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        <span style={{fontFamily: FONT, fontWeight: 800, fontSize: r * 0.36, color: '#fff', letterSpacing: 2,
          textShadow: '0 2px 12px rgba(0,0,0,0.45)'}}>{label}</span>
      </div>
    </div>
  );
};

/** RGB-split glitch text; the split spikes inside [hitFrom, hitFrom+hitLen]. */
export const Glitch: React.FC<{children: string; size: number; hitFrom: number; hitLen?: number; weight?: number; style?: React.CSSProperties}> =
  ({children, size, hitFrom, hitLen = 14, weight = 800, style}) => {
    const {frame} = useScene();
    const hit = frame >= hitFrom && frame < hitFrom + hitLen ? 1 - (frame - hitFrom) / hitLen : 0;
    const jit = hit > 0 ? (rand(frame) - 0.5) * 2 : 0;
    const off = 3 + hit * 22;
    const base: React.CSSProperties = {position: 'absolute', left: 0, top: 0, fontSize: size, fontWeight: weight, whiteSpace: 'nowrap', fontFamily: FONT};
    return (
      <div style={{position: 'relative', display: 'inline-block', fontSize: size, fontWeight: weight, whiteSpace: 'nowrap', fontFamily: FONT, ...style}}>
        <span style={{visibility: 'hidden'}}>{children}</span>
        <span style={{...base, color: C.magenta, opacity: 0.8, transform: `translate(${-off + jit * 10}px, ${jit * 4}px)`, mixBlendMode: 'screen'}}>{children}</span>
        <span style={{...base, color: C.cyan, opacity: 0.8, transform: `translate(${off - jit * 10}px, ${-jit * 4}px)`, mixBlendMode: 'screen'}}>{children}</span>
        <span style={{...base, color: '#fff', clipPath: hit > 0.3 ? `inset(${rand(frame * 3) * 60}% 0 ${rand(frame * 7) * 30}% 0)` : undefined,
          transform: `translateX(${jit * 14}px)`}}>{children}</span>
        {hit > 0.3 && <span style={{...base, color: '#fff', clipPath: `inset(0 0 ${40 + rand(frame * 5) * 40}% 0)`}}>{children}</span>}
      </div>
    );
  };

const KW = /^(def|for|in|if|not|return|while|range|True|False|None|and|or|await|async)$/;
/** Minimal syntax colouring for Python / JSON / shell snippets. */
const colorize = (line: string): React.ReactNode[] => {
  const out: React.ReactNode[] = [];
  const re = /(#.*$)|("(?:[^"\\]|\\.)*")(\s*:)?|(\b[A-Za-z_]\w*\b)(\()?|(\b\d+\b)|(^\s*\$ )|(✓|✕)/g;
  let last = 0, m: RegExpExecArray | null, k = 0;
  while ((m = re.exec(line))) {
    if (m.index > last) out.push(line.slice(last, m.index));
    const [all, com, str, colon, word, paren, num, prompt, mark] = m;
    const span = (text: string, color: string, extra: React.CSSProperties = {}) => <span key={k++} style={{color, ...extra}}>{text}</span>;
    if (com) out.push(span(com, C.faint, {fontStyle: 'italic'}));
    else if (str) { out.push(span(str, colon ? C.cyan : C.gold)); if (colon) out.push(colon); }
    else if (word) {
      if (KW.test(word)) { out.push(span(word, C.magenta, {fontWeight: 700})); if (paren) out.push(paren); }
      else if (paren) { out.push(span(word, C.cyan)); out.push(paren); }
      else if (/^[A-Z_]{3,}$/.test(word)) out.push(span(word, C.gold));
      else out.push(word);
    } else if (num) out.push(span(num, C.lime));
    else if (prompt) out.push(span(prompt, C.lime, {fontWeight: 700}));
    else if (mark) out.push(span(mark, mark === '✓' ? C.lime : C.red, {fontWeight: 800}));
    else out.push(all);
    last = m.index + all.length;
  }
  if (last < line.length) out.push(line.slice(last));
  return out;
};

/** Code window. Lines type in from `from`; `hl` lines glow, others dim. */
export const Code: React.FC<{x: number; y: number; w: number; from: number; to?: number; lines: string[]; hl?: number[]; hlColor?: string;
  title?: string; size?: number; reveal?: number; fx?: Fx; anchor?: Anchor}> =
  ({x, y, w, from, to, lines, hl = [], hlColor = C.violet, title, size = 22, reveal = 3, fx, anchor}) => {
    const {frame} = useScene();
    const lh = size * 1.75;
    return (
      <Pop from={from} to={to} x={x} y={y} fx={fx} anchor={anchor}>
        <div style={{...card({borderRadius: 20}), width: w, boxSizing: 'border-box', overflow: 'hidden'}}>
          <div style={{height: 46, display: 'flex', alignItems: 'center', gap: 9, padding: '0 20px', borderBottom: BORDER,
            background: 'rgba(255,255,255,0.025)'}}>
            {[C.red, C.gold, C.lime].map((c) => <div key={c} style={{width: 12, height: 12, borderRadius: 6, background: tint(c, 0.75)}} />)}
            {title && <span style={{marginLeft: 12, fontFamily: MONO, fontSize: 17, color: C.muted}}>{title}</span>}
          </div>
          <div style={{padding: '16px 0'}}>
            {lines.map((ln, i) => {
              const ro = prog(frame, from + 6 + i * reveal, 6);
              const on = hl.includes(i);
              return (
                <div key={i} style={{height: lh, display: 'flex', alignItems: 'center', whiteSpace: 'pre', fontFamily: MONO, fontSize: size,
                  color: C.ink2, padding: '0 26px', opacity: ro * (hl.length && !on ? 0.38 : 1), transform: `translateX(${(1 - ro) * 20}px)`,
                  background: on ? `linear-gradient(90deg, ${tint(hlColor, 0.3)}, ${tint(hlColor, 0.04)})` : 'transparent',
                  boxShadow: on ? `inset 4px 0 0 ${hlColor}` : 'none'}}>
                  <span style={{width: size * 1.6, color: on ? hlColor : C.faint, fontSize: size * 0.8, flexShrink: 0}}>{i + 1}</span>
                  <span>{colorize(ln)}</span>
                </div>
              );
            })}
          </div>
        </div>
      </Pop>
    );
  };

/** Scene camera: interpolates [frame, zoom, panX, panY] keys; rotation optional as 5th value. */
export const Cam: React.FC<{keys: [number, number, number, number, number?][]; children: React.ReactNode}> = ({keys, children}) => {
  const {frame} = useScene();
  let z = keys[0][1], x = keys[0][2], y = keys[0][3], r = keys[0][4] ?? 0;
  for (let i = 1; i < keys.length; i++) {
    const [f0] = keys[i - 1], [f1, z1, x1, y1, r1 = 0] = keys[i];
    if (frame <= f0) break;
    const t = easeInOut(clamp((frame - f0) / Math.max(1, f1 - f0)));
    z = lerp(z, z1, t); x = lerp(x, x1, t); y = lerp(y, y1, t); r = lerp(r, r1, t);
  }
  return <AbsoluteFill style={{transform: `translate(${x}px, ${y}px) scale(${z}) rotate(${r}deg)`, transformOrigin: '960px 540px'}}>{children}</AbsoluteFill>;
};

/** Screen shake offset that decays after `at`. */
export const shake = (frame: number, at: number, amp = 14, len = 16): string => {
  const t = prog(frame, at, len);
  if (t <= 0 || t >= 1) return 'none';
  const k = (1 - t) * amp;
  return `translate(${(rand(frame * 1.7) - 0.5) * 2 * k}px, ${(rand(frame * 2.3) - 0.5) * 2 * k}px)`;
};

export const useCount = (from: number, len: number, a: number, b: number) => {
  const {frame} = useScene();
  return Math.round(a + (b - a) * ip(frame, from, len, easeOut));
};

export const useVis = (from: number, to = 1e9, len = 14) => {
  const {frame} = useScene();
  return vis(frame, from, to, len);
};
