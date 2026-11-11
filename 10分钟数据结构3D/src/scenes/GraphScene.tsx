import React from 'react';
import * as THREE from 'three';
import {AbsoluteFill} from 'remotion';
import {CurveArrow, Label, Orb, Stage, V3} from '../three';
import {camPath, easeOut, easeOutBack, ip, lerp3, prog, useScene} from '../anim';
import {C, FONT, MONO} from '../theme';
import {Badge} from '../ui';

const NAMES = 'ABCDEFGHIJ'.split('');
const POS: V3[] = [
  [-7.5, 0.4, 0], [-3.8, 3.8, 2], [-3.4, -2.8, -1.8], [0.4, 0.9, 3.6], [0.2, 4.6, -2.6],
  [0.8, -3.9, 1.6], [4.2, 2.2, -1.2], [4.4, -1.6, 3.0], [7.8, 0.8, 0.4], [-0.6, -0.6, -4.0],
];
const EDGES: [number, number, number][] = [
  [0, 1, 4], [0, 2, 2], [1, 3, 5], [1, 4, 3], [2, 5, 6], [2, 9, 3], [3, 6, 2], [3, 7, 4],
  [4, 6, 3], [5, 7, 2], [9, 6, 5], [6, 8, 4], [7, 8, 3], [9, 5, 4], [2, 3, 7],
];
const adj: [number, number][][] = NAMES.map(() => []);
EDGES.forEach(([a, b, w]) => { adj[a].push([b, w]); adj[b].push([a, w]); });
adj.forEach((l) => l.sort((x, y) => x[0] - y[0]));

const bfsLevel: number[] = NAMES.map(() => -1);
const bfsParent: number[] = NAMES.map(() => -1);
{
  const q = [0]; bfsLevel[0] = 0;
  while (q.length) {
    const u = q.shift()!;
    for (const [v] of adj[u]) if (bfsLevel[v] < 0) { bfsLevel[v] = bfsLevel[u] + 1; bfsParent[v] = u; q.push(v); }
  }
}
const maxLevel = Math.max(...bfsLevel);

const tour: number[] = [];
const dfsOrder: number[] = [];
{
  const seen = new Set<number>();
  const go = (u: number) => {
    seen.add(u); dfsOrder.push(u); tour.push(u);
    for (const [v] of adj[u]) if (!seen.has(v)) { go(v); tour.push(u); }
  };
  go(0);
}

const dist: number[] = NAMES.map(() => Infinity);
const prev: number[] = NAMES.map(() => -1);
const settleOrder: number[] = [];
{
  dist[0] = 0;
  const done = new Set<number>();
  while (done.size < NAMES.length) {
    let u = -1;
    for (let i = 0; i < NAMES.length; i++) if (!done.has(i) && (u < 0 || dist[i] < dist[u])) u = i;
    done.add(u); settleOrder.push(u);
    for (const [v, w] of adj[u]) if (dist[u] + w < dist[v]) { dist[v] = dist[u] + w; prev[v] = u; }
  }
}
const TARGET = 8;
const shortest: number[] = [];
for (let v = TARGET; v >= 0; v = prev[v]) shortest.unshift(v);
const onShortest = (a: number, b: number) => shortest.some((x, i) => i > 0 && ((shortest[i - 1] === a && x === b) || (shortest[i - 1] === b && x === a)));

