import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Block, CurveArrow, Label, Orb, Stage, V3} from '../three';
import {camPath, easeOut, easeOutBack, ip, lerp3, prog, useScene} from '../anim';
import {C} from '../theme';
import {Badge, Mono} from '../ui';

type N = {pos: V3; v: number; addr: string};
const NODES: N[] = [
  {pos: [-9.5, 1.3, -1], v: 7, addr: '0x3A10'},
  {pos: [-4.8, -0.5, 1.6], v: 19, addr: '0x7F08'},
  {pos: [0.2, 1.7, -1.6], v: 3, addr: '0x1C40'},
  {pos: [4.9, -0.3, 1.0], v: 42, addr: '0x9B20'},
  {pos: [9.6, 1.5, -0.4], v: 11, addr: '0x52E8'},
];
const NEW: N = {pos: [-2.3, -2.7, 2.4], v: 30, addr: '0x6D04'};
const outOf = (p: V3): V3 => [p[0] + 1.05, p[1], p[2]];
const inTo = (p: V3): V3 => [p[0] - 0.85, p[1], p[2]];

const ListNode: React.FC<{n: N; scale: number; edge?: string; glow?: number; y?: number; opacity?: number}> = ({n, scale, edge = C.muted, glow = 1.4, y = 0, opacity = 1}) => {
  if (scale <= 0.01 || opacity <= 0.01) return null;
  const p: V3 = [n.pos[0], n.pos[1] + y, n.pos[2]];
  return (
    <group>
      <Block position={[p[0] - 0.3, p[1], p[2]]} size={[1.3, 1.15, 1.15]} edge={edge} glow={glow} scale={scale} opacity={opacity} />
      <Block position={[p[0] + 0.72, p[1], p[2]]} size={[0.62, 1.15, 1.15]} color="#1a2a40" edge={edge} glow={glow * 0.8} scale={scale} opacity={opacity} />
      <Label text={String(n.v)} position={[p[0] - 0.3, p[1], p[2] + 0.65]} size={0.5} bold mono opacity={Math.min(scale, opacity)} />
      <Label text="next" position={[p[0] + 0.72, p[1] - 0.32, p[2] + 0.65]} size={0.17} mono color={C.muted} opacity={Math.min(scale, opacity)} />
      <Label text={n.addr} position={[p[0], p[1] + 1.05, p[2]]} size={0.26} mono color={C.muted} opacity={Math.min(scale, opacity) * 0.9} />
    </group>
  );
};

