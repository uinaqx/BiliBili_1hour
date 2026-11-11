import React from 'react';
import {AbsoluteFill} from 'remotion';
import {BORDER, C, FONT, MONO, glow, tint} from '../theme';
import {P, curve, easeOut, ip, pop, rand, useScene, vis} from '../anim';
import {Burst, Comet, Orb, Packet, Pill, Pop, Shock, Svg, Wire, card} from '../kit';

const TODO = ['定位登录失败的原因', '修复 auth.py 的 token 校验', '补充单元测试', '运行测试并确认通过'];

/** Beat 0: a todo list that checks itself off. */
const Todo: React.FC = () => {
  const {frame, at} = useScene();
  const end = at(1, 0.02);
  const o = vis(frame, at(0, 0), end, 14);
  if (o <= 0) return null;
  const checks = TODO.map((_, i) => at(0, 0.3 + i * 0.16));
  const done = checks.filter((f) => frame >= f).length;
  const bar = ip(frame, checks[0], checks[3] - checks[0] + 10, easeOut);
  const X = 960, Y = 500, ROWH = 92, top = Y - 141;
  return (
    <div style={{position: 'absolute', inset: 0, opacity: o}}>
      <Pop from={at(0, 0.02)} x={X} y={Y} fx="drop">
        <div style={{...card({borderRadius: 30}), width: 880, padding: '30px 44px 34px', boxSizing: 'border-box'}}>
          <div style={{display: 'flex', alignItems: 'baseline', justifyContent: 'space-between'}}>
            <span style={{fontFamily: MONO, fontSize: 22, letterSpacing: 8, color: C.violet, fontWeight: 800}}>TODO</span>
            <span style={{fontFamily: MONO, fontSize: 24, color: C.ink2, fontWeight: 700}}>{done} / {TODO.length}</span>
          </div>
          {TODO.map((t, i) => {
            const k = pop(frame, at(0, 0.06) + i * 5, 12);
            const c = pop(frame, checks[i], 9);
            const on = frame >= checks[i];
            const cur = !on && i === done;
            const strike = ip(frame, checks[i] + 3, 10);
            return (
              <div key={t} style={{height: ROWH, display: 'flex', alignItems: 'center', gap: 24, opacity: k, transform: `translateX(${(1 - k) * 80}px)`,
                borderBottom: i < TODO.length - 1 ? BORDER : 'none'}}>
                <div style={{width: 44, height: 44, borderRadius: 12, boxSizing: 'border-box', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  border: `2px solid ${on ? C.lime : cur ? C.violet : C.line}`, background: on ? C.lime : 'transparent',
                  boxShadow: on ? glow(C.lime, 0.7) : cur ? glow(C.violet, 0.5 + 0.5 * Math.sin(frame / 6)) : 'none',
                  transform: `scale(${on ? 0.7 + 0.3 * c : 1})`, color: C.dark, fontSize: 28, fontWeight: 900}}>{on ? '✓' : ''}</div>
                <span style={{position: 'relative', fontSize: 34, fontWeight: 700, color: on ? C.muted : C.ink}}>
                  {t}
                  <span style={{position: 'absolute', left: 0, top: '54%', height: 3, width: `${strike * 100}%`, background: C.lime, borderRadius: 2}} />
                </span>
              </div>
            );
          })}
          <div style={{height: 10, borderRadius: 5, background: C.hair, marginTop: 22, overflow: 'hidden'}}>
            <div style={{width: `${bar * 100}%`, height: '100%', background: `linear-gradient(90deg, ${C.violet}, ${C.lime})`, boxShadow: glow(C.lime, 0.5)}} />
          </div>
        </div>
      </Pop>
      <Svg>
        {checks.map((f, i) => <Burst key={i} x={X - 440 + 44 + 22} y={top + i * ROWH} at={f} color={C.lime} n={18} dist={120} seed={i + 30} />)}
      </Svg>
    </div>
  );
};

const SUBS = [
  {x: 480, task: '查前端调用', color: C.cyan, colors: [C.cyan, C.blue, C.violet] as [string, string, string]},
  {x: 960, task: '查后端接口', color: C.magenta, colors: [C.magenta, C.violet, C.cyan] as [string, string, string]},
  {x: 1440, task: '查数据库', color: C.lime, colors: [C.lime, C.cyan, C.blue] as [string, string, string]},
];
const MAIN: P = [960, 260], SUBY = 600;

