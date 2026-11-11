import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Block, CurveArrow, GlassBox, Label, Orb, Ring, Stage, V3} from '../three';
import {camPath, easeOut, ip, lerp, prog, track, useScene, vis} from '../anim';
import {C} from '../theme';
import {Badge, Mono} from '../ui';

type Seg = [string, number, number]; // 进程, 起, 止
const COLOR: Record<string, string> = {P1: C.cyan, P2: C.pink, P3: C.gold};
const U = 0.95, X0 = -6.0, BH = 1.3;
const FCFS: Seg[] = [['P1', 0, 8], ['P2', 8, 12], ['P3', 12, 14]];
const SJF: Seg[] = [['P3', 0, 2], ['P2', 2, 6], ['P1', 6, 14]];
const RR: Seg[] = [['P1', 0, 2], ['P2', 2, 4], ['P3', 4, 6], ['P1', 6, 8], ['P2', 8, 10], ['P1', 10, 12], ['P1', 12, 14]];
const ROW_Y = {fcfs: 2.6, sjf: 0.4, rr: -1.8};

export const SchedScene: React.FC = () => {
  const {frame, at, bd} = useScene();

  const g0 = 1 - prog(frame, at(1, 0) - 4, 14); // 第 1 句内容
  const g1 = 1 - prog(frame, at(4, 0) - 4, 16); // 甘特图
  const g4 = vis(frame, at(4, 0.0), 1e9, 16); // 多级反馈队列

  const row = (id: string, label: string, y: number, segs: Seg[], beat: number, avg: string, delay = 0.1) => {
    const start = at(beat, delay), span = bd(beat) * 0.62;
    const rowO = ip(frame, start - 8, 14) * g1;
    return (
      <group key={id}>
        <Label text={label} position={[-9.0, y, 0.9]} size={0.42} bold mono color={C.text} opacity={rowO} depthTest={false} />
        <Block position={[X0 + 7 * U - 0.5 * U, y - BH / 2 - 0.12, 0]} size={[14 * U + 0.4, 0.06, 1.8]} color={C.border} edge={C.border} opacity={rowO * 0.8} glow={1} />
        {segs.map(([p, a, b], i) => {
          const t = start + (a / 14) * span;
          const w = (b - a) * U * ip(frame, t, 16, easeOut);
          if (w < 0.02) return null;
          const full = w >= (b - a) * U - 0.01;
          return (
            <group key={i}>
              <Block position={[X0 + a * U + w / 2, y, 0]} size={[Math.max(0.05, w - 0.07), BH, 1.7]} color={C.panel2} edge={COLOR[p]} opacity={g1} glow={2} emissive={0.35} />
              {full && (b - a) >= 2 && <Label text={p} position={[X0 + a * U + w / 2, y, 0.95]} size={0.4} bold mono opacity={g1} depthTest={false} />}
            </group>
          );
        })}
        <Label text={`平均等待 ${avg}`} position={[10.6, y, 0.9]} size={0.36} bold bg="#171433ee" border={C.gold} color={C.gold}
          opacity={ip(frame, start + span + 6, 14) * g1} depthTest={false} />
      </group>
    );
  };

  // 多级反馈队列
  const LANE = [{y: 3.0, t: 'Q0  优先级最高 · 时间片最短', c: C.cyan}, {y: 0.2, t: 'Q1  优先级中 · 时间片较长', c: C.gold}, {y: -2.6, t: 'Q2  优先级低 · 时间片最长', c: C.pink}];
  const long = track(frame, [
    [at(4, 0.08), [-6.4, 3.0, 0]], [at(4, 0.2), [-3.4, 3.0, 0]], [at(4, 0.3), [-3.4, 3.0, 0]], [at(4, 0.4), [-3.4, 0.2, 0]],
    [at(4, 0.5), [-0.6, 0.2, 0]], [at(4, 0.56), [-0.6, 0.2, 0]], [at(4, 0.64), [-0.6, -2.6, 0]], [at(4, 0.72), [3.0, -2.6, 0]],
    [at(4, 0.8), [3.0, -2.6, 0]], [at(4, 0.92), [3.0, 3.0, 0]],
  ]);
  const shortJob = track(frame, [[at(4, 0.3), [-6.4, 3.0, 0]], [at(4, 0.42), [-1.6, 3.0, 0]]]);
  const shortO = ip(frame, at(4, 0.3) - 4, 8) * (1 - prog(frame, at(4, 0.42), 8));

  const cam = camPath(frame, [
    [0, [0, 3, 22], [0, 0.2, 0]],
    [at(1, 0.5), [1, 2.5, 20], [1, 0.3, 0]],
    [at(3, 0.8), [1, 2, 20], [1, 0, 0]],
    [at(4, 0.3), [0, 3, 21], [0, 0.2, 0]],
    [at(4, 1) + 40, [0, 3.5, 22], [0, 0.2, 0]],
  ]);

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={-4.6}>
        {/* —— 第 1 句：就绪队列 + CPU + 指标 —— */}
        {[['P1', 8, 1.6], ['P2', 4, -0.1], ['P3', 2, -1.8]].map(([p, burst, y], k) => {
          const o = ip(frame, at(0, 0.12 + k * 0.1), 16) * g0;
          const w = (burst as number) * 0.55;
          return (
            <group key={p as string}>
              <Block position={[-7 + w / 2, y as number, 0]} size={[w, 1.2, 1.6]} color={C.panel2} edge={COLOR[p as string]} opacity={o} glow={2} />
              <Label text={`${p}  ${burst}`} position={[-7 + w / 2, y as number, 0.9]} size={0.4} bold mono opacity={o} depthTest={false} />
            </group>
          );
        })}
        <Label text="就绪队列" position={[-5.2, 3.0, 0]} size={0.4} color={C.muted} bold opacity={vis(frame, at(0, 0.15)) * g0} />
        <Block position={[6.5, -0.1, 0]} size={[3.0, 3.0, 2.6]} color="#3a1b3e" edge={C.pink} opacity={ip(frame, at(0, 0.3), 18) * g0} glow={2.4} emissive={0.4} />
        <Label text="CPU" position={[6.5, -0.1, 1.5]} size={0.6} bold mono opacity={ip(frame, at(0, 0.3), 18) * g0} depthTest={false} />
        <CurveArrow from={[-1.2, 0.4, 0.5]} to={[4.7, 0.2, 0.5]} bend={[0, 0.7, 0]} color={C.muted} radius={0.05} progress={ip(frame, at(0, 0.34), 22)} opacity={g0} />
        <Label text="选谁？" position={[1.6, 2.0, 0.5]} size={0.5} bold color={C.gold} opacity={vis(frame, at(0, 0.4)) * g0} />
        {['周转时间', '等待时间', '响应时间'].map((m, k) => (
          <Label key={m} text={m} position={[-4.4 + k * 4.4, 4.2, 0]} size={0.42} bold bg="#171433ee" border={[C.cyan, C.gold, C.pink][k]}
            opacity={vis(frame, at(0, 0.55 + k * 0.12), at(1, 0)) * g0} depthTest={false} />
        ))}

        {/* —— 甘特图 —— */}
        {row('fcfs', 'FCFS', ROW_Y.fcfs, FCFS, 1, '6.7')}
        {row('sjf', 'SJF', ROW_Y.sjf, SJF, 2, '2.7', 0.05)}
        {row('rr', 'RR q=2', ROW_Y.rr, RR, 3, '5.3', 0.08)}

        <GlassBox position={[X0 + 9 * U, ROW_Y.fcfs, 0]} size={[6.3 * U, 1.9, 2.4]} color={C.red} fill={0.07} opacity={vis(frame, at(1, 0.72), at(2, 0)) * g1} glow={1.4} />
        <Label text="护航效应：短作业干等" position={[X0 + 9 * U, ROW_Y.fcfs + 1.6, 0.5]} size={0.38} bold color={C.red} opacity={vis(frame, at(1, 0.72), at(2, 0)) * g1} />
        <Label text="长作业可能一直饿着" position={[X0 + 10 * U, ROW_Y.sjf + 1.3, 0.5]} size={0.38} bold color={C.red} opacity={vis(frame, at(2, 0.72), at(3, 0)) * g1} />
        {RR.slice(1).map(([, a], i) => (
          <Block key={i} position={[X0 + a * U, ROW_Y.rr, 0.1]} size={[0.07, BH + 0.5, 1.9]} color={C.gold} edge={C.gold} glow={2.4} emissive={0.8}
            opacity={ip(frame, at(3, 0.7 + i * 0.03), 8) * g1} />
        ))}
        <Label text="每次切换都有开销" position={[X0 + 5 * U, ROW_Y.rr - 1.55, 0.5]} size={0.36} bold color={C.gold} opacity={vis(frame, at(3, 0.72), at(4, 0)) * g1} />

        {/* —— 第 5 句：多级反馈队列 —— */}
        {LANE.map((l, k) => (
          <group key={l.y}>
            <GlassBox position={[0, l.y, 0]} size={[16, 1.9, 2.6]} color={l.c} fill={0.05} opacity={ip(frame, at(4, 0.03 + k * 0.04), 16) * g4} glow={1.2} />
            <Label text={l.t} position={[-4.8, l.y + 1.3, 1.4]} size={0.38} bold color={l.c} opacity={ip(frame, at(4, 0.05 + k * 0.04), 16) * g4} depthTest={false} />
          </group>
        ))}
        <Block position={long} size={[1.8, 1.0, 1.4]} color={C.panel2} edge={C.text} glow={2} opacity={ip(frame, at(4, 0.06), 10) * g4} />
        <Label text="长任务" position={[long[0], long[1], 0.9]} size={0.34} bold opacity={ip(frame, at(4, 0.06), 10) * g4} depthTest={false} />
        <Block position={shortJob} size={[1.4, 0.9, 1.2]} color={C.panel2} edge={C.gold} glow={2} opacity={shortO * g4} />
        <Label text="短任务" position={[shortJob[0], shortJob[1], 0.8]} size={0.32} bold opacity={shortO * g4} depthTest={false} />
        {frame >= at(4, 0.42) && frame < at(4, 0.42) + 26 && (
          <Ring position={[-1.6, 3.0, 0.6]} radius={ip(frame, at(4, 0.42), 24, easeOut) * 1.8} width={0.07} color={C.gold} opacity={1 - prog(frame, at(4, 0.42), 26)} />
        )}
        <Label text="用完时间片 ↓ 降级" position={[-3.6, 1.6, 1.6]} size={0.34} bold color={C.text} opacity={vis(frame, at(4, 0.34), at(4, 0.55)) * g4} depthTest={false} />
        <CurveArrow from={[6.2, -1.8, 1.2]} to={[6.2, 2.4, 1.2]} bend={[1.0, 0, 0]} color={C.cyan} radius={0.06} progress={ip(frame, at(4, 0.76), 24)} opacity={g4} />
        <Label text="老化：等太久，升级" position={[3.4, -1.25, 1.6]} size={0.36} bold color={C.cyan} opacity={vis(frame, at(4, 0.78)) * g4} depthTest={false} />
      </Stage>

      <Badge from={at(1, 0.9)} to={at(2, 0.0)} x={1848} y={170} align="right" color={C.red}>FCFS：简单，但有护航效应</Badge>
      <Badge from={at(2, 0.55)} to={at(3, 0.0)} x={1848} y={170} align="right" color={C.gold}>SJF：平均等待最短</Badge>
      <Badge from={at(3, 0.5)} to={at(4, 0.0)} x={1848} y={170} align="right" color={C.pink}>RR：响应快 · 公平</Badge>
      <Badge from={at(4, 0.1)} x={1848} y={170} align="right" color={C.cyan}>多级反馈队列 <Mono color={C.cyan}>MLFQ</Mono></Badge>
    </AbsoluteFill>
  );
};
