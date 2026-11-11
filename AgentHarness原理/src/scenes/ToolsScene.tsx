import React from 'react';
import {AbsoluteFill} from 'remotion';
import {BORDER, C, FONT, MONO, glow, tint} from '../theme';
import {P, curve, easeInOut, ip, lerp, prog, useScene} from '../anim';
import {Block, Burst, Code, Comet, Orb, Packet, Pill, Pop, Shock, Svg, Wire, card, shake} from '../kit';

const SCHEMA = [
  '{',
  '  "name": "read_file",',
  '  "description": "读取文件内容",',
  '  "parameters": {',
  '    "type": "object",',
  '    "properties": {',
  '      "path": {"type": "string"}',
  '    },',
  '    "required": ["path"]',
  '  }',
  '}',
];
const OTHERS = ['search', 'edit_file', 'run_command'];
const ROW = 430;

export const ToolsScene: React.FC = () => {
  const {frame, at} = useScene();

  const orbMove = ip(frame, at(1, 0), 30, easeInOut);
  const orbPar = ip(frame, at(3, 0), 26, easeInOut);
  const ox = lerp(lerp(1440, 250, orbMove), 290, orbPar), oy = lerp(lerp(470, ROW, orbMove), 540, orbPar);
  const feed = at(0, 0.62);
  const energy = Math.max(0, 1 - Math.abs(frame - (feed + 36)) / 22) + Math.max(0, 1 - Math.abs(frame - at(2, 0.5)) / 18);

  const bubble: P = [640, ROW], check: P = [1010, ROW], exec: P = [1250, ROW], res: P = [1600, ROW];
  const err = at(2, 0.62);
  const back: P[] = [[res[0], ROW + 110], [res[0], 650], [250, 650], [250, ROW + 120]];
  const errBack: P[] = [[exec[0], ROW + 50], [exec[0], 650], [250, 650], [250, ROW + 120]];
  const sh = [shake(frame, at(2, 0.2), 10), shake(frame, err, 16)].find((s) => s !== 'none') ?? 'none';
  const b2 = at(3, 0);
  const execRed = Math.min(prog(frame, err, 4), 1 - prog(frame, err + 40, 10));

  const lanes = [
    {y: 330, call: 'read_file("auth.py")', speed: 0.55, color: C.cyan},
    {y: 540, call: 'read_file("db.py")', speed: 0.8, color: C.magenta},
    {y: 750, call: 'read_file("api.py")', speed: 0.68, color: C.lime},
  ];
  const parStart = at(3, 0.2);

  return (
    <AbsoluteFill style={{transform: sh}}>
      {OTHERS.map((t, i) => (
        <Pop key={t} from={at(0, 0.1) + i * 4} to={at(1, 0)} x={560 + (3 - i) * 34} y={520 - (3 - i) * 34} fx="drop">
          <div style={{...card({borderRadius: 20}), width: 640, height: 520, opacity: 0.35 + i * 0.15, padding: '12px 24px', boxSizing: 'border-box',
            fontFamily: MONO, fontSize: 18, color: C.muted, display: 'flex', justifyContent: 'flex-end'}}>{t}</div>
        </Pop>
      ))}
      <Code x={560} y={520} w={640} from={at(0, 0.02)} to={at(1, 0)} lines={SCHEMA} title="tools/read_file.json" size={21} fx="drop"
        hl={frame > at(0, 0.3) ? (frame > at(0, 0.45) ? [3, 4, 5, 6, 7, 8] : [1, 2]) : []} hlColor={C.cyan} />
      <Pop from={at(0, 0.3)} to={at(0, 0.44)} x={560} y={830} fx="rise"><Pill color={C.cyan}>名字 · 用途</Pill></Pop>
      <Pop from={at(0, 0.46)} to={at(1, 0)} x={560} y={830} fx="rise"><Pill color={C.gold}>参数格式 · JSON Schema</Pill></Pop>
      <Svg>
        <Wire pts={curve([900, 520], [1300, 470], 60)} from={feed} len={16} to={at(1, 0)} color={C.cyan} w={3} flow />
      </Svg>
      {['read_file', ...OTHERS].map((t, i) => (
        <Packet key={t} pts={curve([880, 470 + i * 30], [1400, 470], 60 + i * 20)} from={feed + i * 7} len={30} color={[C.cyan, C.magenta, C.gold, C.lime][i]} tag={t} />
      ))}
      <Pop from={feed} to={at(1, 0)} x={1440} y={680} fx="rise">
        <span style={{fontSize: 26, fontWeight: 800, color: C.ink2}}>工具说明 → 注入上下文</span>
      </Pop>

      <Orb x={ox} y={oy} r={95} from={at(0, 0.05)} energy={energy} />

      <Code x={bubble[0]} y={ROW} w={430} from={at(1, 0.22)} to={b2} lines={['{', '  "tool": "read_file",', '  "args": {"path": "main.py"}', '}']}
        title="tool_call" size={21} fx="left" hl={frame > at(1, 0.55) ? [1, 2] : []} hlColor={C.magenta} />
      <Pop from={at(1, 0.4)} to={at(2, 0)} x={bubble[0]} y={ROW + 170} fx="rise"><Pill color={C.gold}>只是文字，不执行任何东西</Pill></Pop>
      <Svg>
        <Wire pts={[[bubble[0] + 220, ROW], [check[0] - 90, ROW]]} from={at(2, 0)} len={10} to={b2} color={C.magenta} flow />
        <Wire pts={[[check[0] + 90, ROW], [exec[0] - 90, ROW]]} from={at(2, 0.12)} len={10} to={b2} color={C.magenta} flow />
        <Wire pts={[[exec[0] + 90, ROW], [res[0] - 200, ROW]]} from={at(2, 0.24)} len={10} to={b2} color={C.lime} flow />
        <Comet pts={[[bubble[0] + 220, ROW], [res[0] - 200, ROW]]} from={at(2, 0.02)} len={40} color={C.magenta} />
        <Burst x={check[0]} y={ROW} at={at(2, 0.1)} color={C.lime} n={20} dist={150} seed={2} />
        <Burst x={exec[0]} y={ROW} at={at(2, 0.2)} color={C.magenta} n={30} dist={200} seed={4} />
        <Shock x={exec[0]} y={ROW} at={at(2, 0.2)} color={C.magenta} r1={260} />
        <Wire pts={back} from={at(2, 0.38)} len={20} to={b2} color={C.cyan} w={2.5} flow />
        <Comet pts={back} from={at(2, 0.4)} len={34} color={C.cyan} r={11} />
        <Wire pts={errBack} from={err + 6} len={16} to={b2} color={C.red} w={3} />
        <Comet pts={errBack} from={err + 8} len={32} color={C.red} r={12} />
        <Burst x={exec[0]} y={ROW} at={err} color={C.red} n={36} dist={260} seed={8} />
        <Shock x={exec[0]} y={ROW} at={err} color={C.red} r1={380} w={6} />
      </Svg>
      <Block x={check[0]} y={ROW} w={180} h={96} from={at(2, 0)} to={b2} title="校验参数" sub="schema ✓" color={C.lime}
        hl={Math.min(prog(frame, at(2, 0.08), 6), 1 - prog(frame, at(2, 0.3), 10))} size={26} fx="zoom" />
      <Block x={exec[0]} y={ROW} w={180} h={96} from={at(2, 0.1)} to={b2} title="执行" sub="真正读文件" color={execRed > 0 ? C.red : C.magenta}
        hl={Math.max(Math.min(prog(frame, at(2, 0.18), 6), 1 - prog(frame, at(2, 0.36), 10)), execRed)} size={28} fx="zoom" />
      <Code x={res[0]} y={ROW} w={400} from={at(2, 0.26)} to={b2} title="result" size={19} fx="right"
        lines={['def login(user, pw):', '    token = sign(user)', '    return token', '# 共 128 行']} />
      <Pop from={at(2, 0.42)} to={err} x={925} y={690} fx="rise">
        <span style={{fontSize: 24, fontWeight: 700, color: C.cyan}}>结果作为一条新消息，交回模型</span>
      </Pop>
      <Pop from={err} to={b2} x={exec[0]} y={ROW - 110} fx="slam">
        <Pill color={C.red} solid size={22}>FileNotFoundError: mian.py</Pill>
      </Pop>
      <Pop from={err + 12} to={b2} x={925} y={690} fx="rise">
        <span style={{fontSize: 24, fontWeight: 700, color: C.red}}>出错不崩溃：错误信息也交回去，让模型自己改正</span>
      </Pop>

      {lanes.map((l, i) => {
        const t = ip(frame, parStart + 10, 70 / l.speed, (x) => x);
        const done = t >= 1;
        const fan = curve([ox + 110, 540], [560, l.y], i === 1 ? 0 : (i === 0 ? 60 : -60));
        return (
          <React.Fragment key={i}>
            <Svg>
              <Wire pts={fan} from={parStart - 6} len={16} color={l.color} w={2.5} flow />
              <Comet pts={fan} from={parStart - 4} len={16} color={l.color} />
              <Burst x={1490} y={l.y} at={parStart + 10 + 70 / l.speed} color={l.color} n={22} dist={160} seed={i + 11} />
              <Wire pts={curve([1530, l.y], [1640, 540], i === 1 ? 0 : (i === 0 ? -40 : 40))} from={parStart + 12 + 70 / l.speed} len={12}
                color={l.color} w={2.5} />
            </Svg>
            <Pop from={parStart - 2 + i * 3} x={700} y={l.y} fx="left">
              <div style={{...card({borderRadius: 14}), padding: '10px 20px', fontFamily: MONO, fontSize: 22, color: C.ink, border: `1.5px solid ${tint(l.color, 0.6)}`}}>{l.call}</div>
            </Pop>
            <Pop from={parStart + 2} x={1160} y={l.y} fx="zoom">
              <div style={{width: 520, height: 16, borderRadius: 8, background: C.hair, border: BORDER, overflow: 'hidden'}}>
                <div style={{width: `${t * 100}%`, height: '100%', borderRadius: 8, background: `linear-gradient(90deg, ${tint(l.color, 0.4)}, ${l.color})`,
                  boxShadow: glow(l.color, 0.6)}} />
              </div>
            </Pop>
            <Pop from={parStart + 10 + 70 / l.speed} x={1490} y={l.y} fx="slam">
              <div style={{width: 46, height: 46, borderRadius: 23, background: done ? l.color : C.hair, color: C.dark, fontWeight: 900, fontSize: 26,
                display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: glow(l.color, 0.8)}}>✓</div>
            </Pop>
          </React.Fragment>
        );
      })}
      <Pop from={parStart + 10 + 70 / 0.55 + 10} x={1700} y={540} anchor="left" fx="slam" style={{marginLeft: -40}}>
        <div style={{...card({borderRadius: 20}), padding: '18px 26px', textAlign: 'center', border: `1.5px solid ${tint(C.lime, 0.7)}`, boxShadow: glow(C.lime, 0.7)}}>
          <div style={{fontSize: 46, fontWeight: 900, color: C.lime, fontFamily: MONO}}>×3</div>
          <div style={{fontSize: 22, fontWeight: 700, color: C.ink, marginTop: 4}}>一轮拿回</div>
        </div>
      </Pop>
      <Pop from={at(3, 0.05)} x={960} y={190} fx="drop">
        <div style={{display: 'flex', gap: 18, fontFamily: FONT}}>
          <Pill color={C.faint}>串行：3 轮</Pill>
          <Pill color={C.lime} solid>并行：1 轮</Pill>
        </div>
      </Pop>
    </AbsoluteFill>
  );
};
