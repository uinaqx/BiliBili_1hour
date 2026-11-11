import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT, MONO, TITLE_GRAD, tint} from '../theme';
import {P, clamp, easeOut, ip, pop, prog, useScene, vis} from '../anim';
import {Label, Pill, Pop, Svg, useCount} from '../kit';
import {LAYERS, Mover, Slab, Tag, pathLen} from '../net';

const N: P[] = [
  [200, 540], [420, 330], [430, 760], [650, 520], [760, 250], [800, 820], [980, 420],
  [1000, 690], [1220, 280], [1240, 560], [1260, 830], [1480, 360], [1500, 700], [1720, 540],
];
const E: [number, number][] = [
  [0, 1], [0, 2], [1, 3], [2, 3], [1, 4], [2, 5], [3, 6], [3, 7], [4, 6], [5, 7], [4, 8], [6, 8], [6, 9], [7, 9],
  [7, 10], [8, 11], [9, 11], [9, 12], [10, 12], [11, 13], [12, 13], [5, 10],
];
const ROUTE = [0, 1, 3, 6, 9, 12, 13];
const ROUTES = [[0, 1, 4, 8, 11, 13], [0, 1, 3, 6, 9, 11, 13], [0, 2, 3, 7, 9, 12, 13], [0, 2, 5, 10, 12, 13]];
const PK = [C.blue, C.teal, C.indigo, C.purple];
const onRoute = (r: number[], a: number, b: number) => r.some((v, i) => i > 0 && ((r[i - 1] === a && v === b) || (r[i - 1] === b && v === a)));

const Mesh: React.FC = () => {
  const {frame, at} = useScene();
  const o = vis(frame, 0, at(2, 0.02), 18);
  if (o <= 0) return null;
  const route = ip(frame, at(0, 0.32), 20);
  const pkt = at(1, 0.22);
  const ends = clamp(pop(frame, at(0, 0.28)) * 1.4);
  return (
    <AbsoluteFill style={{opacity: o}}>
      <Svg>
        {E.map(([a, b], i) => {
          const d = ip(frame, 4 + i * 2, 30);
          const hot = onRoute(ROUTE, a, b) ? route * (1 - prog(frame, at(1, 0.05), 14)) : 0;
          const used = ROUTES.findIndex((r) => onRoute(r, a, b));
          const pk = used >= 0 ? prog(frame, pkt - 6, 14) * (1 - prog(frame, at(2, 0), 10)) : 0;
          const [x1, y1] = N[a], [x2, y2] = N[b];
          return (
            <g key={i}>
              <line x1={x1} y1={y1} x2={x1 + (x2 - x1) * d} y2={y1 + (y2 - y1) * d} stroke={C.line} strokeWidth={2} />
              {hot > 0 && <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={C.blue} strokeWidth={4} opacity={hot} strokeLinecap="round" />}
              {pk > 0 && <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={PK[used]} strokeWidth={2.5} opacity={pk * 0.55} />}
            </g>
          );
        })}
        {N.map(([x, y], i) => {
          if (i === 0 || i === 13) return null;
          const s = pop(frame, 8 + i * 2);
          const tw = 0.5 + 0.5 * Math.sin(frame / 14 + i);
          const hot = ROUTE.includes(i) ? route * (1 - prog(frame, at(1, 0.05), 14)) : 0;
          return (
            <g key={i} opacity={Math.min(1, s * 1.5)} transform={`translate(${x},${y}) scale(${0.6 + 0.4 * s})`}>
              <circle r={22 + 6 * hot} fill={tint(C.blue, 0.06 + 0.04 * tw + 0.15 * hot)} />
              <circle r={9} fill={C.card} stroke={hot > 0.5 ? C.blue : C.faint} strokeWidth={2.5} />
            </g>
          );
        })}
      </Svg>
      {E.map(([a, b], i) => {
        const period = 70 + (i % 5) * 9, ph = ((frame + i * 31) % period) / period;
        if (frame < 40 || frame > at(0, 0.3)) return null;
        const [x1, y1] = N[a], [x2, y2] = N[b];
        return <div key={i} style={{position: 'absolute', left: x1 + (x2 - x1) * ph - 4, top: y1 + (y2 - y1) * ph - 4, width: 8, height: 8,
          borderRadius: 4, background: i % 3 ? C.blue : C.purple, opacity: Math.min(1, ph * 5, (1 - ph) * 5) * 0.8}} />;
      })}
      <Pop from={at(0, 0.28)} x={N[0][0]} y={N[0][1]}><Endpoint label="浏览器" icon="browser" s={ends} /></Pop>
      <Pop from={at(0, 0.34)} x={N[13][0]} y={N[13][1]}><Endpoint label="服务器" icon="server" s={ends} /></Pop>
      {[0, 1, 2].map((k) => {
        const pts = ROUTE.map((i) => N[i]);
        return <Mover key={k} pts={pts} from={at(0, 0.42) + k * 22} len={70}>
          <div style={{width: 16, height: 16, borderRadius: 8, background: C.blue, boxShadow: `0 0 0 6px ${tint(C.blue, 0.2)}, 0 0 26px ${C.blue}`}} />
        </Mover>;
      })}
      <HopStats />
      <Packets />
    </AbsoluteFill>
  );
};

