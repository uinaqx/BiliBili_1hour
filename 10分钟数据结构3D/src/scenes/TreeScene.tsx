import React from 'react';
import {AbsoluteFill} from 'remotion';
import {CurveArrow, GlassBox, Label, Orb, Stage, V3, Block} from '../three';
import {camPath, easeOut, easeOutBack, ip, lerp3, prog, useScene} from '../anim';
import {C} from '../theme';
import {Badge, Mono} from '../ui';

type T = {v: number; pos: V3; parent: number | null; depth: number};
const NODES: T[] = [
  {v: 50, pos: [0, 4.2, 0], parent: null, depth: 0},
  {v: 30, pos: [-5, 1.6, 0.8], parent: 0, depth: 1},
  {v: 70, pos: [5, 1.6, -0.8], parent: 0, depth: 1},
  {v: 20, pos: [-7.6, -1.0, 0.2], parent: 1, depth: 2},
  {v: 45, pos: [-2.5, -1.0, 1.4], parent: 1, depth: 2},
  {v: 60, pos: [2.5, -1.0, -1.2], parent: 2, depth: 2},
  {v: 80, pos: [7.6, -1.0, 0.4], parent: 2, depth: 2},
  {v: 40, pos: [-4.0, -3.6, 1.8], parent: 4, depth: 3},
  {v: 47, pos: [-1.0, -3.6, 1.0], parent: 4, depth: 3},
];
const INORDER = [3, 1, 7, 4, 8, 0, 5, 2, 6];
const PATH = [0, 1, 4, 8];
const chainPos = (rank: number): V3 => [-8 + rank * 2.0, 5.4 - rank * 1.25, 0];

