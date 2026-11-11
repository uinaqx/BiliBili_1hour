import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Block, CurveArrow, Label, Line, Orb, Stage, V3} from '../three';
import {camPath, easeInOut, easeOutBack, ip, lerp3, prog, useScene} from '../anim';
import {C} from '../theme';
import {Badge, Card, Mono} from '../ui';

const treeSlot = (i: number): V3 => {
  const level = Math.floor(Math.log2(i + 1));
  const pos = i - (2 ** level - 1);
  const W = 17;
  return [((pos + 0.5) / 2 ** level) * W - W / 2, 4.8 - level * 2.25, (level % 2 ? 0.6 : -0.3)];
};
const arrSlot = (i: number): V3 => [(i - 3.5) * 1.75, -4.4, 2];

export const HeapScene: React.FC = () => {
  const {frame, at} = useScene();

  const tIns = at(2, 0.12);
  const s1 = at(2, 0.38), s2 = at(2, 0.56), s3 = at(2, 0.74);
  const tPop = at(3, 0.06), tMove = at(3, 0.18), d1 = at(3, 0.34), d2 = at(3, 0.5);

  // value -> list of [frame, slot]; slot -1 means "gone"
  const moves: Record<number, [number, number][]> = {
    3: [[0, 0], [s3, 1], [d1, 0]],
    8: [[0, 1], [s2, 3], [d2, 1]],
    5: [[0, 2]],
    12: [[0, 3], [s1, 7], [tMove, 0], [d1, 1], [d2, 3]],
    10: [[0, 4]],
    9: [[0, 5]],
    7: [[0, 6]],
    2: [[tIns, 7], [s1, 3], [s2, 1], [s3, 0], [tPop, -1]],
  };
  const MOVE = 20;
  const place = (v: number, slotFn: (i: number) => V3, arc: number) => {
    const m = moves[v];
    let cur = m[0][1];
    for (let k = 1; k < m.length; k++) {
      const [f, to] = m[k];
      if (frame < f) break;
      const t = ip(frame, f, MOVE, easeInOut);
      if (to === -1) {
        const p = slotFn(cur);
        return {pos: [p[0], p[1] + t * 6, p[2] + t * 2] as V3, o: 1 - t, moving: t < 1, slot: cur};
      }
      if (t < 1) {
        const p = lerp3(slotFn(cur), slotFn(to), t);
        p[2] += Math.sin(t * Math.PI) * arc;
        return {pos: p, o: 1, moving: true, slot: to};
      }
      cur = to;
    }
    return {pos: slotFn(cur), o: 1, moving: false, slot: cur};
  };
  const values = Object.keys(moves).map(Number);
  const count = frame >= tMove ? 7 : frame >= tIns ? 8 : 7;

  const grow = (i: number) => ip(frame, at(0, 0.05) + Math.floor(Math.log2(i + 1)) * 14 + i * 2, 20, easeOutBack);
  const arrO = ip(frame, at(1, 0.05), 20);
  const linkO = (i: number) => Math.min(ip(frame, at(1, 0.15) + i * 4, 14), 1 - prog(frame, at(2, 0.05), 14)) * 0.7;
  const focus = Math.min(ip(frame, at(1, 0.55), 14), 1 - prog(frame, at(2, 0.05), 14));

  const cam = camPath(frame, [
    [0, [0, 6, 25], [0, 1.2, 0]],
    [at(0, 0.9), [-4, 3, 21], [0, 1, 0]],
    [at(1, 0.2), [3, 0.8, 22], [0, -0.9, 0]],
    [at(2, 0.1), [-5, 1.6, 21], [-1, -0.6, 0]],
    [at(3, 0.1), [4, 2.2, 21], [0, -0.4, 0]],
    [at(3, 1) + 40, [0, 1.6, 22.5], [0, -0.6, 0]],
  ]);

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={-7}>
        {Array.from({length: 8}, (_, i) => {
          if (i === 0) return null;
          const p = Math.floor((i - 1) / 2);
          const o = i === 7
            ? Math.min(ip(frame, tIns + 6, 12), 1 - prog(frame, tMove, 10))
            : ip(frame, at(0, 0.05) + Math.floor(Math.log2(i + 1)) * 14, 18);
          return <CurveArrow key={'e' + i} from={treeSlot(p)} to={treeSlot(i)} head={false} radius={0.045} color={C.border} glow={1.9}
            opacity={o} trimStart={0.75} trimEnd={0.75} />;
        })}

        {Array.from({length: 8}, (_, i) => {
          const o = i < 7 ? arrO : Math.min(ip(frame, tIns, 12), 1 - prog(frame, tMove + 10, 12));
          const hot = focus > 0 && (i === 1 || i === 3 || i === 4);
          return (
            <group key={'a' + i}>
              <Block position={[arrSlot(i)[0], arrSlot(i)[1], arrSlot(i)[2] - 0.2]} size={[1.6, 1.4, 0.3]} color={C.panel}
                edge={hot ? (i === 1 ? C.orange : C.green) : C.border} glow={hot ? 2.2 : 1.2} opacity={o} />
              <Label text={String(i)} position={[arrSlot(i)[0], arrSlot(i)[1] - 1.1, arrSlot(i)[2]]} size={0.3} mono color={C.muted} opacity={o} />
            </group>
          );
        })}

        {values.map((v) => {
          const t = place(v, treeSlot, 1.6);
          const a = place(v, arrSlot, 1.2);
          const first = moves[v][0][0];
          const s = first === 0 ? grow(t.slot) : ip(frame, first, 18, easeOutBack);
          if (s <= 0.01 || t.o <= 0.01) return null;
          const isRoot = !t.moving && t.slot === 0;
          const color = v === 2 || (v === 12 && frame >= tMove) ? C.orange : isRoot ? C.green : C.muted;
          const glow = t.moving ? 2.4 : isRoot ? 1.6 : 0.95;
          return (
            <group key={v}>
              <Orb position={t.pos} radius={0.75} color={color} glow={glow} scale={s} opacity={t.o} />
              <Label text={String(v)} position={t.pos} size={0.52} bold mono color={C.bg} glow={1} depthTest={false} opacity={s * t.o} />
              {arrO > 0 && <Label text={String(v)} position={[a.pos[0], a.pos[1], a.pos[2] + 0.2]} size={0.5} bold mono color={color === C.muted ? C.text : color}
                opacity={Math.min(arrO, a.o)} />}
              {linkO(t.slot) > 0 && !t.moving && <Line from={t.pos} to={a.pos} color={C.muted} opacity={linkO(t.slot)} glow={1.2} />}
            </group>
          );
        })}

        <Label text="堆顶 = 最小值" position={[treeSlot(0)[0] - 3.0, treeSlot(0)[1] + 0.6, 0]} size={0.4} color={C.green}
          opacity={Math.min(ip(frame, at(0, 0.6), 14), 1 - prog(frame, at(2, 0), 12))} />
        {focus > 0 && <Label text="i = 1 → 左 3、右 4" position={[arrSlot(2)[0], arrSlot(2)[1] + 1.4, 2]} size={0.38} mono color={C.orange} opacity={focus} />}
        {frame > s1 - 10 && frame < at(3, 0) && <Label text="上浮 sift-up：比父小就交换" position={[-5.5, 6.3, 0]} size={0.42} color={C.orange}
          opacity={Math.min(ip(frame, s1 - 10, 12), 1 - prog(frame, at(3, 0) - 12, 12))} />}
        {frame > tMove && <Label text="下沉 sift-down：和较小的孩子交换" position={[-5.5, 6.3, 0]} size={0.42} color={C.orange} opacity={ip(frame, tMove, 12)} />}
        {frame > tPop && frame < tPop + 50 && <Label text="取出 2" position={[treeSlot(0)[0], treeSlot(0)[1] + 3.2, 0]} size={0.46} bold color={C.orange}
          opacity={1 - prog(frame, tPop + 30, 20)} />}
      </Stage>

      <Card from={at(1, 0.35)} to={at(2, 0.05)} x={1160} y={170} w={640}>
        <div style={{color: C.muted, fontSize: 24}}>下标 i 的孩子</div>
        <div><Mono>左 = 2i + 1</Mono>　<Mono color={C.green}>右 = 2i + 2</Mono></div>
        <div style={{color: C.muted, fontSize: 24}}>父 = (i − 1) / 2 向下取整</div>
      </Card>
      <Badge from={at(3, 0.6)} x={1848} y={170} align="right">插入 / 取堆顶 <Mono>O(log n)</Mono></Badge>
      <Badge from={at(3, 0.75)} x={1848} y={240} align="right" color={C.green}>优先队列 · 任务调度</Badge>
    </AbsoluteFill>
  );
};