import React from 'react';
import {C, FONT, MONO, SHADOW, tint} from './theme';
import {P, clamp, easeOut, ip, pointAt, pop, prog, useScene} from './anim';
import {Pop, Wire} from './kit';

export const LAYERS = [
  {id: 'app', name: '应用层', en: 'Application', c: C.purple},
  {id: 'transport', name: '传输层', en: 'Transport', c: C.orange},
  {id: 'network', name: '网络层', en: 'Network', c: C.blue},
  {id: 'link', name: '数据链路层', en: 'Data Link', c: C.green},
  {id: 'phys', name: '物理层', en: 'Physical', c: C.teal},
];

/** One layer slab: dark card with a coloured edge; `hl` lights it up. */
export const Slab: React.FC<{x: number; y: number; w: number; h: number; from: number; to?: number; color: string; name: React.ReactNode;
  en?: string; hl?: number; dim?: number; size?: number}> = ({x, y, w, h, from, to, color, name, en, hl = 0, dim = 0, size = 30}) => (
  <Pop from={from} to={to} x={x} y={y}>
    <div style={{width: w, height: h, borderRadius: 18, boxSizing: 'border-box', position: 'relative', overflow: 'hidden',
      display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 14, opacity: 1 - dim * 0.6,
      background: `linear-gradient(90deg, ${tint(color, 0.14 + 0.16 * hl)}, ${tint(color, 0.04 + 0.08 * hl)})`, backgroundColor: C.card,
      border: `1.5px solid ${tint(color, 0.28 + 0.6 * hl)}`, boxShadow: `${SHADOW}${hl > 0.01 ? `, 0 0 ${36 * hl}px ${tint(color, 0.3)}` : ''}`}}>
      <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: 6, background: color}} />
      <span style={{fontSize: size, fontWeight: 650, color: C.ink, fontFamily: FONT}}>{name}</span>
      {en && <span style={{fontSize: size * 0.62, color: tint(color, 0.85), fontFamily: FONT, fontWeight: 500}}>{en}</span>}
    </div>
  </Pop>
);

export type Field = {t: React.ReactNode; w: number; c: string; sub?: string};

/** A protocol unit drawn as a strip of fields. `born` (frame per field) springs fields in individually. */
export const Seg: React.FC<{fields: Field[]; h?: number; size?: number; born?: (number | undefined)[]}> = ({fields, h = 56, size = 22, born}) => {
  const {frame} = useScene();
  return (
    <div style={{display: 'flex', gap: 4}}>
      {fields.map((f, i) => {
        const b = born?.[i];
        const s = b === undefined ? 1 : pop(frame, b, 13);
        const flash = b === undefined ? 0 : 1 - prog(frame, b + 6, 30);
        return (
          <div key={i} style={{width: f.w * Math.min(1, s), height: h, borderRadius: 12, boxSizing: 'border-box', overflow: 'hidden',
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', opacity: clamp(s * 1.4),
            background: tint(f.c, 0.16 + 0.3 * flash), border: `1.5px solid ${tint(f.c, 0.55 + 0.45 * flash)}`,
            boxShadow: flash > 0 ? `0 0 ${24 * flash}px ${tint(f.c, 0.5)}` : 'none'}}>
            <span style={{fontSize: size, fontWeight: 650, color: f.c, fontFamily: FONT, whiteSpace: 'nowrap'}}>{f.t}</span>
            {f.sub && <span style={{fontSize: size * 0.68, color: C.muted, fontFamily: FONT, whiteSpace: 'nowrap', marginTop: 2}}>{f.sub}</span>}
          </div>
        );
      })}
    </div>
  );
};

export const segWidth = (fields: Field[]) => fields.reduce((a, f) => a + f.w, 0) + (fields.length - 1) * 4;

/** Round router badge with the classic four-arrow glyph. */
export const Router: React.FC<{x: number; y: number; from: number; to?: number; r?: number; color?: string; hl?: number; label?: React.ReactNode}> =
  ({x, y, from, to, r = 46, color = C.blue, hl = 0, label}) => {
    const a = r * 0.42, k = r * 0.16;
    return (
      <Pop from={from} to={to} x={x} y={y}>
        <div style={{position: 'relative', width: r * 2, height: r * 2}}>
          <svg width={r * 2} height={r * 2} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
            <circle cx={r} cy={r} r={r - 1} fill={C.card} stroke={tint(color, 0.45 + 0.55 * hl)} strokeWidth={2} />
            {hl > 0.01 && <circle cx={r} cy={r} r={r + 6 * hl} fill="none" stroke={tint(color, 0.25 * hl)} strokeWidth={8} />}
            <g stroke={color} strokeWidth={3} strokeLinecap="round" strokeLinejoin="round" fill="none" transform={`translate(${r},${r})`}>
              {[0, 90, 180, 270].map((d) => (
                <g key={d} transform={`rotate(${d})`}>
                  <path d={`M${k},0 L${a},0 M${a - k},${-k} L${a},0 L${a - k},${k}`} />
                </g>
              ))}
            </g>
          </svg>
          {label && <div style={{position: 'absolute', top: r * 2 + 10, left: '50%', transform: 'translateX(-50%)', whiteSpace: 'nowrap',
            fontSize: 20, color: C.muted, fontFamily: FONT, fontWeight: 500}}>{label}</div>}
        </div>
      </Pop>
    );
  };

