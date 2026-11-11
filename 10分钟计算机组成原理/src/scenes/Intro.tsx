import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT, MONO, tint} from '../theme';
import {P, easeOut, ip, pointAt, pop, useScene, vis} from '../anim';
import {Block, Chip, Label, Packet, Pill, Pop, Svg, Wire, card} from '../kit';

const CX = 960, CY = 350, CHIP = 250;

const traces: P[][] = [];
for (const dir of [-1, 1]) {
  for (let i = 0; i < 7; i++) {
    const p = -CHIP * 0.35 + (CHIP * 0.7 * i) / 6;
    const x0 = CX + dir * (CHIP / 2 + 26), y0 = CY + p, k = i - 3;
    const mx = x0 + dir * (70 + Math.abs(k) * 36);
    traces.push([[x0, y0], [mx, y0], [mx + dir * 50, y0 + k * 26], [x0 + dir * 780, y0 + k * 26]]);
  }
}

const Hero: React.FC = () => {
  const {frame, at} = useScene();
  const o = vis(frame, 0, at(1, 0), 16);
  if (o <= 0) return null;
  const chipS = pop(frame, 6, 18);
  const title = ip(frame, 30, 26, easeOut);
  return (
    <AbsoluteFill style={{opacity: o}}>
      <Svg>
        {traces.map((t, i) => {
          const p = ip(frame, 14 + (i % 7) * 3, 40);
          const pts = p > 0 ? t.slice(0, 1).concat(t.slice(1)) : t;
          const period = 64, ph = ((frame + i * 23) % period) / period;
          const {p: dot} = pointAt(t, ph);
          return (
            <g key={i}>
              <polyline points={pts.map((v) => v.join(',')).join(' ')} fill="none" stroke={C.line} strokeWidth={2}
                strokeDasharray="1600" strokeDashoffset={1600 * (1 - p)} strokeLinecap="round" strokeLinejoin="round" />
              {frame > 50 && <circle cx={dot[0]} cy={dot[1]} r={5} fill={i % 2 ? C.purple : C.blue}
                opacity={Math.min(1, ph * 6, (1 - ph) * 3) * 0.9} />}
            </g>
          );
        })}
        <g transform={`translate(${CX},${CY}) scale(${0.85 + 0.15 * chipS}) translate(${-CX},${-CY})`} opacity={Math.min(1, chipS * 1.6)}>
          <Chip x={CX} y={CY} size={CHIP} glow={0.5 + 0.5 * Math.sin(frame / 12)} />
        </g>
      </Svg>
      <div style={{position: 'absolute', left: 0, right: 0, top: 580, textAlign: 'center', fontFamily: FONT, opacity: title,
        transform: `translateY(${(1 - title) * 30}px)`}}>
        <div style={{fontSize: 104, fontWeight: 700, letterSpacing: 6, display: 'inline-block',
          backgroundImage: 'linear-gradient(90deg, #1d1d1f 0%, #1d1d1f 35%, #0071e3 70%, #af52de 100%)',
          WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent'}}>计算机组成原理</div>
        <div style={{fontSize: 30, color: C.muted, marginTop: 6, letterSpacing: 2}}>Computer Organization</div>
      </div>
      <Pop from={70} x={CX} y={830}><Pill size={24} color={C.ink2}>10 分钟 · 跟着一条指令走一遍</Pill></Pop>
    </AbsoluteFill>
  );
};

const PROGRAM = [
  ['0x00', 'LOAD  R1, [0x10]', 'p'], ['0x04', 'ADD   R1, R2', 'p'], ['0x08', 'STORE R1, [0x14]', 'p'], ['0x0C', 'HALT', 'p'],
  ['0x10', '0000 0101', 'd'], ['0x14', '0000 0000', 'd'],
];
const MEM_X = 1250, MEM_TOP = 300, ROW_Y = (i: number) => MEM_TOP + 100 + i * 64;

const Stored: React.FC = () => {
  const {frame, at} = useScene();
  const start = at(1, 0) + 4, end = at(2, 0);
  const o = vis(frame, start, end);
  if (o <= 0) return null;
  const fetch0 = at(1, 0.42), step = 24;
  const cur = frame >= fetch0 ? Math.min(3, Math.floor((frame - fetch0) / step)) : -1;
  return (
    <AbsoluteFill>
      <Svg>
        <g opacity={Math.min(1, pop(frame, start))}>
          <Chip x={500} y={540} size={210} />
        </g>
        <Wire pts={[[MEM_X - 330, 540], [640, 540]]} from={at(1, 0.38)} color={C.blue} w={3} to={end} />
      </Svg>
      <Pop from={start + 6} to={end} x={MEM_X} y={MEM_TOP} anchor="top">
        <div style={card({width: 640, padding: '26px 30px 30px', boxSizing: 'border-box'})}>
          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: 14}}>
            <span style={{fontSize: 30, fontWeight: 700, color: C.ink}}>存储器</span>
            <span style={{fontSize: 20, color: C.muted}}>程序和数据都是二进制</span>
          </div>
          {PROGRAM.map(([addr, txt, kind], i) => {
            const on = i === cur;
            const s = pop(frame, start + 12 + i * 5);
            const col = kind === 'p' ? C.blue : C.green;
            return (
              <div key={i} style={{height: 54, marginTop: 10, borderRadius: 14, display: 'flex', alignItems: 'center', padding: '0 18px',
                background: on ? tint(C.blue, 0.1) : C.fill, border: `2px solid ${on ? C.blue : 'transparent'}`,
                opacity: Math.min(1, s * 1.5), transform: `translateX(${(1 - s) * 30}px)`}}>
                <span style={{fontFamily: MONO, fontSize: 20, color: C.muted, width: 80}}>{addr}</span>
                <span style={{fontFamily: MONO, fontSize: 24, color: C.ink, flex: 1}}>{txt}</span>
                <Pill size={18} color={col}>{kind === 'p' ? '程序' : '数据'}</Pill>
              </div>
            );
          })}
        </div>
      </Pop>
      {[0, 1, 2, 3].map((k) => (
        <Packet key={k} pts={[[MEM_X - 330, ROW_Y(k) + 2], [MEM_X - 330, 540], [650, 540]]} from={fetch0 + k * step} len={step - 4}
          color={C.blue} tag={PROGRAM[k][1].split(' ')[0]} />
      ))}
      <Label x={500} y={700} from={at(1, 0.5)} to={end} size={24} color={C.ink2}>自动逐条取出、执行</Label>
      <Pop from={at(1, 0.78)} to={end} x={500} y={330}><Pill solid size={26}>存储程序 Stored Program</Pill></Pop>
    </AbsoluteFill>
  );
};

