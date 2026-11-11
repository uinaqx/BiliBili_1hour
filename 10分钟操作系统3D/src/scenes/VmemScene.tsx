import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Block, CurveArrow, Label, Line, Orb, PolyTube, Ring, Stage, V3} from '../three';
import {camPath, easeOut, ip, lerp, prog, pulse, track, useScene, vis} from '../anim';
import {C} from '../theme';
import {Badge, Mono} from '../ui';

const CPU: V3 = [-9.6, 0.6, 0], PT: V3 = [-4.4, 0.5, 0], TLB: V3 = [-6.6, 3.7, 0];
const ramX = (k: number) => 0.9 + k * 2.1;
const RAM_Y = 2.6;
const DISK: V3 = [5.6, -2.7, 0];
const rowY = (r: number) => 1.5 - r * 0.85 + 0.1;
const ramPos = (k: number): V3 => [ramX(k), RAM_Y, 0];
const ptRow = (r: number): V3 => [PT[0], rowY(r), 0.5];

const REFS = [1, 2, 3, 1, 4, 1];
const STEP_AT = [0.07, 0.2, 0.33, 0.47, 0.62, 0.78];
// 每个槽位在各步之后的页号
const FIFO_SLOTS = [[1, 1, 1, 1, 4, 4], [0, 2, 2, 2, 2, 1], [0, 0, 3, 3, 3, 3]];
const LRU_SLOTS = [[1, 1, 1, 1, 1, 1], [0, 2, 2, 2, 4, 4], [0, 0, 3, 3, 3, 3]];
const FIFO_MSG = ['缺页', '缺页', '缺页', '命中', '缺页 · 淘汰 1', '缺页 · 淘汰 2'];
const LRU_MSG = ['缺页', '缺页', '缺页', '命中', '缺页 · 淘汰 2', '命中'];
const CURVE: [number, number][] = [[0, 0], [1, 0.3], [2, 0.55], [3, 0.75], [4, 0.9], [5, 1.0], [6, 0.94], [7, 0.7], [8, 0.36], [9, 0.16], [10, 0.08]];
const curvePt = (n: number, u: number): V3 => [-7 + n * 1.4, -2.6 + u * 5.2, 0];

