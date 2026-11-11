import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, MONO, SHADOW, tint} from '../theme';
import {P, pop, useScene, vis} from '../anim';
import {Label, Pill, Pop, Svg, Wire, card} from '../kit';

/** Beat 0: opcode + address field. */
const Format: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(0, 0), end = at(1, 0);
  const o = vis(frame, s, end);
  if (o <= 0) return null;
  const seg = (w: number, color: string, big: string, small: string, from: number) => {
    const sp = pop(frame, from);
    return (
      <div style={{width: w, textAlign: 'center', opacity: Math.min(1, sp * 1.5), transform: `translateY(${(1 - sp) * 24}px)`}}>
        <div style={{height: 120, borderRadius: 24, background: color, color: '#fff', fontFamily: MONO, fontSize: 56, fontWeight: 700,
          display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: SHADOW}}>{big}</div>
        <div style={{marginTop: 18, fontSize: 28, fontWeight: 650, color}}>{small}</div>
      </div>
    );
  };
  const formats: [string[], string][] = [[['OP', 'A1', 'A2', 'A3'], '三地址'], [['OP', 'A1', 'A2'], '二地址'], [['OP', 'A'], '一地址'], [['OP'], '零地址']];
  return (
    <AbsoluteFill style={{opacity: o}}>
      <div style={{position: 'absolute', left: 960, top: 300, transform: 'translateX(-50%)', display: 'flex', gap: 14}}>
        {seg(360, C.blue, 'ADD', '操作码 · 做什么', s + 4)}
        {seg(620, C.purple, 'R1, R2', '地址码 · 对谁做', s + 12)}
      </div>
      <Label x={960} y={600} from={at(0, 0.6)} size={22} color={C.muted}>按地址码个数，常见的指令格式</Label>
      {formats.map(([fs, name], k) => (
        <Pop key={name} from={at(0, 0.65) + k * 6} x={k % 2 ? 1300 : 620} y={680 + Math.floor(k / 2) * 90}>
          <div style={{display: 'flex', alignItems: 'center', gap: 16}}>
            <div style={{display: 'flex', gap: 6}}>
              {fs.map((f, i) => (
                <span key={i} style={{width: i ? 90 : 70, height: 52, borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: MONO, fontSize: 20, fontWeight: 600, background: i ? tint(C.purple, 0.12) : tint(C.blue, 0.14), color: i ? C.purple : C.blue}}>{f}</span>
              ))}
            </div>
            <span style={{fontSize: 22, color: C.ink2, fontWeight: 600}}>{name}</span>
          </div>
        </Pop>
      ))}
    </AbsoluteFill>
  );
};

type Mode = {key: string; op: string; md: string; a: string; title: string; formula: string; result: string; color: string};
const MODES: Mode[] = [
  {key: 'imm', op: 'LOAD', md: '#', a: '5', title: '立即寻址', formula: '操作数 = A', result: '5', color: C.blue},
  {key: 'dir', op: 'LOAD', md: '直接', a: '200', title: '直接寻址', formula: 'EA = A', result: '300', color: C.indigo},
  {key: 'ind', op: 'LOAD', md: '间接', a: '200', title: '间接寻址', formula: 'EA = (A)', result: '42', color: C.purple},
  {key: 'reg', op: 'LOAD', md: '寄存器', a: 'R2', title: '寄存器寻址', formula: '操作数 = (R2)', result: '7', color: C.teal},
  {key: 'idx', op: 'LOAD', md: '变址', a: '200', title: '变址寻址', formula: 'EA = (IX) + A', result: '88', color: C.green},
  {key: 'rel', op: 'JMP', md: '相对', a: '+6', title: '相对寻址', formula: 'EA = (PC) + A', result: '1006', color: C.orange},
];
const REGS: [string, string][] = [['R1', '12'], ['R2', '7'], ['IX', '3'], ['PC', '1000']];
const MEM: [string, string][] = [['200', '300'], ['201', '15'], ['202', '9'], ['203', '88'], ['300', '42'], ['1006', 'ADD R1,R2']];
const regY = (i: number) => 330 + i * 70;
const memY = (i: number) => 320 + i * 70;
const toMem = (y: number): P[] => [[560, 312], [560, 236], [1196, 236], [1196, y], [1236, y]];

