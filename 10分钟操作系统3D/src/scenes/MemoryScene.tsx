import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Block, CurveArrow, GlassBox, Label, Stage, V3} from '../three';
import {camPath, easeOut, easeOutBack, ip, lerp, prog, pulse, useScene, vis} from '../anim';
import {C} from '../theme';
import {Badge, Mono} from '../ui';

type Owner = 'A' | 'B' | 'C' | 'D' | 'E' | null;
const MINT = '#8cf5c0';
const OWN: Record<string, string> = {A: C.cyan, B: C.pink, C: C.gold, D: C.violet, E: MINT};
const SCATTER: Owner[] = ['A', 'C', 'B', 'A', null, 'C', 'B', 'A', 'C', null, 'B', 'C'];
const CONTIG: Owner[] = ['A', 'A', 'A', 'B', 'B', 'C', 'C', 'C', 'D', 'D', null, null];
const AFTER: Owner[] = ['A', 'A', 'A', null, null, 'C', 'C', 'C', null, null, null, null];
const PAGE_OF: Record<number, number> = {3: 0, 4: 1, 8: 2, 9: 3, 10: 4};
const CX = 6.6, PITCH = 0.62;
const cellY = (i: number) => 3.5 - i * PITCH;

export const MemoryScene: React.FC = () => {
  const {frame, at, bd} = useScene();

  const g0 = 1 - prog(frame, at(1, 0) - 4, 14);
  const gTable = vis(frame, at(3, 0.0), at(4, 0), 14);
  const g4 = vis(frame, at(4, 0.0), 1e9, 14);

  const cell = (i: number): {o: Owner; s: number; page?: number} => {
    const tCont = at(1, 0.04 + i * 0.015);
    const tAfter = at(1, 0.46);
    if (frame < tCont) return {o: SCATTER[i], s: 0};
    if (frame < tAfter) return {o: CONTIG[i], s: tCont};
    const pi = PAGE_OF[i];
    if (pi !== undefined && frame >= at(2, 0.3 + pi * 0.1)) return {o: 'E', s: at(2, 0.3 + pi * 0.1), page: pi};
    return {o: AFTER[i], s: tAfter};
  };

  // 第 3 句：地址翻译
  const rowHi = ip(frame, at(3, 0.3), 12);
  const resolve = ip(frame, at(3, 0.5), 20);

  const cam = camPath(frame, [
    [0, [1, 3, 24], [0, 0, 0]],
    [at(1, 0.3), [3, 2.5, 22], [2, 0, 0]],
    [at(2, 0.5), [-1, 2.5, 22], [0, 0, 0]],
    [at(3, 0.5), [0, 2.5, 22], [0, -0.2, 0]],
    [at(4, 0.4), [-1, 2, 22], [-1, 0, 0]],
    [at(4, 1) + 40, [2, 3, 23], [0, 0, 0]],
  ]);

  const holeBox = (a: number, b: number, label: string) => {
    const cy = (cellY(a) + cellY(b)) / 2, h = (b - a + 1) * PITCH;
    const o = vis(frame, at(1, 0.66), at(2, 0.05), 12);
    return (
      <group>
        <GlassBox position={[CX, cy, 0]} size={[3.3, h + 0.06, 2.4]} color={C.red} fill={0.12} opacity={o} glow={1.6} />
        <Label text={label} position={[CX + 3.0, cy, 0.5]} size={0.38} bold color={C.red} opacity={o} />
      </group>
    );
  };

  const PTABLE = [3, 4, 8, 9, 10];

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={-5}>
        {/* 物理内存 */}
        {Array.from({length: 12}, (_, i) => {
          const st = cell(i);
          const o = ip(frame, at(0, 0.28 + i * 0.03), 14);
          const pop = st.s > 0 ? 0.82 + 0.18 * ip(frame, st.s, 14, easeOutBack) : 1;
          const col = st.o ? OWN[st.o] : C.border;
          const hit = i === 8 ? resolve * pulse(frame, at(3, 0.5), 40) : 0;
          return (
            <group key={i}>
              <Block position={[CX, cellY(i), 0]} size={[3.0, 0.54, 2.0]} color={st.o ? C.panel2 : C.panel} edge={col} opacity={o * (st.o ? 1 : 0.6)} glow={st.o ? 2 + hit * 2 : 1.1}
                emissive={st.o ? 0.35 + hit : 0.1} scale={pop} />
              {st.o && <Label text={st.page !== undefined ? `E${st.page}` : st.o} position={[CX, cellY(i), 1.05]} size={0.34} bold mono opacity={o} depthTest={false} />}
              <Label text={`${i}`} position={[CX - 2.0, cellY(i), 0.4]} size={0.24} mono color={C.muted} opacity={o} />
            </group>
          );
        })}
        <Label text="物理内存（页框）" position={[CX, 4.7, 0]} size={0.4} bold color={C.violet} opacity={ip(frame, at(0, 0.3), 14)} />

        {/* —— 第 1 句：逻辑地址 → MMU → 物理地址 —— */}
        {(['A', 'B', 'C'] as const).map((p, k) => {
          const x = -10.8 + k * 2.8;
          const o = ip(frame, at(0, 0.06 + k * 0.08), 16) * g0;
          return (
            <group key={p}>
              <Block position={[x, 0, 0]} size={[1.8, 6.4, 1.8]} color={C.panel} edge={OWN[p]} opacity={o} glow={1.8} />
              <Label text={p} position={[x, 0, 1.0]} size={0.7} bold mono color={OWN[p]} opacity={o} depthTest={false} />
              <Label text="0" position={[x, -3.55, 0.6]} size={0.28} mono color={C.muted} opacity={o} />
              <Label text="N" position={[x, 3.6, 0.6]} size={0.28} mono color={C.muted} opacity={o} />
              <CurveArrow from={[x + 1.0, 0.5 - k * 0.5, 0.4]} to={[-3.0, 0.9 - k * 0.9, 0.4]} bend={[0, 0.5, 0]} color={OWN[p]} radius={0.04}
                progress={ip(frame, at(0, 0.36 + k * 0.04), 20)} opacity={g0} />
            </group>
          );
        })}
        <Label text="逻辑地址：每个进程都是 0 ~ N，连续" position={[-7.6, -4.3, 0]} size={0.34} color={C.muted} opacity={vis(frame, at(0, 0.3)) * g0} />
        <Block position={[-1.6, 0, 0]} size={[2.6, 3.2, 2.0]} color="#3a1b3e" edge={C.pink} opacity={ip(frame, at(0, 0.34), 18) * g0} glow={2.4} emissive={0.4} />
        <Label text="MMU" position={[-1.6, 0.2, 1.1]} size={0.6} bold mono opacity={ip(frame, at(0, 0.34), 18) * g0} depthTest={false} />
        <Label text="地址翻译" position={[-1.6, -0.7, 1.1]} size={0.3} color={C.muted} opacity={ip(frame, at(0, 0.34), 18) * g0} depthTest={false} />
        {SCATTER.map((o, i) => (o && i % 2 === 0) ? (
          <CurveArrow key={i} from={[-0.2, (o === 'A' ? 0.7 : o === 'B' ? 0 : -0.7), 0.4]} to={[CX - 1.7, cellY(i), 0.4]} bend={[0, 0.3, 0]} color={OWN[o]} radius={0.028}
            progress={ip(frame, at(0, 0.55 + i * 0.03), 20)} opacity={g0 * 0.9} trimEnd={0.1} />
        ) : null)}
        <Label text="物理地址：散落在各处" position={[1.8, 4.7, 0]} size={0.34} color={C.muted} opacity={vis(frame, at(0, 0.62)) * g0} />

        {/* —— 第 2 句：外部碎片 —— */}
        <Block position={[-2.4, 0.6, 0]} size={[2.8, 5 * PITCH + 0.6, 2.0]} color={'#16342a'} edge={MINT} opacity={vis(frame, at(1, 0.62), at(2, 0.1)) * 1} glow={2.2} emissive={0.4} />
        <Label text="E" position={[-2.4, 0.9, 1.1]} size={0.8} bold mono color={MINT} opacity={vis(frame, at(1, 0.62), at(2, 0.1))} depthTest={false} />
        <Label text="需要连续 5 格" position={[-2.4, -1.4, 1.1]} size={0.34} bold opacity={vis(frame, at(1, 0.64), at(2, 0.1))} depthTest={false} />
        <CurveArrow from={[-0.8, 0.8, 0.4]} to={[CX - 1.8, cellY(9), 0.4]} bend={[0, 0.8, 0]} color={C.red} radius={0.05} progress={ip(frame, at(1, 0.7), 20)} opacity={vis(frame, at(1, 0.7), at(2, 0.1))} />
        <Label text="✗  放不下" position={[2.2, -2.8, 0.6]} size={0.7} bold color={C.red} opacity={vis(frame, at(1, 0.78), at(2, 0.1))} />
        {holeBox(3, 4, '空洞 2')}
        {holeBox(8, 11, '空洞 4')}
        <Label text="空闲共 6 格，却没有连续 5 格 ＝ 外部碎片" position={[-1.6, 4.2, 0]} size={0.44} bold color={C.red} opacity={vis(frame, at(1, 0.74), at(2, 0.05))} />

        {/* —— 第 3 句：分页 —— */}
        {PTABLE.map((cellIdx, pi) => {
          const t = at(2, 0.18 + pi * 0.1);
          const o = ip(frame, t, 14) * (1 - (1 - 0.18) * ip(frame, at(3, 0.0), 12)) * (1 - prog(frame, at(4, 0), 12));
          return (
            <group key={pi}>
              <Block position={[-5.4, 2.4 - pi * 1.3, 0]} size={[2.4, 0.9, 1.5]} color={C.panel2} edge={MINT} opacity={o} glow={1.9} />
              <Label text={`页 ${pi}`} position={[-5.4, 2.4 - pi * 1.3, 0.85]} size={0.38} bold mono opacity={o} depthTest={false} />
              <CurveArrow from={[-4.0, 2.4 - pi * 1.3, 0.3]} to={[CX - 1.8, cellY(cellIdx), 0.3]} bend={[0, 0.6, 0.5]} color={MINT} radius={0.035} progress={ip(frame, t + 6, 24)}
                opacity={o * 0.85} trimEnd={0.05} />
            </group>
          );
        })}
        <Label text="逻辑页（进程 E）" position={[-5.4, 4.0, 0]} size={0.36} bold color={MINT} opacity={vis(frame, at(2, 0.15), at(3, 0.0))} />
        <Label text="页可以放进任意空闲页框" position={[0, -4.3, 0]} size={0.42} bold color={C.cyan} opacity={vis(frame, at(2, 0.78), at(3, 0))} />

        {/* —— 第 4 句：页表 + 地址组成 —— */}
        <Block position={[-1.6, 0.2, 0]} size={[4.8, 4.9, 0.4]} color={C.panel2} edge={C.cyan} opacity={ip(frame, at(3, 0.04), 16) * gTable} glow={1.8} />
        <Label text="页表" position={[-1.6, 2.95, 0.4]} size={0.42} bold color={C.cyan} opacity={ip(frame, at(3, 0.06), 16) * gTable} />
        {PTABLE.map((cellIdx, pi) => {
          const hi = pi === 2 ? rowHi : 0;
          return (
            <group key={pi}>
              {hi > 0 && <Block position={[-1.6, 1.8 - pi * 0.9, 0.3]} size={[4.4, 0.7, 0.2]} color={C.gold} edge={C.gold} opacity={hi * 0.9 * gTable} glow={2.4} emissive={0.8} />}
              <Label text={`页 ${pi}   →   帧 ${cellIdx}`} position={[-1.6, 1.8 - pi * 0.9, 0.45]} size={0.36} mono bold color={hi > 0.5 ? C.bg : C.text}
                opacity={ip(frame, at(3, 0.1 + pi * 0.03), 12) * gTable} depthTest={false} />
            </group>
          );
        })}
        <Label text="页号 2" position={[-3.6, 4.0, 0.3]} size={0.46} bold mono bg="#171433ee" border={C.cyan} color={C.cyan} opacity={vis(frame, at(3, 0.12), at(4, 0)) * gTable} depthTest={false} />
        <Label text="偏移 0x1A" position={[0.2, 4.0, 0.3]} size={0.46} bold mono bg="#171433ee" border={C.gold} color={C.gold} opacity={vis(frame, at(3, 0.12), at(4, 0)) * gTable} depthTest={false} />
        <Label text="逻辑地址" position={[-6.3, 4.0, 0.3]} size={0.34} color={C.muted} opacity={vis(frame, at(3, 0.1), at(4, 0)) * gTable} />
        <CurveArrow from={[-3.6, 3.5, 0.3]} to={[-3.6, 1.2, 0.3]} bend={[-0.7, 0, 0]} color={C.cyan} radius={0.04} progress={ip(frame, at(3, 0.26), 16)} opacity={gTable} />
        <Label text="帧号 8" position={[-3.6, -3.7, 0.3]} size={0.46} bold mono bg="#171433ee" border={C.pink} color={C.pink} opacity={vis(frame, at(3, 0.58), at(4, 0)) * gTable} depthTest={false} />
        <Label text="偏移 0x1A" position={[0.2, -3.7, 0.3]} size={0.46} bold mono bg="#171433ee" border={C.gold} color={C.gold} opacity={vis(frame, at(3, 0.62), at(4, 0)) * gTable} depthTest={false} />
        <Label text="物理地址" position={[-6.3, -3.7, 0.3]} size={0.34} color={C.muted} opacity={vis(frame, at(3, 0.58), at(4, 0)) * gTable} />
        <CurveArrow from={[-3.6, -1.9, 0.3]} to={[-3.6, -3.1, 0.3]} color={C.pink} radius={0.04} progress={ip(frame, at(3, 0.5), 16)} opacity={gTable} />
        <CurveArrow from={[0.3, 3.5, 0.3]} to={[0.3, -3.1, 0.3]} bend={[2.6, 0, 0]} color={C.gold} radius={0.03} progress={ip(frame, at(3, 0.4), 40)} opacity={gTable * 0.8} />

        {/* —— 第 5 句：内部碎片 / 分段 —— */}
        <Block position={[CX + 0.9, cellY(10), 0.12]} size={[1.2, 0.5, 2.05]} color="#4a1620" edge={C.red} opacity={ip(frame, at(4, 0.1), 14) * g4 * 0.9} glow={2.2} emissive={0.6} />
        <Label text="内部碎片" position={[CX + 3.2, cellY(10), 0.6]} size={0.38} bold color={C.red} opacity={vis(frame, at(4, 0.12)) * g4} />
        <Label text="最后一页没用满" position={[CX + 3.5, cellY(10) - 0.6, 0.6]} size={0.28} color={C.muted} opacity={vis(frame, at(4, 0.18)) * g4} />
        {[['代码段', 3.8, C.violet], ['数据段', 2.4, C.gold], ['栈段', 1.6, C.cyan], ['堆段', 3.0, C.pink]].map(([n, w, c], k) => {
          const o = ip(frame, at(4, 0.4 + k * 0.1), 16) * g4;
          return (
            <group key={n as string}>
              <Block position={[-6.4 + (w as number) / 2, 2.6 - k * 1.5, 0]} size={[w as number, 1.0, 1.6]} color={C.panel2} edge={c as string} opacity={o} glow={2} />
              <Label text={n as string} position={[-6.4 + (w as number) / 2, 2.6 - k * 1.5, 0.9]} size={0.38} bold opacity={o} depthTest={false} />
            </group>
          );
        })}
        <Label text="分段：按逻辑模块，长度不一" position={[-3.8, 4.1, 0]} size={0.4} bold color={C.cyan} opacity={vis(frame, at(4, 0.38)) * g4} />
        <Label text="分页：没有外部碎片" position={[-3.4, -4.0, 0]} size={0.4} bold color={MINT} opacity={vis(frame, at(4, 0.08)) * g4} />
      </Stage>

      <Badge from={at(0, 0.8)} to={at(1, 0)} x={1848} y={170} align="right" color={C.pink}>逻辑地址 → <Mono color={C.pink}>MMU</Mono> → 物理地址</Badge>
      <Badge from={at(1, 0.8)} to={at(2, 0)} x={1848} y={170} align="right" color={C.red}>连续分配：外部碎片</Badge>
      <Badge from={at(2, 0.5)} to={at(3, 0)} x={1848} y={170} align="right" color={C.cyan}>分页 <Mono>Paging</Mono></Badge>
      <Badge from={at(3, 0.2)} to={at(4, 0)} x={1848} y={170} align="right" color={C.gold}>物理地址 = 帧号 + 偏移</Badge>
      <Badge from={at(4, 0.1)} x={1848} y={170} align="right" color={C.red}>页内：内部碎片</Badge>
    </AbsoluteFill>
  );
};
