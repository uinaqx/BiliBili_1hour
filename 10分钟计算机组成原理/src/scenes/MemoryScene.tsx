import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT, MONO, SHADOW, tint} from '../theme';
import {P, curve, pop, useScene, vis} from '../anim';
import {Label, Packet, Pill, Pop, Svg, Wire, card} from '../kit';

const LAYERS: [string, string, string][] = [
  ['寄存器', '< 1 ns · 几百 B', C.blue], ['Cache', '1–10 ns · MB 级', C.indigo], ['主存', '约 100 ns · GB 级', C.purple], ['外存', 'μs–ms · TB 级', '#8e8e93'],
];

/** Beat 0: the hierarchy pyramid. */
const Pyramid: React.FC = () => {
  const {frame, at} = useScene();
  const end = at(1, 0);
  const o = vis(frame, at(0, 0), end);
  if (o <= 0) return null;
  return (
    <AbsoluteFill style={{opacity: o}}>
      <Svg>
        {LAYERS.map(([name, , col], i) => {
          const yt = 250 + i * 124, yb = yt + 110, wt = 260 + i * 240, wb = wt + 240;
          const s = pop(frame, at(0, 0.38) + i * 9);
          return (
            <g key={name} opacity={Math.min(1, s * 1.5)} transform={`translate(0 ${(1 - s) * 30})`}>
              <polygon points={`${960 - wt / 2},${yt} ${960 + wt / 2},${yt} ${960 + wb / 2},${yb} ${960 - wb / 2},${yb}`} fill={col}
                style={{filter: 'drop-shadow(0 10px 22px rgba(0,0,0,0.10))'}} />
              <text x={960} y={yt + 68} textAnchor="middle" fontFamily={FONT} fontSize={38} fontWeight={700} fill="#fff">{name}</text>
            </g>
          );
        })}
        <Wire pts={[[230, 720], [230, 250]]} from={at(0, 0.75)} to={end} color={C.blue} w={4} len={24} />
        <Wire pts={[[130, 250], [130, 720]]} from={at(0, 0.8)} to={end} color={C.faint} w={4} len={24} />
      </Svg>
      {LAYERS.map(([name, spec], i) => (
        <Label key={name} x={960 + (380 + i * 240) / 2 + 40} y={250 + i * 124 + 55} from={at(0, 0.45) + i * 9} to={end}
          anchor="left" size={24} color={C.ink2} weight={550}>{spec}</Label>
      ))}
      <Label x={230} y={215} from={at(0, 0.75)} to={end} size={22} color={C.blue} weight={650}>更快 · 更贵</Label>
      <Label x={130} y={758} from={at(0, 0.8)} to={end} size={22} color={C.muted} weight={650}>更大</Label>
    </AbsoluteFill>
  );
};

/** Beat 1: temporal and spatial locality on a grid of memory cells. */
const Locality: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(1, 0), end = at(2, 0);
  const o = vis(frame, s, end);
  if (o <= 0) return null;
  const cols = 16, rows = 6, cs = 62, pitch = 72, x0 = 960 - (cols * pitch - 10) / 2, y0 = 330;
  const tA = at(1, 0.1), tB = at(1, 0.5);
  const pulses = Math.max(0, Math.min(5, Math.floor((frame - tA) / 14) + 1));
  const ring = frame >= tA && frame < tB ? ((frame - tA) % 14) / 14 : -1;
  const sweep = Math.floor((frame - tB - 10) / 6);
  return (
    <AbsoluteFill style={{opacity: o}}>
      {Array.from({length: rows * cols}, (_, k) => {
        const r = Math.floor(k / cols), c = k % cols;
        const sp = pop(frame, s + 4 + (r + c) * 0.8);
        const time = r === 1 && c === 4 && frame >= tA;
        const space = r === 3 && c >= 2 && c <= 13 && c - 2 <= sweep;
        const col = time ? C.orange : space ? C.blue : null;
        return (
          <div key={k} style={{position: 'absolute', left: x0 + c * pitch, top: y0 + r * pitch, width: cs, height: cs, borderRadius: 14,
            background: col ?? '#fff', boxShadow: SHADOW, opacity: Math.min(1, sp * 1.5), transform: `scale(${0.8 + 0.2 * sp})`}} />
        );
      })}
      {ring >= 0 && (
        <div style={{position: 'absolute', left: x0 + 4 * pitch + cs / 2, top: y0 + pitch + cs / 2, width: cs, height: cs, borderRadius: 18,
          border: `3px solid ${C.orange}`, opacity: 1 - ring, transform: `translate(-50%,-50%) scale(${1 + ring * 1.2})`}} />
      )}
      <Label x={x0 + 4 * pitch + cs / 2} y={y0 + pitch - 26} from={tA + 4} size={22} weight={700} color={C.orange}>× {pulses}</Label>
      <Pop from={tA} x={640} y={240}><Pill color={C.orange} size={26}>时间局部性：同一处反复访问</Pill></Pop>
      <Pop from={tB} x={1290} y={240}><Pill color={C.blue} size={26}>空间局部性：附近的也会被访问</Pill></Pop>
      <Pop from={at(1, 0.82)} x={x0 + 2 * pitch - 8} y={y0 + 3 * pitch - 8} anchor="topleft">
        <div style={{width: 4 * pitch + 6, height: cs + 16, borderRadius: 20, border: `3px solid ${C.blue}`, boxSizing: 'border-box'}} />
      </Pop>
      <Label x={x0 + 2 * pitch + 2 * pitch - 5} y={790} from={at(1, 0.85)} size={22} weight={650} color={C.blue}>
        相邻的 4 个单元组成一块，一次整块调入 Cache
      </Label>
    </AbsoluteFill>
  );
};

