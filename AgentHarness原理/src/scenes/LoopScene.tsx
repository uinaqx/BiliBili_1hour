import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT, MONO, glow, tint} from '../theme';
import {P, arc, clamp, curve, ip, prog, useScene} from '../anim';
import {Block, Burst, Cam, Code, Comet, Packet, Pill, Pop, Shock, Svg, Wire, shake} from '../kit';

const CODE = [
  'def run_agent(task):',
  '    history = [user(task)]',
  '    for step in range(MAX_STEPS):',
  '        context = build(SYSTEM, TOOLS, history)',
  '        reply = model(context)',
  '        history.append(reply)',
  '        if not reply.tool_calls:',
  '            return reply.text',
  '        for call in reply.tool_calls:',
  '            result = execute(call)',
  '            history.append(result)',
];

const CX = 1390, CY = 520, R = 220;
const NODES: {label: string; sub: string; color: string; a: number}[] = [
  {label: '组装上下文', sub: 'build', color: C.cyan, a: -90},
  {label: '调用模型', sub: 'model', color: C.violet, a: 0},
  {label: '解析回复', sub: 'parse', color: C.magenta, a: 90},
  {label: '执行工具', sub: 'execute', color: C.lime, a: 180},
];
const npos = (i: number): P => [CX + R * Math.cos((NODES[i].a * Math.PI) / 180), CY + R * Math.sin((NODES[i].a * Math.PI) / 180)];
/** Arc from node i to node i+1 (clockwise), trimmed so it doesn't run under the blocks. */
const seg = (i: number): P[] => arc(CX, CY, R, NODES[i].a + 24, NODES[i].a + 90 - 24, 24);
const LAP: P[] = arc(CX, CY, R, -90, 270, 96);
const LAPS = [56, 44, 36, 30, 26, 24];

