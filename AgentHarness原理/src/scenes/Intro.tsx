import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT, GRAD, MONO, glow, tint} from '../theme';
import {P, clamp, ip, pop, prog, useScene} from '../anim';
import {Burst, Cam, Glitch, Packet, Pop, Shock, Svg, Wire, card, shake} from '../kit';
import {Equation, HarnessRing} from './common';

const CY = 430;

/** Opening title before the first beat. */
const Title: React.FC = () => {
  const {frame, b} = useScene();
  const end = b(0) - 2;
  const out = prog(frame, end - 10, 14);
  if (out >= 1) return null;
  const s = pop(frame, 6, 10);
  const sub = ip(frame, 30, 18);
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', opacity: 1 - out, transform: `scale(${1 + out * 0.6})`,
      filter: out > 0 ? `blur(${out * 20}px)` : undefined}}>
      <Svg>
        <Shock x={960} y={470} at={8} r0={20} r1={900} color={C.magenta} len={40} w={5} />
        <Shock x={960} y={470} at={14} r0={20} r1={700} color={C.cyan} len={40} />
        <Burst x={960} y={470} at={8} n={40} dist={700} len={40} color={C.violet} />
      </Svg>
      <div style={{textAlign: 'center', transform: `scale(${2.2 - 1.2 * s})`, opacity: clamp(s * 2), marginTop: -60}}>
        <div style={{fontFamily: MONO, fontSize: 26, letterSpacing: 14, color: C.cyan, marginBottom: 18, opacity: sub}}>HOW AI AGENTS ACTUALLY RUN</div>
        <Glitch size={150} hitFrom={8} hitLen={18} style={{letterSpacing: 6}}>AGENT HARNESS</Glitch>
      </div>
      <div style={{position: 'absolute', top: 640, fontFamily: FONT, fontSize: 44, fontWeight: 700, opacity: sub,
        transform: `translateY(${(1 - sub) * 30}px)`, backgroundImage: GRAD, WebkitBackgroundClip: 'text', color: 'transparent'}}>
        AI Agent 是怎么跑起来的
      </div>
    </AbsoluteFill>
  );
};

const IN = ['帮我', '修复', '登录', 'bug'];
const OUTT = ['好的', '你可以', '先检查', 'auth.py'];
const CANT = ['读文件', '运行命令', '记住上次对话'];

/** Beat 0: text in, text out — and nothing else. */
const Plain: React.FC = () => {
  const {frame, at} = useScene();
  const end = at(1, 0.05);
  const inPath: P[] = [[100, CY], [830, CY]];
  const outPath: P[] = [[1090, CY], [1820, CY]];
  return (
    <>
      <Pop from={at(0, 0.02)} to={end} x={300} y={CY - 80} fx="left"><span style={{fontSize: 26, fontWeight: 800, color: C.cyan, letterSpacing: 4}}>文字进</span></Pop>
      <Pop from={at(0, 0.2)} to={end} x={1620} y={CY - 80} fx="right"><span style={{fontSize: 26, fontWeight: 800, color: C.magenta, letterSpacing: 4}}>文字出</span></Pop>
      <Svg>
        <Wire pts={inPath} from={at(0, 0)} len={20} to={end} color={C.cyan} w={2} head={false} opacity={0.5} />
        <Wire pts={outPath} from={at(0, 0.18)} len={20} to={end} color={C.magenta} w={2} head={false} opacity={0.5} />
      </Svg>
      {IN.map((t, i) => <Packet key={t} pts={inPath} from={at(0, 0.03) + i * 9} len={30} color={C.cyan} tag={t} />)}
      {OUTT.map((t, i) => <Packet key={t} pts={outPath} from={at(0, 0.2) + i * 9} len={34} color={C.magenta} tag={t} />)}
      {CANT.map((t, i) => {
        const f = at(0, 0.5 + i * 0.12);
        const x = 560 + i * 400;
        const strike = ip(frame, f + 8, 10);
        return (
          <React.Fragment key={t}>
            <Pop from={f} to={end} x={x} y={760} fx="slam">
              <div style={{...card({borderRadius: 20}), padding: '22px 38px', display: 'flex', alignItems: 'center', gap: 16,
                border: `1.5px solid ${tint(C.red, 0.6)}`, boxShadow: glow(C.red, 0.6)}}>
                <span style={{width: 40, height: 40, borderRadius: 20, background: C.red, color: C.dark, fontWeight: 900, fontSize: 26,
                  display: 'flex', alignItems: 'center', justifyContent: 'center'}}>✕</span>
                <span style={{position: 'relative', fontSize: 34, fontWeight: 800, color: C.ink, whiteSpace: 'nowrap'}}>
                  {t}
                  <span style={{position: 'absolute', left: 0, top: '52%', height: 4, width: `${strike * 100}%`, background: C.red,
                    borderRadius: 2, boxShadow: `0 0 10px ${C.red}`}} />
                </span>
              </div>
            </Pop>
            <Svg><Burst x={x} y={760} at={f + 3} color={C.red} n={18} dist={170} seed={i + 3} /></Svg>
          </React.Fragment>
        );
      })}
    </>
  );
};

export const Intro: React.FC = () => {
  const {frame, at, b} = useScene();
  const sats = [
    {label: '循环', color: C.violet, at: at(2, 0.12)},
    {label: '上下文', color: C.cyan, at: at(2, 0.24)},
    {label: '工具', color: C.magenta, at: at(2, 0.33)},
    {label: '权限', color: C.red, at: at(2, 0.42)},
    {label: '停止条件', color: C.gold, at: at(2, 0.5)},
  ];
  const energy = Math.max(0, 1 - Math.abs(frame - (at(0, 0.03) + 40)) / 24) * 0.9;
  const shakeT = [0.5, 0.62, 0.74].map((f) => shake(frame, at(0, f) + 3, 12)).find((s) => s !== 'none') ?? 'none';
  return (
    <AbsoluteFill style={{transform: shakeT}}>
      <Title />
      <Cam keys={[[b(0), 1, 0, 0], [at(1, 0), 1, 0, 0], [at(1, 0.25), 0.94, 0, 10], [at(2, 0.85), 0.94, 0, 10], [at(2, 1), 1.5, 0, 120]]}>
        <HarnessRing id="intro" cx={960} cy={CY} orbFrom={b(0) - 8} ringFrom={at(1, 0.15)} sats={sats} energy={energy} />
        <Equation x={960} y={830} from={at(1, 0.55)} to={at(2, 0.02)} />
        <Pop from={at(2, 0.05)} x={380} y={CY} fx="left">
          <div style={{textAlign: 'right'}}>
            <div style={{fontSize: 22, color: C.muted, fontWeight: 700, letterSpacing: 4}}>模型</div>
            <div style={{fontSize: 40, fontWeight: 800, color: C.ink}}>思考与决策</div>
          </div>
        </Pop>
        <Pop from={at(2, 0.1)} x={1560} y={CY} fx="right">
          <div>
            <div style={{fontSize: 22, color: C.cyan, fontWeight: 700, letterSpacing: 4}}>HARNESS</div>
            <div style={{fontSize: 40, fontWeight: 800, color: C.ink}}>剩下的一切</div>
          </div>
        </Pop>
      </Cam>
      <Plain />
    </AbsoluteFill>
  );
};
