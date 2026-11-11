import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Block, CurveArrow, GlassBox, Label, Stage} from '../three';
import {bounce, camPath, easeOut, ip, lerp, prog, useScene} from '../anim';
import {C} from '../theme';
import {Badge, Mono} from '../ui';

const BASE = -3.2, H = 0.92, CAP = 7;
const slotY = (k: number) => BASE + 0.48 + k * H;

type Item = {label: string; push: number; pop: number; color: string; edge: string; wide?: string; burst?: boolean};

export const StackScene: React.FC = () => {
  const {frame, at} = useScene();

  const items: Item[] = [
    {label: 'A', push: at(1, 0.06), pop: at(3, 0.02), color: C.panel, edge: C.muted, burst: true},
    {label: 'B', push: at(1, 0.16), pop: at(3, 0.02), color: C.panel, edge: C.muted, burst: true},
    {label: 'C', push: at(1, 0.26), pop: at(3, 0.02), color: C.panel, edge: C.muted, burst: true},
    {label: 'D', push: at(1, 0.36), pop: at(1, 0.72), color: '#2e2618', edge: C.orange},
    ...['E', 'F', 'G', 'H', 'I'].map((l, i) => ({label: l, push: at(2, 0.48 + i * 0.07), pop: at(3, 0.02), color: C.panel, edge: C.muted, burst: true})),
    {label: 'main()', push: at(3, 0.14), pop: 1e9, color: '#16283a', edge: C.green, wide: '入口'},
    {label: 'f(x)', push: at(3, 0.3), pop: at(3, 0.84), color: '#16283a', edge: C.green, wide: '参数 · 局部变量'},
    {label: 'g(y)', push: at(3, 0.46), pop: at(3, 0.72), color: '#2e2618', edge: C.orange, wide: '返回地址'},
  ];

  const levelOf = (it: Item) => items.filter((o) => o.push < it.push && frame >= o.push && frame < o.pop + 12).length;
  const overflowT = ip(frame, at(2, 0.48 + 4 * 0.07) + 10, 10);
  const overflowOff = prog(frame, at(3, 0.02), 10);
  const danger = overflowT * (1 - overflowOff);
  const shake = danger * Math.sin(frame * 1.7) * 0.12;

  const visible = items.filter((it) => frame >= it.push && frame < it.pop + 26);
  const topLevel = visible.filter((it) => frame < it.pop).length - 1;
  const topY = topLevel >= 0 ? slotY(topLevel) : BASE;

  const cam = camPath(frame, [
    [0, [9, 9, 20], [0, 0.5, 0]],
    [at(0, 0.9), [6, 4.5, 16], [0, 0.5, 0]],
    [at(1, 0.8), [-5, 3.5, 15], [0, 0.6, 0]],
    [at(2, 0.4), [-2, 4.5, 16], [0, 1.5, 0]],
    [at(3, 0.1), [6, 3, 15.5], [0, 0.2, 0]],
    [at(4, 0.1), [0, 5, 20], [0, 0.5, 0]],
    [at(4, 1) + 40, [-6, 5, 18], [0, 0.5, 0]],
  ]);

  const apps = ['撤销 Ctrl+Z', '括号匹配 ( [ { } ] )', '表达式求值 3+4×2'];

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={BASE}>
        <GlassBox position={[shake, BASE + (CAP * H) / 2 + 0.05, 0]} size={[3.8, CAP * H + 0.1, 3.8]}
          color={danger > 0.3 ? '#ff9b8a' : C.muted} opacity={ip(frame, 8, 24)} fill={0.05} glow={1.2 + danger} />
        <Block position={[0, BASE - 0.12, 0]} size={[4.4, 0.24, 4.4]} edge={C.border} opacity={ip(frame, 8, 24)} />

        {visible.map((it) => {
          const lvl = levelOf(it);
          const drop = ip(frame, it.push, 22, bounce);
          let y = lerp(slotY(lvl) + 7, slotY(lvl), drop);
          let x = shake, z = 0, o = 1, rot = 0;
          if (frame >= it.pop) {
            const t = ip(frame, it.pop, 24, easeOut);
            if (it.burst) {
              const dir = (it.label.charCodeAt(0) % 2 ? 1 : -1) * (1 + (it.label.charCodeAt(0) % 3) * 0.5);
              x += dir * t * 9; y += t * 3; z += t * 3; rot = t * dir;
            } else {
              y += t * 6; x += t * 1.5;
            }
            o = 1 - t;
          }
          const w = it.wide ? 3.3 : 3.0;
          return (
            <group key={it.label}>
              <Block position={[x, y, z]} size={[w, 0.78, 3.0]} color={it.color} edge={danger > 0.3 && lvl >= CAP - 1 ? '#ff9b8a' : it.edge}
                glow={it.edge === C.muted ? 1.4 : 2.1} opacity={o} rotation={[0, 0, rot * 0.4]} />
              <Label text={it.label} position={[x, y, z + 1.6]} size={0.42} bold mono opacity={o} depthTest={false} />
              {it.wide && <Label text={it.wide} position={[x + 3.4, y, z + 1.6]} size={0.34} color={C.green} opacity={o * ip(frame, it.push + 14, 12)}
                depthTest={false} />}
            </group>
          );
        })}

        <CurveArrow from={[-4.6, topY + 0.6, 0.5]} to={[-1.9, topY, 0.5]} bend={[0, 0.4, 0]} color={C.orange} radius={0.05}
          progress={ip(frame, at(0, 0.45), 18)} />
        <Label text="栈顶 top" position={[-5.6, topY + 0.95, 0.5]} size={0.36} color={C.orange} opacity={ip(frame, at(0, 0.45), 18)} />

        {danger > 0 && <Label text="Stack Overflow!" position={[shake, BASE + CAP * H + 1.4, 0]} size={0.62} bold mono color="#ff9b8a" opacity={danger} glow={1.1} />}

        {apps.map((a, k) => {
          const t = at(4, 0.1 + k * 0.25);
          const o = ip(frame, t, 16);
          const ang = (frame - t) * 0.01 + k * 2.1;
          return <Label key={a} text={a} position={[Math.cos(ang) * 6.2, 3.6 - k * 1.5, Math.sin(ang) * 3]} size={0.42} bg="#122033ee" border={C.orange}
            opacity={o} />;
        })}
      </Stage>

      <Badge from={at(1, 0.8)} x={1848} y={170} align="right">后进先出 <Mono>LIFO</Mono></Badge>
      <Badge from={at(2, 0.15)} x={1848} y={240} align="right" color={C.green}>push / pop / peek <Mono color={C.green}>O(1)</Mono></Badge>
      <Badge from={at(3, 0.08)} to={at(4, 0)} x={1848} y={310} align="right" color={C.muted}>函数调用栈</Badge>
    </AbsoluteFill>
  );
};