const ROWC = [C.blue, C.indigo, C.purple, C.teal];
const cacheY = (r: number) => 380 + r * 96;
const blockPos = (j: number): P => [1010 + Math.floor(j / 4) * 150, cacheY(j % 4)];

/** Beats 2–3: direct, fully associative and set-associative mapping. */
const Mapping: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(2, 0), end = at(4, 0);
  const o = vis(frame, s, end);
  if (o <= 0) return null;
  const direct = frame < at(3, 0), full = !direct && frame < at(3, 0.5), assoc = frame >= at(3, 0.5);
  const seq = [1, 5, 9, 13], seqT = seq.map((_, k) => at(2, 0.32 + k * 0.13));
  const curIdx = seqT.reduce((a, t, k) => (frame >= t ? k : a), -1);
  const occupant = direct ? (curIdx >= 0 ? `块 ${seq[curIdx]}` : '') : '';
  const link = (j: number, r: number, from: number, color: string, key: string, opacity = 1) => {
    const [bx, by] = blockPos(j);
    return <Wire key={key} pts={curve([bx - 68, by], [594, cacheY(r)], -(36 + Math.floor(j / 4) * 32))} from={from} len={16}
      color={color} w={3} opacity={opacity} to={key.startsWith('d') ? at(3, 0) : key.startsWith('f') ? at(3, 0.5) : end} />;
  };
  return (
    <AbsoluteFill style={{opacity: o}}>
      <Label x={470} y={315} from={s} size={26} weight={700} color={C.ink}>Cache</Label>
      <Label x={1235} y={315} from={s + 4} size={26} weight={700} color={C.ink}>主存</Label>
      {[0, 1, 2, 3].map((r) => {
        const hl = direct ? (r === 1 && curIdx >= 0 ? 1 : 0) : full ? 1 : r < 2 ? 1 : 0;
        const col = direct ? ROWC[r] : assoc ? C.green : C.orange;
        return (
          <Pop key={r} from={s + r * 3} x={470} y={cacheY(r)}>
            <div style={{width: 240, height: 70, borderRadius: 18, background: hl ? tint(col, 0.14) : '#fff', boxShadow: SHADOW,
              border: `2px solid ${hl ? col : tint(direct ? ROWC[r] : C.line, direct ? 0.4 : 1)}`, display: 'flex', alignItems: 'center',
              justifyContent: 'space-between', padding: '0 20px', boxSizing: 'border-box'}}>
              <span style={{fontSize: 22, color: C.muted}}>行 {r}</span>
              <span style={{fontSize: 24, fontWeight: 650, color: col}}>{r === 1 ? occupant : ''}</span>
            </div>
          </Pop>
        );
      })}
      {Array.from({length: 16}, (_, j) => {
        const [x, y] = blockPos(j);
        const active = direct ? seq.indexOf(j) >= 0 && seq.indexOf(j) <= curIdx : j === 6;
        const col = direct ? ROWC[j % 4] : assoc ? C.green : C.orange;
        return (
          <Pop key={j} from={s + 6 + j} x={x} y={y}>
            <div style={{width: 130, height: 70, borderRadius: 16, background: active ? col : '#fff', boxShadow: SHADOW,
              border: `2px solid ${direct ? tint(ROWC[j % 4], 0.35) : 'rgba(0,0,0,0.05)'}`, display: 'flex', alignItems: 'center',
              justifyContent: 'center', fontSize: 24, fontWeight: 600, color: active ? '#fff' : C.ink2}}>块 {j}</div>
          </Pop>
        );
      })}
      {assoc && (
        <>
          <Pop from={at(3, 0.52)} x={290} y={(cacheY(0) + cacheY(1)) / 2}><Pill color={C.green} size={22}>组 0</Pill></Pop>
          <Pop from={at(3, 0.55)} x={290} y={(cacheY(2) + cacheY(3)) / 2}><Pill color={C.muted} size={22}>组 1</Pill></Pop>
        </>
      )}
      <Svg>
        {seq.map((j, k) => link(j, 1, seqT[k], ROWC[1], `d${j}`, curIdx > k ? 0.3 : 1))}
        {[0, 1, 2, 3].map((r) => link(6, r, at(3, 0.08) + r * 5, C.orange, `f${r}`))}
        {[0, 1].map((r) => link(6, r, at(3, 0.6) + r * 6, C.green, `s${r}`))}
      </Svg>
      <Pop from={s + 10} to={at(3, 0)} x={960} y={200}><Pill solid size={26}>直接映射：行号 = 块号 mod 行数</Pill></Pop>
      <Pop from={at(3, 0.02)} to={at(3, 0.5)} x={960} y={200}><Pill solid color={C.orange} size={26}>全相联：放进任意一行</Pill></Pop>
      <Pop from={at(3, 0.5)} x={960} y={200}><Pill solid color={C.green} size={26}>2 路组相联：组号 = 块号 mod 组数</Pill></Pop>
      <Pop from={at(2, 0.8)} to={at(3, 0)} x={960} y={812}><Pill color={C.red} size={24}>块 1、5、9、13 争同一行 → 冲突</Pill></Pop>
      <Pop from={at(3, 0.25)} to={at(3, 0.5)} x={960} y={812}><Pill color={C.orange} size={24}>冲突最少，但要和每一行比较标记</Pill></Pop>
      <Pop from={at(3, 0.72)} x={960} y={812}><Pill color={C.green} size={24}>块 6 → 组 0，组内两行任选</Pill></Pop>
    </AbsoluteFill>
  );
};

