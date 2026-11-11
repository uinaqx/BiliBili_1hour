import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Block, CurveArrow, GlassBox, Label, Orb, Ring, Stage, V3} from '../three';
import {camPath, easeOut, ip, lerp, prog, pulse, track, useScene, vis} from '../anim';
import {C} from '../theme';
import {Badge, Mono} from '../ui';

const fly = (a: V3, b: V3, t: number): V3 => [lerp(a[0], b[0], t), lerp(a[1], b[1], t) + Math.sin(Math.PI * t) * 0.9, lerp(a[2], b[2], t) + Math.sin(Math.PI * t) * 0.8];
const CY = 0.5;
const POS_A: V3 = [-8.5, CY, 0], POS_B: V3 = [8.5, CY, 0];

export const SyncScene: React.FC = () => {
  const {frame, at, bd} = useScene();
  const t0 = (f: number) => at(0, f);
  const dur = (f: number) => bd(0) * f;

  const gA = 1 - prog(frame, at(4, 0) - 6, 16); // 第 1~4 句内容
  const g4 = vis(frame, at(4, 0.02), 1e9, 16); // 生产者消费者
  const gRace = 1 - prog(frame, at(2, 0) - 6, 16);

  // —— 第 1 句：竞态 ——
  const orbs: {p: V3; v: string; c: string}[] = [];
  const phases: [number, number, V3, V3, string, string][] = [
    [0.08, 0.2, [0, CY, 0], POS_A, '0', C.pink],
    [0.24, 0.36, [0, CY, 0], POS_B, '0', C.gold],
    [0.46, 0.58, POS_A, [0, CY, 0], '1', C.pink],
    [0.62, 0.74, POS_B, [0, CY, 0], '1', C.gold],
  ];
  for (const [a, b, from, to, v, c] of phases) {
    if (frame >= t0(a) && frame <= t0(b) + 6) orbs.push({p: fly(from, to, ip(frame, t0(a), dur(b - a))), v, c});
  }
  const counterVal = frame < t0(0.58) ? 0 : 1;
  const regA = frame < t0(0.2) ? '' : frame < t0(0.4) ? 'reg = 0' : 'reg = 1';
  const regB = frame < t0(0.36) ? '' : frame < t0(0.54) ? 'reg = 0' : 'reg = 1';
  const wrong = vis(frame, t0(0.8), at(2, 0), 14);

  // —— 第 3、4 句：临界区 / 锁 ——
  const posA = track(frame, [[0, POS_A], [at(2, 0.2), POS_A], [at(2, 0.4), [-3.3, CY, 0]], [at(3, 0.18), [-3.3, CY, 0]], [at(3, 0.32), [-8.5, CY, 0]]]);
  const posB = track(frame, [[0, POS_B], [at(2, 0.3), POS_B], [at(2, 0.45), [7.8, CY, 0]], [at(3, 0.44), [7.8, CY, 0]], [at(3, 0.56), [3.3, CY, 0]]]);
  const bWait = frame > at(2, 0.45) && frame < at(3, 0.42);
  const bShake = bWait ? Math.sin(frame * 1.4) * 0.07 : 0;
  const open = ip(frame, at(3, 0.34), 10) - ip(frame, at(3, 0.58), 10);
  const locked = frame < at(3, 0.3) || frame > at(3, 0.58);
  const inRoom = vis(frame, at(2, 0.02), at(4, 0), 16);
  const lockLabel = frame < at(3, 0.3) ? 'lock()' : frame < at(3, 0.58) ? 'unlock()' : 'lock()';

  // —— 信号量 ——
  const sT = (f: number) => at(3, f);
  const slots: V3[] = [[1.2, -3.6, 0], [2.8, -3.6, 0]];
  const home = (i: number) => slots[i];
  const away: V3 = [-3.2, -3.6, 0];
  const tok = (i: number): V3 => {
    const goT = i === 0 ? 0.68 : 0.78;
    const backT = i === 1 ? 0.93 : 9;
    return track(frame, [[sT(goT) - 1, home(i)], [sT(goT) + 6, away.map((v, k) => (k === 0 ? v - i * 1.2 : v)) as V3], [sT(backT), away.map((v, k) => (k === 0 ? v - i * 1.2 : v)) as V3], [sT(backT) + 12, home(i)]]);
  };
  const S = frame < sT(0.68) ? 2 : frame < sT(0.78) ? 1 : frame < sT(0.93) ? 0 : 1;
  const semO = vis(frame, sT(0.6), at(4, 0), 14);

  // —— 第 5 句：生产者消费者 ——
  const fill = [0.1, 0.17, 0.24, 0.31, 0.38];
  const drain = [0.56, 0.64, 0.72, 0.8, 0.88];
  const n = fill.filter((f) => frame >= at(4, f)).length - drain.filter((f) => frame >= at(4, f)).length;
  const slotX = (i: number) => -4 + i * 2;

  const cam = camPath(frame, [
    [0, [0, 3, 23], [0, 0.4, 0]],
    [at(1, 0.5), [0, 2.5, 19.5], [0, 0.4, 0]],
    [at(2, 0.4), [0, 3, 20], [0, 0.4, 0]],
    [at(3, 0.5), [0, 1.5, 20], [0, -0.7, 0]],
    [at(4, 0.2), [0, 3, 20], [0, 0.2, 0]],
    [at(4, 1) + 40, [0, 4, 21], [0, 0.2, 0]],
  ]);

  const thread = (name: string, p: V3, color: string, o: number, reg: string, warn = false) => (
    <group>
      <Block position={p} size={[3, 2, 2]} color={warn ? '#4a1620' : C.panel2} edge={warn ? C.red : color} opacity={o} glow={2} />
      <Label text={name} position={[p[0], p[1] + 0.2, p[2] + 1.15]} size={0.42} bold opacity={o} depthTest={false} />
      <Label text={reg} position={[p[0], p[1] - 1.5, p[2] + 0.6]} size={0.34} mono color={color} opacity={o} depthTest={false} />
    </group>
  );

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={-5}>
        {/* 共享计数器 */}
        <Block position={[0, CY, 0]} size={[2.8, 2.2, 2.2]} color={C.panel2} edge={C.cyan} opacity={ip(frame, 10, 20) * gA} glow={2.2} emissive={0.4} />
        <Label text={`counter = ${counterVal}`} position={[0, CY + 0.2, 1.2]} size={0.4} bold mono opacity={ip(frame, 14, 16) * gA} depthTest={false} />
        <Label text="共享数据" position={[0, CY + 1.9, 0]} size={0.34} color={C.cyan} opacity={ip(frame, 20, 16) * gA * gRace} />

        {/* 两个线程 */}
        {thread('线程 A', posA, C.pink, ip(frame, 14, 16) * gA, frame < at(2, 0) ? regA : '')}
        {thread('线程 B', [posB[0] + bShake, posB[1], posB[2]], C.gold, ip(frame, 18, 16) * gA, frame < at(2, 0) ? regB : '', bWait)}

        {orbs.map((o, i) => (
          <group key={i}>
            <Orb position={o.p} radius={0.34} color={o.c} glow={1.8} />
            <Label text={o.v} position={[o.p[0], o.p[1] + 0.75, o.p[2]]} size={0.4} bold mono depthTest={false} />
          </group>
        ))}
        {wrong > 0 && <Label text="结果 = 1   ✗  应该是 2" position={[0, 3.6, 0.5]} size={0.6} bold color={C.red} opacity={wrong * gRace} />}

        {/* 第 2 句：三步 */}
        {['① 读取', '② 计算 +1', '③ 写回'].map((s, k) => (
          <Label key={s} text={s} position={[-4.6 + k * 4.6, -2.7, 0.6]} size={0.42} bold bg="#171433ee" border={[C.cyan, C.gold, C.pink][k]}
            opacity={vis(frame, at(1, 0.1 + k * 0.16), at(2, 0)) * gA} depthTest={false} />
        ))}
        <Label text="交错执行 → 更新丢失" position={[0, 3.6, 0.5]} size={0.5} bold color={C.red} opacity={vis(frame, at(1, 0.62), at(2, 0)) * gA} />

        {/* 第 3 句：临界区 */}
        <GlassBox position={[0, CY, 0]} size={[10, 4.4, 4.4]} color={C.cyan} fill={0.05} opacity={inRoom} glow={1.4} />
        <Label text="临界区" position={[-3.3, CY + 2.9, 0]} size={0.5} bold color={C.cyan} opacity={inRoom} />
        <Label text="任何时刻最多一个线程" position={[3.0, CY + 2.9, 0]} size={0.38} bold color={C.gold} opacity={vis(frame, at(2, 0.55), at(3, 0)) * gA} />
        <Label text="等待" position={[7.8, CY + 1.7, 0.5]} size={0.4} bold color={C.red} opacity={vis(frame, at(2, 0.5), at(3, 0.42)) * gA} />

        {/* 第 4 句：锁 */}
        <Block position={[5.0, CY, 0]} size={[0.3, 3.8, 4.2]} color={C.gold} edge={locked ? C.red : C.cyan} opacity={vis(frame, at(2, 0.6), at(4, 0)) * (1 - open * 0.92) * gA} glow={2.2} emissive={0.5} />
        <Label text={lockLabel} position={[0, CY + 3.7, 0.5]} size={0.6} bold mono color={lockLabel === 'unlock()' ? C.cyan : C.gold}
          opacity={vis(frame, at(3, 0.03), at(3, 0.64), 10) * gA} />
        {frame >= at(3, 0.3) && frame < at(3, 0.3) + 24 && (
          <Ring position={[5.0, CY, 0]} radius={ip(frame, at(3, 0.3), 22, easeOut) * 2.2} width={0.07} color={C.cyan} opacity={1 - prog(frame, at(3, 0.3), 24)} rotation={[0, Math.PI / 2, 0]} />
        )}

        {/* 信号量 */}
        <Block position={[2.0, -3.9, 0]} size={[4.2, 0.2, 2]} color={C.panel2} edge={C.gold} opacity={semO * gA} glow={1.6} />
        <Label text={`信号量  S = ${S}`} position={[2.0, -2.5, 0.6]} size={0.46} bold mono color={C.gold} opacity={semO * gA} />
        <Block position={[away[0] - 0.6, -3.6, 0]} size={[3.2, 1.0, 1.6]} color={C.panel2} edge={C.pink} opacity={semO * gA} glow={1.8} />
        <Label text="进程" position={[away[0] - 0.6, -3.6, 0.9]} size={0.34} bold opacity={semO * gA} depthTest={false} />
        {[0, 1].map((i) => <Orb key={i} position={tok(i)} radius={0.36} color={C.gold} glow={1.8} opacity={semO * gA} />)}
        <Label text="P：申请" position={[-1.0, -2.6, 0.6]} size={0.36} bold color={C.pink} opacity={vis(frame, sT(0.66), sT(0.86)) * semO * gA} />
        <Label text="P：没有了 → 阻塞" position={[-1.0, -2.6, 0.6]} size={0.36} bold color={C.red} opacity={vis(frame, sT(0.86), sT(0.92)) * semO * gA} />
        <Label text="V：释放" position={[-1.0, -2.6, 0.6]} size={0.36} bold color={C.cyan} opacity={vis(frame, sT(0.92), at(4, 0)) * semO * gA} />

        {/* —— 第 5 句：生产者 / 消费者 —— */}
        {[1.4, -1.4].map((y, k) => (
          <group key={y}>
            <Block position={[-9, y, 0]} size={[2.8, 1.5, 1.8]} color={C.panel2} edge={C.pink} opacity={ip(frame, at(4, 0.04 + k * 0.03), 16) * g4}
              glow={2} />
            <Label text="生产者" position={[-9, y, 1.0]} size={0.38} bold opacity={ip(frame, at(4, 0.04), 16) * g4} depthTest={false} />
          </group>
        ))}
        {[1.4, -1.4].map((y, k) => (
          <group key={y}>
            <Block position={[9, y, 0]} size={[2.8, 1.5, 1.8]} color={C.panel2} edge={C.cyan} opacity={ip(frame, at(4, 0.06 + k * 0.03), 16) * g4}
              glow={2} />
            <Label text="消费者" position={[9, y, 1.0]} size={0.38} bold opacity={ip(frame, at(4, 0.06), 16) * g4} depthTest={false} />
          </group>
        ))}
        {[0, 1, 2, 3, 4].map((i) => {
          const f0 = at(4, fill[i]), d0 = at(4, drain[i]);
          const inT = ip(frame, f0, 14, easeOut), outT = ip(frame, d0, 14);
          const has = frame >= f0 && frame < d0 + 14;
          const x = frame < d0 ? lerp(-8.4, slotX(i), inT) : lerp(slotX(i), 8.4, outT);
          return (
            <group key={i}>
              <Block position={[slotX(i), 0, 0]} size={[1.7, 1.7, 1.7]} color={C.panel} edge={C.muted} opacity={ip(frame, at(4, 0.08 + i * 0.02), 14) * g4} glow={1.2} />
              {has && <Orb position={[x, 0, 0.2]} radius={0.62} color={[C.cyan, C.pink, C.gold, C.violet, C.cyan][i]} glow={1.6} opacity={g4} />}
            </group>
          );
        })}
        <Label text="缓冲区" position={[0, -1.7, 0.6]} size={0.4} bold color={C.muted} opacity={ip(frame, at(4, 0.1), 14) * g4} />
        {[['empty', 5 - n, C.cyan, -5], ['full', n, C.pink, 0], ['mutex', 1, C.gold, 5]].map(([nm, v, c, x]) => (
          <Label key={nm as string} text={`${nm} = ${v}`} position={[x as number, 3.0, 0.4]} size={0.46} bold mono bg="#171433ee" border={c as string}
            opacity={ip(frame, at(4, 0.12), 14) * g4} depthTest={false} />
        ))}
        <Label text="已满 → 生产者阻塞" position={[-6.0, -3.0, 0.6]} size={0.4} bold color={C.red} opacity={vis(frame, at(4, 0.43), at(4, 0.58)) * g4} />
        <Label text="已空 → 消费者阻塞" position={[6.0, -3.0, 0.6]} size={0.4} bold color={C.red} opacity={vis(frame, at(4, 0.92), 1e9) * g4} />
        <Ring position={[0, 0, 0.5]} radius={3 + pulse(frame, at(4, 0.4), 30) * 1} width={0.06} color={C.red} opacity={pulse(frame, at(4, 0.4), 30) * 0.6 * g4} rotation={[0, 0, 0]} />
      </Stage>

      <Badge from={at(0, 0.8)} to={at(2, 0)} x={1848} y={170} align="right" color={C.red}>竞态条件 <Mono color={C.red}>Race Condition</Mono></Badge>
      <Badge from={at(2, 0.6)} to={at(3, 0)} x={1848} y={170} align="right" color={C.cyan}>互斥 <Mono>Mutual Exclusion</Mono></Badge>
      <Badge from={at(3, 0.1)} to={at(4, 0)} x={1848} y={170} align="right" color={C.gold}>互斥锁 · 信号量 <Mono color={C.gold}>P / V</Mono></Badge>
      <Badge from={at(4, 0.1)} x={1848} y={170} align="right" color={C.pink}>生产者—消费者</Badge>
    </AbsoluteFill>
  );
};
