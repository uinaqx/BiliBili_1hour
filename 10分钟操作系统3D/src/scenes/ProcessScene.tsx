import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Block, CurveArrow, GlassBox, Label, Orb, Ring, Stage, V3} from '../three';
import {camPath, easeOut, ip, prog, track, useScene, vis} from '../anim';
import {C} from '../theme';
import {Badge, Mono} from '../ui';

const LAYERS = [
  {name: '代码 Text', y: -1.9, color: C.violet},
  {name: '数据 Data', y: -0.5, color: C.gold},
  {name: '堆 Heap', y: 0.9, color: C.pink},
  {name: '栈 Stack', y: 2.3, color: C.cyan},
];
const PCB_FIELDS = ['PID   1024', '状态   RUNNING', 'PC · SP · 寄存器', '打开文件   0 1 2 …', '页表基址   0x7F00'];

const NEW: V3 = [-9.5, 1.6, 0], READY: V3 = [-3.2, 1.6, 0], RUN: V3 = [3.2, 1.6, 0], TERM: V3 = [9.5, 1.6, 0], BLOCK: V3 = [0, -3.2, 0];
const NODES: {n: string; en: string; p: V3; color: string; at: number}[] = [
  {n: '新建', en: 'New', p: NEW, color: C.muted, at: 0.1},
  {n: '就绪', en: 'Ready', p: READY, color: C.gold, at: 0.28},
  {n: '运行', en: 'Running', p: RUN, color: C.cyan, at: 0.46},
  {n: '阻塞', en: 'Blocked', p: BLOCK, color: C.pink, at: 0.64},
  {n: '终止', en: 'Exit', p: TERM, color: C.red, at: 0.8},
];

