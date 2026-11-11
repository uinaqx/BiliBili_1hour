import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT, MONO, tint} from '../theme';
import {P, clamp, pop, prog, useScene, vis} from '../anim';
import {Label, Pill, Pop, Svg, Wire, card} from '../kit';

const COLOR: Record<string, string> = {
  IF: C.blue, ID: C.indigo, EX: C.purple, MEM: C.orange, WB: C.green, '洗': C.blue, '烘': C.orange, '叠': C.green, '●': '#c7c7cc',
};

type Row = {label: React.ReactNode; cells: (string | null)[]; ghost?: boolean; flushAt?: number; from?: number};
type GanttProps = {x: number; y: number; from: number; to?: number; rows: Row[]; cycles: number; cw?: number; rh?: number; labelW?: number;
  sweep?: {start: number; per: number}; mark?: (r: number, c: number) => string | undefined; header?: boolean};

const geo = (g: {x: number; y: number; cw?: number; rh?: number; labelW?: number; header?: boolean}) => {
  const cw = g.cw ?? 130, rh = g.rh ?? 64, lw = g.labelW ?? 150, top = g.y + (g.header === false ? 0 : 46);
  return {cx: (c: number) => g.x + lw + c * cw + cw / 2, cy: (r: number) => top + r * rh + rh / 2, cw, rh, lw, top};
};

const Gantt: React.FC<GanttProps> = (g) => {
  const {frame} = useScene();
  const o = vis(frame, g.from, g.to);
  if (o <= 0) return null;
  const {cx, cy, cw, rh, lw, top} = geo(g);
  const cursor = g.sweep ? clamp((frame - g.sweep.start) / g.sweep.per, 0, g.cycles) : -1;
  return (
    <div style={{position: 'absolute', left: 0, top: 0, opacity: o, fontFamily: FONT}}>
      {g.header !== false && Array.from({length: g.cycles}, (_, c) => (
        <div key={c} style={{position: 'absolute', left: cx(c), top: g.y + 16, transform: 'translate(-50%,-50%)', fontSize: 20,
          color: cursor >= 0 && Math.floor(cursor) === c ? C.blue : C.muted, fontWeight: 600}}>{c + 1}</div>
      ))}
      {g.rows.map((row, r) => {
        const rf = row.from ?? g.from + r * 5;
        const ro = vis(frame, rf);
        const flushed = row.flushAt !== undefined ? prog(frame, row.flushAt, 14) : 0;
        return (
          <React.Fragment key={r}>
            <div style={{position: 'absolute', left: g.x, top: cy(r), width: lw - 20, transform: 'translateY(-50%)', textAlign: 'right',
              fontSize: 22, fontWeight: 600, color: C.ink2, opacity: ro, whiteSpace: 'nowrap', fontFamily: typeof row.label === 'string' && /[A-Z]/.test(row.label) ? MONO : FONT}}>
              {row.label}
            </div>
            {row.cells.map((cell, c) => {
              if (!cell) return null;
              const appear = g.sweep ? g.sweep.start + c * g.sweep.per : rf + c * 2;
              const s = pop(frame, appear);
              if (s <= 0.001) return null;
              const col = COLOR[cell] ?? C.ink2;
              const ring = g.mark?.(r, c);
              return (
                <div key={c} style={{position: 'absolute', left: cx(c), top: cy(r), width: cw - 10, height: rh - 12, borderRadius: 14,
                  transform: `translate(-50%,-50%) scale(${0.7 + 0.3 * s})`, opacity: Math.min(1, s * 1.5) * (1 - 0.75 * flushed),
                  background: row.ghost ? `repeating-linear-gradient(135deg, ${tint(col, 0.22)} 0 10px, ${tint(col, 0.1)} 10px 20px)` : cell === '●' ? '#e5e5ea' : col,
                  color: row.ghost ? col : cell === '●' ? C.muted : '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: MONO, fontSize: cell.length > 2 ? 20 : 22, fontWeight: 700,
                  boxShadow: ring ? `0 0 0 4px ${ring}` : '0 2px 8px rgba(0,0,0,0.06)'}}>
                  {cell === '●' ? '气泡' : cell}
                  {flushed > 0 && <div style={{position: 'absolute', left: 8, right: 8, top: '50%', height: 3, background: C.red,
                    transform: `scaleX(${flushed})`, transformOrigin: 'left'}} />}
                </div>
              );
            })}
          </React.Fragment>
        );
      })}
      {cursor >= 0 && cursor < g.cycles && (
        <div style={{position: 'absolute', left: g.x + lw + cursor * cw, top: top - 8, width: 3, height: g.rows.length * rh + 16, borderRadius: 2,
          background: C.blue, opacity: 0.6}} />
      )}
    </div>
  );
};

const at5 = (k: number, n: number) => Array.from({length: n}, (_, c) => ['IF', 'ID', 'EX', 'MEM', 'WB'][c - k] ?? null);