export const Glyph: React.FC<{kind: 'browser' | 'server'; color?: string}> = ({kind, color = C.blue}) => kind === 'browser' ? (
  <div style={{width: 46, height: 36, borderRadius: 6, border: `3px solid ${color}`, boxSizing: 'border-box', position: 'relative'}}>
    <div style={{position: 'absolute', left: 0, right: 0, top: 7, height: 3, background: color}} />
  </div>
) : (
  <div style={{display: 'flex', flexDirection: 'column', gap: 5}}>
    {[0, 1, 2].map((i) => <div key={i} style={{width: 44, height: 11, borderRadius: 3, border: `2.5px solid ${color}`, boxSizing: 'border-box'}} />)}
  </div>
);

const Endpoint: React.FC<{label: string; icon: 'browser' | 'server'; s: number}> = ({label, icon}) => (
  <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10, fontFamily: FONT}}>
    <div style={{width: 96, height: 96, borderRadius: 28, background: C.card, border: `2px solid ${tint(C.blue, 0.7)}`,
      boxShadow: `0 0 40px ${tint(C.blue, 0.3)}`, display: 'flex', alignItems: 'center', justifyContent: 'center'}}><Glyph kind={icon} /></div>
    <div style={{fontSize: 24, color: C.ink, fontWeight: 600, position: 'absolute', top: 112, whiteSpace: 'nowrap'}}>{label}</div>
  </div>
);

const HopStats: React.FC = () => {
  const {frame, at} = useScene();
  const hops = useCount(at(0, 0.45), 50, 0, 14);
  const km = useCount(at(0, 0.45), 60, 0, 1200);
  const o = vis(frame, at(0, 0.45), at(1, 0.02));
  if (o <= 0) return null;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: 120, display: 'flex', justifyContent: 'center', gap: 80, opacity: o, fontFamily: FONT}}>
      {[[String(hops), '台设备'], [km.toLocaleString('en-US'), '公里'], ['< 1', '秒']].map(([v, u]) => (
        <div key={u} style={{textAlign: 'center'}}>
          <span style={{fontSize: 64, fontWeight: 700, color: C.ink, fontVariantNumeric: 'tabular-nums'}}>{v}</span>
          <span style={{fontSize: 26, color: C.muted, marginLeft: 8}}>{u}</span>
        </div>
      ))}
    </div>
  );
};