export const GraphScene: React.FC = () => {
  const {frame, at} = useScene();

  const spin = frame * 0.0035;
  const nodeIn = (i: number) => ip(frame, at(0, 0.05) + i * 5, 18, easeOutBack);
  const edgeIn = (k: number) => ip(frame, at(0, 0.3) + k * 4, 18, easeOut);
  const weightO = Math.min(ip(frame, at(1, 0.15), 16), 1 - prog(frame, at(2, 0), 12) * 0.85 + prog(frame, at(4, 0), 12) * 0.85);
  const matrixO = Math.min(ip(frame, at(1, 0.4), 16), 1 - prog(frame, at(2, 0), 14));

  const bfsT = (l: number) => at(2, 0.18 + (l * 0.7) / maxLevel);
  const bfsOn = frame >= at(2, 0) && frame < at(3, 0);
  const waveR = ip(frame, at(2, 0.15), (at(2, 0.95) - at(2, 0.15)), (x) => x) * 16;

  const dfsStep = (at(3, 0.9) - at(3, 0.1)) / (tour.length - 1);
  const dfsK = Math.min(tour.length - 2, Math.max(0, Math.floor((frame - at(3, 0.1)) / dfsStep)));
  const dfsT = ip(frame, at(3, 0.1) + dfsK * dfsStep, dfsStep * 0.8, easeOut);
  const dfsOn = frame >= at(3, 0.05) && frame < at(4, 0);
  const dfsSeenAt = (i: number) => at(3, 0.1) + tour.indexOf(i) * dfsStep;
  const orb = lerp3(POS[tour[dfsK]], POS[tour[dfsK + 1]], frame < at(3, 0.1) ? 0 : dfsT);

  const djOn = frame >= at(4, 0);
  const settleT = (i: number) => at(4, 0.1 + settleOrder.indexOf(i) * 0.055);
  const pathT = ip(frame, at(4, 0.72), 24);

  const cam = camPath(frame, [
    [0, [0, 6, 28], [0, 0.3, 0]],
    [at(0, 0.9), [-4, 4, 22], [0, 0.3, 0]],
    [at(1, 0.9), [3, 3, 21], [2, 0.3, 0]],
    [at(2, 0.9), [-2, 6, 24], [0, 0.3, 0]],
    [at(3, 0.9), [4, 2, 21], [0, 0, 0]],
    [at(4, 1) + 40, [0, 5, 23], [0, 0.3, 0]],
  ]);

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={-6.5} bloom={1.25}>
        <group rotation={[0, spin, 0]}>
          {EDGES.map(([a, b, w], k) => {
            let color = C.border, glow = 2.0, r = 0.045;
            if (bfsOn && (bfsParent[b] === a || bfsParent[a] === b) && frame >= bfsT(Math.max(bfsLevel[a], bfsLevel[b]))) { color = C.orange; glow = 1.6; }
            if (dfsOn) {
              const i = tour.findIndex((x, j) => j > 0 && ((tour[j - 1] === a && x === b) || (tour[j - 1] === b && x === a)));
              if (i > 0 && frame >= at(3, 0.1) + (i - 1) * dfsStep + dfsStep * 0.8) { color = C.green; glow = 1.6; }
            }
            if (djOn && onShortest(a, b) && pathT > 0) { color = C.orange; glow = 1 + pathT * 1.4; r = 0.045 + pathT * 0.06; }
            const mid = lerp3(POS[a], POS[b], 0.5);
            return (
              <group key={k}>
                <CurveArrow from={POS[a]} to={POS[b]} head={k < 3 && frame > at(1, 0.05) && frame < at(2, 0)} radius={r} progress={edgeIn(k)} color={color}
                  glow={glow} trimStart={0.75} trimEnd={0.8} />
                <Label text={String(w)} position={[mid[0], mid[1] + 0.35, mid[2]]} size={0.32} mono color={C.orange} opacity={weightO * edgeIn(k)} />
              </group>
            );
          })}

          {NAMES.map((n, i) => {
            let color = C.muted, glow = 0.9;
            if (i === 0) { color = C.orange; glow = 1.4; }
            if (bfsOn && frame >= bfsT(bfsLevel[i])) { color = C.orange; glow = 1.2 + (1 - prog(frame, bfsT(bfsLevel[i]), 18)) * 1.8; }
            if (dfsOn && frame >= dfsSeenAt(i)) { color = C.green; glow = 1.2 + (1 - prog(frame, dfsSeenAt(i), 18)) * 1.8; }
            if (djOn && frame >= settleT(i)) { color = shortest.includes(i) && pathT > 0 ? C.orange : C.green; glow = 1.2 + (1 - prog(frame, settleT(i), 18)) * 1.6; }
            const s = nodeIn(i);
            return (
              <group key={n}>
                <Orb position={POS[i]} radius={0.62} color={color} glow={glow} scale={s} />
                <Label text={n} position={POS[i]} size={0.5} bold mono color={C.bg} glow={1} depthTest={false} opacity={s} />
                {bfsOn && <Label text={`L${bfsLevel[i]}`} position={[POS[i][0], POS[i][1] + 1.05, POS[i][2]]} size={0.3} mono color={C.orange}
                  opacity={ip(frame, bfsT(bfsLevel[i]), 10)} />}
                {dfsOn && <Label text={`#${dfsOrder.indexOf(i) + 1}`} position={[POS[i][0], POS[i][1] + 1.05, POS[i][2]]} size={0.3} mono color={C.green}
                  opacity={ip(frame, dfsSeenAt(i), 10)} />}
                {djOn && <Label text={`d=${dist[i]}`} position={[POS[i][0], POS[i][1] + 1.05, POS[i][2]]} size={0.32} mono
                  color={shortest.includes(i) && pathT > 0 ? C.orange : C.green} opacity={ip(frame, settleT(i), 10)} />}
              </group>
            );
          })}

          {bfsOn && waveR > 0 && (
            <mesh position={POS[0]} scale={waveR}>
              <sphereGeometry args={[1, 36, 22]} />
              <meshBasicMaterial color={new THREE.Color(C.orange).multiplyScalar(1.4)} transparent opacity={0.05 * (1 - waveR / 16)}
                side={THREE.BackSide} depthWrite={false} toneMapped={false} wireframe />
            </mesh>
          )}
          {dfsOn && frame >= at(3, 0.08) && <Orb position={[orb[0], orb[1] + 0.9, orb[2]]} radius={0.24} color={C.green} glow={3} />}
          <Label text="起点" position={[POS[0][0] - 1.6, POS[0][1] + 0.9, POS[0][2]]} size={0.36} color={C.orange} opacity={ip(frame, at(2, 0.05), 12)} />
        </group>
      </Stage>

      {matrixO > 0 && (
        <div style={{position: 'absolute', right: 70, top: 150, opacity: matrixO, padding: 22, borderRadius: 16, background: 'rgba(18,32,51,0.9)',
          border: `1px solid ${C.border}`, fontFamily: MONO}}>
          <div style={{fontFamily: FONT, fontSize: 22, color: C.muted, marginBottom: 10}}>邻接矩阵</div>
          <div style={{display: 'grid', gridTemplateColumns: `repeat(11, 30px)`, gap: 3, fontSize: 16, color: C.muted}}>
            <div />
            {NAMES.map((n) => <div key={n} style={{textAlign: 'center'}}>{n}</div>)}
            {NAMES.map((r, i) => (
              <React.Fragment key={r}>
                <div style={{textAlign: 'center'}}>{r}</div>
                {NAMES.map((_, j) => {
                  const e = EDGES.find(([a, b]) => (a === i && b === j) || (a === j && b === i));
                  const lit = e && frame >= at(1, 0.4) + (i * 10 + j) * 0.6;
                  return <div key={j} style={{height: 30, borderRadius: 5, background: lit ? '#3a2a1c' : '#0f1a2a',
                    border: `1px solid ${lit ? C.orange : C.border}`, color: C.orange, fontSize: 15, display: 'flex', alignItems: 'center',
                    justifyContent: 'center'}}>{lit ? e![2] : ''}</div>;
                })}
              </React.Fragment>
            ))}
          </div>
          <div style={{fontFamily: FONT, fontSize: 22, color: C.muted, marginTop: 14}}>邻接表　<span style={{color: C.text, fontFamily: MONO}}>A → B(4), C(2)</span></div>
        </div>
      )}
      <Badge from={at(2, 0.1)} to={at(3, 0)} x={1848} y={170} align="right">BFS：队列，一层一层</Badge>
      <Badge from={at(3, 0.08)} to={at(4, 0)} x={1848} y={170} align="right" color={C.green}>DFS：栈，一路到底再回退</Badge>
      <Badge from={at(4, 0.08)} x={1848} y={170} align="right">Dijkstra：每次确定最近的顶点</Badge>
      <Badge from={at(4, 0.74)} x={1848} y={240} align="right" color={C.green}>
        最短路径 <span style={{fontFamily: MONO, color: C.orange}}>{shortest.map((i) => NAMES[i]).join(' → ')} = {dist[TARGET]}</span>
      </Badge>
    </AbsoluteFill>
  );
};