/** Beat 0: laundry analogy. */
const Laundry: React.FC = () => {
  const {at} = useScene();
  const s = at(0, 0), end = at(1, 0);
  const seq = [0, 1, 2].map((k) => ({label: `第 ${k + 1} 批`, cells: Array.from({length: 9}, (_, c) => (c >= 3 * k && c < 3 * k + 3 ? ['洗', '烘', '叠'][c - 3 * k] : null))}));
  const pipe = [0, 1, 2].map((k) => ({label: `第 ${k + 1} 批`, cells: Array.from({length: 9}, (_, c) => (c >= k && c < k + 3 ? ['洗', '烘', '叠'][c - k] : null))}));
  const sweep = {start: at(0, 0.3), per: Math.round((at(0, 0.85) - at(0, 0.3)) / 9)};
  return (
    <>
      <Label x={440} y={206} from={s + 4} to={end} anchor="left" size={28} weight={700} color={C.ink}>顺序执行：一批做完再下一批</Label>
      <Gantt x={420} y={230} from={s + 6} to={end} rows={seq} cycles={9} cw={92} rh={56} labelW={140} sweep={sweep} />
      <Label x={440} y={496} from={s + 10} to={end} anchor="left" size={28} weight={700} color={C.blue}>流水线：前一批烘干时，后一批开始洗</Label>
      <Gantt x={420} y={520} from={s + 10} to={end} rows={pipe} cycles={9} cw={92} rh={56} labelW={140} sweep={sweep} header={false} />
      <Pop from={at(0, 0.85)} to={end} x={1560} y={330}><Pill color={C.ink2} size={26}>9 个时段</Pill></Pop>
      <Pop from={at(0, 0.88)} to={end} x={1560} y={600}><Pill solid size={26}>5 个时段</Pill></Pop>
    </>
  );
};

const G5 = {x: 260, y: 250, cw: 150, rh: 68, labelW: 120};

/** Beats 1–2: five-stage pipeline and its timing formula. */
const FiveStage: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(1, 0), end = at(3, 0);
  const rows = [0, 1, 2, 3, 4].map((k) => ({label: `I${k + 1}`, cells: at5(k, 9)}));
  const sweep = {start: at(1, 0.18), per: Math.round((at(1, 0.8) - at(1, 0.18)) / 9)};
  const {cx, cy} = geo(G5);
  const legend: [string, string][] = [['IF', '取指'], ['ID', '译码'], ['EX', '执行'], ['MEM', '访存'], ['WB', '写回']];
  const bk = (c0: number, c1: number, text: string, color: string, from: number) => {
    const o = vis(frame, from, end);
    if (o <= 0) return null;
    const l = cx(c0) - G5.cw / 2 + 6, r = cx(c1) + G5.cw / 2 - 6;
    return (
      <div style={{position: 'absolute', left: l, width: r - l, top: cy(4) + 44, opacity: o, textAlign: 'center', fontFamily: FONT}}>
        <div style={{height: 10, borderBottom: `3px solid ${color}`, borderLeft: `3px solid ${color}`, borderRight: `3px solid ${color}`, borderRadius: '0 0 6px 6px'}} />
        <div style={{fontSize: 22, fontWeight: 700, color, marginTop: 6, fontFamily: MONO}}>{text}</div>
      </div>
    );
  };
  return (
    <>
      <Pop from={s + 4} to={end} x={960} y={196}>
        <div style={{display: 'flex', gap: 12}}>
          {legend.map(([k, n]) => <Pill key={k} color={COLOR[k]} size={22}><span style={{fontFamily: MONO}}>{k}</span> {n}</Pill>)}
        </div>
      </Pop>
      <Gantt {...G5} from={s + 6} to={end} rows={rows} cycles={9} sweep={sweep} />
      <Pop from={at(1, 0.62)} to={at(2, 0)} x={960} y={800}><Pill solid color={C.green} size={26}>从第 5 个周期起，每个周期完成一条指令</Pill></Pop>
      {bk(0, 4, 'k = 5', C.blue, at(2, 0.1))}
      {bk(5, 8, 'n − 1 = 4', C.purple, at(2, 0.2))}
      <Pop from={at(2, 0.35)} to={end} x={700} y={820}>
        <div style={card({padding: '18px 34px', display: 'flex', alignItems: 'baseline', gap: 18})}>
          <span style={{fontFamily: MONO, fontSize: 38, fontWeight: 700, color: C.ink}}>T = (k + n − 1)·Δt</span>
          <span style={{fontSize: 22, color: C.muted}}>5 + 5 − 1 = 9 周期</span>
        </div>
      </Pop>
      <Pop from={at(2, 0.6)} to={end} x={1360} y={820}>
        <div style={card({padding: '18px 30px', fontSize: 24, color: C.ink2})}>
          n = 100：流水 <b style={{color: C.blue}}>104</b> 周期 · 不流水 <b>500</b> 周期
        </div>
      </Pop>
    </>
  );
};