export const TreeScene: React.FC = () => {
  const {frame, at} = useScene();

  const grow = (d: number) => at(0, 0.06 + d * 0.16);
  const step = (k: number) => at(2, 0.1 + k * 0.24);
  const searchOn = frame >= step(0) && frame < at(3, 0.95);
  const visitT = (rank: number) => at(4, 0.1 + rank * 0.085);
  const degen = ip(frame, at(5, 0.08), 40);
  const rebalance = ip(frame, at(5, 0.62), 44);

  const dimOf = (i: number) => {
    if (!searchOn) return 0;
    const leftOf = (root: number, side: 'L' | 'R') => {
      const r = NODES[root].v;
      const inSub = (j: number): boolean => {
        let p: number | null = j;
        while (p !== null && NODES[p].parent !== root) p = NODES[p].parent;
        return p !== null && (side === 'L' ? NODES[p].v < r : NODES[p].v > r);
      };
      return inSub(i);
    };
    if (frame > step(0) + 16 && leftOf(0, 'R')) return 1;
    if (frame > step(1) + 16 && leftOf(1, 'L')) return 1;
    if (frame > step(2) + 16 && leftOf(4, 'L')) return 1;
    return 0;
  };

  const rankOf = (i: number) => INORDER.indexOf(i);
  const posOf = (i: number): V3 => {
    const base = NODES[i].pos;
    const chain = chainPos(rankOf(i));
    return lerp3(lerp3(base, chain, degen), base, rebalance);
  };

  const pathIdx = Math.min(3, Math.max(0, Math.floor((frame - step(0)) / (step(1) - step(0)))));
  const pathT = ip(frame, step(pathIdx), 18, easeOut);
  const orbPos = frame < step(1) ? NODES[0].pos : lerp3(NODES[PATH[pathIdx - 1] ?? 0].pos, NODES[PATH[pathIdx]].pos, pathT);
  const orbO = Math.min(ip(frame, step(0) - 8, 8), 1 - prog(frame, at(3, 0.2), 14));
  const cmp = ['47 < 50 → 左', '47 > 30 → 右', '47 > 45 → 右', '47 = 47 找到！'];

  const subtreeO = Math.min(ip(frame, at(1, 0.45), 18), 1 - prog(frame, at(2, 0.05), 14));
  const sortedO = Math.min(1, 1 - prog(frame, at(5, 0.02), 16));

  const cam = camPath(frame, [
    [0, [0, 8, 26], [0, 1, 0]],
    [at(0, 0.9), [-4, 3.5, 20], [0, 0.3, 0]],
    [at(1, 0.9), [4, 3, 19], [0, 0.2, 0]],
    [at(2, 0.1), [-5, 3, 18], [-2.5, 0.6, 0]],
    [at(2, 0.9), [-3, 1.5, 16], [-1.8, -0.5, 0]],
    [at(3, 0.3), [0, 3, 21], [0, 0.4, 0]],
    [at(4, 0.1), [0, -0.6, 24], [0, -2.1, 0]],
    [at(5, 0.1), [2, 3, 25], [0, 0.4, 0]],
    [at(5, 0.6), [-3, 3, 24], [0, 0.6, 0]],
    [at(5, 1) + 40, [3, 3.2, 22], [0, 0.6, 0]],
  ]);

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={-7.5}>
        {NODES.map((n, i) => {
          if (n.parent === null) return null;
          const t = ip(frame, grow(n.depth) - 14, 18, easeOut);
          const onPath = searchOn && PATH.includes(i) && frame >= step(PATH.indexOf(i));
          return <CurveArrow key={'e' + i} from={posOf(n.parent)} to={posOf(i)} head={false} radius={0.05} progress={t}
            color={onPath ? C.orange : C.border} glow={onPath ? 2 : 1.8} opacity={(1 - dimOf(i) * 0.75) * (1 - degen * (1 - rebalance))} trimStart={0.6} trimEnd={0.6} />;
        })}
        {INORDER.slice(0, -1).map((a, r) => (
          <CurveArrow key={'c' + r} from={posOf(a)} to={posOf(INORDER[r + 1])} head={false} radius={0.05} color="#ff9b8a"
            opacity={degen * (1 - rebalance)} trimStart={0.6} trimEnd={0.6} />
        ))}

        {NODES.map((n, i) => {
          const s = ip(frame, grow(n.depth), 20, easeOutBack);
          const isFound = searchOn && i === 8 && frame >= step(3);
          const onPath = searchOn && PATH.includes(i) && frame >= step(PATH.indexOf(i));
          const visit = frame >= visitT(rankOf(i)) && frame < at(5, 0.05);
          const flash = 1 - prog(frame, visitT(rankOf(i)), 16);
          let color = C.muted, glow = 0.9;
          if (onPath) { color = C.orange; glow = 1.6; }
          if (isFound) { color = C.green; glow = 2.2; }
          if (visit) { color = C.green; glow = 1 + flash * 1.6; }
          if (i === 0 && !onPath && !visit) { color = C.orange; glow = 1.2; }
          const o = 1 - dimOf(i) * 0.75;
          const p = posOf(i);
          return (
            <group key={i}>
              <Orb position={p} radius={0.72} color={color} glow={glow} scale={s} opacity={o} />
              <Label text={String(n.v)} position={p} size={0.5} bold mono color={C.bg} glow={1} depthTest={false} opacity={s * o} />
            </group>
          );
        })}

        <Label text="根 root" position={[1.8, 5.4, 0]} size={0.38} color={C.orange} opacity={Math.min(ip(frame, at(0, 0.6), 14), 1 - prog(frame, at(1, 0.4), 12))} />
        <Label text="叶子 leaf" position={[-7.6, -2.5, 0.2]} size={0.34} color={C.muted} opacity={Math.min(ip(frame, at(0, 0.75), 14), 1 - prog(frame, at(1, 0.4), 12))} />
        <Label text="叶子 leaf" position={[7.6, -2.5, 0.4]} size={0.34} color={C.muted} opacity={Math.min(ip(frame, at(0, 0.8), 14), 1 - prog(frame, at(1, 0.4), 12))} />

        <GlassBox position={[-4.4, -0.8, 0.8]} size={[8.0, 6.4, 3.2]} color={C.green} opacity={subtreeO} fill={0.06} />
        <GlassBox position={[5.1, 0.3, -0.3]} size={[6.4, 4.2, 3.2]} color={C.orange} opacity={subtreeO} fill={0.06} />
        <Label text="左子树 < 50" position={[-4.4, 2.9, 0.8]} size={0.42} color={C.green} opacity={subtreeO} />
        <Label text="右子树 > 50" position={[5.1, 2.8, -0.3]} size={0.42} color={C.orange} opacity={subtreeO} />

        {orbO > 0 && <Orb position={[orbPos[0], orbPos[1] + 1.15, orbPos[2]]} radius={0.24} color={C.orange} glow={3} opacity={orbO} />}
        {cmp.map((c, k) => (
          <Label key={c} text={c} position={[NODES[PATH[k]].pos[0] + 2.6, NODES[PATH[k]].pos[1] + 0.9, NODES[PATH[k]].pos[2]]} size={0.36} mono
            color={k === 3 ? C.green : C.orange} bg="#122033dd" opacity={Math.min(ip(frame, step(k) + 8, 12), 1 - prog(frame, at(3, 0.2), 12))} />
        ))}

        {[0, 1, 2, 3].map((d) => (
          <Label key={'lv' + d} text={`第 ${d + 1} 层`} position={[-11, [4.2, 1.6, -1, -3.6][d], 0]} size={0.34} color={C.muted}
            opacity={Math.min(ip(frame, at(3, 0.35) + d * 6, 12), 1 - prog(frame, at(4, 0.05), 12))} />
        ))}

        {INORDER.map((i, r) => {
          const t = ip(frame, visitT(r), 22, easeOut);
          if (t <= 0) return null;
          const target: V3 = [-8 + r * 2, -5.1, 1.5];
          const p = lerp3(NODES[i].pos, target, t);
          return (
            <group key={'s' + r}>
              <Block position={p} size={[1.5, 1.1, 1.1]} color="#16283a" edge={C.green} glow={1.8} opacity={t * sortedO} />
              <Label text={String(NODES[i].v)} position={p} size={0.42} bold mono opacity={t * sortedO} depthTest={false} />
            </group>
          );
        })}
        <Label text="中序遍历：左 → 根 → 右 = 有序" position={[0, 6.1, 0]} size={0.44} color={C.green}
          opacity={Math.min(ip(frame, at(4, 0.4), 14), sortedO)} />

        {degen > 0 && <Label text="顺序插入 → 退化成链 O(n)" position={[3.5, 5.6, 0]} size={0.44} color="#ff9b8a" opacity={degen * (1 - rebalance)} />}
        {rebalance > 0 && <Label text="自平衡：旋转恢复矮胖  AVL · 红黑树" position={[0, 6.4, 0]} size={0.44} color={C.green} opacity={rebalance} />}
      </Stage>

      <Badge from={at(1, 0.2)} to={at(5, 0)} x={1848} y={170} align="right" color={C.green}>左 &lt; 根 &lt; 右</Badge>
      <Badge from={at(3, 0.2)} x={1848} y={240} align="right">平衡时 <Mono>O(log n)</Mono></Badge>
    </AbsoluteFill>
  );
};