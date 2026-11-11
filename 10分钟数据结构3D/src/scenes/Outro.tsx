import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Block, CurveArrow, Label, Line, Orb, Ring, Stage, V3} from '../three';
import {camPath, easeInOut, easeOut, ip, lerp, prog, useScene} from '../anim';
import {C, FONT} from '../theme';

type IconProps = {hot: number};
const edgeOf = (hot: number) => (hot > 0 ? C.orange : C.muted);
const glowOf = (hot: number) => 1.3 + hot * 1.2;

const ArrayIcon: React.FC<IconProps> = ({hot}) => (
  <group>{[0, 1, 2, 3].map((i) => <Block key={i} position={[(i - 1.5) * 0.75, 0, 0]} size={[0.66, 0.66, 0.66]} edge={edgeOf(hot)} glow={glowOf(hot)} />)}</group>
);
const ListIcon: React.FC<IconProps> = ({hot}) => (
  <group>
    {[0, 1, 2].map((i) => <Orb key={i} position={[(i - 1) * 1.1, (i % 2) * 0.4 - 0.2, 0]} radius={0.28} color={hot ? C.orange : C.muted} glow={glowOf(hot) * 0.8} />)}
    <CurveArrow from={[-0.8, -0.2, 0]} to={[-0.3, 0.2, 0]} radius={0.03} color={edgeOf(hot)} />
    <CurveArrow from={[0.3, 0.2, 0]} to={[0.8, -0.2, 0]} radius={0.03} color={edgeOf(hot)} />
  </group>
);
const StackIcon: React.FC<IconProps> = ({hot}) => (
  <group>{[0, 1, 2].map((i) => <Block key={i} position={[0, (i - 1) * 0.42, 0]} size={[1.4, 0.34, 1.1]} edge={edgeOf(hot)} glow={glowOf(hot)} />)}</group>
);
const QueueIcon: React.FC<IconProps & {frame: number}> = ({hot, frame}) => (
  <group rotation={[0.9, frame * 0.02, 0]}>
    {Array.from({length: 6}, (_, i) => {
      const a = (i / 6) * Math.PI * 2;
      return <Block key={i} position={[Math.cos(a) * 0.8, 0, Math.sin(a) * 0.8]} size={[0.4, 0.4, 0.4]} edge={edgeOf(hot)} glow={glowOf(hot)} />;
    })}
  </group>
);
const HashIcon: React.FC<IconProps> = ({hot}) => (
  <group>{[0, 1, 2, 3].map((i) => <Block key={i} position={[(i - 1.5) * 0.55, -0.4 + [1, 2, 1, 3][i] * 0.25, 0]} size={[0.42, [1, 2, 1, 3][i] * 0.5, 0.42]}
    edge={edgeOf(hot)} glow={glowOf(hot)} />)}</group>
);
const TreeIcon: React.FC<IconProps> = ({hot}) => {
  const p: V3[] = [[0, 0.6, 0], [-0.6, -0.1, 0], [0.6, -0.1, 0], [-0.9, -0.8, 0], [-0.3, -0.8, 0]];
  return (
    <group>
      {[[0, 1], [0, 2], [1, 3], [1, 4]].map(([a, b]) => <Line key={a + '-' + b} from={p[a]} to={p[b]} color={edgeOf(hot)} glow={1.6} />)}
      {p.map((q, i) => <Orb key={i} position={q} radius={0.2} color={hot ? C.green : C.muted} glow={glowOf(hot) * 0.8} />)}
    </group>
  );
};
const HeapIcon: React.FC<IconProps> = ({hot}) => {
  const p: V3[] = [[0, 0.6, 0], [-0.55, -0.1, 0], [0.55, -0.1, 0], [-0.8, -0.8, 0], [-0.3, -0.8, 0], [0.3, -0.8, 0], [0.8, -0.8, 0]];
  return (
    <group>
      {[[0, 1], [0, 2], [1, 3], [1, 4], [2, 5], [2, 6]].map(([a, b]) => <Line key={a + '-' + b} from={p[a]} to={p[b]} color={edgeOf(hot)} glow={1.6} />)}
      {p.map((q, i) => <Orb key={i} position={q} radius={i === 0 ? 0.26 : 0.17} color={i === 0 ? C.orange : hot ? C.green : C.muted} glow={glowOf(hot) * 0.8} />)}
    </group>
  );
};
const GraphIcon: React.FC<IconProps> = ({hot}) => {
  const p: V3[] = [[-0.8, 0.3, 0.2], [0, 0.8, -0.3], [0.8, 0.2, 0.2], [0.3, -0.6, 0.4], [-0.5, -0.6, -0.3]];
  return (
    <group>
      {[[0, 1], [1, 2], [2, 3], [3, 4], [4, 0], [1, 3], [0, 3]].map(([a, b]) => <Line key={a + '-' + b} from={p[a]} to={p[b]} color={edgeOf(hot)} glow={1.6} />)}
      {p.map((q, i) => <Orb key={i} position={q} radius={0.18} color={hot ? C.orange : C.muted} glow={glowOf(hot) * 0.8} />)}
    </group>
  );
};