const Packets: React.FC = () => {
  const {frame, at} = useScene();
  const start = at(1, 0), split = at(1, 0.14), launch = at(1, 0.22), end = at(2, 0.02);
  if (frame < start) return null;
  const o = vis(frame, start, end);
  const gap = ip(frame, split, 14, easeOut) * 18;
  const SPEED = 9;
  const arrive = ROUTES.map((r, k) => launch + k * 10 + Math.round(pathLen(r.map((i) => N[i])) / SPEED));
  return (
    <AbsoluteFill style={{opacity: o}}>
      <Pop from={start + 2} to={launch + 4} x={N[0][0] + 40} y={170} anchor="left">
        <div style={{display: 'flex', gap}}>
          {PK.map((c, k) => <div key={k} style={{width: 92, height: 54, borderRadius: 12, background: tint(c, 0.2), border: `1.5px solid ${c}`,
            display: 'flex', alignItems: 'center', justifyContent: 'center', color: C.ink, fontFamily: MONO, fontSize: 24, fontWeight: 600}}>{k + 1}</div>)}
        </div>
      </Pop>
      <Label x={N[0][0] + 40} y={118} anchor="left" from={start + 6} to={launch + 4} size={22}>一份数据 → 切成分组</Label>
      {ROUTES.map((r, k) => (
        <Mover key={k} pts={r.map((i) => N[i])} from={launch + k * 10} len={arrive[k] - launch - k * 10}>
          <Tag color={PK[k]}>{k + 1}</Tag>
        </Mover>
      ))}
      <Label x={1720} y={118} anchor="right" from={launch + 30} size={22}>按序号重新组装</Label>
      <div style={{position: 'absolute', right: 200, top: 170, transform: 'translateY(-50%)', display: 'flex', gap: 6}}>
        {PK.map((c, k) => {
          const s = pop(frame, arrive[k]);
          return <div key={k} style={{width: 92, height: 54, borderRadius: 12, boxSizing: 'border-box', border: `1.5px dashed ${C.line}`,
            position: 'relative', opacity: Math.min(1, prog(frame, launch, 14))}}>
            <div style={{position: 'absolute', inset: -1.5, borderRadius: 12, background: tint(c, 0.2), border: `1.5px solid ${c}`,
              opacity: clamp(s * 1.5), transform: `scale(${0.7 + 0.3 * s})`, display: 'flex', alignItems: 'center', justifyContent: 'center',
              color: C.ink, fontFamily: MONO, fontSize: 24, fontWeight: 600}}>{k + 1}</div>
          </div>;
        })}
      </div>
      <Pop from={Math.max(...arrive) + 8} x={1520} y={250}><Pill color={C.green} size={20}>各走各的路 · 到达顺序可能不同</Pill></Pop>
    </AbsoluteFill>
  );
};

const Title: React.FC = () => {
  const {frame, at} = useScene();
  const t = ip(frame, 24, 26, easeOut);
  const o = t * (1 - prog(frame, at(0, 0.24), 16));
  if (o <= 0) return null;
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', fontFamily: FONT, opacity: o}}>
      <div style={{position: 'absolute', width: 1100, height: 420, borderRadius: 400, background: `radial-gradient(ellipse, ${C.bg} 30%, transparent 70%)`}} />
      <div style={{textAlign: 'center', transform: `translateY(${(1 - t) * 30}px)`}}>
        <div style={{fontSize: 26, letterSpacing: 8, color: C.blue, fontWeight: 600}}>10 MINUTES</div>
        <div style={{fontSize: 128, fontWeight: 700, letterSpacing: 8, display: 'inline-block', backgroundImage: TITLE_GRAD,
          WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent', marginTop: 6}}>计算机网络</div>
        <div style={{fontSize: 32, color: C.muted, marginTop: 4, letterSpacing: 3}}>Computer Networking</div>
      </div>
    </AbsoluteFill>
  );
};

const Roadmap: React.FC = () => {
  const {frame, at} = useScene();
  const start = at(2, 0.05);
  if (frame < start - 2) return null;
  const order = [4, 3, 2, 1, 0];
  return (
    <AbsoluteFill>
      {LAYERS.map((l, i) => {
        const k = order.indexOf(i);
        const sweep = ip(frame, at(2, 0.55) + k * 8, 12) * (1 - ip(frame, at(2, 0.55) + k * 8 + 14, 16));
        return <Slab key={l.id} x={960} y={300 + i * 104} w={720} h={88} from={start + k * 7} color={l.c} name={l.name} en={l.en} hl={sweep} />;
      })}
      <Svg>
        <defs>
          <linearGradient id="up" gradientUnits="userSpaceOnUse" x1="0" y1="716" x2="0" y2="296">
            <stop offset="0" stopColor={C.teal} /><stop offset="1" stopColor={C.purple} />
          </linearGradient>
        </defs>
        {frame > at(2, 0.4) && (() => {
          const p = ip(frame, at(2, 0.4), 30);
          const y1 = 716, y2 = 716 - 420 * p;
          return <g>
            <line x1={1400} y1={y1} x2={1400} y2={y2} stroke="url(#up)" strokeWidth={4} strokeLinecap="round" />
            <path d={`M1388,${y2 + 14} L1400,${y2} L1412,${y2 + 14}`} stroke={C.purple} strokeWidth={4} fill="none" strokeLinecap="round" strokeLinejoin="round" />
          </g>;
        })()}
      </Svg>
      <Label x={1430} y={506} anchor="left" from={at(2, 0.45)} size={24} color={C.ink2}>从下往上</Label>
    </AbsoluteFill>
  );
};

export const Intro: React.FC = () => (
  <AbsoluteFill>
    <Mesh />
    <Title />
    <Roadmap />
  </AbsoluteFill>
);
