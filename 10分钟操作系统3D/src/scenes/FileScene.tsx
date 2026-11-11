import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Block, CurveArrow, Label, Line, Orb, PolyTube, Ring, Stage, V3} from '../three';
import {camPath, easeOut, ip, lerp, prog, pulse, track, useScene, vis} from '../anim';
import {C} from '../theme';
import {Badge, Mono} from '../ui';

type Node = {n: string; p: V3; parent: number; dir: boolean};
const TREE: Node[] = [
  {n: '/', p: [-1, 3.6, 0], parent: -1, dir: true},
  {n: 'home', p: [-6.5, 1.2, 0], parent: 0, dir: true},
  {n: 'bin', p: [-1, 1.2, 0], parent: 0, dir: true},
  {n: 'etc', p: [4.5, 1.2, 0], parent: 0, dir: true},
  {n: 'user', p: [-8.5, -1.2, 0], parent: 1, dir: true},
  {n: 'share', p: [-4.5, -1.2, 0], parent: 1, dir: true},
  {n: 'notes.txt', p: [-10.0, -3.4, 0], parent: 4, dir: false},
  {n: 'pic.png', p: [-7.0, -3.4, 0], parent: 4, dir: false},
  {n: 'ls', p: [-2.0, -1.2, 0], parent: 2, dir: false},
  {n: 'passwd', p: [4.5, -1.2, 0], parent: 3, dir: false},
];
const PATH = [0, 1, 4, 6];

const CELL_X = (i: number) => -6.0 + i * 1.1;
const CELL = 0.92;