export const Linked: React.FC = () => {
  const {frame, at, bd} = useScene();

  const appear = (k: number) => ip(frame, at(0, 0.04 + k * 0.07), 20, easeOutBack);
  const grow = (k: number) => ip(frame, at(0, 0.42 + k * 0.09), 18, easeOut);

  // traversal: orb hops node0 -> node3
  const hop = bd(1) * 0.17, t0 = at(1, 0.25);
  const seg = Math.floor((frame - t0) / hop);
  const segT = ip(frame, t0 + Math.max(0, seg) * hop, hop * 0.85);
  const travelling = frame >= t0 && seg < 3;
  const found = frame >= t0 + 3 * hop;
  const orbPos: V3 = travelling
    ? lerp3(NODES[seg].pos, NODES[seg + 1].pos, segT).map((x, i) => x + (i === 1 ? 1.1 + Math.sin(segT * Math.PI) * 1.2 : 0)) as V3
    : [NODES[3].pos[0], NODES[3].pos[1] + 1.1, NODES[3].pos[2]];
  const orbO = Math.min(ip(frame, t0 - 6, 8), 1 - prog(frame, at(2, 0), 12));
  const visited = (k: number) => frame >= t0 + k * hop && frame < at(2, 0);

  // insertion
  const newIn = ip(frame, at(2, 0.12), 22, easeOutBack);
  const step1 = ip(frame, at(2, 0.42), 22, easeOut);
  const unlink12 = ip(frame, at(2, 0.66), 14);
  const step2 = ip(frame, at(2, 0.72), 22, easeOut);
  // deletion
  const bypass = ip(frame, at(3, 0.25), 26, easeOut);
  const fall = ip(frame, at(3, 0.5), 30);
  // doubly linked
  const back = (k: number) => ip(frame, at(4, 0.22 + k * 0.07), 20, easeOut);

  const P = NODES.map((n) => n.pos);
  const cam = camPath(frame, [
    [0, [-3, 6, 27], [0, 0, 0]],
    [at(0, 0.9), [2, 4, 22], [0, 0.3, 0]],
    [at(1, 0.2), [-8, 3.5, 15], [-6, 0.4, 0]],
    [at(1, 0.85), [3, 3.5, 15], [3, 0.4, 0]],
    [at(2, 0.1), [-3, 0.8, 15.5], [-2.2, -1.3, 0]],
    [at(3, 0.15), [3, 5.5, 17], [2.5, 0.5, 0]],
    [at(4, 0.15), [0, 2.2, 21.5], [0, -0.6, 0]],
    [at(4, 1) + 40, [2, 3, 21], [0, -0.4, 0]],
  ]);

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={-5.5}>
        {NODES.map((n, k) => {
          const isHit = k === 3 && found && frame < at(2, 0);
          const edge = isHit ? C.green : visited(k) ? C.orange : C.muted;
          const glow = isHit ? 2.6 : visited(k) ? 2.2 : 1.4;
          return <ListNode key={k} n={n} scale={appear(k)} edge={k === 3 && fall > 0 ? '#ff9b8a' : edge} glow={glow}
            y={k === 3 ? -fall * 6 : 0} opacity={k === 3 ? 1 - fall : 1} />;
        })}
        <ListNode n={NEW} scale={newIn} edge={C.orange} glow={2} />

        <Label text="head" position={[P[0][0] - 1.1, P[0][1] + 2.1, P[0][2]]} size={0.38} mono color={C.orange} opacity={grow(0)} />
        <CurveArrow from={[P[0][0] - 1.1, P[0][1] + 1.75, P[0][2]]} to={[P[0][0] - 0.6, P[0][1] + 0.7, P[0][2]]} progress={grow(0)} color={C.orange} radius={0.035} />
        <Label text="null" position={[P[4][0] + 2.6, P[4][1], P[4][2]]} size={0.38} mono color={C.muted} opacity={grow(4)} />
        <CurveArrow from={outOf(P[4])} to={[P[4][0] + 2.0, P[4][1], P[4][2]]} progress={grow(4)} radius={0.04} />

        <CurveArrow from={outOf(P[0])} to={inTo(P[1])} bend={[0, 0.8, 0]} progress={grow(0)} color={visited(0) ? C.orange : C.muted} />
        <CurveArrow from={outOf(P[1])} to={inTo(P[2])} bend={[0, 0.8, 0]} progress={grow(1) * (1 - unlink12)} color={visited(1) ? C.orange : C.muted} />
        <CurveArrow from={outOf(P[2])} to={inTo(P[3])} bend={[0, 0.8, 0]} progress={grow(2) * (1 - bypass)} color={visited(2) ? C.orange : C.muted} />
        <CurveArrow from={outOf(P[3])} to={inTo(P[4])} bend={[0, 0.8, 0]} progress={grow(3)} opacity={1 - fall} />

        <CurveArrow from={outOf(NEW.pos)} to={inTo(P[2])} bend={[0.6, -0.5, 0]} progress={step1} color={C.green} radius={0.06} />
        <CurveArrow from={outOf(P[1])} to={inTo(NEW.pos)} bend={[-0.4, -0.8, 0]} progress={step2} color={C.green} radius={0.06} />
        <Label text="①" position={[1.2, -1.4, 1.5]} size={0.55} color={C.green} bold opacity={Math.min(step1, 1 - prog(frame, at(3, 0), 12))} />
        <Label text="②" position={[-4.9, -1.9, 2.2]} size={0.55} color={C.green} bold opacity={Math.min(step2, 1 - prog(frame, at(3, 0), 12))} />

        <CurveArrow from={outOf(P[2])} to={inTo(P[4])} bend={[0, 3.2, 0]} progress={bypass} color={C.green} radius={0.06} />

        {[[P[1], P[0]], [NEW.pos, P[1]], [P[2], NEW.pos], [P[4], P[2]]].map(([a, b2], k) => (
          <CurveArrow key={'b' + k} from={[a[0] - 0.9, a[1] - 0.3, a[2]]} to={[b2[0] + 1.0, b2[1] - 0.35, b2[2]]}
            bend={[0, -1.3, 0.4]} progress={back(k)} color={C.green} radius={0.04} />
        ))}

        {orbO > 0 && <Orb position={orbPos} radius={0.32} color={C.orange} glow={3} opacity={orbO} />}
        {found && frame < at(2, 0) && (
          <Label text="找到 42：走了 4 个节点" position={[P[3][0], P[3][1] + 2.4, P[3][2]]} size={0.4} color={C.green}
            opacity={1 - prog(frame, at(2, 0) - 12, 12)} />
        )}
      </Stage>

      <Badge from={at(1, 0.8)} to={at(2, 0)} x={1848} y={170} align="right">查找 <Mono>O(n)</Mono></Badge>
      <Badge from={at(2, 0.9)} x={1848} y={170} align="right" color={C.green}>已知位置插入 / 删除 <Mono color={C.green}>O(1)</Mono></Badge>
      <Badge from={at(4, 0.55)} x={1848} y={240} align="right" color={C.muted}>双向链表：prev + next</Badge>
    </AbsoluteFill>
  );
};