import React from 'react';
import {AbsoluteFill} from 'remotion';
import {BORDER, C, MONO, glow, tint} from '../theme';
import {P, easeOut, ip, pop, prog, useScene, vis} from '../anim';
import {Burst, Code, Comet, Packet, Pill, Pop, Shock, Svg, Wire, card, shake} from '../kit';

const GATE_X = 760, IN_Y = 520;
const LANES = [
  {y: 300, color: C.lime, label: '自动放行'},
  {y: 520, color: C.gold, label: '按规则检查'},
  {y: 740, color: C.red, label: '人工确认'},
];
const CALLS: [string, number][] = [['read_file', 0], ['search', 0], ['edit_file', 1], ['curl', 1], ['rm -rf build/', 2]];

/** Beat 0: tool calls routed through a permission gate. */
const Gate: React.FC = () => {
  const {frame, at} = useScene();
  const end = at(1, 0.02);
  const o = vis(frame, at(0, 0), end, 14);
  if (o <= 0) return null;
  const hits = CALLS.map((_, i) => at(0, 0.1 + i * 0.11) + 26);
  const flash = Math.max(...hits.map((h, i) => (frame >= h ? (1 - prog(frame, h, 14)) * (CALLS[i][1] === 2 ? 1.6 : 1) : 0)));
  const danger = frame >= hits[4] ? 1 - prog(frame, hits[4] + 20, 30) * 0.6 : 0;
  const dlg = at(0, 0.7);
  return (
    <div style={{position: 'absolute', inset: 0, opacity: o}}>
      <Svg>
        <defs>
          <linearGradient id="gate" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor={C.lime} />
            <stop offset="0.5" stopColor={C.gold} />
            <stop offset="1" stopColor={C.red} />
          </linearGradient>
        </defs>
        <rect x={GATE_X - 10} y={220} width={20} height={600} rx={10} fill="url(#gate)" opacity={0.35 + 0.65 * Math.min(1, flash)} />
        <rect x={GATE_X - 36} y={220} width={72} height={600} rx={36} fill="url(#gate)" opacity={0.08 + 0.2 * Math.min(1, flash)} />
        <Wire pts={[[80, IN_Y], [GATE_X - 20, IN_Y]]} from={at(0, 0)} len={14} color={C.ink2} w={2} head={false} opacity={0.35} />
        {LANES.map((l, i) => <Wire key={i} pts={[[GATE_X + 20, IN_Y], [GATE_X + 120, l.y], [1140, l.y]]} from={at(0, 0.04) + i * 4} len={16}
          color={l.color} w={2.5} opacity={0.6} />)}
        {CALLS.map(([, lane], i) => (
          <React.Fragment key={i}>
            <Shock x={GATE_X} y={IN_Y} at={hits[i]} color={LANES[lane].color} r0={20} r1={lane === 2 ? 420 : 200} w={lane === 2 ? 6 : 3} />
            {lane === 2 && <Burst x={GATE_X} y={IN_Y} at={hits[i]} color={C.red} n={40} dist={300} seed={4} />}
          </React.Fragment>
        ))}
      </Svg>
      <Pop from={at(0, 0.02)} x={GATE_X} y={180} fx="drop"><span style={{fontFamily: MONO, fontSize: 22, letterSpacing: 8, color: C.ink, fontWeight: 800}}>权限网关</span></Pop>
      {CALLS.map(([t, lane], i) => {
        const f = at(0, 0.1 + i * 0.11);
        const pts: P[] = [[80, IN_Y], [GATE_X, IN_Y], [GATE_X + 120, LANES[lane].y], [1010, LANES[lane].y]];
        return <Packet key={t} pts={pts} from={f} len={48} color={LANES[lane].color} tag={t} hold={lane === 2 ? 400 : 14} />;
      })}
      {LANES.map((l, i) => (
        <Pop key={i} from={at(0, 0.06) + i * 4} x={1160} y={l.y} anchor="left" fx="right">
          <Pill color={l.color} solid={i === 2 && danger > 0.3}>{l.label}</Pill>
        </Pop>
      ))}
      <Pop from={dlg} x={1650} y={700} fx="slam">
        <div style={{...card({borderRadius: 22}), width: 400, padding: '24px 28px', boxSizing: 'border-box', border: `1.5px solid ${tint(C.red, 0.8)}`,
          boxShadow: `${glow(C.red, 0.5 + 0.5 * Math.abs(Math.sin(frame / 8)))}`}}>
          <div style={{fontSize: 24, fontWeight: 800, color: C.gold}}>⚠ 需要你的确认</div>
          <div style={{fontFamily: MONO, fontSize: 24, color: C.ink, marginTop: 14, padding: '10px 14px', background: C.hair, borderRadius: 10}}>rm -rf build/</div>
          <div style={{display: 'flex', gap: 14, marginTop: 18, justifyContent: 'flex-end'}}>
            <span style={{padding: '8px 22px', borderRadius: 12, border: BORDER, color: C.ink2, fontSize: 22, fontWeight: 700}}>拒绝</span>
            <span style={{padding: '8px 22px', borderRadius: 12, background: C.red, color: C.dark, fontSize: 22, fontWeight: 800}}>允许</span>
          </div>
        </div>
      </Pop>
    </div>
  );
};