/** Beat 1: the main agent spawns sub-agents with their own clean contexts. */
const Spawn: React.FC = () => {
  const {frame, at} = useScene();
  const end = at(2, 0.02);
  const o = vis(frame, at(1, 0), end, 14);
  if (o <= 0) return null;
  const back = at(1, 0.72);
  const energy = Math.max(0, 1 - Math.abs(frame - (back + 30)) / 20);
  return (
    <div style={{position: 'absolute', inset: 0, opacity: o}}>
      <Orb x={MAIN[0]} y={MAIN[1]} r={78} from={at(1, 0)} label="MAIN" energy={energy} />
      <Svg>
        {SUBS.map((s, i) => {
          const f = at(1, 0.12 + i * 0.06);
          const p = curve([MAIN[0], MAIN[1] + 90], [s.x, SUBY - 80], i === 1 ? 0 : i === 0 ? -50 : 50);
          const r = curve([s.x, SUBY - 80], [MAIN[0], MAIN[1] + 90], i === 1 ? 0 : i === 0 ? 50 : -50);
          return (
            <React.Fragment key={i}>
              <Wire pts={p} from={f} len={14} color={s.color} w={2.5} flow />
              <Comet pts={p} from={f} len={16} color={s.color} />
              <Shock x={s.x} y={SUBY} at={f + 14} color={s.color} r1={240} />
              <Comet pts={r} from={back + i * 6} len={24} color={C.lime} r={10} />
            </React.Fragment>
          );
        })}
      </Svg>
      {SUBS.map((s, i) => {
        const f = at(1, 0.12 + i * 0.06) + 12;
        const fill = ip(frame, f + 10, 60 + i * 14, easeOut) * (0.55 + 0.12 * i);
        return (
          <React.Fragment key={i}>
            <Orb x={s.x} y={SUBY} r={54} from={f} label={`SUB ${i + 1}`} colors={s.colors} />
            <Pop from={f + 6} x={s.x} y={SUBY + 120} fx="rise">
              <span style={{fontSize: 28, fontWeight: 800, color: C.ink}}>{s.task}</span>
            </Pop>
            <Pop from={f + 10} x={s.x} y={SUBY + 175} fx="zoom">
              <div style={{width: 300}}>
                <div style={{fontFamily: MONO, fontSize: 16, color: C.muted, marginBottom: 6, letterSpacing: 2}}>独立上下文</div>
                <div style={{height: 16, borderRadius: 8, background: C.hair, border: BORDER, overflow: 'hidden', display: 'flex'}}>
                  {Array.from({length: 12}, (_, k) => (k / 12 < fill ? (
                    <div key={k} style={{flex: 1, marginRight: 2, background: tint(s.color, 0.45 + 0.5 * rand(k + i * 13))}} />
                  ) : <div key={k} style={{flex: 1, marginRight: 2}} />))}
                </div>
              </div>
            </Pop>
          </React.Fragment>
        );
      })}
      {SUBS.map((s, i) => (
        <Packet key={i} pts={curve([s.x, SUBY - 80], [MAIN[0], MAIN[1] + 90], i === 1 ? 0 : i === 0 ? 50 : -50)} from={back + i * 6} len={24}
          color={C.lime} tag="结论 ✓" />
      ))}
    </div>
  );
};

/** Beat 2: main context with and without sub-agents. */
const Compare: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(2, 0);
  if (frame < s - 2) return null;
  const W = 1000, X = 560;
  const fillA = ip(frame, s + 10, 50, easeOut) * 0.94;
  const fillB = ip(frame, s + 24, 30, easeOut);
  const row = (y: number, label: string, sub: string, color: string, body: React.ReactNode, f: number) => (
    <>
      <Pop from={f} x={X - 40} y={y} anchor="right" fx="left">
        <div style={{textAlign: 'right'}}>
          <div style={{fontSize: 32, fontWeight: 800, color: C.ink}}>{label}</div>
          <div style={{fontSize: 20, color, fontWeight: 700, marginTop: 4}}>{sub}</div>
        </div>
      </Pop>
      <Pop from={f + 4} x={X} y={y} anchor="left" fx="zoom">
        <div style={{width: W, height: 70, borderRadius: 16, background: C.hair, border: BORDER, overflow: 'hidden', display: 'flex', padding: 6, boxSizing: 'border-box', gap: 4}}>
          {body}
        </div>
      </Pop>
    </>
  );
  const chunks = 30;
  return (
    <>
      {row(400, '不用子 Agent', '中间过程全挤进来', C.red, Array.from({length: chunks}, (_, k) => (
        <div key={k} style={{flex: 1, borderRadius: 5, background: k / chunks < fillA ? tint(k % 3 ? C.violet : C.magenta, 0.4 + 0.4 * rand(k)) : 'transparent'}} />
      )), s + 4)}
      {row(620, '使用子 Agent', '只收回结论', C.lime, (
        <>
          <div style={{width: 120, borderRadius: 8, background: tint(C.gold, 0.6)}} />
          {[0, 1, 2].map((k) => (
            <div key={k} style={{width: 110, borderRadius: 8, background: C.lime, opacity: fillB > k / 3 ? 1 : 0, boxShadow: glow(C.lime, 0.5),
              display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18, fontWeight: 800, color: C.dark,
              transform: `scale(${fillB > k / 3 ? 1 : 0.4})`}}>结论</div>
          ))}
        </>
      ), s + 14)}
      <Pop from={s + 60} x={X + W * 0.94 + 10} y={330} fx="slam"><Pill color={C.red} solid size={22}>挤满了</Pill></Pop>
      <Pop from={at(2, 0.55)} x={960} y={790} fx="rise">
        <div style={{display: 'flex', gap: 20, fontFamily: FONT}}>
          <Pill color={C.lime} size={28}>上下文清爽</Pill>
          <Pill color={C.cyan} size={28}>子任务并行</Pill>
        </div>
      </Pop>
      <Svg><Shock x={960} y={620} at={s + 40} color={C.lime} r1={600} len={36} /></Svg>
    </>
  );
};

export const PlanScene: React.FC = () => (
  <AbsoluteFill>
    <Todo />
    <Spawn />
    <Compare />
  </AbsoluteFill>
);
