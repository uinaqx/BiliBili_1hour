import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Block, CurveArrow, Label, Orb, PolyTube, Ring, Stage, V3} from '../three';
import {camPath, easeOut, ip, lerp, prog, pulse, track, useScene, vis} from '../anim';
import {C} from '../theme';
import {Badge, Mono} from '../ui';

const LX = (t: number) => -7 + t * 1.1; // 时间轴：1 个单位 = 1.1
const FCFS = [53, 98, 183, 37, 122, 14, 124, 65, 67];
const SCAN = [53, 65, 67, 98, 122, 124, 183, 37, 14];
const trackX = (cx: number, t: number) => cx - 3.4 + (t / 199) * 6.8;
const stepY = (i: number) => 2.4 - i * 0.62;

export const IoScene: React.FC = () => {
  const {frame, at, bd} = useScene();

  const g0 = vis(frame, 0, at(1, 0) - 4, 14);
  const g1 = vis(frame, at(1, 0.0), at(2, 0) - 4, 14);
  const g2 = vis(frame, at(2, 0.0), at(3, 0) - 4, 14);
  const g3 = vis(frame, at(3, 0.0), at(4, 0) - 4, 14);
  const g4 = vis(frame, at(4, 0.0), 1e9, 14);

  // —— 第 2 句：阻塞与中断时间线 ——
  const grow = (a: number, b: number, f0: number, f1: number) => (b - a) * ip(frame, at(1, f0), bd(1) * (f1 - f0), easeOut);
  const bar = (key: string, y: number, a: number, w: number, color: string, label: string, tag?: string, o = 1) => {
    if (w < 0.02) return null;
    return (
      <group key={key}>
        <Block position={[LX(a) + (w * 1.1) / 2, y, 0]} size={[Math.max(0.05, w * 1.1 - 0.07), 1.1, 1.6]} color={C.panel2} edge={color} opacity={o * g1} glow={2} emissive={0.3} />
        {w > 1.2 && <Label text={label} position={[LX(a) + (w * 1.1) / 2, y, 0.9]} size={0.34} bold mono opacity={o * g1} depthTest={false} />}
        {tag && w > 2 && <Label text={tag} position={[LX(a) + (w * 1.1) / 2, y - 1.2, 0.5]} size={0.34} bold color={color} opacity={o * g1} />}
      </group>
    );
  };

  // —— 第 3 句：CPU 搬运 vs DMA ——
  const cpuY = track(frame, [[at(2, 0.44), [0, 0, 0]], [at(2, 0.58), [0, 3.4, 0]]])[1];
  const cpuBusy = frame < at(2, 0.44);
  const chunk = ip(frame, at(2, 0.6), bd(2) * 0.24);

  // —— 第 5 句：磁盘调度 ——
  const sp = ip(frame, at(3, 0.1), bd(3) * 0.6);
  const pts = (seq: number[], cx: number): V3[] => seq.map((t, i) => [trackX(cx, t), stepY(i), 0]);
  const headAt = (seq: number[], cx: number): V3 => {
    const u = sp * (seq.length - 1);
    const i = Math.min(seq.length - 2, Math.floor(u)), f = u - i;
    return [lerp(trackX(cx, seq[i]), trackX(cx, seq[i + 1]), f), lerp(stepY(i), stepY(i + 1), f), 0.2];
  };
  const reqDots = [98, 183, 37, 122, 14, 124, 65, 67];

  // —— 第 6 句：缓存 ——
  const miss = track(frame, [[at(4, 0.08), [-8, 0, 0.5]], [at(4, 0.2), [-1.6, 0, 0.5]], [at(4, 0.3), [8, 0, 0.5]], [at(4, 0.4), [1.2, 0, 0.5]], [at(4, 0.5), [-8, 0, 0.5]]]);
  const hit = track(frame, [[at(4, 0.62), [-8, 0, 0.5]], [at(4, 0.72), [-1.6, 0, 0.5]], [at(4, 0.82), [-8, 0, 0.5]]]);

  const cam = camPath(frame, [
    [0, [0, 3, 23], [0, 0, 0]],
    [at(1, 0.4), [0, 2.5, 21], [0, 0, 0]],
    [at(2, 0.5), [0, 3, 20], [0, 0.8, 0]],
    [at(3, 0.5), [0, 2, 21], [0, 0, 0]],
    [at(4, 0.4), [0, 2.5, 20], [0, 0, 0]],
    [at(4, 1) + 40, [2, 3, 21], [0, 0, 0]],
  ]);

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={-5}>
        {/* —— 驱动分层 —— */}
        <Block position={[0, 3.8, 0]} size={[6, 1.2, 2]} color={C.panel2} edge={C.cyan} opacity={ip(frame, at(0, 0.04), 16) * g0} glow={2} />
        <Label text="应用程序" position={[0, 3.8, 1.1]} size={0.46} bold opacity={ip(frame, at(0, 0.04), 16) * g0} depthTest={false} />
        <Block position={[0, 1.7, 0]} size={[15, 0.7, 2]} color="#3a1b3e" edge={C.pink} opacity={ip(frame, at(0, 0.14), 16) * g0} glow={2.2} emissive={0.4} />
        <Label text="内核：统一接口  read() / write()" position={[0, 1.7, 1.1]} size={0.4} bold mono opacity={ip(frame, at(0, 0.14), 16) * g0} depthTest={false} />
        {[['键盘驱动', -5.2, 0], ['磁盘驱动', 0, 1], ['网卡驱动', 5.2, 2]].map(([n, x, k]) => {
          const o = ip(frame, at(0, 0.3 + (k as number) * 0.1), 14) * g0;
          return (
            <group key={n as string}>
              <Block position={[x as number, -0.4, 0]} size={[3.4, 0.9, 1.8]} color={C.panel2} edge={C.gold} opacity={o} glow={1.9} />
              <Label text={n as string} position={[x as number, -0.4, 1.0]} size={0.36} bold opacity={o} depthTest={false} />
              <CurveArrow from={[x as number, 1.3, 0.3]} to={[x as number, 0.1, 0.3]} color={C.gold} radius={0.04} progress={o} opacity={g0} />
              <CurveArrow from={[x as number, -0.95, 0.3]} to={[x as number, -2.0, 0.3]} color={C.gold} radius={0.04} progress={o} opacity={g0} />
            </group>
          );
        })}
        <CurveArrow from={[0, 3.1, 0.3]} to={[0, 2.1, 0.3]} color={C.cyan} radius={0.05} progress={ip(frame, at(0, 0.2), 14)} opacity={g0} />
        {/* 三种设备 */}
        <group>
          <Block position={[-5.2, -2.7, 0]} size={[3.6, 0.5, 1.7]} color={C.panel2} edge={C.violet} opacity={ip(frame, at(0, 0.5), 14) * g0} glow={1.8} />
          {Array.from({length: 7}, (_, i) => <Block key={i} position={[-6.3 + i * 0.37, -2.35, 0.3]} size={[0.28, 0.18, 0.28]} color={C.panel} edge={C.violet} opacity={ip(frame, at(0, 0.54), 14) * g0} glow={1.4} />)}
          <mesh position={[0, -2.7, 0]} scale={ip(frame, at(0, 0.58), 14) * g0 + 0.001}>
            <cylinderGeometry args={[1.35, 1.35, 0.45, 48]} />
            <meshStandardMaterial color={C.panel2} emissive={C.violet} emissiveIntensity={0.35} metalness={0.4} roughness={0.3} transparent opacity={0.9} />
          </mesh>
          <Block position={[5.2, -2.7, 0]} size={[2.8, 0.9, 1.6]} color={C.panel2} edge={C.violet} opacity={ip(frame, at(0, 0.66), 14) * g0} glow={1.8} />
          {[-0.7, 0, 0.7].map((x) => <Block key={x} position={[5.2 + x, -2.7, 0.85]} size={[0.4, 0.4, 0.2]} color={C.panel} edge={C.gold} opacity={ip(frame, at(0, 0.7), 14) * g0} glow={1.8} />)}
        </group>
        {['键盘', '硬盘', '网卡'].map((n, k) => <Label key={n} text={n} position={[-5.2 + k * 5.2, -3.8, 0.8]} size={0.34} bold color={C.violet} opacity={ip(frame, at(0, 0.6 + k * 0.05), 14) * g0} />)}
        <Label text="驱动屏蔽差异，上层统一读写" position={[0, -4.6, 0]} size={0.44} bold color={C.gold} opacity={vis(frame, at(0, 0.78)) * g0} />

        {/* —— 阻塞 / 中断时间线 —— */}
        {[['CPU', 1.9], ['设备', -0.5], ['进程 P1', -2.9]].map(([n, y]) => (
          <group key={n as string}>
            <Label text={n as string} position={[-9.4, y as number, 0.6]} size={0.4} bold color={C.muted} opacity={ip(frame, at(1, 0.04), 14) * g1} />
            <Block position={[LX(6) - 0.55, (y as number) - 0.75, 0]} size={[13.6, 0.05, 1.8]} color={C.border} edge={C.border} opacity={ip(frame, at(1, 0.04), 14) * g1 * 0.8} glow={1} />
          </group>
        ))}
        {bar('c1', 1.9, 0, grow(0, 3, 0.08, 0.2), C.cyan, 'P1', undefined)}
        {bar('c2', 1.9, 3, grow(3, 9, 0.3, 0.68), C.pink, 'P2 运行', undefined)}
        {bar('c3', 1.9, 9, grow(9, 12, 0.78, 0.94), C.cyan, 'P1', undefined)}
        {bar('d1', -0.5, 3, grow(3, 9, 0.3, 0.68), C.gold, '设备工作中', undefined)}
        {bar('p1', -2.9, 0, grow(0, 3, 0.08, 0.2), C.cyan, '运行', undefined)}
        {bar('p2', -2.9, 3, grow(3, 9, 0.3, 0.68), C.red, '阻塞', 'CPU 不空等')}
        {bar('p3', -2.9, 9, grow(9, 12, 0.78, 0.94), C.cyan, '就绪→运行', undefined)}
        <Label text="发起读写" position={[LX(3), 3.6, 0.6]} size={0.38} bold color={C.gold} opacity={vis(frame, at(1, 0.24), at(2, 0)) * g1} />
        <Block position={[LX(3), 0.5, 0]} size={[0.06, 6.6, 0.2]} color={C.gold} edge={C.gold} opacity={ip(frame, at(1, 0.24), 10) * g1 * 0.8} glow={2.4} emissive={0.8} />
        <Block position={[LX(9), 0.5, 0]} size={[0.06, 6.6, 0.2]} color={C.pink} edge={C.pink} opacity={ip(frame, at(1, 0.72), 10) * g1 * 0.8} glow={2.4} emissive={0.8} />
        <Label text="中断！唤醒 P1" position={[LX(9), 3.6, 0.6]} size={0.42} bold color={C.pink} opacity={vis(frame, at(1, 0.72), at(2, 0)) * g1} />
        {frame >= at(1, 0.72) && frame < at(1, 0.72) + 30 && (
          <Ring position={[LX(9), -0.5, 0.5]} radius={ip(frame, at(1, 0.72), 28, easeOut) * 3} width={0.09} color={C.pink} opacity={1 - prog(frame, at(1, 0.72), 30)} />
        )}

        {/* —— CPU 搬运 vs DMA —— */}
        <Block position={[-8, 0, 0]} size={[2.6, 2.0, 1.8]} color={C.panel2} edge={C.violet} opacity={ip(frame, at(2, 0.02), 14) * g2} glow={1.8} />
        <Label text="设备" position={[-8, 0, 1.0]} size={0.44} bold opacity={ip(frame, at(2, 0.02), 14) * g2} depthTest={false} />
        <Block position={[8, 0, 0]} size={[2.6, 2.0, 1.8]} color={C.panel2} edge={C.cyan} opacity={ip(frame, at(2, 0.02), 14) * g2} glow={1.8} />
        <Label text="内存" position={[8, 0, 1.0]} size={0.44} bold opacity={ip(frame, at(2, 0.02), 14) * g2} depthTest={false} />
        <Block position={[0, cpuY, 0]} size={[2.8, 2.0, 1.8]} color={cpuBusy ? '#4a1620' : '#3a1b3e'} edge={cpuBusy ? C.red : C.pink} opacity={ip(frame, at(2, 0.02), 14) * g2}
          glow={cpuBusy ? 2.6 + pulse(frame, at(2, 0.04), 20) : 2.2} emissive={0.4} />
        <Label text="CPU" position={[0, cpuY, 1.0]} size={0.52} bold mono opacity={ip(frame, at(2, 0.02), 14) * g2} depthTest={false} />
        {Array.from({length: 9}, (_, k) => {
          const t0 = at(2, 0.04 + k * 0.04), len = bd(2) * 0.14;
          const p = prog(frame, t0, len);
          if (p <= 0 || p >= 1 || frame > at(2, 0.46)) return null;
          const pos: V3 = p < 0.5 ? [lerp(-6.4, -1.5, p * 2), 0, 0.3] : [lerp(1.5, 6.4, (p - 0.5) * 2), 0, 0.3];
          return <Orb key={k} position={pos} radius={0.22} color={[C.cyan, C.pink, C.gold][k % 3]} glow={1.8} opacity={g2} />;
        })}
        <Label text="CPU 逐字节搬运，忙个不停" position={[0, -2.4, 0.5]} size={0.46} bold color={C.red} opacity={vis(frame, at(2, 0.1), at(2, 0.46)) * g2} />
        <Block position={[0, -1.7, 0]} size={[3.2, 1.0, 1.6]} color={C.panel2} edge={C.gold} opacity={ip(frame, at(2, 0.5), 16) * g2} glow={2.2} emissive={0.4} />
        <Label text="DMA" position={[0, -1.7, 0.9]} size={0.5} bold mono color={C.gold} opacity={ip(frame, at(2, 0.5), 16) * g2} depthTest={false} />
        {chunk > 0 && chunk < 1.01 && frame < at(2, 0.92) && [0, 1, 2, 3, 4, 5].map((k) => (
          <Orb key={k} position={[lerp(-6.4, 6.4, chunk) - k * 0.55, 0.0, 0.3]} radius={0.22} color={[C.cyan, C.pink, C.gold][k % 3]} glow={1.8} opacity={g2 * (chunk > 0.95 ? 1 - (chunk - 0.95) * 20 : 1)} />
        ))}
        <Label text="DMA 整块搬运，CPU 去干别的" position={[0, -3.4, 0.5]} size={0.46} bold color={C.cyan} opacity={vis(frame, at(2, 0.6), at(2, 0.9)) * g2} />
        {frame >= at(2, 0.9) && frame < at(2, 0.9) + 30 && (
          <Ring position={[0, 3.4, 1]} radius={ip(frame, at(2, 0.9), 28, easeOut) * 2.4} width={0.08} color={C.pink} opacity={1 - prog(frame, at(2, 0.9), 30)} />
        )}
        <Label text="搬完，只打断 CPU 一次" position={[0, 5.2, 0.5]} size={0.42} bold color={C.pink} opacity={vis(frame, at(2, 0.9), 1e9) * g2} />

        {/* —— 磁盘调度 —— */}
        {[[-6.4, '先来先服务 FCFS', FCFS, C.pink], [6.4, '电梯算法 SCAN', SCAN, C.cyan]].map(([cx, title, seq, color]) => {
          const c = cx as number, s = seq as number[], col = color as string;
          const h = headAt(s, c);
          return (
            <group key={title as string}>
              <Label text={title as string} position={[c, 4.1, 0]} size={0.5} bold color={col} opacity={ip(frame, at(3, 0.03), 14) * g3} />
              <Block position={[c, 3.4, 0]} size={[7.2, 0.06, 0.6]} color={C.border} edge={C.border} opacity={ip(frame, at(3, 0.04), 14) * g3} glow={1} />
              <Label text="0" position={[c - 3.7, 3.4, 0.3]} size={0.24} mono color={C.muted} opacity={ip(frame, at(3, 0.04), 14) * g3} />
              <Label text="199" position={[c + 3.8, 3.4, 0.3]} size={0.24} mono color={C.muted} opacity={ip(frame, at(3, 0.04), 14) * g3} />
              {reqDots.map((t, i) => <Orb key={i} position={[trackX(c, t), 3.4, 0]} radius={0.11} color={C.gold} glow={1.4} opacity={ip(frame, at(3, 0.05 + i * 0.01), 10) * g3} />)}
              <Orb position={[trackX(c, 53), 3.4, 0]} radius={0.17} color={C.text} glow={1.6} opacity={ip(frame, at(3, 0.05), 10) * g3} />
              {sp > 0.01 && <PolyTube points={pts(s, c)} progress={Math.min(0.999, sp)} color={col} radius={0.05} opacity={g3} />}
              {sp > 0.01 && <Orb position={h} radius={0.22} color={col} glow={2} opacity={g3} />}
            </group>
          );
        })}
        <Label text="磁头起点 53" position={[0, -3.0, 0.3]} size={0.3} color={C.muted} opacity={vis(frame, at(3, 0.08), at(3, 0.7)) * g3} />
        <Label text="总移动 640 道" position={[-6.4, -3.7, 0.5]} size={0.55} bold color={C.pink} opacity={vis(frame, at(3, 0.78)) * g3} />
        <Label text="总移动 299 道" position={[6.4, -3.7, 0.5]} size={0.55} bold color={C.cyan} opacity={vis(frame, at(3, 0.82)) * g3} />
        <Label text="来回乱跳" position={[-6.4, -2.9, 0.5]} size={0.36} color={C.red} opacity={vis(frame, at(3, 0.72)) * g3} />
        <Label text="一路扫过去，顺路处理" position={[6.4, -2.9, 0.5]} size={0.36} color={C.cyan} opacity={vis(frame, at(3, 0.72)) * g3} />

        {/* —— 缓存 —— */}
        <Block position={[-8, 0, 0]} size={[2.6, 2.0, 1.8]} color={C.panel2} edge={C.cyan} opacity={ip(frame, at(4, 0.02), 14) * g4} glow={1.8} />
        <Label text="应用" position={[-8, 0, 1.0]} size={0.44} bold opacity={ip(frame, at(4, 0.02), 14) * g4} depthTest={false} />
        <Block position={[0, 0, 0]} size={[3.6, 2.4, 1.8]} color={C.panel2} edge={C.gold} opacity={ip(frame, at(4, 0.04), 14) * g4} glow={2} />
        <Label text="缓存（内存）" position={[0, 0.2, 1.0]} size={0.44} bold opacity={ip(frame, at(4, 0.04), 14) * g4} depthTest={false} />
        <Block position={[0, -0.7, 0.6]} size={[1.0, 0.5, 0.8]} color={C.panel2} edge={C.pink} opacity={ip(frame, at(4, 0.42), 14) * g4} glow={2.2} emissive={0.6} />
        <Block position={[8, 0, 0]} size={[2.6, 2.0, 1.8]} color={C.panel2} edge={C.violet} opacity={ip(frame, at(4, 0.04), 14) * g4} glow={1.8} />
        <Label text="硬盘" position={[8, 0, 1.0]} size={0.44} bold opacity={ip(frame, at(4, 0.04), 14) * g4} depthTest={false} />
        <Orb position={miss} radius={0.3} color={C.pink} glow={1.8} opacity={vis(frame, at(4, 0.08), at(4, 0.52), 8) * g4} />
        <Orb position={hit} radius={0.3} color={C.cyan} glow={1.8} opacity={vis(frame, at(4, 0.62), at(4, 0.84), 8) * g4} />
        <Label text="第一次读：缓存没有，去硬盘（慢）" position={[0, 2.8, 0.5]} size={0.46} bold color={C.pink} opacity={vis(frame, at(4, 0.1), at(4, 0.56)) * g4} />
        <Label text="第二次读：命中，不再碰硬盘（快）" position={[0, 2.8, 0.5]} size={0.46} bold color={C.cyan} opacity={vis(frame, at(4, 0.6), 1e9) * g4} />
      </Stage>

      <Badge from={at(0, 0.7)} to={at(1, 0)} x={1848} y={170} align="right" color={C.gold}>设备驱动 <Mono color={C.gold}>Driver</Mono></Badge>
      <Badge from={at(1, 0.2)} to={at(2, 0)} x={1848} y={170} align="right" color={C.pink}>阻塞 → 中断唤醒</Badge>
      <Badge from={at(2, 0.1)} to={at(3, 0)} x={1848} y={170} align="right" color={C.cyan}><Mono>DMA</Mono> 直接内存访问</Badge>
      <Badge from={at(3, 0.1)} to={at(4, 0)} x={1848} y={190} align="right" color={C.cyan}>磁盘调度：减少磁头移动</Badge>
      <Badge from={at(4, 0.1)} x={1848} y={170} align="right" color={C.gold}>缓存 <Mono color={C.gold}>Cache</Mono></Badge>
    </AbsoluteFill>
  );
};