export const ProcessScene: React.FC = () => {
  const {frame, at, bd} = useScene();

  const g1 = 1 - prog(frame, at(2, 0) - 6, 16); // 第 1~2 句内容
  const g2 = vis(frame, at(2, 0.02), at(4, 0), 16); // 状态机
  const g3 = vis(frame, at(4, 0.02), 1e9, 16); // 线程

  const token = track(frame, [
    [at(2, 0.82), NEW],
    [at(2, 0.96), READY],
    [at(3, 0.02), READY],
    [at(3, 0.18), RUN],
    [at(3, 0.26), RUN],
    [at(3, 0.44), READY],
    [at(3, 0.5), READY],
    [at(3, 0.56), RUN],
    [at(3, 0.62), RUN],
    [at(3, 0.74), BLOCK],
    [at(3, 0.82), BLOCK],
    [at(3, 0.96), READY],
  ]);
  const tokenO = vis(frame, at(2, 0.8), at(4, 0), 10);

  const cam = camPath(frame, [
    [0, [3, 4, 26], [0, 0, 0]],
    [at(0, 0.9), [-3, 3, 22], [-2, 0.2, 0]],
    [at(1, 0.6), [4, 3, 22], [2, 0.2, 0]],
    [at(2, 0.3), [0, 3, 24], [0, -0.3, 0]],
    [at(3, 0.5), [1, 2.5, 22], [0, -0.3, 0]],
    [at(4, 0.2), [-5, 3, 22], [0, 0, 0]],
    [at(4, 1) + 40, [4, 4, 23], [0, 0, 0]],
  ]);

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={-5}>
        {/* —— 第 1 句：程序 → 进程 —— */}
        <Block position={[-9, 0.2, 0]} size={[2.8, 3.6, 0.5]} color={C.panel2} edge={C.muted} opacity={ip(frame, at(0, 0.05), 20) * g1} />
        <Label text="程序" position={[-9, 0.7, 0.5]} size={0.5} bold opacity={ip(frame, at(0, 0.1), 16) * g1} depthTest={false} />
        <Label text="硬盘上的代码" position={[-9, -0.3, 0.5]} size={0.3} color={C.muted} opacity={ip(frame, at(0, 0.1), 16) * g1} depthTest={false} />
        <CurveArrow from={[-7.4, 0.4, 0.5]} to={[-4.8, 0.4, 0.5]} color={C.cyan} radius={0.06} progress={ip(frame, at(0, 0.25), 24)} opacity={g1} />
        <Label text="运行" position={[-6.1, 1.1, 0.5]} size={0.36} color={C.cyan} opacity={vis(frame, at(0, 0.3)) * g1} />

        <GlassBox position={[-1.6, 0.2, 0]} size={[5.4, 6.4, 3.6]} color={C.cyan} fill={0.04} opacity={ip(frame, at(0, 0.3), 24) * g1} glow={1.1} />
        {LAYERS.map((l, k) => {
          const o = ip(frame, at(0, 0.38 + k * 0.1), 16) * g1;
          return (
            <group key={l.name}>
              <Block position={[-1.6, l.y, 0]} size={[4.6, 1.0, 2.8]} color={C.panel2} edge={l.color} opacity={o} glow={1.9} scale={0.9 + 0.1 * o} />
              <Label text={l.name} position={[-1.6, l.y, 1.5]} size={0.4} bold mono opacity={o} depthTest={false} />
            </group>
          );
        })}
        <Label text="独立的地址空间" position={[-1.6, 4.2, 0]} size={0.44} bold color={C.cyan} opacity={vis(frame, at(0, 0.7)) * g1} />
        <Label text="高地址" position={[1.9, 2.3, 1.5]} size={0.28} color={C.muted} opacity={vis(frame, at(0, 0.8)) * g1} />
        <Label text="低地址" position={[1.9, -1.9, 1.5]} size={0.28} color={C.muted} opacity={vis(frame, at(0, 0.8)) * g1} />

        {/* —— 第 2 句：PCB —— */}
        <CurveArrow from={[1.4, 0.3, 0.8]} to={[3.7, 0.3, 0.8]} color={C.pink} radius={0.06} progress={ip(frame, at(1, 0.05), 20)} opacity={g1} />
        <Block position={[6.6, 0.2, 0]} size={[5.4, 5.6, 0.5]} color="#2a1a40" edge={C.pink} opacity={ip(frame, at(1, 0.05), 20) * g1} glow={2} emissive={0.3} />
        <Label text="PCB  进程控制块" position={[6.6, 3.4, 0.4]} size={0.46} bold mono color={C.pink} opacity={ip(frame, at(1, 0.1), 16) * g1} />
        {PCB_FIELDS.map((f, k) => (
          <Label key={f} text={f} position={[6.6, 1.8 - k * 1.0, 0.45]} size={0.36} mono bold={k === 1}
            color={k === 1 ? C.cyan : C.text} opacity={ip(frame, at(1, 0.18 + k * 0.13), 14) * g1} depthTest={false} />
        ))}

        {/* —— 第 3、4 句：五态模型 —— */}
        {NODES.map((n) => {
          const o = ip(frame, at(2, n.at), 16) * g2;
          const hot = Math.max(0, 1 - Math.hypot(token[0] - n.p[0], token[1] - n.p[1]) / 1.8) * tokenO;
          return (
            <group key={n.n}>
              <Orb position={n.p} radius={0.95} color={n.color} glow={1.1 + hot} opacity={0.92 * o} scale={o * (1 + hot * 0.12)} />
              <Label text={n.n} position={[n.p[0], n.p[1], n.p[2] + 1.1]} size={0.5} bold color={C.bg} glow={1} opacity={o} depthTest={false} />
              <Label text={n.en} position={[n.p[0], n.p[1] - 1.55, n.p[2]]} size={0.3} mono color={n.color} opacity={o} />
            </group>
          );
        })}
        <Label text="只欠 CPU" position={[READY[0], READY[1] + 1.6, 0]} size={0.34} color={C.gold} opacity={vis(frame, at(2, 0.55), at(3, 0)) * g2} />
        <Label text="等待 I/O 或事件" position={[BLOCK[0], BLOCK[1] - 1.9, 0]} size={0.34} color={C.pink} opacity={vis(frame, at(2, 0.7), at(3, 0)) * g2} />

        <CurveArrow from={[-8.4, 1.6, 0]} to={[-4.3, 1.6, 0]} color={C.muted} radius={0.045} progress={ip(frame, at(2, 0.72), 20)} opacity={g2} />
        <CurveArrow from={[-2.1, 1.0, 0]} to={[2.1, 1.0, 0]} bend={[0, -0.7, 0]} color={C.gold} radius={0.05} progress={ip(frame, at(3, 0.03), 20)} opacity={g2} />
        <CurveArrow from={[2.1, 2.3, 0]} to={[-2.1, 2.3, 0]} bend={[0, 0.8, 0]} color={C.cyan} radius={0.05} progress={ip(frame, at(3, 0.27), 20)} opacity={g2} />
        <CurveArrow from={[3.5, 0.6, 0]} to={[1.0, -2.3, 0]} bend={[0.4, -0.2, 0]} color={C.pink} radius={0.05} progress={ip(frame, at(3, 0.56), 20)} opacity={g2} />
        <CurveArrow from={[-1.0, -2.3, 0]} to={[-3.5, 0.6, 0]} bend={[-0.2, -0.2, 0]} color={C.pink} radius={0.05} progress={ip(frame, at(3, 0.76), 20)} opacity={g2} />
        <CurveArrow from={[4.3, 1.6, 0]} to={[8.5, 1.6, 0]} color={C.red} radius={0.045} progress={ip(frame, at(2, 0.84), 20)} opacity={g2} />

        <Label text="调度" position={[0, -0.4, 0.5]} size={0.4} bold color={C.gold} opacity={vis(frame, at(3, 0.05)) * g2} />
        <Label text="时间片用完" position={[0, 3.6, 0.5]} size={0.4} bold color={C.cyan} opacity={vis(frame, at(3, 0.28)) * g2} />
        <Label text="等待 I/O" position={[3.8, -1.7, 0.5]} size={0.4} bold color={C.pink} opacity={vis(frame, at(3, 0.58)) * g2} />
        <Label text="I/O 完成" position={[-3.8, -1.7, 0.5]} size={0.4} bold color={C.pink} opacity={vis(frame, at(3, 0.78)) * g2} />
        <Label text="退出" position={[6.4, 2.4, 0.5]} size={0.36} color={C.red} opacity={vis(frame, at(2, 0.88)) * g2} />

        <Orb position={token} radius={0.34} color={C.text} glow={2} opacity={tokenO} />
        {frame >= at(3, 0.18) && frame < at(3, 0.18) + 24 && (
          <Ring position={RUN} radius={1 + ip(frame, at(3, 0.18), 22, easeOut) * 1.6} width={0.07} color={C.cyan} opacity={1 - prog(frame, at(3, 0.18), 24)} />
        )}

        {/* —— 第 5 句：线程 —— */}
        <GlassBox position={[0, 0, 0]} size={[16.5, 6.4, 4.2]} color={C.cyan} fill={0.04} opacity={ip(frame, at(4, 0.04), 24) * g3} glow={1.1} />
        <Label text="进程" position={[-6.8, 3.6, 2.2]} size={0.42} bold color={C.cyan} opacity={g3 * ip(frame, at(4, 0.06), 12)} />
        {['代码', '数据', '堆 · 文件'].map((n, k) => (
          <group key={n}>
            <Block position={[-4.6, 1.6 - k * 1.5, 0]} size={[4.0, 1.1, 2.6]} color={C.panel2} edge={C.gold} opacity={ip(frame, at(4, 0.12 + k * 0.06), 14) * g3} glow={1.8} />
            <Label text={n} position={[-4.6, 1.6 - k * 1.5, 1.4]} size={0.38} bold opacity={ip(frame, at(4, 0.12 + k * 0.06), 14) * g3} depthTest={false} />
          </group>
        ))}
        <Label text="共享" position={[-4.6, 3.2, 1.4]} size={0.4} bold color={C.gold} opacity={vis(frame, at(4, 0.2)) * g3} />
        {[0, 1, 2].map((k) => {
          const t = at(4, 0.34 + k * 0.1);
          const o = ip(frame, t, 16) * g3;
          const x = 1.2 + k * 2.9;
          return (
            <group key={k}>
              <Orb position={[x, 2.4, 0]} radius={0.5} color={C.pink} opacity={o} scale={o} />
              <Label text={`线程 ${k + 1}`} position={[x, 3.3, 0]} size={0.34} bold opacity={o} />
              <Block position={[x, 0.9, 0]} size={[2.2, 1.1, 2.4]} color={C.panel2} edge={C.pink} opacity={o} glow={1.8} />
              <Label text="栈" position={[x, 0.9, 1.3]} size={0.36} bold opacity={o} depthTest={false} />
              <Block position={[x, -0.5, 0]} size={[2.2, 1.1, 2.4]} color={C.panel2} edge={C.pink} opacity={o} glow={1.8} />
              <Label text="寄存器" position={[x, -0.5, 1.3]} size={0.34} bold opacity={o} depthTest={false} />
              <CurveArrow from={[x - 1.0, 2.2, 0]} to={[-2.4, 1.9, 0]} bend={[0, 1.4, 0]} color={C.gold} radius={0.03} progress={ip(frame, t + 10, 24)} opacity={g3 * 0.8} />
            </group>
          );
        })}
        <Label text="私有：栈 + 寄存器" position={[4.1, -2.1, 0]} size={0.38} bold color={C.pink} opacity={vis(frame, at(4, 0.6)) * g3} />
      </Stage>

      <Badge from={at(0, 0.7)} to={at(2, 0)} x={1848} y={170} align="right">程序 ≠ 进程</Badge>
      <Badge from={at(1, 0.7)} to={at(2, 0)} x={1848} y={240} align="right" color={C.pink}><Mono color={C.pink}>PCB</Mono> = 进程的身份证</Badge>
      <Badge from={at(3, 0.1)} to={at(4, 0)} x={1848} y={170} align="right" color={C.gold}>五态模型</Badge>
      <Badge from={at(4, 0.5)} x={1848} y={170} align="right" color={C.cyan}>线程：更轻量</Badge>
    </AbsoluteFill>
  );
};