const TARGETS: [string, number][] = [['~/.ssh 私钥', 290], ['系统目录 /etc', 500], ['任意外网地址', 710]];

/** Beat 1: everything runs inside a sandbox; escapes bounce off its wall. */
const Sandbox: React.FC = () => {
  const {frame, at} = useScene();
  const end = at(2, 0.02);
  const o = vis(frame, at(1, 0), end, 14);
  if (o <= 0) return null;
  const draw = ip(frame, at(1, 0.02), 24, easeOut);
  const hits = TARGETS.map((_, i) => at(1, 0.3 + i * 0.15) + 18);
  const red = Math.max(...hits.map((h) => (frame >= h ? 1 - prog(frame, h, 18) : 0)));
  const per = 2 * (900 + 480);
  return (
    <div style={{position: 'absolute', inset: 0, opacity: o, transform: TARGETS.map((_, i) => shake(frame, hits[i], 12)).find((s) => s !== 'none')}}>
      <Svg>
        <rect x={420} y={260} width={900} height={480} rx={36} fill={tint(C.cyan, 0.04 + 0.08 * red)} stroke={red > 0.05 ? C.red : C.cyan} strokeWidth={3}
          strokeDasharray={`${per * draw} ${per}`} style={{filter: `drop-shadow(0 0 ${12 + 24 * red}px ${red > 0.05 ? C.red : C.cyan})`}} />
        <rect x={420} y={260} width={900} height={480} rx={36} fill="none" stroke={C.cyan} strokeOpacity={0.3} strokeWidth={1}
          strokeDasharray="6 14" strokeDashoffset={-frame * 1.5} transform="translate(0 0)" />
        {TARGETS.map(([, y], i) => {
          const f = at(1, 0.3 + i * 0.15);
          return (
            <React.Fragment key={i}>
              <Wire pts={[[1330, y], [1500, y]]} from={at(1, 0.1)} len={12} color={C.faint} w={2} dash="6 8" head={false} />
              <Comet pts={[[1000, 500], [1320, y]]} from={f} len={18} color={C.red} r={11} />
              <Burst x={1320} y={y} at={f + 18} color={C.red} n={26} dist={180} seed={i + 21} />
              <Shock x={1320} y={y} at={f + 18} color={C.red} r1={220} />
            </React.Fragment>
          );
        })}
      </Svg>
      <Pop from={at(1, 0.02)} x={480} y={232} anchor="left" fx="drop">
        <span style={{fontFamily: MONO, fontSize: 22, fontWeight: 800, letterSpacing: 8, color: C.cyan}}>SANDBOX · 只能访问项目目录</span>
      </Pop>
      <Code x={870} y={500} w={620} from={at(1, 0.08)} size={24} title="sandbox shell" reveal={10}
        lines={['$ npm test', '✓ 42 passed', '$ cat ~/.ssh/id_rsa', '✕ permission denied', '$ curl evil.example.com', '✕ network blocked']}
        hl={frame > at(1, 0.45) ? [3, 5] : []} hlColor={C.red} />
      {TARGETS.map(([t, y], i) => (
        <Pop key={t} from={at(1, 0.12) + i * 4} x={1520} y={y} anchor="left" fx="right">
          <div style={{padding: '12px 22px', borderRadius: 14, border: `1.5px solid ${frame >= hits[i] ? C.red : C.line}`, color: C.ink2, fontSize: 24,
            fontWeight: 700, background: C.card, whiteSpace: 'nowrap'}}>{t} {frame >= hits[i] && <span style={{color: C.red, marginLeft: 8}}>✕</span>}</div>
        </Pop>
      ))}
      <Pop from={at(1, 0.82)} x={870} y={810} fx="rise"><span style={{fontSize: 30, fontWeight: 800, color: C.ink}}>判断失误，也被关在盒子里</span></Pop>
    </div>
  );
};