export const VmemScene: React.FC = () => {
  const {frame, at, bd} = useScene();

  const gM = vis(frame, 0, at(3, 0) - 4, 14); // 机器（第 1~3 句）
  const gBar = 1 - prog(frame, at(1, 0) - 4, 14);
  const gPT = vis(frame, at(0, 0.5), at(3, 0) - 4, 14);
  const g3 = vis(frame, at(3, 0.0), at(4, 0) - 4, 14);
  const g4 = vis(frame, at(4, 0.0), 1e9, 14);

  // —— 第 2 句：缺页 ——
  const loaded = frame >= at(1, 0.6);
  const acc = track(frame, [[at(1, 0.08), CPU], [at(1, 0.22), ptRow(1)]]);
  const accO = vis(frame, at(1, 0.08), at(1, 0.36), 8);
  const page = track(frame, [[at(1, 0.36), [DISK[0] - 1.4, DISK[1] + 0.4, 0]], [at(1, 0.58), ramPos(2)]]);
  const pageO = vis(frame, at(1, 0.36), at(1, 0.62), 8);
  const retry = track(frame, [[at(1, 0.72), CPU], [at(1, 0.8), ptRow(1)], [at(1, 0.92), ramPos(2)]]);
  const retryO = vis(frame, at(1, 0.72), at(2, 0), 10);

  // —— 第 3 句：TLB ——
  const slow = track(frame, [[at(2, 0.05), CPU], [at(2, 0.17), ptRow(0)], [at(2, 0.3), ramPos(0)]]);
  const slowO = vis(frame, at(2, 0.05), at(2, 0.34), 8);
  const fast = track(frame, [[at(2, 0.55), CPU], [at(2, 0.63), [TLB[0], TLB[1], 0.5]], [at(2, 0.72), ramPos(0)]]);
  const fastO = vis(frame, at(2, 0.55), at(2, 0.78), 8);
  const tlbFilled = ip(frame, at(2, 0.4), 14);

  // —— 第 4 句：FIFO / LRU ——
  const step = STEP_AT.filter((s) => frame >= at(3, s)).length; // 已完成的步数
  const slotLabel = (slots: number[][], k: number) => (step === 0 ? 0 : slots[k][step - 1]);
  const panel = (cx: number, title: string, slots: number[][], msgs: string[], color: string) => (
    <group>
      <Label text={title} position={[cx, 2.5, 0]} size={0.56} bold color={color} opacity={ip(frame, at(3, 0.02), 14) * g3} />
      {[0, 1, 2].map((k) => {
        const v = slotLabel(slots, k);
        const changed = step > 0 && (step < 2 ? false : slots[k][step - 1] !== slots[k][step - 2]) ? 1 : 0;
        const boom = changed && msgs[step - 1].includes('淘汰') ? pulse(frame, at(3, STEP_AT[step - 1]), 30) : 0;
        return (
          <group key={k}>
            <Block position={[cx + (k - 1) * 2.0, 0.6, 0]} size={[1.7, 1.7, 1.7]} color={boom ? '#4a1620' : C.panel2} edge={v ? (boom ? C.red : color) : C.border}
              opacity={ip(frame, at(3, 0.03), 14) * g3} glow={v ? 2 + boom * 2 : 1} emissive={0.3 + boom * 0.5} />
            {v > 0 && <Label text={`${v}`} position={[cx + (k - 1) * 2.0, 0.6, 1.0]} size={0.8} bold mono opacity={g3} depthTest={false} />}
          </group>
        );
      })}
      {step > 0 && (
        <Label text={msgs[step - 1]} position={[cx, -1.5, 0.6]} size={0.46} bold color={msgs[step - 1].startsWith('命中') ? C.cyan : msgs[step - 1].includes('淘汰') ? C.red : C.gold}
          opacity={g3} depthTest={false} />
      )}
    </group>
  );

  // —— 第 5 句：抖动曲线 ——
  const cp = ip(frame, at(4, 0.06), bd(4) * 0.5);
  const upto = cp * 10;
  const ptsFull = CURVE.map(([n, u]) => curvePt(n, u));
  const head = (() => {
    const i = Math.min(9, Math.floor(upto)), f = upto - i;
    return [lerp(ptsFull[i][0], ptsFull[i + 1][0], f), lerp(ptsFull[i][1], ptsFull[i + 1][1], f), 0] as V3;
  })();

  const cam = camPath(frame, [
    [0, [0, 3, 24], [-1, 0.5, 0]],
    [at(1, 0.5), [-1, 3, 22], [-1, 0.5, 0]],
    [at(2, 0.5), [-2, 3, 22], [-2, 1, 0]],
    [at(3, 0.3), [0, 2, 22], [0, 0.5, 0]],
    [at(4, 0.3), [1, 2.5, 22], [0, 0, 0]],
    [at(4, 1) + 40, [-1, 3, 23], [0, 0, 0]],
  ]);

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={-5}>
        {/* —— 第 1 句：虚拟地址空间 —— */}
        <Block position={[-9.6, 0.4, 0]} size={[2.2, 6.6, 1.6]} color={C.panel} edge={C.violet} opacity={ip(frame, at(0, 0.04), 18) * gBar} glow={1.5} />
        {Array.from({length: 8}, (_, i) => {
          const inRam = i === 0 || i === 2;
          return <Block key={i} position={[-9.6, 3.35 - i * 0.78, 0.2]} size={[1.9, 0.62, 1.4]} color={C.panel2} edge={inRam ? C.cyan : C.muted}
            opacity={ip(frame, at(0, 0.1 + i * 0.03), 12) * gBar * (inRam ? 1 : 0.7)} glow={inRam ? 2 : 1} />;
        })}
        <Label text="虚拟地址空间（很大）" position={[-9.6, 4.5, 0]} size={0.34} bold color={C.violet} opacity={vis(frame, at(0, 0.1)) * gBar} />

        {/* CPU */}
        <Block position={CPU} size={[2.4, 2.4, 2]} color="#3a1b3e" edge={C.pink} opacity={ip(frame, at(1, 0.0), 16) * gM} glow={2.2} emissive={0.4} />
        <Label text="CPU" position={[CPU[0], CPU[1], 1.1]} size={0.6} bold mono opacity={ip(frame, at(1, 0.0), 16) * gM} depthTest={false} />

        {/* 内存 */}
        {[0, 1, 2, 3].map((k) => {
          const filled = k < 2 || (k === 2 && loaded);
          const pageNo = k === 0 ? 0 : k === 1 ? 2 : 1;
          const o = ip(frame, at(0, 0.3 + k * 0.05), 14) * gM;
          const pop = k === 2 ? ip(frame, at(1, 0.58), 12, easeOut) : 1;
          return (
            <group key={k}>
              <Block position={ramPos(k)} size={[1.8, 1.8, 1.8]} color={filled ? C.panel2 : C.panel} edge={filled ? C.cyan : C.border} opacity={o * (filled ? 1 : 0.6)} glow={filled ? 2 : 1}
                scale={k === 2 ? 0.8 + 0.2 * pop : 1} />
              <Label text={`帧 ${k}`} position={[ramX(k), RAM_Y + 1.35, 0]} size={0.26} mono color={C.muted} opacity={o} />
              {filled && (k !== 2 || loaded) && <Label text={`页 ${pageNo}`} position={[ramX(k), RAM_Y, 1.0]} size={0.4} bold mono opacity={o * (k === 2 ? pop : 1)} depthTest={false} />}
            </group>
          );
        })}
        <Label text="物理内存（很小）" position={[ramX(1.5), RAM_Y + 2.1, 0]} size={0.38} bold color={C.cyan} opacity={ip(frame, at(0, 0.34), 14) * gM} />

        {/* 硬盘 */}
        <Block position={DISK} size={[7.4, 1.6, 3]} color={C.panel} edge={C.violet} opacity={ip(frame, at(0, 0.45), 16) * gM} glow={1.5} />
        {Array.from({length: 5}, (_, j) => (
          <Block key={j} position={[DISK[0] - 2.8 + j * 1.4, DISK[1] + 1.25, 0]} size={[1.0, 0.9, 1.2]} color={C.panel2} edge={C.muted} opacity={ip(frame, at(0, 0.5 + j * 0.03), 12) * gM} glow={1.2} />
        ))}
        <Label text="硬盘（交换区）" position={[DISK[0], DISK[1] - 1.5, 0.8]} size={0.38} bold color={C.violet} opacity={ip(frame, at(0, 0.5), 14) * gM} />
        <Label text="只把正在用的页放进内存" position={[0.5, -5.0, 0]} size={0.4} bold color={C.text} opacity={vis(frame, at(0, 0.62), at(1, 0)) * gM} />

        {/* 页表 */}
        <Block position={PT} size={[3.9, 3.7, 0.4]} color={C.panel2} edge={C.gold} opacity={ip(frame, at(0, 0.52), 16) * gPT} glow={1.8} />
        <Label text="页表" position={[PT[0], PT[1] + 2.2, 0.4]} size={0.4} bold color={C.gold} opacity={ip(frame, at(0, 0.55), 14) * gPT} />
        {[0, 1, 2, 3].map((r) => {
          const valid = r === 0 || r === 2 || (r === 1 && loaded);
          const frameNo = r === 0 ? 0 : r === 2 ? 1 : r === 1 ? 2 : -1;
          const flash = r === 1 ? pulse(frame, at(1, 0.62), 28) : 0;
          return (
            <group key={r}>
              {flash > 0 && <Block position={[PT[0], rowY(r), 0.3]} size={[3.6, 0.7, 0.2]} color={C.cyan} edge={C.cyan} opacity={flash * 0.8 * gPT} glow={2.4} emissive={0.8} />}
              <Label text={`页${r}  ${valid ? '有效 ✓' : '无效 ✗'}  ${valid ? `帧${frameNo}` : '磁盘'}`} position={[PT[0], rowY(r), 0.5]} size={0.3} mono bold
                color={valid ? C.text : C.red} opacity={ip(frame, at(0, 0.58 + r * 0.03), 12) * gPT} depthTest={false} />
            </group>
          );
        })}
        <Label text="有效位" position={[PT[0] + 2.7, PT[1] + 1.3, 0.5]} size={0.3} bold color={C.gold} opacity={vis(frame, at(1, 0.0), at(1, 0.3)) * gPT} />

        {/* TLB */}
        <Block position={TLB} size={[2.8, 1.2, 1.4]} color={C.panel2} edge={C.cyan} opacity={vis(frame, at(2, 0.0), at(3, 0), 14) * gM} glow={2} emissive={0.3 + tlbFilled * 0.3} />
        <Label text="TLB" position={[TLB[0], TLB[1] + 0.1, 0.8]} size={0.46} bold mono color={C.cyan} opacity={vis(frame, at(2, 0.0), at(3, 0), 14) * gM} depthTest={false} />
        <Label text={tlbFilled > 0.5 ? '页0→帧0' : '（空）'} position={[TLB[0], TLB[1] - 0.4, 0.8]} size={0.24} mono color={C.muted} opacity={vis(frame, at(2, 0.0), at(3, 0), 14) * gM} depthTest={false} />

        {/* 动画令牌 */}
        <Orb position={acc} radius={0.3} color={C.gold} glow={1.8} opacity={accO * gM} />
        <Orb position={page} radius={0.3} color={C.pink} glow={1.8} opacity={pageO * gM} />
        <Orb position={retry} radius={0.3} color={C.cyan} glow={1.8} opacity={retryO * gM} />
        <Orb position={slow} radius={0.3} color={C.pink} glow={1.8} opacity={slowO * gM} />
        <Orb position={fast} radius={0.3} color={C.cyan} glow={1.8} opacity={fastO * gM} />
        {frame >= at(1, 0.24) && frame < at(1, 0.24) + 30 && (
          <Ring position={[CPU[0], CPU[1], 1.2]} radius={ip(frame, at(1, 0.24), 28, easeOut) * 2.6} width={0.08} color={C.red} opacity={1 - prog(frame, at(1, 0.24), 30)} />
        )}
        <Label text="缺页中断！" position={[-7.2, -1.8, 0.6]} size={0.6} bold color={C.red} opacity={vis(frame, at(1, 0.24), at(1, 0.42)) * gM} />
        <Label text="内核：从硬盘读入这一页" position={[1.6, 0.4, 0.8]} size={0.4} bold color={C.pink} opacity={vis(frame, at(1, 0.38), at(1, 0.64)) * gM} />
        <Label text="更新页表 → 重新执行" position={[-4.6, -2.7, 0.8]} size={0.4} bold color={C.cyan} opacity={vis(frame, at(1, 0.62), at(2, 0)) * gM} />
        <Label text="查页表 + 访问内存：慢" position={[-3.2, -3.6, 0.8]} size={0.4} bold color={C.pink} opacity={vis(frame, at(2, 0.1), at(2, 0.4)) * gM} />
        <Label text="TLB 命中：一步到位" position={[-3.8, 5.0, 0.8]} size={0.42} bold color={C.cyan} opacity={vis(frame, at(2, 0.6), at(3, 0)) * gM} />

        {/* —— 第 4 句：置换 —— */}
        {panel(-5.8, 'FIFO  先进先出', FIFO_SLOTS, FIFO_MSG, C.pink)}
        {panel(5.8, 'LRU  最近最少使用', LRU_SLOTS, LRU_MSG, C.cyan)}
        {REFS.map((r, i) => {
          const cur = step === i + 1 ? 1 : 0;
          return (
            <Label key={i} text={`${r}`} position={[-3.75 + i * 1.5, 3.9, 0.4]} size={0.56} bold mono bg="#171433ee" border={cur ? C.gold : C.border} color={cur ? C.gold : C.text}
              opacity={ip(frame, at(3, 0.03 + i * 0.02), 12) * g3 * (step > i ? 1 : 0.55)} depthTest={false} />
          );
        })}
        <Label text="访问序列" position={[-6.2, 3.9, 0.4]} size={0.34} color={C.muted} opacity={ip(frame, at(3, 0.04), 12) * g3} />
        <Label text="共缺页 5 次" position={[-5.8, -2.6, 0.6]} size={0.5} bold color={C.pink} opacity={vis(frame, at(3, 0.88)) * g3} />
        <Label text="共缺页 4 次" position={[5.8, -2.6, 0.6]} size={0.5} bold color={C.cyan} opacity={vis(frame, at(3, 0.88)) * g3} />

        {/* —— 第 5 句：抖动 —— */}
        <Line from={[-7.4, -2.6, 0]} to={[8.2, -2.6, 0]} color={C.muted} opacity={ip(frame, at(4, 0.02), 14) * g4} />
        <Line from={[-7.4, -2.6, 0]} to={[-7.4, 3.0, 0]} color={C.muted} opacity={ip(frame, at(4, 0.02), 14) * g4} />
        <Label text="并发进程数 →" position={[6.6, -3.3, 0]} size={0.34} color={C.muted} opacity={ip(frame, at(4, 0.04), 14) * g4} />
        <Label text="CPU 利用率" position={[-7.4, 3.55, 0]} size={0.34} color={C.muted} opacity={ip(frame, at(4, 0.04), 14) * g4} />
        {cp > 0.01 && <PolyTube points={ptsFull} progress={Math.min(0.999, cp)} color={cp > 0.52 ? C.red : C.cyan} radius={0.08} opacity={g4} />}
        {cp > 0.01 && <Orb position={head} radius={0.28} color={cp > 0.52 ? C.red : C.cyan} glow={2} opacity={g4} />}
        <Label text="页框够用" position={[-5.0, 1.8, 0]} size={0.4} bold color={C.cyan} opacity={vis(frame, at(4, 0.22)) * g4} />
        <Label text="抖动 Thrashing" position={[5.4, 0.9, 0]} size={0.6} bold color={C.red} opacity={vis(frame, at(4, 0.42)) * g4} />
        <Label text="一直在换页，没空干活" position={[5.4, 0.1, 0]} size={0.34} color={C.red} opacity={vis(frame, at(4, 0.46)) * g4} />
        <CurveArrow from={[4.4, -1.6, 0]} to={[0.3, 1.8, 0]} bend={[-0.6, 1.0, 0]} color={C.gold} radius={0.06} progress={ip(frame, at(4, 0.7), 24)} opacity={g4} />
        <Label text="减少并发进程 / 增加页框" position={[2.2, -1.9, 0.5]} size={0.4} bold color={C.gold} opacity={vis(frame, at(4, 0.72)) * g4} />
      </Stage>

      <Badge from={at(0, 0.7)} to={at(1, 0)} x={1848} y={170} align="right" color={C.violet}>程序可用的空间 &gt; 物理内存</Badge>
      <Badge from={at(1, 0.3)} to={at(2, 0)} x={1848} y={170} align="right" color={C.red}>缺页中断 <Mono color={C.red}>Page Fault</Mono></Badge>
      <Badge from={at(2, 0.1)} to={at(3, 0)} x={1848} y={170} align="right" color={C.cyan}>快表 <Mono>TLB</Mono></Badge>
      <Badge from={at(3, 0.1)} to={at(4, 0)} x={1848} y={170} align="right" color={C.gold}>页面置换</Badge>
    </AbsoluteFill>
  );
};
