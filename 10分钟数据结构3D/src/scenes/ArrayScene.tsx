import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Block, GlassBox, Label, Stage, V3} from '../three';
import {camPath, easeOut, easeOutBack, ip, lerp, prog, useScene} from '../anim';
import {C} from '../theme';
import {Badge, Card, Mono} from '../ui';

const VALUES = [12, 7, 33, 18, 5, 26, 41, 9];
const GAP = 1.95;
const slotX = (k: number) => (k - 3.5) * GAP;

export const ArrayScene: React.FC = () => {
  const {frame, at} = useScene();

  const insStart = at(3, 0.3), shiftStep = 7, shiftLen = 16;
  const insDrop = insStart + 5 * shiftStep + shiftLen;
  const delStart = at(4, 0.06), delGone = delStart + 26;

  const indexOf = (id: number) => {
    let k = id === 8 ? 3 : id;
    if (id >= 3 && id !== 8) k += ip(frame, insStart + (7 - id) * shiftStep, shiftLen);
    const afterInsert = id === 8 ? 3 : id >= 3 ? id + 1 : id;
    if (afterInsert >= 3) k -= ip(frame, delGone + (afterInsert - 3) * shiftStep, shiftLen);
    return k;
  };

  const cam = camPath(frame, [
    [0, [-6, 7, 22], [0, 0, 0]],
    [at(0, 0.7), [-1.5, 4.2, 15.5], [0, 0, 0]],
    [at(1, 0.2), [2.5, 3.6, 13], [1.2, 0.2, 0]],
    [at(1, 0.9), [5.5, 2.8, 10.5], [slotX(5), 0.3, 0]],
    [at(2, 0.25), [-3, 5.5, 15], [0, 0, 0]],
    [at(3, 0.15), [0, 6.5, 17.5], [1, 0.5, 0]],
    [at(4, 0.6), [3, 5, 16.5], [0.5, 0, 0]],
    [at(4, 1) + 60, [1, 4.4, 15.5], [0, 0, 0]],
  ]);

  const beam = Math.min(ip(frame, at(1, 0.35), 12), 1 - prog(frame, at(2, 0.1), 15));
  const cacheIn = ip(frame, at(2, 0.25), 18, easeOut);
  const cacheX = lerp(slotX(1.5), slotX(5.5), ip(frame, at(2, 0.62), 22));
  const cacheOut = 1 - prog(frame, at(3, 0), 14);
  const slots = 8 + (frame > insStart ? 1 : 0) - (frame > delGone + 3 * shiftStep + shiftLen ? 1 : 0);

  const cells = [...VALUES.map((v, id) => ({id, v})), {id: 8, v: 99}];

  return (
    <AbsoluteFill>
      <Stage pos={[cam.pos[0], cam.pos[1], cam.pos[2]]} target={cam.target} floor={-2.6}>
        {Array.from({length: 34}, (_, i) => {
          const x = (i - 16.5) * GAP;
          const o = ip(frame, Math.abs(i - 16.5) * 1.2, 20);
          return <Block key={'t' + i} position={[x, -1.45, 0]} size={[1.8, 0.16, 1.8]} color={C.panel} edge={C.border} glow={1.1} opacity={o * 0.9} />;
        })}

        {cells.map(({id, v}) => {
          const k = indexOf(id);
          let y = 0, scale = 1, color = C.panel, edge = C.muted, glow = 1.4;
          if (id === 8) {
            const appear = ip(frame, at(3, 0.05), 18, easeOutBack);
            scale = appear;
            y = lerp(2.6, 0, ip(frame, insDrop, 16));
            color = '#3a2a1c'; edge = C.orange; glow = 2.2;
          } else {
            const rise = ip(frame, 10 + id * 5, 24, easeOutBack);
            y = lerp(-3, 0, rise);
            scale = rise;
          }
          if (id === 5) {
            const hot = Math.min(ip(frame, at(1, 0.42), 8), 1 - prog(frame, at(2, 0.05), 15));
            if (hot > 0) { edge = C.orange; glow = 1.4 + hot * 1.6; color = '#2e2618'; y += hot * 0.35; }
          }
          if (id === 2) {
            const lift = ip(frame, delStart, 18, easeOut);
            y += lift * 2.4; edge = lift > 0 ? '#ff9b8a' : edge; glow += lift;
            scale *= 1 - ip(frame, delStart + 12, 16);
          }
          const pos: V3 = [slotX(k), y, 0];
          return (
            <group key={id}>
              <Block position={pos} color={color} edge={edge} glow={glow} scale={scale} />
              {scale > 0.05 && <Label text={String(v)} position={[pos[0], pos[1], 0.9]} size={0.62} bold mono opacity={Math.min(1, scale)} />}
            </group>
          );
        })}

        {Array.from({length: 9}, (_, k) => {
          const o = Math.min(ip(frame, at(0, 0.35) + k * 4, 12), k < slots ? 1 : 1 - prog(frame, delGone + 50, 10));
          const show = k < 8 || frame > insStart;
          return show && <Label key={'i' + k} text={String(k)} position={[slotX(k), -2.15, 0.6]} size={0.42} mono color={C.muted} opacity={o} />;
        })}
        {Array.from({length: 8}, (_, k) => {
          const o = Math.min(ip(frame, at(0, 0.55) + k * 3, 12), 1 - prog(frame, at(2, 0.15), 12));
          const hot = k === 5 && frame > at(1, 0.42);
          return <Label key={'a' + k} text={'0x' + (0x1000 + k * 4).toString(16).toUpperCase()} position={[slotX(k), 1.35, 0]} size={0.3}
            mono color={hot ? C.orange : C.muted} opacity={o} />;
        })}

        {beam > 0 && (
          <group position={[slotX(5), 4.6, 0]}>
            <mesh>
              <cylinderGeometry args={[0.07, 0.07, 7.5 * beam, 16]} />
              <meshBasicMaterial color={[3, 2.1, 1.3]} toneMapped={false} transparent opacity={beam} />
            </mesh>
            <mesh>
              <cylinderGeometry args={[0.5, 0.9, 7.5 * beam, 32, 1, true]} />
              <meshBasicMaterial color={C.orange} transparent opacity={0.08 * beam} depthWrite={false} />
            </mesh>
          </group>
        )}

        {cacheIn * cacheOut > 0 && (
          <group position={[cacheX, 0, 0]}>
            <GlassBox size={[GAP * 4 + 0.2, 2.3, 2.3]} color={C.green} opacity={cacheIn * cacheOut} />
            <Label text="一次读入一整块：缓存行" position={[0, 1.75, 0]} size={0.38} color={C.green} opacity={cacheIn * cacheOut} />
          </group>
        )}

        {frame > at(3, 0) && frame < at(3, 0) + 200 && (
          <Label text="插入 → 后面元素依次后移" position={[slotX(5), 3.1, 0]} size={0.36} color={C.orange}
            opacity={Math.min(ip(frame, at(3, 0.1), 12), 1 - prog(frame, insDrop + 20, 14))} />
        )}
        {frame > delStart && (
          <Label text="删除 → 后面元素依次前移" position={[slotX(4), 3.1, 0]} size={0.36} color="#ff9b8a"
            opacity={Math.min(ip(frame, delStart, 12), 1 - prog(frame, delGone + 70, 14))} />
        )}
      </Stage>

      <Card from={at(1, 0.15)} to={at(2, 0.05)} x={1150} y={170} w={640}>
        <div style={{color: C.muted, fontSize: 24}}>第 i 个元素的地址</div>
        <div><Mono>base + i × size</Mono></div>
        <div style={{fontSize: 26, marginTop: 6}}><Mono color={C.text}>0x1000 + 5 × 4 = </Mono><Mono>0x1014</Mono></div>
      </Card>
      <Badge from={at(1, 0.6)} to={at(2, 0.05)} x={1150} y={400} color={C.green}>随机访问 <Mono color={C.green}>O(1)</Mono></Badge>
      <Badge from={at(4, 0.45)} x={1848} y={170} align="right" color={C.green}>按下标访问 <Mono color={C.green}>O(1)</Mono></Badge>
      <Badge from={at(4, 0.55)} x={1848} y={240} align="right">插入 / 删除 <Mono>O(n)</Mono></Badge>
    </AbsoluteFill>
  );
};