export const LoopScene: React.FC = () => {
  const {frame, at} = useScene();

  const hlAt: [number, number[]][] = [
    [at(0, 0.15), [3]], [at(1, 0), [4, 5]], [at(1, 0.42), [6, 7]], [at(1, 0.72), [8]], [at(2, 0), [9, 10]], [at(3, 0), [2]],
  ];
  const hl = hlAt.reduce<number[]>((acc, [f, l]) => (frame >= f ? l : acc), []);

  const lap0 = at(3, 0.04);
  const lapStarts = LAPS.reduce<number[]>((acc, d, i) => [...acc, i === 0 ? lap0 : acc[i - 1] + LAPS[i - 1]], []);
  const lapsEnd = lapStarts[LAPS.length - 1] + LAPS[LAPS.length - 1];
  const exitAt = Math.max(lapsEnd + 4, at(3, 0.72));
  const lapsDone = lapStarts.filter((f) => frame >= f).length;
  const step = frame < at(2, 0.8) ? 1 : 2 + lapsDone;
  const bump = [at(2, 0.8), ...lapStarts].filter((f) => frame >= f).pop() ?? -1e9;

  /** Which node is lit, from the comet schedule. */
  const nodeHl = (i: number) => {
    const wins: [number, number, number][] = [
      [0, at(0, 0.1), at(0, 0.75)], [1, at(0, 0.85), at(1, 0.3)], [2, at(1, 0.35), at(2, 0.1)], [3, at(2, 0.15), at(2, 0.55)],
      [0, at(2, 0.6), at(2, 0.82)], [1, at(2, 0.85), at(3, 0.02)], [2, exitAt - 10, exitAt + 30],
    ];
    let v = 0;
    for (const [n, a, b] of wins) if (n === i) v = Math.max(v, Math.min(prog(frame, a, 8), 1 - prog(frame, b, 10)));
    if (frame >= lap0 && frame < lapsEnd) {
      const k = lapStarts.findIndex((f, j) => frame >= f && frame < f + LAPS[j]);
      if (k >= 0) {
        const t = (frame - lapStarts[k]) / LAPS[k];
        const d = Math.abs(((t * 4 - i + 4) % 4));
        v = Math.max(v, clamp(1 - Math.min(d, 4 - d) * 1.6));
      }
    }
    return v;
  };

  const buildIn = [['SYSTEM', C.gold], ['TOOLS', C.magenta], ['history', C.cyan]] as const;
  const codeLine3: P = [800, 490];
  const exitPath: P[] = [[CX + 100, CY + R], [CX + 260, CY + R]];
  const sh = shake(frame, at(2, 0.3), 12);
  const shExit = shake(frame, exitAt + 16, 18, 20);

  return (
    <AbsoluteFill style={{transform: sh !== 'none' ? sh : shExit}}>
      <Cam keys={[[0, 1, 0, 0], [at(3, 0), 1, 0, 0], [at(3, 0.2), 1.12, -200, 0]]}>
        <div style={{position: 'absolute', inset: 0, opacity: 1 - 0.7 * ip(frame, at(3, 0), 20), filter: `blur(${2 * ip(frame, at(3, 0), 20)}px)`}}>
          <Code x={520} y={540} w={780} from={at(0, 0)} lines={CODE} hl={hl} title="agent_loop.py" size={21} fx="left"
            hlColor={hl[0] === 9 || hl[0] === 6 ? C.lime : C.violet} />
        </div>
        <Svg>
          {NODES.map((_, i) => <Wire key={i} pts={seg(i)} from={at(0, 0.05) + i * 6} len={18} color={tint(NODES[(i + 1) % 4].color, 1)} w={2.5}
            opacity={0.55} flow={frame >= lap0 && frame < lapsEnd} />)}
          <Comet pts={seg(0)} from={at(0, 0.75)} len={26} color={C.violet} />
          <Comet pts={seg(1)} from={at(1, 0.26)} len={24} color={C.magenta} />
          <Comet pts={seg(2)} from={at(2, 0.05)} len={24} color={C.lime} />
          <Comet pts={seg(3)} from={at(2, 0.52)} len={24} color={C.cyan} />
          <Comet pts={seg(0)} from={at(2, 0.78)} len={22} color={C.violet} />
          {lapStarts.map((f, i) => <Comet key={i} pts={LAP} from={f} len={LAPS[i]} color={[C.cyan, C.violet, C.magenta, C.lime][i % 4]}
            tail={0.2 + i * 0.03} r={9 + i} />)}
          <Burst x={npos(3)[0]} y={npos(3)[1]} at={at(2, 0.3)} color={C.lime} n={30} dist={200} seed={5} />
          <Shock x={npos(3)[0]} y={npos(3)[1]} at={at(2, 0.3)} color={C.lime} r1={300} />
          <Wire pts={exitPath} from={exitAt} len={12} color={C.lime} w={4} />
          <Comet pts={exitPath} from={exitAt} len={14} color={C.lime} r={12} />
          <Burst x={CX + 380} y={CY + R} at={exitAt + 14} color={C.lime} n={44} dist={320} len={40} seed={9} />
          <Shock x={CX + 380} y={CY + R} at={exitAt + 14} color={C.lime} r1={520} len={36} w={6} />
          {buildIn.map(([t], i) => {
            const p = curve(codeLine3, [CX - 90, CY - R], -60 - i * 30);
            return <Wire key={t} pts={p} from={at(0, 0.25) + i * 8} len={18} to={at(0, 0.8)} color={buildIn[i][1]} w={1.5} head={false} opacity={0.4} />;
          })}
        </Svg>
        {buildIn.map(([t, c], i) => (
          <Packet key={t} pts={curve(codeLine3, [CX - 90, CY - R], -60 - i * 30)} from={at(0, 0.28) + i * 8} len={30} color={c} tag={t} />
        ))}
        {NODES.map((n, i) => {
          const [x, y] = npos(i);
          return <Block key={i} x={x} y={y} w={200} h={86} from={at(0, 0.02) + i * 5} title={n.label} sub={n.sub} color={n.color}
            hl={nodeHl(i)} size={27} fx="zoom" />;
        })}
        <Pop from={at(0, 0.1)} x={CX} y={CY} fx="zoom">
          <div style={{textAlign: 'center', fontFamily: MONO}}>
            <div style={{fontSize: 18, color: C.muted, letterSpacing: 6}}>STEP</div>
            <div key={step} style={{fontSize: 92, fontWeight: 800, color: C.ink, lineHeight: 1, textShadow: glow(C.violet, 0.8),
              transform: `scale(${1 + 0.35 * (1 - clamp((frame - bump) / 8))})`}}>{step}</div>
            <div style={{fontSize: 18, color: C.faint, marginTop: 4}}>/ MAX 50</div>
          </div>
        </Pop>
        <Pop from={at(1, 0.4)} to={at(2, 0)} x={CX + 210} y={CY + R + 70} anchor="left" fx="right">
          <Pill color={C.lime}>A · 最终答案 → 用户</Pill>
        </Pop>
        <Pop from={at(1, 0.68)} to={at(2, 0.6)} x={CX} y={CY + R + 70} anchor="right" fx="left">
          <Pill color={C.magenta}>B · tool_call: read_file</Pill>
        </Pop>
        <Pop from={at(2, 0.32)} to={at(2, 0.95)} x={CX - R - 120} y={CY + 110} fx="drop">
          <Pill color={C.lime} solid size={22}>结果 → history</Pill>
        </Pop>
        <Pop from={at(3, 0.08)} to={exitAt} x={CX} y={CY - R - 90} fx="drop">
          <div style={{fontFamily: FONT, fontSize: 30, fontWeight: 800, letterSpacing: 10, color: C.ink}}>
            思考 <span style={{color: C.violet}}>→</span> 行动 <span style={{color: C.magenta}}>→</span> 观察
          </div>
        </Pop>
        <Pop from={exitAt + 12} x={CX + 380} y={CY + R} fx="slam">
          <Pill color={C.lime} solid size={30}>DONE · 最终答案</Pill>
        </Pop>
        <Pop from={exitAt + 22} x={CX + 380} y={CY + R + 70} fx="rise">
          <span style={{fontFamily: FONT, fontSize: 24, fontWeight: 700, color: C.muted}}>ReAct 循环</span>
        </Pop>
      </Cam>
    </AbsoluteFill>
  );
};
