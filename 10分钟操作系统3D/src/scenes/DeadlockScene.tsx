import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Block, CurveArrow, Label, Orb, PolyTube, Ring, Stage, V3} from '../three';
import {camPath, easeOut, ip, lerp, prog, pulse, useScene, vis} from '../anim';
import {C} from '../theme';
import {Badge, Mono} from '../ui';

const R1: V3 = [-4.5, 2.0, 0], P1: V3 = [4.5, 2.0, 0], R2: V3 = [4.5, -2.0, 0], P2: V3 = [-4.5, -2.0, 0];
const CONDITIONS = [
  {t: '互斥', s: '资源一次只给一个进程', c: C.cyan},
  {t: '占有并等待', s: '拿着一个，还想要另一个', c: C.gold},
  {t: '不可抢占', s: '不能强行夺走别人的资源', c: C.pink},
  {t: '循环等待', s: '首尾相接，形成一个环', c: C.red},
];
const BANK = [
  {p: 'P1', alloc: 5, need: 5, done: 0.52},
  {p: 'P2', alloc: 2, need: 2, done: 0.38},
  {p: 'P3', alloc: 2, need: 7, done: 0.66},
];
const BW = 0.72;

export const DeadlockScene: React.FC = () => {
  const {frame, at, bd} = useScene();

  const g0 = vis(frame, 0, at(1, 0) - 4, 14);
  const g1 = vis(frame, at(1, 0.0), at(2, 0) - 4, 14);
  const g2 = vis(frame, at(2, 0.0), at(4, 0) - 4, 14);
  const g4 = vis(frame, at(4, 0.0), 1e9, 14);

  // —— 第 1 句：窄桥 ——
  const meet = ip(frame, at(0, 0.1), bd(0) * 0.45);
  const carL = lerp(-10, -2.0, meet), carR = lerp(10, 2.0, meet);
  const crash = pulse(frame, at(0, 0.58), 30);
  const stuck = frame > at(0, 0.58);

  // —— 第 3、4 句：资源分配图 ——
  const e1 = ip(frame, at(2, 0.1), 20);
  const e2 = ip(frame, at(2, 0.26), 20);
  const e3 = ip(frame, at(2, 0.42), 20);
  const e4 = ip(frame, at(2, 0.58), 20);
  const loop = ip(frame, at(2, 0.72), 26);
  const fixed = ip(frame, at(3, 0.2), 14); // 建立顺序后：R2→P2 消失，P1→R2 变成持有
  const noLoop = 1 - ip(frame, at(3, 0.08), 12);

  // —— 银行家算法 ——
  const avail = frame < at(4, 0.38) ? 3 : frame < at(4, 0.52) ? 5 : 10;
  const availShown = frame < at(4, 0.66) ? avail : 10 + 2;

  const cam = camPath(frame, [
    [0, [0, 3, 22], [0, 0, 0]],
    [at(0, 0.9), [4, 2.5, 19], [0, 0, 0]],
    [at(1, 0.5), [0, 2.5, 22], [0, 0.6, 0]],
    [at(2, 0.3), [0, 3, 22], [0, 0, 0]],
    [at(3, 0.6), [3, 2.5, 22], [0, 0, 0]],
    [at(4, 0.2), [0, 3, 22], [0, 0.4, 0]],
    [at(4, 1) + 40, [-3, 3.5, 23], [0, 0.4, 0]],
  ]);

  const Car = ({x, color, dir}: {x: number; color: string; dir: number}) => (
    <group>
      <Block position={[x, -0.4, 0]} size={[3.4, 1.2, 1.7]} color={stuck ? '#4a1620' : C.panel2} edge={stuck ? C.red : color} glow={2.2} opacity={g0} />
      <Block position={[x - dir * 0.2, 0.35, 0]} size={[1.8, 0.7, 1.5]} color={C.panel} edge={stuck ? C.red : color} glow={1.6} opacity={g0} />
      <Orb position={[x + dir * 1.75, -0.4, 0.4]} radius={0.16} color={C.gold} glow={2} opacity={g0} />
      <Orb position={[x + dir * 1.75, -0.4, -0.4]} radius={0.16} color={C.gold} glow={2} opacity={g0} />
    </group>
  );

  const edge = (from: V3, to: V3, color: string, progress: number, opacity: number, bend: V3 = [0, 0, 0]) => (
    <CurveArrow from={from} to={to} bend={bend} color={color} radius={0.06} progress={progress} opacity={opacity} trimStart={1.3} trimEnd={1.45} />
  );
  const E = g2;

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={-5}>
        {/* —— 窄桥 —— */}
        <Block position={[0, -1.4, 0]} size={[22, 0.4, 2.4]} color={C.panel} edge={C.muted} opacity={ip(frame, 6, 20) * g0} glow={1.3} />
        <Block position={[-10.8, -1.7, 0]} size={[2.6, 1.0, 3.6]} color={C.panel} edge={C.violet} opacity={ip(frame, 6, 20) * g0} glow={1.2} />
        <Block position={[10.8, -1.7, 0]} size={[2.6, 1.0, 3.6]} color={C.panel} edge={C.violet} opacity={ip(frame, 6, 20) * g0} glow={1.2} />
        <Car x={carL} color={C.pink} dir={1} />
        <Car x={carR} color={C.cyan} dir={-1} />
        <Label text="你先退" position={[carL, 1.9, 0.6]} size={0.42} bold color={C.pink} opacity={vis(frame, at(0, 0.6), at(1, 0)) * g0} />
        <Label text="你先退" position={[carR, 1.9, 0.6]} size={0.42} bold color={C.cyan} opacity={vis(frame, at(0, 0.6), at(1, 0)) * g0} />
        <Label text="互相等待，谁也走不了" position={[0, 3.6, 0]} size={0.6} bold color={C.red} opacity={vis(frame, at(0, 0.72), at(1, 0)) * g0} />
        {crash > 0 && <Ring position={[0, -0.4, 0.5]} radius={1 + ip(frame, at(0, 0.58), 28, easeOut) * 3} width={0.09} color={C.red} opacity={crash} />}

        {/* —— 四个必要条件 —— */}
        {CONDITIONS.map((c, k) => {
          const o = ip(frame, at(1, 0.06 + k * 0.17), 16) * g1;
          const broken = k === 3 ? ip(frame, at(1, 0.82), 12) : 0;
          const x = -7.8 + k * 5.2;
          return (
            <group key={c.t}>
              <Block position={[x, 0.6 - broken * 0.6, 0]} size={[4.4, 3.4, 1.3]} color={broken ? '#2b1020' : C.panel2} edge={c.c} opacity={o * (1 - broken * 0.55)} glow={2}
                emissive={0.3} rotation={[0, 0, broken * 0.18]} />
              <Label text={`${k + 1}`} position={[x, 1.8, 0.8]} size={0.5} bold mono color={c.c} opacity={o} depthTest={false} />
              <Label text={c.t} position={[x, 0.7, 0.8]} size={0.5} bold opacity={o} depthTest={false} />
              <Label text={c.s} position={[x, -0.4, 0.8]} size={0.26} color={C.muted} opacity={o} depthTest={false} />
            </group>
          );
        })}
        <Label text="四个条件同时满足  →  死锁" position={[0, 3.6, 0]} size={0.5} bold color={C.red} opacity={vis(frame, at(1, 0.66), at(1, 0.8)) * g1} />
        <Label text="破坏任意一个  →  死锁不会发生" position={[0, 3.6, 0]} size={0.5} bold color={C.cyan} opacity={vis(frame, at(1, 0.82), at(2, 0)) * g1} />

        {/* —— 资源分配图 —— */}
        {[['R1', R1], ['R2', R2]].map(([n, p]) => (
          <group key={n as string}>
            <Block position={p as V3} size={[1.9, 1.9, 1.9]} color={C.panel2} edge={C.gold} glow={2.2} opacity={ip(frame, 10, 20) * E} />
            <Label text={n as string} position={[(p as V3)[0], (p as V3)[1], 1.1]} size={0.6} bold mono opacity={ip(frame, 14, 16) * E} depthTest={false} />
          </group>
        ))}
        {[['P1', P1], ['P2', P2]].map(([n, p]) => (
          <group key={n as string}>
            <Orb position={p as V3} radius={1.0} color={C.cyan} glow={1.2} opacity={0.92 * ip(frame, 14, 20) * E} scale={ip(frame, 14, 20, easeOut)} />
            <Label text={n as string} position={[(p as V3)[0], (p as V3)[1], 1.2]} size={0.6} bold mono opacity={ip(frame, 18, 16) * E} depthTest={false} />
          </group>
        ))}
        {edge(R1, P1, C.gold, e1, E)}
        {edge(P1, R2, C.cyan, e2, E * (1 - fixed))}
        {edge(R2, P2, C.gold, e3, E * (1 - fixed))}
        {edge(P2, R1, C.cyan, e4, E)}
        {edge(R2, P1, C.gold, fixed, E, [0.6, 0, 0])}
        {loop > 0.01 && <PolyTube points={[[-4.5, 2.0, -0.6], [4.5, 2.0, -0.6], [4.5, -2.0, -0.6], [-4.5, -2.0, -0.6], [-4.5, 2.0, -0.6]]} progress={Math.min(0.999, loop)}
          color={C.red} radius={0.045} opacity={noLoop * E * 0.9} />}
        <Label text="环  =  死锁" position={[0, 0, 0.6]} size={0.8} bold color={C.red} opacity={vis(frame, at(2, 0.84), at(3, 0.08)) * E} />
        <Label text="资源 → 进程：持有" position={[-4.4, -4.2, 0]} size={0.34} color={C.gold} opacity={vis(frame, at(2, 0.1)) * E} />
        <Label text="进程 → 资源：申请" position={[4.4, -4.2, 0]} size={0.34} color={C.cyan} opacity={vis(frame, at(2, 0.1)) * E} />
        <Label text="编号 1" position={[R1[0], R1[1] + 1.5, 0]} size={0.34} bold color={C.gold} opacity={vis(frame, at(3, 0.1)) * E} />
        <Label text="编号 2" position={[R2[0], R2[1] - 1.5, 0]} size={0.34} bold color={C.gold} opacity={vis(frame, at(3, 0.1)) * E} />
        <Label text="都按 1 → 2 的顺序申请，不再成环 ✓" position={[0, 3.9, 0.6]} size={0.5} bold color={C.cyan} opacity={vis(frame, at(3, 0.45)) * E} />

        {/* —— 银行家算法 —— */}
        <Label text={`可用  ${availShown}`} position={[6.2, 3.2, 0.3]} size={0.6} bold mono color={C.gold} opacity={ip(frame, at(4, 0.06), 14) * g4} />
        {Array.from({length: 12}, (_, i) => {
          const show = i < availShown;
          return <Block key={i} position={[3.6 + (i % 6) * 0.95, 1.8 - Math.floor(i / 6) * 0.95, 0]} size={[0.7, 0.7, 0.7]} color={C.panel2} edge={C.gold}
            opacity={(show ? ip(frame, at(4, 0.06), 14) : 0) * g4} glow={2} emissive={0.5} />;
        })}
        {BANK.map((r, k) => {
          const y = 2.4 - k * 2.0;
          const done = ip(frame, at(4, r.done), 14);
          const o = ip(frame, at(4, 0.04 + k * 0.05), 16) * g4 * (1 - done);
          const test = pulse(frame, at(4, r.done - 0.1), bd(4) * 0.1);
          return (
            <group key={r.p}>
              <Label text={r.p} position={[-8.6, y, 0.5]} size={0.5} bold mono opacity={o} depthTest={false} />
              <Block position={[-7.4 + (r.alloc * BW) / 2, y, 0]} size={[r.alloc * BW - 0.06, 1.0, 1.4]} color={C.panel2} edge={C.cyan} opacity={o} glow={2 + test} emissive={0.4} />
              <Block position={[-7.4 + r.alloc * BW + (r.need * BW) / 2, y, 0]} size={[r.need * BW - 0.06, 1.0, 1.4]} color={C.panel} edge={C.pink} opacity={o * 0.8} glow={1.6 + test} />
              <Label text={`已分配 ${r.alloc}`} position={[-7.4 + (r.alloc * BW) / 2, y, 0.8]} size={0.28} bold opacity={o} depthTest={false} />
              <Label text={`还需 ${r.need}`} position={[-7.4 + r.alloc * BW + (r.need * BW) / 2, y, 0.8]} size={0.28} bold color={C.pink} opacity={o} depthTest={false} />
              {done > 0 && done < 1 && <Ring position={[-7.4 + (r.alloc * BW), y, 0.8]} radius={0.5 + done * 2} width={0.07} color={C.cyan} opacity={1 - done} />}
            </group>
          );
        })}
        <Label text="安全序列  P2 → P1 → P3  ✓" position={[-1.0, -3.2, 0.5]} size={0.6} bold color={C.cyan} opacity={vis(frame, at(4, 0.7), at(4, 0.84)) * g4} />
        <Label text="已发生？检测出环 → 撤销一个进程" position={[-1.0, -3.2, 0.5]} size={0.5} bold color={C.red} opacity={vis(frame, at(4, 0.86), 1e9) * g4} />
      </Stage>

      <Badge from={at(1, 0.9)} to={at(2, 0)} x={1848} y={170} align="right" color={C.red}>四条件缺一不可</Badge>
      <Badge from={at(3, 0.05)} to={at(4, 0)} x={1848} y={170} align="right" color={C.cyan}>预防：破坏循环等待</Badge>
      <Badge from={at(4, 0.1)} to={at(4, 0.8)} x={1848} y={170} align="right" color={C.gold}>避免：银行家算法</Badge>
      <Badge from={at(4, 0.84)} x={1848} y={170} align="right" color={C.red}>检测 + 恢复</Badge>
    </AbsoluteFill>
  );
};