/** Beat 2: timeout, retry and step limit. */
const Guards: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(2, 0);
  if (frame < s - 2) return null;
  const xs = [480, 960, 1440];
  const t0 = s + 10;
  const remain = Math.max(0, 30 - Math.floor(ip(frame, t0, 90, (x) => x) * 30));
  const sweep = ip(frame, t0, 90, (x) => x);
  const tries = [t0 + 20, t0 + 50, t0 + 80].filter((f) => frame >= f).length;
  const steps = Math.round(ip(frame, t0 + 10, 90, easeOut) * 50);
  const R = 70, circ = 2 * Math.PI * R;
  const box = (i: number, color: string, title: string, body: React.ReactNode, caption: string) => (
    <Pop key={i} from={s + 4 + i * 6} x={xs[i]} y={500} fx="slam">
      <div style={{...card({borderRadius: 28}), width: 380, height: 330, boxSizing: 'border-box', display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center', border: `1.5px solid ${tint(color, 0.6)}`, boxShadow: `${glow(color, 0.5)}`}}>
        <div style={{fontSize: 22, fontFamily: MONO, letterSpacing: 6, color, fontWeight: 800}}>{title}</div>
        <div style={{height: 180, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{body}</div>
        <div style={{fontSize: 28, fontWeight: 800, color: C.ink}}>{caption}</div>
      </div>
    </Pop>
  );
  return (
    <>
      <Svg>{xs.map((x, i) => <Shock key={i} x={x} y={500} at={s + 8 + i * 6} color={[C.cyan, C.magenta, C.gold][i]} r1={340} />)}</Svg>
      {box(0, C.cyan, 'TIMEOUT', (
        <svg width={170} height={170}>
          <circle cx={85} cy={85} r={R} fill="none" stroke={C.hair} strokeWidth={10} />
          <circle cx={85} cy={85} r={R} fill="none" stroke={remain === 0 ? C.red : C.cyan} strokeWidth={10} strokeLinecap="round"
            strokeDasharray={`${circ * (1 - sweep)} ${circ}`} transform="rotate(-90 85 85)" />
          <text x={85} y={98} textAnchor="middle" fontFamily={MONO} fontWeight={800} fontSize={40} fill={remain === 0 ? C.red : C.ink}>{remain}s</text>
        </svg>
      ), remain === 0 ? '超时 → 终止' : '超时')}
      {box(1, C.magenta, 'RETRY', (
        <div style={{display: 'flex', gap: 18}}>
          {[0, 1, 2].map((k) => {
            const on = tries > k, ok = k === 2;
            const p = pop(frame, [t0 + 20, t0 + 50, t0 + 80][k], 10);
            return <div key={k} style={{width: 74, height: 74, borderRadius: 37, display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 34, fontWeight: 900, color: on ? C.dark : C.faint, background: on ? (ok ? C.lime : C.red) : C.hair,
              transform: `scale(${on ? 0.6 + 0.4 * p : 1})`, boxShadow: on ? glow(ok ? C.lime : C.red, 0.7) : 'none'}}>{on ? (ok ? '✓' : '✕') : k + 1}</div>;
          })}
        </div>
      ), '失败重试')}
      {box(2, C.gold, 'MAX STEPS', (
        <div style={{width: 280}}>
          <div style={{fontFamily: MONO, fontSize: 56, fontWeight: 800, color: steps >= 50 ? C.red : C.ink, textAlign: 'center'}}>
            {steps}<span style={{fontSize: 28, color: C.muted}}> / 50</span>
          </div>
          <div style={{height: 14, borderRadius: 7, background: C.hair, marginTop: 14, overflow: 'hidden'}}>
            <div style={{width: `${(steps / 50) * 100}%`, height: '100%', background: `linear-gradient(90deg, ${C.gold}, ${steps >= 50 ? C.red : C.gold})`,
              boxShadow: glow(C.gold, 0.6)}} />
          </div>
        </div>
      ), '步数上限')}
      <Pop from={at(2, 0.75)} x={960} y={770} fx="rise">
        <span style={{fontSize: 30, fontWeight: 800, color: C.ink}}>不会卡死 · 不会无限循环</span>
      </Pop>
    </>
  );
};

export const SafetyScene: React.FC = () => {
  const {frame, at} = useScene();
  const hit = at(0, 0.1 + 4 * 0.11) + 26;
  return (
    <AbsoluteFill style={{transform: shake(frame, hit, 18, 20)}}>
      <Gate />
      <Sandbox />
      <Guards />
    </AbsoluteFill>
  );
};
