import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT, MONO, SHADOW, tint} from '../theme';
import {easeOut, ip, pop, useScene, vis} from '../anim';
import {Chip, Label, Pop, Svg} from '../kit';

const TERMS: [string, string, string, string, number][] = [
  ['指令条数', 'IC', '程序有多少条指令', '10⁹', 760], ['CPI', '', '每条指令平均几个周期', '2', 1120], ['时钟周期', 'T', '= 1 / 主频', '0.5 ns', 1480],
];
const COLS = [C.blue, C.purple, C.orange];

/** Beats 0–1: CPU time = IC × CPI × T. */
const Perf: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(0, 0), end = at(2, 0);
  const o = vis(frame, s, end);
  if (o <= 0) return null;
  const cpiPulse = vis(frame, at(0, 0.68), at(1, 0));
  return (
    <AbsoluteFill style={{opacity: o}}>
      <Label x={380} y={400} from={s + 4} size={48} weight={700} color={C.ink}>CPU 时间</Label>
      <Label x={548} y={400} from={s + 8} size={48} weight={400} color={C.faint}>=</Label>
      <Label x={940} y={400} from={at(0, 0.32)} size={44} color={C.faint}>×</Label>
      <Label x={1300} y={400} from={at(0, 0.46)} size={44} color={C.faint}>×</Label>
      {TERMS.map(([t, abbr, sub, num, x], i) => (
        <React.Fragment key={t}>
          <Pop from={at(0, 0.2 + i * 0.14)} x={x} y={400}>
            <div style={{width: 280, height: 140, borderRadius: 26, background: '#fff', boxShadow: i === 1 && cpiPulse > 0
              ? `${SHADOW}, 0 0 0 ${8 * cpiPulse}px ${tint(COLS[i], 0.15)}` : SHADOW, display: 'flex', flexDirection: 'column',
              alignItems: 'center', justifyContent: 'center', border: `2px solid ${tint(COLS[i], 0.4)}`}}>
              <div style={{fontSize: 38, fontWeight: 700, color: COLS[i]}}>{t}{abbr && <span style={{fontSize: 22, marginLeft: 8, opacity: 0.7}}>{abbr}</span>}</div>
              <div style={{fontSize: 19, color: C.muted, marginTop: 8}}>{sub}</div>
            </div>
          </Pop>
          <Pop from={at(1, 0.2 + i * 0.12)} x={x} y={570}>
            <div style={{fontFamily: MONO, fontSize: 50, fontWeight: 700, color: COLS[i]}}>
              {num === '10⁹' ? <>10<sup style={{fontFamily: FONT, fontSize: 30, verticalAlign: 'super', lineHeight: 0}}>9</sup></> : num}
            </div>
          </Pop>
        </React.Fragment>
      ))}
      <Label x={940} y={570} from={at(1, 0.32)} size={40} color={C.faint}>×</Label>
      <Label x={1300} y={570} from={at(1, 0.44)} size={40} color={C.faint}>×</Label>
      <Label x={1480} y={630} from={at(1, 0.48)} size={20} color={C.muted}>主频 2 GHz</Label>
      <Pop from={at(1, 0.7)} x={960} y={760}>
        <div style={{display: 'flex', alignItems: 'baseline', gap: 22}}>
          <span style={{fontSize: 34, color: C.muted}}>执行时间</span>
          <span style={{fontSize: 96, fontWeight: 700, color: C.blue}}>= 1 秒</span>
        </div>
      </Pop>
    </AbsoluteFill>
  );
};

const RECAP: [string, string][] = [
  ['数据表示', '补码 · 浮点数'], ['运算器', '全加器 · ALU'], ['存储系统', '分层 · Cache · 虚存'], ['指令系统', '格式 · 寻址方式'],
  ['CPU', '数据通路 · 控制器'], ['流水线', '重叠执行 · 冒险'], ['总线', '宽度 · 带宽 · 仲裁'], ['输入输出', '中断 · DMA'],
];
const RECAP_T = [0.06, 0.16, 0.27, 0.37, 0.47, 0.6, 0.76, 0.84];

/** Beat 2: chapter recap grid. */
const Recap: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(2, 0), end = at(3, 0.1);
  const o = vis(frame, s, end, 18);
  if (o <= 0) return null;
  const cur = RECAP_T.reduce((a, t, k) => (frame >= at(2, t) ? k : a), -1);
  return (
    <AbsoluteFill style={{opacity: o, transform: `scale(${1 - 0.04 * ip(frame, end, 18)})`}}>
      {RECAP.map(([t, sub], k) => {
        const x = 375 + (k % 4) * 390, y = 400 + Math.floor(k / 4) * 220;
        const on = k === cur, seen = k <= cur;
        return (
          <Pop key={t} from={s + 4 + k * 3} x={x} y={y}>
            <div style={{width: 360, height: 180, borderRadius: 28, boxSizing: 'border-box', padding: '26px 30px', boxShadow: SHADOW,
              background: on ? C.blue : '#fff', transform: `scale(${on ? 1.04 : 1})`, transition: 'none'}}>
              <div style={{fontSize: 20, fontWeight: 650, color: on ? 'rgba(255,255,255,0.75)' : seen ? C.blue : C.faint, fontFamily: MONO}}>
                {String(k + 1).padStart(2, '0')}
              </div>
              <div style={{fontSize: 38, fontWeight: 700, color: on ? '#fff' : C.ink, marginTop: 10}}>{t}</div>
              <div style={{fontSize: 22, color: on ? 'rgba(255,255,255,0.85)' : C.muted, marginTop: 8}}>{sub}</div>
            </div>
          </Pop>
        );
      })}
    </AbsoluteFill>
  );
};

/** Beat 3: closing title. */
const Final: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(3, 0.15);
  if (frame < s) return null;
  const chip = pop(frame, s, 18);
  const t = ip(frame, s + 12, 26, easeOut);
  const thanks = ip(frame, at(3, 0.7), 22, easeOut);
  return (
    <AbsoluteFill>
      <Svg>
        <g opacity={Math.min(1, chip * 1.5)} transform={`translate(960 360) scale(${0.85 + 0.15 * chip}) translate(-960 -360)`}>
          <Chip x={960} y={360} size={200} glow={0.5 + 0.5 * Math.sin(frame / 12)} />
        </g>
      </Svg>
      <div style={{position: 'absolute', left: 0, right: 0, top: 540, textAlign: 'center', fontFamily: FONT, opacity: t, transform: `translateY(${(1 - t) * 24}px)`}}>
        <div style={{fontSize: 92, fontWeight: 700, letterSpacing: 6, display: 'inline-block',
          backgroundImage: 'linear-gradient(90deg, #1d1d1f 0%, #1d1d1f 35%, #0071e3 70%, #af52de 100%)',
          WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent'}}>计算机组成原理</div>
        <div style={{fontSize: 28, color: C.muted, marginTop: 8}}>各司其职 · 紧密配合</div>
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 780, textAlign: 'center', fontFamily: FONT, fontSize: 40, fontWeight: 600,
        color: C.ink2, letterSpacing: 8, opacity: thanks}}>感谢观看</div>
    </AbsoluteFill>
  );
};

export const Outro: React.FC = () => (
  <AbsoluteFill>
    <Perf />
    <Recap />
    <Final />
  </AbsoluteFill>
);