import React from 'react';
import {AbsoluteFill} from 'remotion';
import {BORDER, C, FONT, GRAD, MONO, glow, tint} from '../theme';
import {easeOut, ip, prog, useScene, vis} from '../anim';
import {Burst, Cam, Glitch, Pop, Shock, Svg} from '../kit';
import {Equation, HarnessRing} from './common';

const RECAP = [['循环', C.violet], ['工具', C.magenta], ['上下文', C.cyan], ['权限', C.red], ['规划', C.lime]] as const;

/** Beat 0: the full picture again. */
const Recap: React.FC = () => {
  const {frame, at} = useScene();
  const end = at(1, 0.02);
  if (frame > end + 16) return null;
  const marks = RECAP.map((_, i) => at(0, 0.42 + i * 0.1));
  const cur = marks.reduce((a, f, i) => (frame >= f ? i : a), -1);
  return (
    <div style={{position: 'absolute', inset: 0, opacity: 1 - prog(frame, end, 14)}}>
      <HarnessRing id="recap" cx={960} cy={450} orbFrom={at(0, 0)} ringFrom={at(0, 0.05)} to={end}
        sats={RECAP.map(([label, color], i) => ({label, color, at: at(0, 0.1) + i * 4}))}
        hl={(i) => (i === cur ? 1 - prog(frame, marks[i] + 20, 10) * 0.6 : 0)} energy={cur >= 0 ? 0.4 : 0} />
      <Equation x={960} y={840} from={at(0, 0.08)} to={end} size={56} />
    </div>
  );
};

/** Beat 1: same model, two harnesses. */
const Versus: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(1, 0), end = at(2, 0.02);
  const o = vis(frame, s, end, 14);
  if (o <= 0) return null;
  const weak = ip(frame, s + 30, 40, easeOut) * 0.32;
  const strong = ip(frame, s + 40, 50, easeOut) * 0.92;
  const bar = (x: number, v: number, color: string, label: string) => (
    <Pop from={s + 24} x={x} y={780} fx="rise">
      <div style={{width: 520}}>
        <div style={{display: 'flex', justifyContent: 'space-between', fontSize: 22, fontWeight: 700, color: C.muted, marginBottom: 10}}>
          <span>任务完成度</span><span style={{color, fontFamily: MONO}}>{label}</span>
        </div>
        <div style={{height: 20, borderRadius: 10, background: C.hair, border: BORDER, overflow: 'hidden'}}>
          <div style={{width: `${v * 100}%`, height: '100%', borderRadius: 10, background: `linear-gradient(90deg, ${tint(color, 0.4)}, ${color})`, boxShadow: glow(color, 0.7)}} />
        </div>
      </div>
    </Pop>
  );
  return (
    <div style={{position: 'absolute', inset: 0, opacity: o}}>
      <Pop from={s + 2} x={960} y={190} fx="drop">
        <div style={{fontSize: 30, fontWeight: 800, color: C.ink, letterSpacing: 4}}>同一个模型 · 不同的 Harness</div>
      </Pop>
      <HarnessRing id="weak" cx={540} cy={470} R={170} orbR={70} orbFrom={s + 4} ringFrom={s + 10} dim={0.5} label="BASIC" start={-150}
        sats={[{label: '循环', color: C.violet, at: s + 20}, {label: '工具', color: C.magenta, at: s + 24}]} />
      <HarnessRing id="strong" cx={1380} cy={470} R={170} orbR={70} orbFrom={s + 8} ringFrom={s + 14} label="FULL" energy={0.6}
        sats={RECAP.map(([label, color], i) => ({label, color, at: s + 24 + i * 4}))} />
      {bar(540, weak, C.gold, '勉强能用')}
      {bar(1380, strong, C.lime, '稳定可靠')}
      <Pop from={s + 50} x={960} y={470} fx="slam">
        <span style={{fontFamily: FONT, fontSize: 64, fontWeight: 900, color: C.faint}}>VS</span>
      </Pop>
      <Svg><Shock x={1380} y={470} at={s + 60} color={C.lime} r1={420} len={36} w={5} /></Svg>
    </div>
  );
};

/** Beat 2: closing statement. */
const Final: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(2, 0);
  if (frame < s - 2) return null;
  const line1 = [['模型', C.violet], ['决定', C.ink], ['怎么想', C.ink]] as const;
  const line2 = [['Harness', C.cyan], ['决定', C.ink], ['看到什么', C.ink], ['·', C.faint], ['能做什么', C.ink], ['·', C.faint], ['何时停下', C.ink]] as const;
  const word = (t: string, c: string, f: number, size: number, k: string) => (
    <Pop key={k} from={f} x={0} y={0} anchor="topleft" fx="slam" style={{position: 'relative'}}>
      <span style={{fontSize: size, fontWeight: 900, color: c, whiteSpace: 'nowrap', textShadow: c === C.ink ? 'none' : `0 0 40px ${tint(c, 0.7)}`}}>{t}</span>
    </Pop>
  );
  const thanks = at(2, 0.74);
  const out = ip(frame, thanks - 6, 14);
  return (
    <>
      <Svg>
        <Shock x={960} y={420} at={s + 4} color={C.violet} r1={900} len={40} w={5} />
        <Burst x={960} y={540} at={thanks} n={56} dist={900} len={46} color={C.magenta} seed={17} />
        <Shock x={960} y={540} at={thanks} color={C.cyan} r1={1100} len={44} w={6} />
      </Svg>
      <div style={{position: 'absolute', left: 0, right: 0, top: 300, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 40,
        fontFamily: FONT, opacity: 1 - out * 0.85, transform: `scale(${1 - out * 0.15}) translateY(${-out * 80}px)`, filter: out > 0 ? `blur(${out * 6}px)` : undefined}}>
        <div style={{display: 'flex', gap: 28}}>{line1.map(([t, c], i) => word(t, c, s + 4 + i * 6, 96, `a${i}`))}</div>
        <div style={{display: 'flex', gap: 22, alignItems: 'baseline'}}>{line2.map(([t, c], i) => word(t, c, at(2, 0.25) + i * 5, 60, `b${i}`))}</div>
      </div>
      <Pop from={thanks} x={960} y={720} fx="zoom">
        <div style={{textAlign: 'center'}}>
          <Glitch size={110} hitFrom={thanks} hitLen={20}>感谢观看</Glitch>
          <div style={{marginTop: 18, fontFamily: MONO, fontSize: 24, letterSpacing: 10, opacity: ip(frame, thanks + 16, 16),
            backgroundImage: GRAD, WebkitBackgroundClip: 'text', color: 'transparent'}}>AGENT = MODEL + HARNESS</div>
        </div>
      </Pop>
    </>
  );
};

export const Outro: React.FC = () => {
  const {at, dur} = useScene();
  return (
    <AbsoluteFill>
      <Cam keys={[[0, 1, 0, 0], [at(2, 0), 1, 0, 0], [dur, 1.08, 0, 0]]}>
        <Recap />
        <Versus />
        <Final />
      </Cam>
    </AbsoluteFill>
  );
};
