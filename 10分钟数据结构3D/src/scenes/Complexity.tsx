import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Block, Label, Line, PolyTube, Stage, V3} from '../three';
import {camPath, easeOut, ip, lerp, prog, useScene} from '../anim';
import {C, FONT, MONO} from '../theme';

const X0 = -8, X1 = 8, Y0 = -2.4, NMAX = 20, TB = 0.6;
const curve = (f: (n: number) => number, cap = 30): V3[] =>
  Array.from({length: 61}, (_, i) => {
    const n = (i / 60) * NMAX;
    return [lerp(X0, X1, i / 60), Math.min(Y0 + f(n), Y0 + cap), 0] as V3;
  }).filter((p, i, arr) => i === 0 || arr[i - 1][1] < Y0 + cap - 0.01);

const CURVES = [
  {name: 'O(1)', f: () => 0.4, color: C.green, beat: 1, frac: 0.05},
  {name: 'O(log n)', f: (n: number) => Math.log2(n + 1) * 0.42, color: C.green, beat: 1, frac: 0.18},
  {name: 'O(n)', f: (n: number) => n * 0.33, color: C.muted, beat: 1, frac: 0.36},
  {name: 'O(n²)', f: (n: number) => n * n * 0.075, color: C.ember, beat: 1, frac: 0.55},
  {name: 'O(n log n)', f: (n: number) => n * Math.log2(n + 1) * 0.085, color: C.orange, beat: 2, frac: 0.05},
];

export const Complexity: React.FC = () => {
  const {frame, at} = useScene();

  const axes = ip(frame, at(0, 0.1), 24, easeOut);
  const chartO = 1 - prog(frame, at(3, 0.02), 20);
  const towerT = ip(frame, at(3, 0.12), 70, (x) => x * x * (3 - 2 * x));
  const towerO = ip(frame, at(3, 0.05), 14);

  const n2Up = ip(frame, at(1, 0.55) + 30, 60);
  const cam = camPath(frame, [
    [0, [-6, 3.5, 22], [0, 1.6, 0]],
    [at(0, 0.9), [-3, 3, 20.5], [0, 1.9, 0]],
    [at(1, 0.55), [4, 3.5, 21.5], [0, 2.4, 0]],
    [at(1, 0.55) + 90, [7, 9, 36], [1, 8.5, 0]],
    [at(2, 0.05), [-2, 3.8, 21.5], [0, 2.4, 0]],
    [at(3, 0.05), [0, 3, 19], [0, 2.4, 0]],
    [at(3, 0.6), [2, 7, 30], [0, 8, 0]],
    [at(3, 1) + 40, [3, 10, 41], [0, 11, 0]],
  ]);

  const bigLog = Math.round(lerp(0, 20, ip(frame, at(3, 0.15), 30)));
  const bigN2 = Math.round(lerp(0, 1e12, ip(frame, at(3, 0.15), 80, (x) => x * x * x)));

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={Y0} fog={[30, 110]}>
        {chartO > 0 && (
          <group>
            <Line from={[X0, Y0, 0]} to={[lerp(X0, X1 + 1, axes), Y0, 0]} color={C.text} opacity={axes * chartO} glow={0.9} />
            <Line from={[X0, Y0, 0]} to={[X0, lerp(Y0, 8, axes), 0]} color={C.text} opacity={axes * chartO} glow={0.9} />
            <Label text="数据量 n" position={[X1 + 1.6, Y0 - 0.5, 0]} size={0.4} color={C.muted} opacity={axes * chartO} />
            <Label text="操作次数" position={[X0, 8.8, 0]} size={0.4} color={C.muted} opacity={axes * chartO} />
            {CURVES.map((c) => {
              const pts = curve(c.f);
              const t = ip(frame, at(c.beat, c.frac), 50, (x) => x);
              const end = pts[Math.max(0, Math.floor((pts.length - 1) * t))];
              return (
                <group key={c.name}>
                  <PolyTube points={pts} progress={t} color={c.color} radius={0.08} glow={1.7} opacity={chartO} />
                  {t > 0.05 && <Label text={c.name} position={[end[0] + 1.2, end[1] + 0.4, 0]} size={0.46} bold mono color={c.color} opacity={chartO} />}
                </group>
              );
            })}
            {n2Up > 0 && <Label text="冲上天际 ↑" position={[1.5, 14, 0]} size={0.6} bold color={C.ember} opacity={n2Up * (1 - prog(frame, at(2, 0), 12))} />}
            <Label text="归并排序 · 快速排序（平均）" position={[4.5, 2.2, 0]} size={0.36} color={C.orange} opacity={Math.min(ip(frame, at(2, 0.5), 14), chartO)} />
          </group>
        )}

        {towerO > 0 && (
          <group>
            <Block position={[-4.5, TB - 0.15, 0]} size={[12, 0.3, 4]} color={C.panel} edge={C.border} opacity={towerO} />
            <Block position={[-4.5, TB + 0.4, 0]} size={[2.6, 0.8, 2.6]} color="#16283a" edge={C.green} glow={2.4} opacity={towerO} />
            <Label text="O(log n)：20 步" position={[-4.5, TB + 1.6, 0]} size={0.55} bold color={C.green} opacity={towerO} />
            <Block position={[4.5, TB + (towerT * 60) / 2, 0]} size={[2.6, Math.max(0.05, towerT * 60), 2.6]} color="#2e1d16" edge={C.ember} glow={2.4}
              opacity={towerO} />
            <Label text="O(n²)" position={[4.5, TB + towerT * 60 + 1.2, 0]} size={0.6} bold mono color={C.ember} opacity={towerO} />
          </group>
        )}
      </Stage>

      {towerO > 0 && (
        <div style={{position: 'absolute', left: 110, top: 190, fontFamily: FONT, opacity: towerO}}>
          <div style={{fontSize: 30, color: C.muted}}>n = 1 000 000</div>
          <div style={{marginTop: 26, fontSize: 30, color: C.green}}>O(log n) ≈ <span style={{fontFamily: MONO, fontSize: 64}}>{bigLog}</span> 步</div>
          <div style={{marginTop: 18, fontSize: 30, color: C.ember}}>O(n²) = <span style={{fontFamily: MONO, fontSize: 64}}>{bigN2.toLocaleString('en-US')}</span> 步</div>
        </div>
      )}
    </AbsoluteFill>
  );
};
