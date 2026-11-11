import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Block, CurveArrow, Label, Ring, Stage, V3} from '../three';
import {camPath, easeOut, easeOutBack, ip, lerp, prog, useScene} from '../anim';
import {C} from '../theme';
import {Badge, Mono} from '../ui';

const HEAD_X = -5.4, STEP = 1.95;

type Q = {v: string; enter: number; leave: number; prio?: boolean};

/** Linear queue: elements slide toward the head as earlier ones leave. */
const LinearQueue: React.FC<{items: Q[]; frame: number; opacity: number; rearArrows?: boolean; frontIn?: number}> = ({items, frame, opacity, rearArrows, frontIn = 0}) => {
  return (
    <group>
      {items.map((it, i) => {
        if (frame < it.enter - 2 || frame > it.leave + 30) return null;
        let idx = 0;
        if (it.prio) {
          const ahead = items.filter((o, j) => j < i && frame < o.leave + 18).length;
          idx = lerp(ahead, 0, ip(frame, it.enter + 20, 26));
        } else {
          for (let j = 0; j < i; j++) if (!items[j].prio) idx += 1 - ip(frame, items[j].leave, 18);
          for (const p of items) if (p.prio) idx += ip(frame, p.enter + 20, 26);
        }
        const enterT = ip(frame, it.enter, 22, easeOut);
        let x = lerp(HEAD_X + 14, HEAD_X + idx * STEP, enterT);
        let y = it.prio ? Math.sin(ip(frame, it.enter + 20, 26) * Math.PI) * 2.2 : 0;
        const leaveT = ip(frame, it.leave, 24, easeOut);
        x -= leaveT * 5; y += leaveT * 1.2;
        const o = Math.min(enterT, 1 - leaveT) * opacity;
        const edge = it.prio ? C.green : leaveT > 0 ? C.orange : C.muted;
        return (
          <group key={it.v}>
            <Block position={[x, y, 0]} size={[1.6, 1.6, 1.6]} edge={edge} glow={it.prio ? 2.4 : 1.5} opacity={o} />
            <Label text={it.v} position={[x, y, 0.9]} size={0.55} bold mono opacity={o} />
          </group>
        );
      })}
      <Label text="队头 front" position={[HEAD_X - 1.2, 1.9, 0]} size={0.36} color={C.orange} opacity={opacity} />
      <Label text="队尾 rear" position={[HEAD_X + 6.2, 1.9, 0]} size={0.36} color={C.green} opacity={opacity} />
      <CurveArrow from={[HEAD_X - 0.4, 0, 1.4]} to={[HEAD_X - 4.4, 0, 1.4]} color={C.orange} radius={0.05} progress={opacity} glow={1.8}
        opacity={opacity} />
      <CurveArrow from={[HEAD_X + 13, 0, 1.4]} to={[HEAD_X + 8.6, 0, 1.4]} color={C.green} radius={0.05} progress={opacity} glow={1.8}
        opacity={opacity} />
      {rearArrows && <CurveArrow from={[HEAD_X + 8.6, -0.6, 1.4]} to={[HEAD_X + 13, -0.6, 1.4]} color={C.green} radius={0.05} progress={frontIn} opacity={opacity} />}
      {rearArrows && <CurveArrow from={[HEAD_X - 4.4, -0.6, 1.4]} to={[HEAD_X - 0.4, -0.6, 1.4]} color={C.orange} radius={0.05} progress={frontIn} opacity={opacity} />}
    </group>
  );
};

const R = 4.6, SLOTS = 8;
const ringAt = (k: number, r = R): V3 => {
  const a = (k / SLOTS) * Math.PI * 2 - Math.PI / 2;
  return [Math.cos(a) * r, 0, Math.sin(a) * r];
};