const SEG: [string, string, number, string][] = [['标记', 'Tag', 520, C.purple], ['行号', 'Index', 300, C.blue], ['块内偏移', 'Offset', 240, C.green]];
const TAGS = ['0x1A3', '0x07F', '0x2C4', '0x011'];
const rowY = (r: number) => 540 + r * 66;

/** Beat 4: address split and hit check. */
const Lookup: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(4, 0), end = at(5, 0);
  const o = vis(frame, s, end);
  if (o <= 0) return null;
  let x = 430;
  const segs = SEG.map(([a, b, w, c]) => { const l = x; x += w; return {a, b, w, c, l}; });
  const row = frame >= at(4, 0.4) ? 2 : -1;
  const word = frame >= at(4, 0.82);
  return (
    <AbsoluteFill style={{opacity: o}}>
      <Label x={430} y={262} from={s} anchor="left" size={22} color={C.muted}>主存地址</Label>
      {segs.map((g, i) => (
        <Pop key={g.a} from={s + 4 + i * 8} x={g.l + g.w / 2} y={330}>
          <div style={{width: g.w - 6, height: 84, borderRadius: 18, background: tint(g.c, 0.12), border: `2px solid ${tint(g.c, 0.6)}`,
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
            <span style={{fontSize: 28, fontWeight: 700, color: g.c}}>{g.a}</span>
            <span style={{fontSize: 18, color: C.muted}}>{i === 0 ? '0x2C4' : g.b}</span>
          </div>
        </Pop>
      ))}
      <Pop from={at(4, 0.18)} x={960} y={rowY(1.5)}>
        <div style={card({width: 820, padding: '14px 10px', boxSizing: 'border-box'})}>
          {TAGS.map((t, r) => (
            <div key={r} style={{height: 56, marginTop: r ? 10 : 0, borderRadius: 14, display: 'flex', alignItems: 'center',
              background: r === row ? tint(C.blue, 0.1) : C.fill, border: `2px solid ${r === row ? C.blue : 'transparent'}`}}>
              <span style={{width: 80, textAlign: 'center', fontSize: 20, color: C.muted}}>V=1</span>
              <span style={{width: 220, fontFamily: MONO, fontSize: 24, color: C.purple, textAlign: 'center'}}>{t}</span>
              {[0, 1, 2, 3].map((w) => (
                <span key={w} style={{width: 110, height: 40, marginLeft: 8, borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: MONO, fontSize: 20, background: r === row && w === 2 && word ? C.green : '#fff',
                  color: r === row && w === 2 && word ? '#fff' : C.ink2}}>w{w}</span>
              ))}
            </div>
          ))}
        </div>
      </Pop>
      <Svg>
        <Wire pts={[[1100, 374], [1100, 424], [520, 424], [520, rowY(2)], [548, rowY(2)]]} from={at(4, 0.28)} len={22} color={C.blue} to={end} />
        <Wire pts={[[690, 286], [690, 236], [1640, 236], [1640, rowY(2) - 44]]} from={at(4, 0.5)} len={24} color={C.purple} to={end} />
        <Wire pts={[[1372, rowY(2)], [1596, rowY(2)]]} from={at(4, 0.55)} color={C.purple} to={end} />
      </Svg>
      <Pop from={at(4, 0.6)} x={1640} y={rowY(2)}>
        <div style={{width: 80, height: 80, borderRadius: 40, background: '#fff', boxShadow: SHADOW, border: `2px solid ${C.purple}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 36, fontWeight: 700, color: C.purple}}>=</div>
      </Pop>
      <Pop from={at(4, 0.7)} x={1640} y={rowY(2) + 90}><Pill solid color={C.green} size={26}>命中 Hit</Pill></Pop>
    </AbsoluteFill>
  );
};

const MISSES = [13, 37, 58, 72, 91];

/** Beat 5: hit rate and average access time. */
const Amat: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(5, 0), end = at(6, 0);
  const o = vis(frame, s, end);
  if (o <= 0) return null;
  return (
    <AbsoluteFill style={{opacity: o}}>
      {Array.from({length: 100}, (_, k) => {
        const sp = pop(frame, s + 6 + k * 0.45);
        const miss = MISSES.includes(k);
        return (
          <div key={k} style={{position: 'absolute', left: 300 + (k % 10) * 42, top: 300 + Math.floor(k / 10) * 42, width: 30, height: 30,
            borderRadius: 15, background: miss ? C.orange : C.green, opacity: Math.min(1, sp * 1.5) * (miss ? 1 : 0.85),
            transform: `scale(${sp})`}} />
        );
      })}
      <Pop from={at(5, 0.15)} x={505} y={770}>
        <div style={{display: 'flex', gap: 22}}>
          <Pill color={C.green} size={24}>命中 95</Pill>
          <Pill color={C.orange} size={24}>缺失 5</Pill>
        </div>
      </Pop>
      <Pop from={at(5, 0.25)} x={1290} y={520}>
        <div style={card({width: 820, padding: '36px 44px', boxSizing: 'border-box', fontSize: 34, color: C.ink, lineHeight: 1.6})}>
          <div style={{fontSize: 24, color: C.muted}}>平均访问时间</div>
          <div>= 命中时间 + 缺失率 × 缺失代价</div>
          <div style={{opacity: vis(frame, at(5, 0.5)), fontFamily: MONO}}>= 1 + 0.05 × 100</div>
          <div style={{opacity: vis(frame, at(5, 0.75)), fontSize: 72, fontWeight: 700, color: C.blue, marginTop: 6}}>= 6 ns</div>
        </div>
      </Pop>
    </AbsoluteFill>
  );
};

const VP_MAP = [5, 2, 7, 0, -1, 3];
const vpY = (i: number) => 340 + i * 76;
const pfY = (i: number) => 320 + i * 60;

/** Beat 6: virtual memory, page table and TLB. */
const Virtual: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(6, 0);
  if (frame < s - 2) return null;
  const t = (f: number) => at(6, f);
  const pf = frame >= t(0.68) ? 7 : -1;
  const tlbNew = frame >= t(0.78);
  const miss = vis(frame, t(0.5), t(0.62));
  return (
    <AbsoluteFill>
      <Label x={360} y={290} from={s} size={24} weight={700} color={C.ink}>虚拟地址空间</Label>
      <Label x={960} y={290} from={s + 4} size={24} weight={700} color={C.ink}>页表</Label>
      <Label x={1560} y={270} from={s + 8} size={24} weight={700} color={C.ink}>物理内存</Label>
      {VP_MAP.map((p, i) => (
        <React.Fragment key={i}>
          <Pop from={s + 4 + i * 3} x={360} y={vpY(i)}>
            <div style={{width: 220, height: 60, borderRadius: 16, background: i === 2 && frame >= t(0.4) ? C.blue : '#fff', boxShadow: SHADOW,
              display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, fontWeight: 600,
              color: i === 2 && frame >= t(0.4) ? '#fff' : C.ink2}}>虚拟页 {i}</div>
          </Pop>
          <Pop from={s + 10 + i * 3} x={960} y={vpY(i)}>
            <div style={{width: 300, height: 60, borderRadius: 16, background: i === 2 && frame >= t(0.6) ? tint(C.blue, 0.12) : '#fff',
              border: `2px solid ${i === 2 && frame >= t(0.6) ? C.blue : 'transparent'}`, boxShadow: SHADOW, display: 'flex',
              alignItems: 'center', justifyContent: 'center', gap: 14, fontFamily: MONO, fontSize: 24, color: C.ink2}}>
              {i} → {p >= 0 ? <span style={{color: C.blue}}>页框 {p}</span> : <span style={{color: C.orange, fontFamily: FONT, fontSize: 21}}>不在内存（磁盘）</span>}
            </div>
          </Pop>
        </React.Fragment>
      ))}
      {Array.from({length: 8}, (_, k) => (
        <Pop key={k} from={s + 14 + k * 2} x={1560} y={pfY(k)}>
          <div style={{width: 220, height: 48, borderRadius: 14, background: k === pf ? C.blue : '#fff', boxShadow: SHADOW,
            display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 21, fontWeight: 600, color: k === pf ? '#fff' : C.muted}}>页框 {k}</div>
        </Pop>
      ))}
      <Svg>
        {VP_MAP.map((p, i) => (
          <g key={i}>
            <Wire pts={[[472, vpY(i)], [806, vpY(i)]]} from={t(0.12) + i * 4} color={C.line} w={2} len={12} />
            {p >= 0 && <Wire pts={[[1112, vpY(i)], [1448, pfY(p)]]} from={t(0.2) + i * 4} color={i === 2 && pf >= 0 ? C.blue : C.line}
              w={i === 2 && pf >= 0 ? 4 : 2} len={12} />}
          </g>
        ))}
      </Svg>
      <Pop from={t(0.3)} x={960} y={190}>
        <div style={card({padding: '14px 26px', display: 'flex', alignItems: 'center', gap: 22, borderRadius: 20})}>
          <span style={{fontSize: 24, fontWeight: 700, color: C.teal}}>TLB 快表</span>
          <span style={{fontFamily: MONO, fontSize: 22, color: C.ink2, background: C.fill, padding: '6px 14px', borderRadius: 10}}>0 → 5</span>
          <span style={{fontFamily: MONO, fontSize: 22, color: tlbNew ? '#fff' : C.faint, background: tlbNew ? C.teal : C.fill, padding: '6px 14px',
            borderRadius: 10}}>{tlbNew ? '2 → 7' : '— —'}</span>
          {miss > 0 && <span style={{opacity: miss}}><Pill color={C.red} size={20}>未命中</Pill></span>}
        </div>
      </Pop>
      <Packet pts={[[472, vpY(2)], [700, 260], [820, 200]]} from={t(0.4)} len={14} color={C.blue} tag="页号 2" />
      <Packet pts={[[960, 232], [960, vpY(2)]]} from={t(0.56)} len={10} color={C.blue} tag="查页表" />
      <Packet pts={[[1112, vpY(2)], [1448, pfY(7)]]} from={t(0.64)} len={10} color={C.blue} />
      <Pop from={t(0.88)} x={960} y={820}><Pill color={C.teal} size={24}>再次访问页 2：TLB 直接命中，不必查页表</Pill></Pop>
    </AbsoluteFill>
  );
};

export const MemoryScene: React.FC = () => (
  <AbsoluteFill>
    <Pyramid />
    <Locality />
    <Mapping />
    <Lookup />
    <Amat />
    <Virtual />
  </AbsoluteFill>
);
