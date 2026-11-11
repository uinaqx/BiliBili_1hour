import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Block, CurveArrow, GlassBox, Label, Orb, Ring, Stage, V3} from '../three';
import {along, camPath, easeOut, ip, lerp, prog, pulse, useScene, vis} from '../anim';
import {C} from '../theme';
import {Badge, Mono} from '../ui';

const UY = 2.4, KY = -2.4;
const APPS = [
  {name: '应用 A', x: -5.2},
  {name: '应用 B', x: -1.6},
  {name: '应用 C', x: 2.0},
];

export const KernelScene: React.FC = () => {
  const {frame, at, bd} = useScene();

  const userIn = ip(frame, at(0, 0.08), 24);
  const kernelIn = ip(frame, at(0, 0.42), 24);
  const gateIn = ip(frame, at(0, 0.72), 20);

  // 应用 B 崩溃（第 2 句）
  const crashT = at(1, 0.22), burstT = at(1, 0.6), reviveT = at(2, 0.04);
  const crashing = frame >= crashT && frame < burstT;
  const dead = frame >= burstT && frame < reviveT;
  const shake = crashing ? Math.sin(frame * 1.9) * 0.14 * prog(frame, crashT, 10) : 0;

  // 系统调用数据包
  const A0: V3 = [-5.2, 1.7, 1.5], G: V3 = [-5.2, 0, 1.5], K: V3 = [-2.6, KY + 0.2, 1.5];
  const downT = ip(frame, at(3, 0.08), bd(3) * 0.3);
  const upT = ip(frame, at(3, 0.62), bd(3) * 0.28);
  let pk: V3 | null = null;
  let pkColor: string = C.gold;
  if (frame >= at(3, 0.08) && frame < at(3, 0.62)) pk = along([A0, G, K], downT);
  else if (frame >= at(3, 0.62) && frame < at(3, 0.92)) { pk = along([K, G, A0], upT); pkColor = C.cyan; }
  const kernelBusy = pulse(frame, at(3, 0.38), bd(3) * 0.26);

  const cam = camPath(frame, [
    [0, [0, 3.5, 24], [0, 0, 0]],
    [at(0, 0.9), [3, 3, 21], [0, 0, 0]],
    [at(1, 0.5), [-4, 4, 20], [-1, 1.5, 0]],
    [at(2, 0.5), [2, 2, 20], [0, 0, 0]],
    [at(3, 0.5), [0, 1.5, 22], [-1.5, -0.3, 0]],
    [at(4, 0.2), [4, 1, 21], [2, -1.5, 0]],
    [at(4, 1) + 40, [0, 2, 23], [0, 0, 0]],
  ]);

  const triggers = [
    {name: '键盘中断', y: -0.7, color: C.gold},
    {name: '时钟中断', y: -2.4, color: C.cyan},
    {name: '缺页异常', y: -4.0, color: C.red},
  ];

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={-6}>
        {/* 两个特权区域 */}
        <GlassBox position={[0, UY, 0]} size={[16, 3.8, 5.2]} color={C.cyan} opacity={userIn} fill={0.05} glow={1.3} />
        <GlassBox position={[0, KY, 0]} size={[16, 3.8, 5.2]} color={C.pink} opacity={kernelIn} fill={0.06 + kernelBusy * 0.08} glow={1.3 + kernelBusy} />
        <Label text="用户态  User Mode" position={[-5.6, UY + 2.35, 2.6]} size={0.44} bold color={C.cyan} opacity={userIn} />
        <Label text="内核态  Kernel Mode" position={[-6.4, KY + 1.35, 2.6]} size={0.44} bold color={C.pink} opacity={kernelIn} />

        {/* 系统调用门 */}
        <Block position={[0, 0, 0]} size={[16, 0.14, 5.2]} color={C.gold} edge={C.gold} opacity={gateIn} glow={2} emissive={0.5} />
        <Label text="系统调用接口" position={[5.6, 0, 3.0]} size={0.36} color={C.gold} bold bg="#171433ee" border={C.gold} opacity={gateIn} depthTest={false} />

        {/* 应用 */}
        {APPS.map((a, k) => {
          const o0 = ip(frame, at(0, 0.28 + k * 0.1), 18);
          const isB = k === 1;
          const bad = isB && (crashing || dead);
          const o = isB ? (frame >= reviveT ? ip(frame, reviveT, 16) : o0 * (1 - prog(frame, burstT, 8))) : o0;
          const x = a.x + (isB ? shake : 0);
          const safe = isB ? 0 : pulse(frame, crashT, 50) * 0.35;
          return (
            <group key={a.name}>
              <Block position={[x, UY, 0]} size={[2.8, 1.5, 2.2]} color={bad ? '#4a1620' : C.panel2} edge={bad ? C.red : C.cyan} opacity={o}
                glow={bad ? 2.6 : 1.8 + safe} scale={1 + safe * 0.1} />
              <Label text={a.name} position={[x, UY, 1.3]} size={0.4} bold opacity={o} depthTest={false} />
            </group>
          );
        })}
        {frame >= burstT && frame < burstT + 40 && (
          <Ring position={[-1.6, UY, 1.2]} radius={ip(frame, burstT, 36, easeOut) * 3} width={0.1} color={C.red} opacity={1 - prog(frame, burstT, 40)} />
        )}
        <Label text="崩溃" position={[-1.6, UY + 1.5, 1.3]} size={0.5} bold color={C.red} opacity={vis(frame, crashT + 6, reviveT - 4)} depthTest={false} />
        <Label text="继续运行" position={[-5.2, UY + 1.5, 1.3]} size={0.34} color={C.cyan} opacity={vis(frame, burstT, at(2, 0.0))} depthTest={false} />
        <Label text="继续运行" position={[2.0, UY + 1.5, 1.3]} size={0.34} color={C.cyan} opacity={vis(frame, burstT, at(2, 0.0))} depthTest={false} />

        {/* 内核 + 硬件 */}
        <Block position={[-1.4, KY, 0]} size={[6.4, 1.7, 2.6]} color="#3a1b3e" edge={C.pink} opacity={kernelIn} glow={2.2 + kernelBusy * 1.5} emissive={0.35 + kernelBusy * 0.5} />
        <Label text="内核 Kernel" position={[-1.4, KY, 1.4]} size={0.48} bold color={C.text} opacity={kernelIn} depthTest={false} />
        {['CPU', '内存', '设备'].map((n, k) => (
          <group key={n}>
            <Block position={[3.9 + (k % 2) * 2.1, KY + 0.6 - Math.floor(k / 2) * 1.2 - (k === 1 ? 0.0 : 0), 0]} size={[1.8, 0.9, 1.8]} color={C.panel2} edge={C.violet}
              opacity={kernelIn} glow={1.4} />
            <Label text={n} position={[3.9 + (k % 2) * 2.1, KY + 0.6 - Math.floor(k / 2) * 1.2, 1.1]} size={0.3} opacity={kernelIn} depthTest={false} />
          </group>
        ))}

        {/* 第 3 句：系统调用清单 */}
        {['read()', 'write()', 'fork()'].map((n, k) => (
          <Label key={n} text={n} position={[-4.6 + k * 3.4, 0.95, 1.8]} size={0.42} mono bold bg="#171433ee" border={C.gold}
            opacity={vis(frame, at(2, 0.5 + k * 0.14), at(3, 0.0))} depthTest={false} />
        ))}
        <CurveArrow from={[-5.2, UY - 0.9, 1.4]} to={[-5.2, 0.2, 1.4]} color={C.gold} radius={0.05} progress={ip(frame, at(2, 0.3), 24)}
          opacity={1 - prog(frame, at(3, 0.05), 10)} />

        {/* 第 4 句：数据包往返 */}
        {pk && <Orb position={pk} radius={0.38} color={pkColor} glow={1.8} />}
        {frame >= at(3, 0.2) && frame < at(3, 0.2) + 30 && (
          <Ring position={[-5.2, 0, 1.5]} radius={ip(frame, at(3, 0.2), 28, easeOut) * 2.2} width={0.07} color={C.gold} opacity={1 - prog(frame, at(3, 0.2), 30)}
            rotation={[-Math.PI / 2, 0, 0]} />
        )}
        <Label text="① 陷入 trap" position={[-2.2, 0.95, 1.8]} size={0.38} color={C.gold} bold opacity={vis(frame, at(3, 0.2), at(3, 0.6))} depthTest={false} />
        <Label text="② 内核执行" position={[-1.4, KY - 1.4, 1.5]} size={0.38} color={C.pink} bold opacity={vis(frame, at(3, 0.4), at(3, 0.66))} depthTest={false} />
        <Label text="③ 返回用户态" position={[-2.0, 0.95, 1.8]} size={0.38} color={C.cyan} bold opacity={vis(frame, at(3, 0.68), at(4, 0.0))} depthTest={false} />

        {/* 第 5 句：中断与异常 */}
        {triggers.map((t, k) => {
          const t0 = at(4, 0.1 + k * 0.24);
          const f = prog(frame, t0, bd(4) * 0.2);
          const p = along([[9.2, t.y, 1.6], [3.2, KY, 1.6]], f);
          const o = ip(frame, t0 - 6, 8) * (1 - prog(frame, t0 + bd(4) * 0.2, 8));
          return (
            <group key={t.name}>
              <Orb position={p} radius={0.3} color={t.color} opacity={o} glow={1.6} />
              <Label text={t.name} position={[p[0] + 1.6, p[1] + 0.55, p[2]]} size={0.36} bold color={t.color} opacity={o} depthTest={false} />
              {frame >= t0 + bd(4) * 0.2 && frame < t0 + bd(4) * 0.2 + 26 && (
                <Ring position={[3.2, KY, 1.6]} radius={ip(frame, t0 + bd(4) * 0.2, 24, easeOut) * 2} width={0.07} color={t.color}
                  opacity={1 - prog(frame, t0 + bd(4) * 0.2, 26)} />
              )}
            </group>
          );
        })}
      </Stage>

      <Badge from={at(0, 0.8)} x={1848} y={170} align="right">权限分级 <Mono>Ring 3 / Ring 0</Mono></Badge>
      <Badge from={at(1, 0.55)} to={at(2, 0)} x={1848} y={240} align="right" color={C.pink}>故障被隔离</Badge>
      <Badge from={at(3, 0.02)} to={at(3, 0.3)} x={1848} y={240} align="right" color={C.cyan}>当前：用户态</Badge>
      <Badge from={at(3, 0.3)} to={at(3, 0.66)} x={1848} y={240} align="right" color={C.pink}>当前：内核态</Badge>
      <Badge from={at(3, 0.7)} to={at(4, 0)} x={1848} y={240} align="right" color={C.cyan}>当前：用户态</Badge>
      <Badge from={at(4, 0.08)} x={1848} y={240} align="right" color={C.gold}>中断 · 异常 → 进入内核</Badge>
    </AbsoluteFill>
  );
};