const ITEMS = [
  {name: '数组', use: '按位置读取'},
  {name: '链表', use: '频繁插入删除'},
  {name: '栈', use: '后进先出'},
  {name: '队列', use: '先进先出'},
  {name: '哈希表', use: '按键查找'},
  {name: '平衡树', use: '有序 · 范围查询'},
  {name: '堆', use: '反复取最值'},
  {name: '图', use: '关系网络'},
];

export const Outro: React.FC = () => {
  const {frame, at} = useScene();
  const R = 8.2;
  const spin = frame * 0.0022;
  const hotAt = (k: number) => (k < 4 ? at(0, 0.08 + k * 0.22) : at(1, 0.06 + (k - 4) * 0.22));
  const gather = ip(frame, at(2, 0.3), 46, easeInOut);
  const blast = prog(frame, at(2, 0.3) + 40, 34);
  const finalO = ip(frame, at(2, 0.3) + 56, 24, easeOut);

  const cam = camPath(frame, [
    [0, [0, 9, 24], [0, 0, 0]],
    [at(1, 0.9), [0, 6, 21], [0, 0, 0]],
    [at(2, 0.4), [0, 3, 17], [0, 0, 0]],
    [at(2, 1) + 40, [0, 2, 15], [0, 0.5, 0]],
  ]);

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={-3.5} bloom={1.4}>
        <group rotation={[0, spin, 0]}>
          {ITEMS.map((it, k) => {
            const a = (k / 8) * Math.PI * 2;
            const r = lerp(R, 0, gather);
            const pos: V3 = [Math.sin(a) * r, Math.sin(k * 1.3) * 0.4 * (1 - gather), Math.cos(a) * r];
            const appear = ip(frame, k * 4, 22, easeOut);
            const hot = frame >= hotAt(k) ? 1 - prog(frame, hotAt(k), 30) * 0.6 : 0;
            const s = appear * (1 - gather);
            if (s <= 0.01) return null;
            const Icon = [ArrayIcon, ListIcon, StackIcon, null, HashIcon, TreeIcon, HeapIcon, GraphIcon][k];
            return (
              <group key={it.name} position={pos} scale={s} rotation={[0, -spin, 0]}>
                {Icon ? <Icon hot={hot} /> : <QueueIcon hot={hot} frame={frame} />}
                <Label text={it.name} position={[0, 1.55, 0]} size={0.5} bold color={hot ? C.orange : C.text} />
                <Label text={it.use} position={[0, -1.6, 0]} size={0.42} color={hot ? C.green : C.muted} opacity={ip(frame, hotAt(k), 14)} />
                {hot > 0.5 && <Ring position={[0, 0, 0]} radius={1.6 + (1 - hot) * 2} width={0.05} color={C.orange} opacity={(hot - 0.4) * 1.6} />}
              </group>
            );
          })}
        </group>
        {blast > 0 && blast < 1 && (
          <>
            <Ring position={[0, 0, 0]} radius={blast * 26} width={0.12} color={C.orange} opacity={1 - blast} rotation={[-Math.PI / 2, 0, 0]} />
            <Ring position={[0, 0, 0]} radius={blast * 18} width={0.08} color={C.green} opacity={1 - blast} />
          </>
        )}
        {gather > 0.6 && blast < 1 && <Orb position={[0, 0, 0]} radius={0.6 + blast * 0.6} color={C.orange} glow={3} opacity={1 - blast} />}
      </Stage>

      {finalO > 0 && (
        <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', fontFamily: FONT}}>
          <div style={{textAlign: 'center', opacity: finalO, transform: `translateY(${(1 - finalO) * 30}px)`}}>
            <div style={{fontSize: 76, fontWeight: 800, color: C.text, letterSpacing: 10, textShadow: `0 0 40px ${C.orange}55`}}>没有最好的结构</div>
            <div style={{fontSize: 76, fontWeight: 800, color: C.orange, letterSpacing: 10, marginTop: 6}}>只有最合适的</div>
            <div style={{fontSize: 32, color: C.muted, marginTop: 34, letterSpacing: 8, opacity: ip(frame, at(2, 0.8), 20)}}>感谢观看</div>
          </div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