/** Beat 3: structural hazard. */
const Structural: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(3, 0), end = at(4, 0);
  const rows = [0, 1, 2, 3].map((k) => ({label: `I${k + 1}`, cells: at5(k, 8)}));
  const {cx, cy} = geo(G5);
  return (
    <>
      <Pop from={s + 4} to={end} x={960} y={196}><Pill solid color={C.red} size={26}>结构冒险：争用同一个硬件</Pill></Pop>
      <Gantt {...G5} from={s + 6} to={end} rows={rows} cycles={8}
        mark={(r, c) => (c === 3 && (r === 0 || r === 3) && frame >= at(3, 0.35) ? C.red : undefined)} />
      <Label x={cx(3)} y={cy(3) + 80} from={at(3, 0.4)} to={end} size={22} weight={700} color={C.red}>第 4 周期：I1 访存 + I4 取指，都要用存储器</Label>
      <Pop from={at(3, 0.7)} to={end} x={960} y={810}><Pill color={C.green} size={26}>解决：指令 Cache 与数据 Cache 分开</Pill></Pop>
    </>
  );
};

const GD = {x: 220, y: 300, cw: 150, rh: 90, labelW: 300};

/** Beat 4: data hazard — stall, then forwarding. */
const DataHazard: React.FC = () => {
  const {at} = useScene();
  const s = at(4, 0), end = at(5, 0), p2 = at(4, 0.38), p3 = at(4, 0.68);
  const i1 = {label: 'ADD R1, R2, R3', cells: at5(0, 8)};
  const i2 = (cells: (string | null)[], from?: number) => ({label: 'SUB R4, R1, R5', cells, from});
  const {cx, cy} = geo(GD);
  const back: P[] = [[cx(4), cy(0) + 30], [cx(4), cy(0) + 45], [cx(2), cy(1) - 45], [cx(2), cy(1) - 30]];
  const fwd: P[] = [[cx(2) + 40, cy(0) + 30], [cx(3) - 40, cy(1) - 30]];
  return (
    <>
      <Pop from={s + 4} to={end} x={960} y={196}><Pill solid color={C.purple} size={26}>数据冒险：要用的结果还没写回</Pill></Pop>
      <Gantt {...GD} from={s + 6} to={p2} rows={[i1, i2(at5(1, 8))]} cycles={8} mark={(r, c) => (r === 1 && c === 2 ? C.red : r === 0 && c === 4 ? C.red : undefined)} />
      <Gantt {...GD} from={p2} to={p3} rows={[i1, i2([null, 'IF', '●', '●', 'ID', 'EX', 'MEM', 'WB'], p2)]} cycles={8} />
      <Gantt {...GD} from={p3} to={end} rows={[i1, i2(at5(1, 8), p3)]} cycles={8} mark={(r, c) => (r === 0 && c === 2 ? C.green : r === 1 && c === 3 ? C.green : undefined)} />
      <Svg>
        <Wire pts={back} from={at(4, 0.15)} to={p2} color={C.red} w={4} />
        <Wire pts={fwd} from={p3 + 14} to={end} color={C.green} w={5} />
      </Svg>
      <Label x={cx(2.5)} y={cy(1) + 80} from={at(4, 0.2)} to={p2} size={22} weight={700} color={C.red}>SUB 在第 3 周期读 R1，ADD 第 5 周期才写回</Label>
      <Label x={cx(2.5)} y={cy(1) + 80} from={p2 + 6} to={p3} size={22} weight={700} color={C.muted}>插入气泡：SUB 暂停两个周期</Label>
      <Label x={cx(2.5)} y={cy(1) + 80} from={p3 + 18} to={end} size={22} weight={700} color={C.green}>旁路：EX 的结果直接送给下一条的 EX，不用等</Label>
    </>
  );
};

/** Beat 5: control hazard and branch prediction. */
const ControlHazard: React.FC = () => {
  const {at} = useScene();
  const s = at(5, 0);
  const flush = at(5, 0.55);
  const rows: Row[] = [
    {label: 'BEQ 分支', cells: at5(0, 8)},
    {label: '下一条？', cells: at5(1, 8), ghost: true, flushAt: flush},
    {label: '再下一条？', cells: at5(2, 8), ghost: true, flushAt: flush},
    {label: '跳转目标', cells: at5(3, 8), from: at(5, 0.65)},
  ];
  const GC = {...G5, labelW: 170};
  const {cx, cy} = geo(GC);
  return (
    <>
      <Pop from={s + 4} x={960} y={196}><Pill solid color={C.orange} size={26}>控制冒险：跳不跳，算出来才知道</Pill></Pop>
      <Gantt {...GC} from={s + 6} rows={rows} cycles={8} mark={(r, c) => (r === 0 && c === 2 ? C.orange : undefined)} />
      <Label x={cx(2) + 25} y={cy(3) + 90} from={at(5, 0.25)} size={22} weight={700} color={C.orange}>BEQ 到第 3 周期 EX 才知道是否跳转</Label>
      <Pop from={at(5, 0.3)} x={700} y={810}><Pill color={C.blue} size={24}>分支预测：先按猜测的方向取指</Pill></Pop>
      <Pop from={flush} x={1300} y={810}><Pill color={C.red} size={24}>猜错 → 清空，重新取正确的指令</Pill></Pop>
    </>
  );
};

export const PipelineScene: React.FC = () => (
  <AbsoluteFill>
    <Laundry />
    <FiveStage />
    <Structural />
    <DataHazard />
    <ControlHazard />
  </AbsoluteFill>
);