/** Beats 1–4: one diagram, six addressing modes. */
const Addressing: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(1, 0), end = at(5, 0);
  const o = vis(frame, s, end);
  if (o <= 0) return null;
  const bounds = [at(1, 0.12), at(2, 0), at(2, 0.5), at(3, 0), at(3, 0.5), at(4, 0), end];
  const mi = Math.max(0, bounds.reduce((a, b, i) => (frame >= b && i < 6 ? i : a), 0));
  const m = MODES[mi], m0 = bounds[mi], m1 = bounds[mi + 1];
  const on = (f: number) => frame >= m0 + f;
  const memHl = (i: number) => {
    if (m.key === 'dir') return i === 0 && on(18);
    if (m.key === 'ind') return (i === 0 && on(16) && !on(34)) || (i === 4 && on(34));
    if (m.key === 'idx') return i === 3 && on(34);
    if (m.key === 'rel') return i === 5 && on(34);
    return false;
  };
  const regHl = (i: number) => (m.key === 'reg' && i === 1 && on(18)) || (m.key === 'idx' && i === 2 && on(8)) || (m.key === 'rel' && i === 3 && on(8));
  const adderY = m.key === 'rel' ? memY(5) : memY(3);
  return (
    <AbsoluteFill style={{opacity: o}}>
      <Label x={430} y={262} from={s} size={22} color={C.muted}>指令</Label>
      <Label x={920} y={272} from={s + 4} size={24} weight={700} color={C.ink}>寄存器</Label>
      <Label x={1470} y={268} from={s + 8} size={24} weight={700} color={C.ink}>主存</Label>
      {MODES.map((md, k) => (
        <Pop key={md.key} from={bounds[k]} to={bounds[k + 1]} x={430} y={360}>
          <div style={{display: 'flex', borderRadius: 20, overflow: 'hidden', boxShadow: SHADOW, fontFamily: MONO, fontSize: 30, fontWeight: 650}}>
            <span style={{width: 140, height: 90, display: 'flex', alignItems: 'center', justifyContent: 'center', background: C.blue, color: '#fff'}}>{md.op}</span>
            <span style={{width: 120, height: 90, display: 'flex', alignItems: 'center', justifyContent: 'center', background: tint(md.color, 0.14),
              color: md.color, fontSize: 24}}>{md.md}</span>
            <span style={{width: 180, height: 90, display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#fff', color: C.ink,
              boxShadow: md.key === 'imm' && frame >= bounds[0] + 10 ? `inset 0 0 0 4px ${C.blue}` : undefined}}>{md.a}</span>
          </div>
        </Pop>
      ))}
      {REGS.map(([n, v], i) => (
        <Pop key={n} from={s + 6 + i * 3} x={920} y={regY(i)}>
          <div style={{width: 280, height: 56, borderRadius: 16, background: regHl(i) ? m.color : '#fff', boxShadow: SHADOW, display: 'flex',
            alignItems: 'center', justifyContent: 'space-between', padding: '0 24px', boxSizing: 'border-box', fontFamily: MONO, fontSize: 24,
            color: regHl(i) ? '#fff' : C.ink}}>
            <span style={{opacity: 0.7}}>{n}</span><span style={{fontWeight: 650}}>{v}</span>
          </div>
        </Pop>
      ))}
      {MEM.map(([a, v], i) => (
        <Pop key={a} from={s + 10 + i * 3} x={1470} y={memY(i)}>
          <div style={{width: 460, height: 56, borderRadius: 16, background: memHl(i) ? m.color : '#fff', boxShadow: SHADOW, display: 'flex',
            alignItems: 'center', justifyContent: 'space-between', padding: '0 24px', boxSizing: 'border-box', fontFamily: MONO, fontSize: 24,
            color: memHl(i) ? '#fff' : C.ink}}>
            <span style={{opacity: 0.6}}>{a}</span><span style={{fontWeight: 650}}>{v}</span>
          </div>
        </Pop>
      ))}
      <Svg>
        {m.key === 'dir' && <Wire pts={toMem(memY(0))} from={m0 + 6} len={14} to={m1} color={m.color} />}
        {m.key === 'ind' && <>
          <Wire pts={toMem(memY(0))} from={m0 + 4} len={12} to={m1} color={m.color} />
          <Wire pts={[[1702, memY(0)], [1770, memY(0)], [1770, memY(4)], [1706, memY(4)]]} from={m0 + 20} len={14} to={m1} color={m.color} />
        </>}
        {m.key === 'reg' && <Wire pts={[[652, 360], [720, 360], [720, regY(1)], [776, regY(1)]]} from={m0 + 6} len={12} to={m1} color={m.color} />}
        {(m.key === 'idx' || m.key === 'rel') && <>
          <Wire pts={[[560, 312], [560, 236], [1150, 236], [1150, adderY - 30]]} from={m0 + 6} len={16} to={m1} color={m.color} />
          <Wire pts={[[1062, regY(m.key === 'idx' ? 2 : 3)], [1106, regY(m.key === 'idx' ? 2 : 3)], [1106, adderY], [1120, adderY]]}
            from={m0 + 8} len={14} to={m1} color={m.color} />
          <Wire pts={[[1180, adderY], [1236, adderY]]} from={m0 + 26} len={8} to={m1} color={m.color} />
        </>}
      </Svg>
      {(m.key === 'idx' || m.key === 'rel') && (
        <Pop from={m0 + 20} to={m1} x={1150} y={adderY}>
          <div style={{width: 56, height: 56, borderRadius: 28, background: m.color, color: '#fff', fontSize: 34, fontWeight: 700,
            display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: SHADOW}}>+</div>
        </Pop>
      )}
      {m.key === 'ind' && <Label x={1790} y={(memY(0) + memY(4)) / 2} from={m0 + 26} to={m1} anchor="left" size={20} color={m.color} weight={650}>
        <span style={{writingMode: 'vertical-rl'}}>300 是地址</span></Label>}
      {m.key === 'idx' && <Label x={1150} y={adderY + 56} from={m0 + 26} to={m1} size={20} color={m.color} weight={650} mono>200+3=203</Label>}
      {m.key === 'rel' && <Label x={1150} y={adderY + 56} from={m0 + 26} to={m1} size={20} color={m.color} weight={650} mono>1000+6</Label>}
      {MODES.map((md, k) => (
        <React.Fragment key={md.key}>
          <Pop from={bounds[k]} to={bounds[k + 1]} x={960} y={186}><Pill solid color={md.color} size={28}>{md.title}</Pill></Pop>
          <Pop from={bounds[k] + 10} to={bounds[k + 1]} x={430} y={480}><Pill color={md.color} size={26}><span style={{fontFamily: MONO}}>{md.formula}</span></Pill></Pop>
          <Pop from={bounds[k] + 30} to={bounds[k + 1]} x={430} y={620}>
            <div style={card({padding: '20px 34px', display: 'flex', gap: 18, alignItems: 'baseline'})}>
              <span style={{fontSize: 22, color: C.muted}}>{md.key === 'rel' ? '跳转到' : '操作数'}</span>
              <span style={{fontFamily: MONO, fontSize: 52, fontWeight: 700, color: md.color}}>{md.result}</span>
            </div>
          </Pop>
        </React.Fragment>
      ))}
      <Pop from={at(1, 0.6)} to={at(2, 0)} x={430} y={740}><Pill color={C.ink2} size={22}>数据就在指令里，不用再访存</Pill></Pop>
      <Pop from={at(2, 0.8)} to={at(3, 0)} x={430} y={740}><Pill color={C.ink2} size={22}>多访问一次内存</Pill></Pop>
      <Pop from={at(3, 0.25)} to={at(3, 0.5)} x={430} y={740}><Pill color={C.ink2} size={22}>不访存，最快</Pill></Pop>
      <Pop from={at(3, 0.8)} to={at(4, 0)} x={430} y={740}><Pill color={C.ink2} size={22}>IX 递增，就能逐个访问数组</Pill></Pop>
      <Pop from={at(4, 0.6)} to={end} x={430} y={740}><Pill color={C.ink2} size={22}>程序搬到哪里都能运行</Pill></Pop>
    </AbsoluteFill>
  );
};