export const FileScene: React.FC = () => {
  const {frame, at, bd} = useScene();

  const g0 = vis(frame, 0, at(1, 0) - 4, 14);
  const g1 = vis(frame, at(1, 0.0), at(2, 0) - 4, 14);
  const g2 = vis(frame, at(2, 0.0), at(3, 0) - 4, 14);
  const g3 = vis(frame, at(3, 0.0), at(4, 0) - 4, 14);
  const g4 = vis(frame, at(4, 0.0), 1e9, 14);

  // —— 第 1 句：目录树 + 路径 ——
  const pathT = ip(frame, at(0, 0.5), bd(0) * 0.4);
  const pathPts: V3[] = PATH.map((i) => [TREE[i].p[0], TREE[i].p[1], 0.3]);

  // —— 第 3 句：三种分配 ——
  const ROWS = [
    {y: 2.8, name: '连续', note: '读得快 · 容易有碎片', color: C.gold, cells: [2, 3, 4, 5, 6]},
    {y: 0.2, name: '链接', note: '无碎片 · 只能顺序访问', color: C.cyan, cells: [1, 4, 6, 9, 11]},
    {y: -2.4, name: '索引', note: '随机访问方便', color: C.pink, cells: [3, 5, 8, 10], idx: 0},
  ];

  // —— 第 5 句：日志 ——
  const logW = ip(frame, at(4, 0.08), bd(4) * 0.2);
  const commit = ip(frame, at(4, 0.34), 12);
  const apply1 = ip(frame, at(4, 0.4), bd(4) * 0.12);
  const crashT = at(4, 0.58);
  const crashed = frame >= crashT && frame < at(4, 0.9);
  const replay = ip(frame, at(4, 0.7), bd(4) * 0.2);
  const mainOK = frame >= at(4, 0.9);
  const orbJ = frame < crashT
    ? (frame < at(4, 0.3) ? track(frame, [[at(4, 0.08), [-9.0, -0.4, 0]], [at(4, 0.28), [-5.8, -1.4, 0.8]]]) : track(frame, [[at(4, 0.4), [-4.0, -1.2, 0.8]], [at(4, 0.52), [0.2, -1.2, 0.8]]]))
    : track(frame, [[at(4, 0.7), [-4.0, -1.2, 0.8]], [at(4, 0.88), [4.4, -1.2, 0.8]]]);
  const orbO = frame < at(4, 0.28) ? ip(frame, at(4, 0.08), 8) * (1 - prog(frame, at(4, 0.28), 8))
    : frame < at(4, 0.4) ? 0 : frame < crashT ? 1 - prog(frame, crashT - 6, 6) : vis(frame, at(4, 0.7), at(4, 0.9), 8);

  const cam = camPath(frame, [
    [0, [-2, 3, 24], [-3, 0, 0]],
    [at(1, 0.5), [0, 2.5, 22], [0, 0, 0]],
    [at(2, 0.5), [0, 2.5, 23], [0, 0, 0]],
    [at(3, 0.5), [0, 2, 22], [0, -0.3, 0]],
    [at(4, 0.4), [0, 2.5, 22], [0, 0, 0]],
    [at(4, 1) + 40, [-2, 3, 23], [0, 0, 0]],
  ]);

  const cube = (p: V3, color: string, o: number, label?: string, s = 0.8) => (
    <group>
      <Block position={p} size={[s, s, s]} color={C.panel2} edge={color} opacity={o} glow={2} />
      {label && <Label text={label} position={[p[0], p[1], p[2] + s / 2 + 0.05]} size={0.26} bold mono opacity={o} depthTest={false} />}
    </group>
  );

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={-5}>
        {/* —— 目录树 —— */}
        {TREE.map((t, i) => {
          const o = ip(frame, at(0, 0.04 + i * 0.045), 14) * g0;
          const onPath = PATH.includes(i);
          const hi = onPath ? ip(frame, at(0, 0.5 + PATH.indexOf(i) * 0.1), 12) : 0;
          const par = t.parent >= 0 ? TREE[t.parent] : null;
          return (
            <group key={t.n}>
              {par && <Line from={[par.p[0], par.p[1] - 0.45, 0]} to={[t.p[0], t.p[1] + 0.45, 0]} color={C.muted} opacity={o * 0.8} />}
              <Block position={t.p} size={t.dir ? [2.0, 0.9, 1.2] : [2.2, 0.7, 1.0]} color={C.panel2} edge={hi > 0.5 ? C.gold : t.dir ? C.cyan : C.pink} opacity={o}
                glow={hi > 0.5 ? 2.6 : 1.6} emissive={0.3 + hi * 0.5} />
              <Label text={t.n} position={[t.p[0], t.p[1], 0.65]} size={t.dir ? 0.4 : 0.32} bold mono opacity={o} depthTest={false} />
            </group>
          );
        })}
        {pathT > 0.01 && <PolyTube points={pathPts} progress={Math.min(0.999, pathT)} color={C.gold} radius={0.07} opacity={g0} />}
        <Label text="/home/user/notes.txt" position={[3.6, -2.2, 0.4]} size={0.62} bold mono bg="#171433ee" border={C.gold} color={C.gold} opacity={vis(frame, at(0, 0.62)) * g0} depthTest={false} />
        <Label text="从根目录出发，一路沿着路径找到文件" position={[3.6, -3.4, 0.4]} size={0.34} color={C.muted} opacity={vis(frame, at(0, 0.75)) * g0} />

        {/* —— inode —— */}
        <Block position={[-7.4, 0.8, 0]} size={[4.0, 3.2, 0.4]} color={C.panel2} edge={C.cyan} opacity={ip(frame, at(1, 0.04), 16) * g1} glow={1.8} />
        <Label text="目录" position={[-7.4, 2.7, 0.4]} size={0.4} bold color={C.cyan} opacity={ip(frame, at(1, 0.06), 14) * g1} />
        {[['notes.txt', 1024], ['pic.png', 1031]].map(([n, id], k) => (
          <group key={n as string}>
            {k === 0 && <Block position={[-7.4, 1.5, 0.3]} size={[3.7, 0.7, 0.2]} color={C.gold} edge={C.gold} opacity={ip(frame, at(1, 0.3), 12) * 0.9 * g1} glow={2.4} emissive={0.8} />}
            <Label text={`${n}  →  ${id}`} position={[-7.4, 1.5 - k * 0.9, 0.45]} size={0.3} mono bold color={k === 0 && frame > at(1, 0.3) ? C.bg : C.text}
              opacity={ip(frame, at(1, 0.1 + k * 0.05), 12) * g1} depthTest={false} />
          </group>
        ))}
        <CurveArrow from={[-5.2, 1.5, 0.5]} to={[-2.6, 1.0, 0.5]} bend={[0, 0.6, 0]} color={C.gold} radius={0.05} progress={ip(frame, at(1, 0.34), 20)} opacity={g1} />
        <Block position={[0.3, 0.3, 0]} size={[4.8, 5.4, 0.5]} color="#2a1a40" edge={C.pink} opacity={ip(frame, at(1, 0.36), 18) * g1} glow={2} emissive={0.3} />
        <Label text="inode #1024" position={[0.3, 2.5, 0.4]} size={0.46} bold mono color={C.pink} opacity={ip(frame, at(1, 0.4), 14) * g1} />
        {['大小   12 KB', '权限   rw-r--r--', '时间   2026-11-02', '数据块指针 →'].map((f, k) => (
          <Label key={f} text={f} position={[0.3, 1.4 - k * 1.0, 0.45]} size={0.34} mono bold={k === 3} color={k === 3 ? C.cyan : C.text}
            opacity={ip(frame, at(1, 0.44 + k * 0.08), 12) * g1} depthTest={false} />
        ))}
        {[0, 1, 2].map((k) => (
          <group key={k}>
            {cube([6.4, 1.8 - k * 1.5, 0], C.cyan, ip(frame, at(1, 0.74 + k * 0.05), 12) * g1, `块${k}`, 1.0)}
            <CurveArrow from={[2.8, 0.5, 0.3]} to={[5.7, 1.8 - k * 1.5, 0.3]} bend={[0, 0.3, 0]} color={C.cyan} radius={0.03} progress={ip(frame, at(1, 0.72 + k * 0.05), 18)} opacity={g1 * 0.9} />
          </group>
        ))}
        <Label text="文件名只是目录里的一个条目" position={[-5.4, -3.2, 0.4]} size={0.42} bold color={C.gold} opacity={vis(frame, at(1, 0.55), at(2, 0)) * g1} />
        <Label text="文件的真身是 inode" position={[0.3, -3.2, 0.4]} size={0.42} bold color={C.pink} opacity={vis(frame, at(1, 0.84), at(2, 0)) * g1} />

        {/* —— 三种数据块分配 —— */}
        {ROWS.map((r, k) => {
          const t0 = at(2, 0.04 + k * 0.3);
          return (
            <group key={r.name}>
              <Label text={r.name} position={[-9.4, r.y, 0.5]} size={0.5} bold color={r.color} opacity={ip(frame, t0, 14) * g2} />
              {Array.from({length: 12}, (_, i) => {
                const used = r.cells.indexOf(i);
                const isIndexCell = r.idx === i;
                const lit = used >= 0 ? ip(frame, t0 + 8 + used * 8, 12, easeOut) : isIndexCell ? ip(frame, t0 + 8, 12) : 0;
                return <Block key={i} position={[CELL_X(i), r.y, 0]} size={[CELL, CELL, CELL]} color={lit > 0 ? C.panel2 : C.panel}
                  edge={lit > 0 ? (isIndexCell ? C.gold : r.color) : C.border} opacity={ip(frame, t0 - 4, 14) * g2 * (lit > 0 ? 1 : 0.55)} glow={lit > 0 ? 2 : 1} emissive={0.15 + lit * 0.3} />;
              })}
              {isIdx(r) && <Label text="索引" position={[CELL_X(0), r.y, 0.55]} size={0.28} bold color={C.gold} opacity={ip(frame, t0 + 8, 12) * g2} depthTest={false} />}
              <Label text={r.note} position={[9.3, r.y, 0.5]} size={0.34} bold color={r.color} opacity={ip(frame, t0 + 50, 14) * g2} />
            </group>
          );
        })}
        {/* 链接箭头 */}
        {ROWS[1].cells.slice(0, -1).map((c, i) => (
          <CurveArrow key={i} from={[CELL_X(c), ROWS[1].y + 0.5, 0]} to={[CELL_X(ROWS[1].cells[i + 1]), ROWS[1].y + 0.5, 0]} bend={[0, 0.7, 0]} color={C.cyan} radius={0.03}
            progress={ip(frame, at(2, 0.34 + 0.14 + i * 0.03), 14)} opacity={g2} trimStart={0.2} trimEnd={0.25} />
        ))}
        {/* 索引箭头 */}
        {ROWS[2].cells.map((c, i) => (
          <CurveArrow key={i} from={[CELL_X(0), ROWS[2].y - 0.5, 0]} to={[CELL_X(c), ROWS[2].y - 0.5, 0]} bend={[0, -0.9 - i * 0.12, 0]} color={C.pink} radius={0.03}
            progress={ip(frame, at(2, 0.64 + 0.14 + i * 0.03), 14)} opacity={g2} trimStart={0.2} trimEnd={0.25} />
        ))}

        {/* —— inode 多级指针 —— */}
        <Block position={[-8.4, 0.0, 0]} size={[3.2, 6.0, 0.5]} color="#2a1a40" edge={C.pink} opacity={ip(frame, at(3, 0.04), 16) * g3} glow={2} emissive={0.3} />
        <Label text="inode" position={[-8.4, 3.4, 0.4]} size={0.46} bold mono color={C.pink} opacity={ip(frame, at(3, 0.06), 14) * g3} />
        {[['直接指针', 2.4, C.cyan], ['一级间接', 0.2, C.gold], ['二级间接', -2.2, C.violet]].map(([n, y, c], k) => (
          <group key={n as string}>
            <Block position={[-8.4, y as number, 0.3]} size={[2.8, 0.9, 0.2]} color={C.panel2} edge={c as string} opacity={ip(frame, at(3, 0.1 + k * 0.1), 12) * g3} glow={2} />
            <Label text={n as string} position={[-8.4, y as number, 0.5]} size={0.34} bold opacity={ip(frame, at(3, 0.1 + k * 0.1), 12) * g3} depthTest={false} />
          </group>
        ))}
        {[0, 1, 2].map((k) => cube([-4.4 + k * 1.2, 2.4, 0], C.cyan, ip(frame, at(3, 0.16 + k * 0.04), 12) * g3))}
        <CurveArrow from={[-6.9, 2.4, 0.3]} to={[-5.1, 2.4, 0.3]} color={C.cyan} radius={0.04} progress={ip(frame, at(3, 0.14), 14)} opacity={g3} />
        <Label text="小文件：一步到数据" position={[2.4, 2.4, 0.3]} size={0.36} bold color={C.cyan} opacity={vis(frame, at(3, 0.2)) * g3} />

        <CurveArrow from={[-6.9, 0.2, 0.3]} to={[-4.8, 0.2, 0.3]} color={C.gold} radius={0.04} progress={ip(frame, at(3, 0.3), 14)} opacity={g3} />
        {cube([-4.2, 0.2, 0], C.gold, ip(frame, at(3, 0.34), 12) * g3, '索引', 1.1)}
        {[0, 1, 2, 3, 4].map((k) => (
          <group key={k}>
            {cube([-1.4 + k * 1.2, 0.2, 0], C.cyan, ip(frame, at(3, 0.4 + k * 0.03), 12) * g3)}
            <CurveArrow from={[-3.6, 0.2, 0]} to={[-1.4 + k * 1.2 - 0.5, 0.2, 0]} bend={[0, 0.5 + k * 0.1, 0]} color={C.gold} radius={0.025} progress={ip(frame, at(3, 0.4 + k * 0.03), 12)} opacity={g3 * 0.8} />
          </group>
        ))}

        <CurveArrow from={[-6.9, -2.2, 0.3]} to={[-4.8, -2.2, 0.3]} color={C.violet} radius={0.04} progress={ip(frame, at(3, 0.56), 14)} opacity={g3} />
        {cube([-4.2, -2.2, 0], C.violet, ip(frame, at(3, 0.6), 12) * g3, '一级', 1.1)}
        {[0, 1, 2].map((k) => (
          <group key={k}>
            {cube([-1.2, -1.0 - k * 1.2, 0], C.violet, ip(frame, at(3, 0.66 + k * 0.04), 12) * g3, '二级', 0.9)}
            <CurveArrow from={[-3.6, -2.2, 0]} to={[-1.8, -1.0 - k * 1.2, 0]} bend={[0, 0.2, 0]} color={C.violet} radius={0.025} progress={ip(frame, at(3, 0.66 + k * 0.04), 12)} opacity={g3 * 0.8} />
            {[0, 1, 2].map((j) => (
              <group key={j}>
                {cube([1.4 + j * 1.0, -1.0 - k * 1.2, 0], C.cyan, ip(frame, at(3, 0.74 + k * 0.04 + j * 0.02), 10) * g3, undefined, 0.7)}
              </group>
            ))}
            <Line from={[-0.7, -1.0 - k * 1.2, 0]} to={[1.0, -1.0 - k * 1.2, 0]} color={C.violet} opacity={ip(frame, at(3, 0.74 + k * 0.04), 10) * g3 * 0.8} />
          </group>
        ))}
        <Label text="大文件：多级间接，照样放得下" position={[6.6, 0.4, 0.3]} size={0.38} bold color={C.violet} opacity={vis(frame, at(3, 0.82)) * g3} />

        {/* —— 日志 —— */}
        <Block position={[-5.2, 0, 0]} size={[4.6, 4.2, 2.0]} color={C.panel} edge={C.pink} opacity={ip(frame, at(4, 0.03), 16) * g4} glow={1.8} />
        <Label text="日志区  Journal" position={[-5.2, 2.6, 0.5]} size={0.4} bold color={C.pink} opacity={ip(frame, at(4, 0.04), 14) * g4} />
        <Block position={[5.2, 0, 0]} size={[4.6, 4.2, 2.0]} color={C.panel} edge={crashed ? C.red : C.cyan} opacity={ip(frame, at(4, 0.03), 16) * g4} glow={1.8 + (crashed ? 1.2 : 0)} />
        <Label text="文件系统数据区" position={[5.2, 2.6, 0.5]} size={0.4} bold color={crashed ? C.red : C.cyan} opacity={ip(frame, at(4, 0.04), 14) * g4} />
        {['要改：inode、位图、数据'].map((t) => (
          <Label key={t} text={t} position={[-5.2, 0.6, 1.1]} size={0.28} mono bold color={C.text} opacity={logW * g4} depthTest={false} />
        ))}
        <Label text="✓ 已提交" position={[-5.2, -0.5, 1.1]} size={0.42} bold color={C.cyan} opacity={commit * g4} depthTest={false} />
        <Label text={mainOK ? '已恢复一致 ✓' : crashed ? '写到一半 ✗' : apply1 > 0 ? '写入中…' : '（原样）'} position={[5.2, 0.4, 1.1]} size={0.4} bold
          color={mainOK ? C.cyan : crashed ? C.red : C.muted} opacity={ip(frame, at(4, 0.06), 14) * g4} depthTest={false} />
        <Block position={[5.2 - 2.0 + (mainOK ? 4.0 : crashed ? 1.7 : apply1 * 2.2) / 2, -1.2, 0.2]} size={[Math.max(0.05, mainOK ? 4.0 : crashed ? 1.7 : apply1 * 2.2), 0.5, 1.2]}
          color={crashed ? '#4a1620' : C.panel2} edge={crashed ? C.red : C.cyan} opacity={g4 * (apply1 > 0.02 || mainOK ? 1 : 0)} glow={2} />
        <Orb position={orbJ} radius={0.3} color={C.gold} glow={1.8} opacity={orbO * g4} />
        <Label text="① 先写日志" position={[-5.2, -2.8, 0.6]} size={0.4} bold color={C.pink} opacity={vis(frame, at(4, 0.1), at(4, 0.4)) * g4} />
        <Label text="② 再真正执行" position={[0, -2.8, 0.6]} size={0.4} bold color={C.cyan} opacity={vis(frame, at(4, 0.4), at(4, 0.6)) * g4} />
        <Label text="断电！" position={[0, 1.2, 1.0]} size={0.9} bold color={C.red} opacity={vis(frame, crashT, at(4, 0.7)) * g4} />
        {frame >= crashT && frame < crashT + 30 && (
          <Ring position={[0, 0.4, 1]} radius={ip(frame, crashT, 28, easeOut) * 5} width={0.1} color={C.red} opacity={1 - prog(frame, crashT, 30)} />
        )}
        <Label text="重启：按日志重放，恢复一致" position={[0, -2.8, 0.6]} size={0.42} bold color={C.gold} opacity={vis(frame, at(4, 0.72), 1e9) * g4} />
      </Stage>

      <Badge from={at(0, 0.7)} to={at(1, 0)} x={1848} y={170} align="right" color={C.gold}>目录 = 树 · 路径 = 导航</Badge>
      <Badge from={at(1, 0.5)} to={at(2, 0)} x={1848} y={170} align="right" color={C.pink}><Mono color={C.pink}>inode</Mono> 记录文件的元数据</Badge>
      <Badge from={at(2, 0.1)} to={at(3, 0)} x={1848} y={170} align="right" color={C.cyan}>数据块分配方式</Badge>
      <Badge from={at(3, 0.1)} to={at(4, 0)} x={1848} y={170} align="right" color={C.violet}>多级间接指针</Badge>
      <Badge from={at(4, 0.1)} x={1848} y={170} align="right" color={C.pink}>日志 <Mono color={C.pink}>Journaling</Mono></Badge>
    </AbsoluteFill>
  );
};

function isIdx(r: {idx?: number}) {
  return r.idx !== undefined;
}
