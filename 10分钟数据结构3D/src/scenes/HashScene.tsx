import React from 'react';
import * as THREE from 'three';
import {AbsoluteFill} from 'remotion';
import {Block, CurveArrow, GlassBox, Label, Ring, Stage, V3} from '../three';
import {camPath, easeInOut, easeOut, ip, lerp, lerp3, prog, useScene} from '../anim';
import {C} from '../theme';
import {Badge, Card, Mono} from '../ui';

const HASH: V3 = [-3.2, 1.2, 0];
const bucketX = (k: number, n: number) => (n === 8 ? 1.0 + k * 1.45 : 0.4 + k * 0.76);
const BASE = -2.4;

type K = {key: string; b8: number; b16: number; start: number; level?: number; probe?: number};

export const HashScene: React.FC = () => {
  const {frame, at} = useScene();

  const keys: K[] = [
    {key: 'apple', b8: 3, b16: 3, start: at(1, 0.14)},
    {key: 'cat', b8: 6, b16: 6, start: at(1, 0.42)},
    {key: 'dog', b8: 1, b16: 9, start: at(1, 0.68)},
    {key: 'sun', b8: 3, b16: 11, start: at(2, 0.12), level: 1},
    {key: 'moon', b8: 5, b16: 13, start: at(2, 0.62)},
    {key: 'key', b8: 7, b16: 7, start: at(3, 0.1), probe: 6},
  ];
  const resize = ip(frame, at(4, 0.12), 40, easeInOut);
  const n = resize > 0 ? 16 : 8;
  const bucketCount = resize > 0.02 ? 16 : 8;

  const torusSpin = frame * 0.05;
  const fly = 34, dwell = 18;

  const cam = camPath(frame, [
    [0, [-6, 5, 22], [-1, 0.5, 0]],
    [at(1, 0.1), [-4, 4, 18], [0, 0.5, 0]],
    [at(2, 0.1), [6, 3.5, 15], [5, -0.2, 0]],
    [at(3, 0.1), [12, 3.5, 13], [9, -0.5, 0]],
    [at(4, 0.1), [5, 5, 16.5], [5, 0, 0]],
    [at(4, 1) + 40, [3.5, 4.5, 17], [4.5, 0, 0]],
  ]);

  const collision = Math.min(ip(frame, keys[3].start + fly + dwell + 14, 8), 1 - prog(frame, at(2, 0.55), 14));

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={BASE - 0.4}>
        {/* hash function */}
        <group position={HASH} rotation={[0, Math.PI / 2.4, 0]} scale={ip(frame, 10, 30, easeOut)}>
          <mesh rotation={[torusSpin, 0, 0]}>
            <torusGeometry args={[1.5, 0.09, 16, 120]} />
            <meshBasicMaterial color={new THREE.Color(C.orange).multiplyScalar(2)} toneMapped={false} />
          </mesh>
          <mesh rotation={[0, torusSpin * 0.7, torusSpin * 0.5]}>
            <torusGeometry args={[1.15, 0.05, 12, 100]} />
            <meshBasicMaterial color={new THREE.Color(C.green).multiplyScalar(1.8)} toneMapped={false} />
          </mesh>
          <mesh>
            <sphereGeometry args={[0.95, 32, 24]} />
            <meshBasicMaterial color={C.orange} transparent opacity={0.08} depthWrite={false} />
          </mesh>
        </group>
        <Label text="hash(key) % n" position={[HASH[0], HASH[1] + 2.3, 0]} size={0.4} mono color={C.orange} opacity={ip(frame, 20, 20)} />

        {/* buckets */}
        {Array.from({length: bucketCount}, (_, k) => {
          const n0 = 8;
          const x = k < 8 ? lerp(bucketX(k, n0), bucketX(k, 16), resize) : bucketX(k, 16);
          const o = k < 8 ? ip(frame, at(0, 0.3) + k * 3, 14) : ip(frame, at(4, 0.2) + (k - 8) * 3, 14);
          const w = lerp(1.25, 0.66, resize);
          const hot = collision > 0 && k === 3;
          const probeHot = frame > keys[5].start + fly && frame < at(4, 0) && (k === 6 || k === 7);
          return (
            <group key={k}>
              <GlassBox position={[x, BASE + 2.4, 0]} size={[w, 4.8, w]} color={hot ? '#ff9b8a' : probeHot ? C.orange : C.muted}
                fill={hot ? 0.16 : 0.04} glow={hot ? 2.2 : 1.1} opacity={o} />
              <Label text={String(k)} position={[x, BASE - 0.45, w / 2 + 0.1]} size={0.32} mono color={C.muted} opacity={o} />
            </group>
          );
        })}

        {keys.map((k, i) => {
          if (frame < k.start - 40) return null;
          const startPos: V3 = [-11, 3.2 - i * 0.95, 0];
          const appear = ip(frame, at(0, 0.08) + i * 4, 14);
          const lvl = k.level ?? 0;
          const b8 = k.b8;
          const target8: V3 = [bucketX(b8, 8), BASE + 0.5 + lvl * 1.15, 0];
          const target16: V3 = [bucketX(k.b16, 16), BASE + 0.45, 0];
          let p: V3;
          const t1 = ip(frame, k.start, fly, easeInOut);
          const t2 = ip(frame, k.start + fly + dwell, fly, easeInOut);
          if (frame < k.start + fly + dwell) p = lerp3(startPos, HASH, t1);
          else if (k.probe !== undefined) {
            const probeAt: V3 = [bucketX(k.probe, 8), BASE + 1.65, 0];
            const t3 = ip(frame, k.start + fly * 2 + dwell + 14, 24, easeOut);
            p = t3 <= 0 ? lerp3(HASH, probeAt, t2) : lerp3(probeAt, target8, t3);
            p[1] += Math.sin(t3 * Math.PI) * 1.2;
          } else {
            p = lerp3(HASH, target8, t2);
            p[1] += Math.sin(t2 * Math.PI) * 2;
          }
          if (resize > 0) p = lerp3(target8, target16, resize).map((v, j) => (j === 1 ? v + Math.sin(resize * Math.PI) * 1.5 : v)) as V3;
          const inHash = frame > k.start + fly - 6 && frame < k.start + fly + dwell;
          const size = lerp(1.05, 0.62, resize);
          const visible = k.start - 40 < frame;
          const o = appear * (visible ? 1 : 0);
          return (
            <group key={k.key}>
              <Block position={p} size={[size, size, size]} color="#2e2618" edge={inHash ? C.green : C.orange} glow={inHash ? 3 : 1.8} opacity={o}
                scale={inHash ? 0.8 : 1} />
              <Label text={k.key} position={[p[0], p[1], p[2] + size * 0.5 + 0.05]} size={lerp(0.3, 0.2, resize)} mono bold opacity={o} depthTest={false} />
              {frame > k.start + fly - 4 && frame < k.start + fly + dwell + 20 && (
                <Label text={`→ ${k.probe ?? b8}`} position={[HASH[0] + 0.2, HASH[1] - 2.0, 0]} size={0.5} bold mono color={C.green}
                  opacity={Math.min(ip(frame, k.start + fly - 4, 8), 1 - prog(frame, k.start + fly + dwell + 6, 12))} />
              )}
            </group>
          );
        })}

        <CurveArrow from={[bucketX(3, 8), BASE + 1.05, 0.2]} to={[bucketX(3, 8), BASE + 1.15 + 0.2, 0.2]} progress={resize > 0 ? 0 : ip(frame, keys[3].start + fly * 2 + dwell, 12)}
          color={C.green} radius={0.06} />
        {collision > 0 && <Label text="冲突！链地址法：挂成链表" position={[bucketX(3, 8), BASE + 5.4, 0]} size={0.4} color="#ff9b8a" opacity={collision} />}
        {frame > keys[5].start + fly && frame < at(4, 0.05) && (
          <Label text="6 已占 → 探测 7" position={[bucketX(6.5, 8), BASE + 5.4, 0]} size={0.4} color={C.orange}
            opacity={Math.min(ip(frame, keys[5].start + fly + dwell, 12), 1 - prog(frame, at(4, 0), 10))} />
        )}
        {resize > 0 && <Ring position={[6, BASE + 2.4, 0]} radius={lerp(1, 12, ip(frame, at(4, 0.12), 30, easeOut))} width={0.06} color={C.green}
          opacity={1 - prog(frame, at(4, 0.12), 30)} rotation={[0, Math.PI / 2, 0]} />}
        {resize > 0 && <Label text="扩容：8 → 16 个桶，重新分布" position={[6, BASE + 5.6, 0]} size={0.42} color={C.green} opacity={ip(frame, at(4, 0.25), 14)} />}
      </Stage>

      <Card from={at(1, 0.05)} to={at(2, 0.05)} x={1150} y={150} w={660}>
        <div><Mono>hash("apple") = 9 832 107</Mono></div>
        <div><Mono color={C.text}>9 832 107 % 8 = </Mono><Mono color={C.green}>3</Mono></div>
      </Card>
      <Badge from={at(4, 0.5)} x={1848} y={170} align="right" color={C.green}>平均 查找 / 插入 / 删除 <Mono color={C.green}>O(1)</Mono></Badge>
      <Badge from={at(4, 0.7)} x={1848} y={240} align="right" color={C.muted}>Python dict · Java HashMap</Badge>
    </AbsoluteFill>
  );
};