/** Beat 5: CISC vs RISC. */
const CiscRisc: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(5, 0);
  if (frame < s - 2) return null;
  const col = (x: number, title: string, sub: string, color: string, widths: number[], tags: string[], from: number) => (
    <Pop from={from} x={x} y={530}>
      <div style={card({width: 700, height: 560, padding: '36px 44px', boxSizing: 'border-box'})}>
        <div style={{fontSize: 40, fontWeight: 700, color}}>{title}</div>
        <div style={{fontSize: 22, color: C.muted, marginTop: 4}}>{sub}</div>
        <div style={{marginTop: 28, display: 'flex', flexDirection: 'column', gap: 12}}>
          {widths.map((w, i) => {
            const sp = pop(frame, from + 10 + i * 4);
            return <div key={i} style={{width: w * sp, height: 30, borderRadius: 9, background: tint(color, 0.25 + 0.1 * (i % 3))}} />;
          })}
        </div>
        <div style={{display: 'flex', gap: 10, marginTop: 30, flexWrap: 'wrap'}}>
          {tags.map((t) => <Pill key={t} color={color} size={22}>{t}</Pill>)}
        </div>
      </div>
    </Pop>
  );
  return (
    <AbsoluteFill>
      {col(560, 'CISC', '复杂指令集 · x86', C.orange, [180, 470, 260, 600, 120, 360], ['指令多', '长度可变', '寻址方式多'], s + 4)}
      {col(1360, 'RISC', '精简指令集 · ARM / RISC-V', C.blue, [400, 400, 400, 400, 400, 400], ['指令少', '长度固定', '适合流水线'], at(5, 0.35))}
      <Pop from={at(5, 0.8)} x={1360} y={765}><Pill solid size={24}>手机芯片 ARM 属于 RISC</Pill></Pop>
    </AbsoluteFill>
  );
};

export const IsaScene: React.FC = () => (
  <AbsoluteFill>
    <Format />
    <Addressing />
    <CiscRisc />
  </AbsoluteFill>
);