const MEM: P = [960, 330], IN: P = [380, 330], OUT: P = [1540, 330], ALU: P = [800, 650], CU: P = [1120, 650];

const FiveParts: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(2, f);
  const start = t(0);
  if (frame < start - 2) return null;
  const tour: P[] = [[510, 330], [808, 330], [880, 392], [880, 598], [840, 598], [840, 392], [1112, 330], [1408, 330]];
  return (
    <AbsoluteFill>
      <Pop from={t(0.6)} x={960} y={652}>
        <div style={{width: 680, height: 220, borderRadius: 34, border: `2px dashed ${tint(C.blue, 0.45)}`, background: tint(C.blue, 0.03)}} />
      </Pop>
      <Label x={640} y={560} anchor="left" from={t(0.62)} color={C.blue} size={22} weight={650}>CPU 中央处理器</Label>
      <Svg>
        <Wire pts={[[512, 330], [806, 330]]} from={t(0.5)} color={C.blue} />
        <Wire pts={[[1112, 330], [1406, 330]]} from={t(0.54)} color={C.blue} />
        <Wire pts={[[880, 392], [880, 596]]} from={t(0.56)} color={C.blue} />
        <Wire pts={[[840, 598], [840, 394]]} from={t(0.58)} color={C.blue} />
        <Wire pts={[[1050, 598], [1050, 394]]} from={t(0.66)} color={C.orange} dash="10 10" />
        <Wire pts={[[1008, 650], [914, 650]]} from={t(0.68)} color={C.orange} dash="10 10" />
        <Wire pts={[[1232, 650], [1540, 650], [1540, 394]]} from={t(0.7)} color={C.orange} dash="10 10" />
        <Wire pts={[[1120, 702], [1120, 800], [380, 800], [380, 394]]} from={t(0.72)} color={C.orange} dash="10 10" len={26} />
      </Svg>
      <Block x={ALU[0]} y={ALU[1]} w={220} h={104} from={t(0.1)} title="运算器" sub="ALU" color={C.blue} />
      <Block x={CU[0]} y={CU[1]} w={220} h={104} from={t(0.18)} title="控制器" sub="CU" color={C.orange} />
      <Block x={MEM[0]} y={MEM[1]} w={300} h={120} from={t(0.27)} title="存储器" sub="程序 + 数据" color={C.purple} />
      <Block x={IN[0]} y={IN[1]} w={260} h={120} from={t(0.36)} title="输入设备" sub="键盘 · 鼠标" />
      <Block x={OUT[0]} y={OUT[1]} w={260} h={120} from={t(0.44)} title="输出设备" sub="显示器 · 打印机" />
      <Pop from={t(0.8)} x={1560} y={760}>
        <div style={{display: 'flex', flexDirection: 'column', gap: 10, fontSize: 21, color: C.ink2}}>
          <span><span style={{display: 'inline-block', width: 34, height: 3, background: C.blue, verticalAlign: 'middle', marginRight: 10}} />数据</span>
          <span><span style={{display: 'inline-block', width: 34, borderTop: `3px dashed ${C.orange}`, verticalAlign: 'middle', marginRight: 10}} />控制</span>
        </div>
      </Pop>
      {[0, 1].map((k) => <Packet key={k} pts={tour} from={at(3, 0.05) + k * 60} len={110} color={C.blue} r={11} />)}
    </AbsoluteFill>
  );
};

const JOURNEY = ['数据表示', '运算器', '存储系统', '指令系统', 'CPU', '流水线', '总线', '输入输出'];

const Journey: React.FC = () => {
  const {at} = useScene();
  return (
    <Pop from={at(3, 0.1)} x={960} y={150}>
      <div style={{display: 'flex', alignItems: 'center', gap: 10}}>
        {JOURNEY.map((j, i) => (
          <React.Fragment key={j}>
            <Pop from={at(3, 0.12) + i * 6} x={0} y={0} anchor="topleft" style={{position: 'relative'}}>
              <Pill size={22} color={i % 2 ? C.indigo : C.blue}>{j}</Pill>
            </Pop>
            {i < JOURNEY.length - 1 && <span style={{color: C.faint, fontSize: 20}}>›</span>}
          </React.Fragment>
        ))}
      </div>
    </Pop>
  );
};

export const Intro: React.FC = () => (
  <AbsoluteFill>
    <Hero />
    <Stored />
    <FiveParts />
    <Journey />
  </AbsoluteFill>
);