/** Any content travelling along a polyline. `drop` makes it fall and fade on arrival. `stop` halts at that fraction (lost packet). */
export const Mover: React.FC<{pts: P[]; from: number; len: number; hold?: number; drop?: boolean; stop?: number; children: React.ReactNode}> =
  ({pts, from, len, hold = 0, drop, stop = 1, children}) => {
    const {frame} = useScene();
    const end = from + len * stop;
    const tail = drop || stop < 1 ? 24 : 6;
    if (frame < from || frame > end + hold + tail) return null;
    const {p} = pointAt(pts, Math.min(stop, ip(frame, from, len)));
    const after = frame - end - hold;
    const fade = after > 0 ? 1 - clamp(after / tail) : 1;
    const fall = drop && after > 0 ? easeOut(clamp(after / tail)) * 60 : 0;
    const o = Math.min(prog(frame, from, 5), fade);
    return (
      <div style={{position: 'absolute', left: p[0], top: p[1] + fall, transform: `translate(-50%,-50%) rotate(${fall * 0.3}deg)`, opacity: o}}>
        {children}
      </div>
    );
  };

/** Small capsule tag used as a moving packet. */
export const Tag: React.FC<{children: React.ReactNode; color?: string; mono?: boolean; size?: number}> = ({children, color = C.blue, mono = true, size = 21}) => (
  <div style={{padding: `${size * 0.3}px ${size * 0.75}px`, borderRadius: 999, background: tint(color, 0.22), border: `1.5px solid ${color}`,
    color: C.ink, fontSize: size, fontWeight: 600, fontFamily: mono ? MONO : FONT, whiteSpace: 'nowrap',
    boxShadow: `0 0 22px ${tint(color, 0.35)}`, backdropFilter: 'blur(8px)'}}>{children}</div>
);

export type Msg = {dir: 'cs' | 'sc'; y: number; label: React.ReactNode; from: number; color?: string; lost?: boolean; len?: number};

/** Two-lifeline sequence diagram (client on the left, server on the right). */
export const SeqDiagram: React.FC<{x1: number; x2: number; top: number; bottom: number; from: number; to?: number; msgs: Msg[];
  left?: string; right?: string; drop?: number}> = ({x1, x2, top, bottom, from, to = 1e9, msgs, left = '客户端', right = '服务器', drop = 80}) => {
  const {frame} = useScene();
  const o = Math.min(ip(frame, from, 14, easeOut), 1 - prog(frame, to, 12));
  if (o <= 0) return null;
  const line = ip(frame, from + 6, 24);
  return (
    <div style={{position: 'absolute', inset: 0, opacity: o}}>
      <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        {[x1, x2].map((x) => (
          <line key={x} x1={x} y1={top} x2={x} y2={top + (bottom - top) * line} stroke={C.line} strokeWidth={2} strokeDasharray="2 8"
            strokeLinecap="round" />
        ))}
        {msgs.map((m, i) => {
          const a: P = m.dir === 'cs' ? [x1, m.y] : [x2, m.y];
          const b: P = m.dir === 'cs' ? [x2, m.y + drop] : [x1, m.y + drop];
          const pts: P[] = m.lost ? [a, [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2]] : [a, b];
          return <Wire key={i} pts={pts} from={m.from} len={m.len ?? 20} color={m.color ?? C.blue} w={3} head={!m.lost} />;
        })}
      </svg>
      {msgs.map((m, i) => {
        const mx = (x1 + x2) / 2, my = m.y + drop / 2;
        const s = pop(frame, m.from + 4);
        const angle = (Math.atan2(drop, (x2 - x1) * (m.dir === 'cs' ? 1 : -1)) * 180) / Math.PI;
        const rot = m.dir === 'cs' ? angle : angle - 180;
        const lostO = m.lost ? pop(frame, m.from + (m.len ?? 20) * 0.5) : 0;
        return (
          <React.Fragment key={i}>
            <div style={{position: 'absolute', left: m.lost ? (x1 + mx) / 2 + 30 : mx, top: m.lost ? (m.y + my) / 2 - 8 : my,
              transform: `translate(-50%,-50%) rotate(${rot}deg) translateY(-26px)`, opacity: clamp(s * 1.5),
              fontFamily: MONO, fontSize: 23, fontWeight: 600, color: m.color ?? C.blue, whiteSpace: 'nowrap'}}>{m.label}</div>
            {m.lost && lostO > 0 && (
              <div style={{position: 'absolute', left: mx, top: my, transform: `translate(-50%,-50%) scale(${0.6 + 0.4 * lostO})`, opacity: clamp(lostO * 1.5),
                width: 44, height: 44, borderRadius: 22, background: tint(C.red, 0.2), border: `2px solid ${C.red}`, color: C.red,
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 26, fontWeight: 700, fontFamily: FONT}}>✕</div>
            )}
          </React.Fragment>
        );
      })}
      {[[x1, left], [x2, right]].map(([x, t]) => (
        <div key={String(x)} style={{position: 'absolute', left: Number(x), top: top - 34, transform: 'translate(-50%,-50%)',
          padding: '10px 28px', borderRadius: 16, background: C.card, boxShadow: SHADOW, color: C.ink, fontSize: 26, fontWeight: 650, fontFamily: FONT}}>{t}</div>
      ))}
    </div>
  );
};

/** State badge next to a lifeline. */
export const State: React.FC<{x: number; y: number; from: number; to?: number; color?: string; anchor?: 'left' | 'right'; children: React.ReactNode}> =
  ({x, y, from, to, color = C.muted, anchor = 'right', children}) => (
    <Pop from={from} to={to} x={x} y={y} anchor={anchor} rise={8}>
      <div style={{fontFamily: MONO, fontSize: 19, fontWeight: 600, color, padding: '5px 12px', borderRadius: 10,
        background: tint(color, 0.12), whiteSpace: 'nowrap'}}>{children}</div>
    </Pop>
  );

/** Path length helper so packets can move at a constant speed. */
export const pathLen = (pts: P[]) => pts.slice(1).reduce((a, p, i) => a + Math.hypot(p[0] - pts[i][0], p[1] - pts[i][1]), 0);