export const QueueScene: React.FC = () => {
  const {frame, at} = useScene();

  const lin: Q[] = [
    {v: 'A', enter: at(0, 0.02), leave: at(0, 0.45)},
    {v: 'B', enter: at(0, 0.06), leave: at(0, 0.7)},
    {v: 'C', enter: at(0, 0.1), leave: 1e9},
    {v: 'D', enter: at(0, 0.14), leave: 1e9},
    {v: 'E', enter: at(0, 0.55), leave: 1e9},
    {v: 'F', enter: at(0, 0.8), leave: 1e9},
  ];
  const linO = Math.min(ip(frame, 0, 14), 1 - prog(frame, at(1, 0.02), 18));

  // circular queue
  const ringO = Math.min(ip(frame, at(1, 0.06), 24), 1 - prog(frame, at(3, 0.0), 20));
  const ev = (f: number) => frame >= f;
  const tDeq = at(1, 0.4), tE1 = at(1, 0.52), tE2 = at(1, 0.66), tE3 = at(1, 0.8);
  const cells: {k: number; v: string; on: number; off: number}[] = [
    {k: 2, v: 'C', on: at(1, 0.12), off: tDeq},
    {k: 3, v: 'D', on: at(1, 0.15), off: 1e9},
    {k: 4, v: 'E', on: at(1, 0.18), off: 1e9},
    {k: 5, v: 'F', on: at(1, 0.21), off: 1e9},
    {k: 6, v: 'G', on: tE1, off: 1e9},
    {k: 7, v: 'H', on: tE2, off: 1e9},
    {k: 0, v: 'I', on: tE3, off: 1e9},
  ];
  const head = 2 + ip(frame, tDeq + 6, 16);
  const tail = 6 + ip(frame, tE1 + 6, 16) + ip(frame, tE2 + 6, 16) + ip(frame, tE3 + 6, 16);
  const ringSpin = (frame - at(1, 0)) * 0.002;

  // deque / priority
  const dq: Q[] = [
    {v: '5', enter: at(3, 0.04), leave: 1e9},
    {v: '8', enter: at(3, 0.07), leave: 1e9},
    {v: '6', enter: at(3, 0.1), leave: 1e9},
    {v: '9', enter: at(3, 0.13), leave: 1e9},
    {v: '1', enter: at(3, 0.55), leave: 1e9, prio: true},
  ];
  const dqO = ip(frame, at(3, 0.02), 20);

  const cam = camPath(frame, [
    [0, [-2, 4, 20], [0, 0, 0]],
    [at(0, 0.9), [3, 3, 17], [0, 0, 0]],
    [at(1, 0.15), [0, 12.5, 14.5], [0, -1.6, 0]],
    [at(1, 0.9), [5.5, 11, 13.5], [0, -1.6, 0]],
    [at(2, 0.9), [-5.5, 10.5, 14], [0, -1.6, 0]],
    [at(3, 0.15), [0, 4, 19], [0, 0, 0]],
    [at(3, 1) + 40, [2, 4.5, 18], [0, 0, 0]],
  ]);

  const apps = ['打印任务排队', '消息队列', '广度优先搜索 BFS'];

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={-2.2}>
        {linO > 0 && <LinearQueue items={lin} frame={frame} opacity={linO} />}

        {ringO > 0 && (
          <group rotation={[0, ringSpin, 0]}>
            <Ring position={[0, -0.85, 0]} radius={R + 1.3} width={0.05} color={C.border} rotation={[-Math.PI / 2, 0, 0]} opacity={ringO} glow={1.4} />
            {Array.from({length: SLOTS}, (_, k) => {
              const p = ringAt(k);
              const a = (k / SLOTS) * Math.PI * 2 - Math.PI / 2;
              return (
                <group key={k}>
                  <Block position={[p[0], -0.7, p[2]]} size={[1.7, 0.18, 1.7]} edge={C.border} rotation={[0, -a, 0]} opacity={ringO} />
                  <Label text={String(k)} position={ringAt(k, R + 1.75).map((v, i) => (i === 1 ? -0.6 : v)) as V3} size={0.34} mono color={C.muted} opacity={ringO} />
                </group>
              );
            })}
            {cells.map((c) => {
              if (!ev(c.on)) return null;
              const pop = ip(frame, c.off, 22, easeOut);
              const s = ip(frame, c.on, 18, easeOutBack);
              const p = ringAt(c.k);
              const o = ringO * (1 - pop);
              const wrap = c.k === 0;
              return (
                <group key={c.v}>
                  <Block position={[p[0], 0.2 + pop * 3, p[2]]} size={[1.3, 1.3, 1.3]} edge={wrap ? C.green : c.off < 1e9 ? C.orange : C.muted}
                    glow={wrap ? 2.4 : 1.5} scale={s} opacity={o} />
                  <Label text={c.v} position={[p[0], 0.25 + pop * 3, p[2]]} size={0.5} bold mono opacity={o * s} depthTest={false} />
                </group>
              );
            })}
            {[{v: head, c: C.orange, t: 'front'}, {v: tail, c: C.green, t: 'rear'}].map((ptr) => {
              const p = ringAt(ptr.v, R - 1.2);
              return (
                <group key={ptr.t}>
                  <CurveArrow from={[0, 0.2, 0]} to={[p[0], 0.2, p[2]]} color={ptr.c} radius={0.07} progress={ringO} opacity={ringO} />
                  <Label text={ptr.t} position={[p[0] * 0.55, 1.0, p[2] * 0.55]} size={0.36} mono color={ptr.c} opacity={ringO} />
                </group>
              );
            })}
            {frame > tE3 && <Label text="rear 绕回 0" position={[ringAt(0, R)[0], 2.2, ringAt(0, R)[2]]} size={0.4} color={C.green}
              opacity={Math.min(ip(frame, tE3 + 10, 12), ringO)} />}
          </group>
        )}

        {apps.map((a, k) => {
          const t = at(2, 0.12 + k * 0.24);
          const o = Math.min(ip(frame, t, 16), ringO);
          const ang = k * 2.1 + (frame - t) * 0.006;
          return <Label key={a} text={a} position={[Math.cos(ang) * 7.6, 2.6 + k * 0.4, Math.sin(ang) * 7.6]} size={0.46} bg="#122033ee" border={C.orange} opacity={o} />;
        })}

        {dqO > 0 && <LinearQueue items={dq} frame={frame} opacity={dqO} rearArrows frontIn={ip(frame, at(3, 0.2), 20)} />}
        {dqO > 0 && <Label text="双端队列：两端都能进出" position={[0, 3.3, 0]} size={0.42} color={C.green} opacity={Math.min(ip(frame, at(3, 0.2), 16), 1 - prog(frame, at(3, 0.5), 12))} />}
        {dqO > 0 && <Label text="优先队列：优先级高的先出 → 用堆实现" position={[0, 3.3, 0]} size={0.42} color={C.green} opacity={ip(frame, at(3, 0.55), 16)} />}
      </Stage>

      <Badge from={at(0, 0.3)} x={1848} y={170} align="right">先进先出 <Mono>FIFO</Mono></Badge>
      <Badge from={at(1, 0.3)} to={at(3, 0)} x={1848} y={240} align="right" color={C.green}>循环队列：下标 = (i + 1) % n</Badge>
    </AbsoluteFill>
  );
};
