import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT, MONO, SHADOW, tint} from '../theme';
import {ip, pop, useScene, vis} from '../anim';
import {Block, Label, Packet, Pill, Pop, Svg, Wire, card} from '../kit';

const BUS_Y = 580;
const TOP_Y = 400, BOT_Y = 740;
const X = {PC: 330, IR: 590, CU: 850, REG: 1110, ALU: 1370, MAR: 1110, MDR: 1370};
const MEM_X = 1690;

const STAGES = ['取指', '译码', '执行', '写回'];

/** Beats 0–3: the datapath with one instruction walking through it. */
const Datapath: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(0, 0), end = at(4, 0);
  const o = vis(frame, s, end);
  if (o <= 0) return null;
  const f1 = (f: number) => at(1, f), f2 = (f: number) => at(2, f);
  const stage = frame < f1(0.05) ? -1 : frame < f2(0.05) ? 0 : frame < f2(0.3) ? 1 : frame < f2(0.72) ? 2 : frame < at(3, 0) ? 3 : -1;
  const pc = frame >= f1(0.88) ? '0x104' : '0x100';
  const ir = frame >= f1(0.85) ? 'ADD R1,R2' : '—';
  const r1 = frame >= f2(0.85) ? '19' : '12';
  const hl = (k: string) => {
    if (stage === 0) return (k === 'PC' && frame < f1(0.3)) || (k === 'MAR' && frame >= f1(0.3) && frame < f1(0.5)) ||
      (k === 'MDR' && frame >= f1(0.55) && frame < f1(0.68)) || (k === 'IR' && frame >= f1(0.82)) ? 1 : 0;
    if (stage === 1) return k === 'CU' || k === 'IR' ? 1 : 0;
    if (stage === 2) return k === 'ALU' || (k === 'REG' && frame < f2(0.5)) ? 1 : 0;
    if (stage === 3) return k === 'REG' ? 1 : 0;
    return 0;
  };
  const busGlow = ip(frame, at(3, 0.08), 30);
  const memRow = stage === 0 && frame >= f1(0.42);
  return (
    <AbsoluteFill style={{opacity: o}}>
      <Svg>
        <line x1={200} y1={BUS_Y} x2={1500} y2={BUS_Y} stroke={C.line} strokeWidth={10} strokeLinecap="round"
          strokeDasharray={1400} strokeDashoffset={1400 * (1 - ip(frame, s + 4, 30))} />
        {busGlow > 0 && <line x1={200} y1={BUS_Y} x2={200 + 1300 * busGlow} y2={BUS_Y} stroke={C.blue} strokeWidth={10} strokeLinecap="round" opacity={0.85} />}
        {(['PC', 'IR', 'CU', 'REG', 'ALU'] as const).map((k, i) => (
          <line key={k} x1={X[k]} y1={TOP_Y + 52} x2={X[k]} y2={BUS_Y} stroke={busGlow > 0 ? tint(C.blue, 0.7) : C.line} strokeWidth={4}
            opacity={ip(frame, s + 16 + i * 3, 12)} />
        ))}
        {(['MAR', 'MDR'] as const).map((k, i) => (
          <line key={k} x1={X[k]} y1={BUS_Y} x2={X[k]} y2={BOT_Y - 52} stroke={busGlow > 0 ? tint(C.blue, 0.7) : C.line} strokeWidth={4}
            opacity={ip(frame, s + 30 + i * 3, 12)} />
        ))}
        <Wire pts={[[X.MAR, BOT_Y + 52], [X.MAR, 840], [MEM_X - 40, 840], [MEM_X - 40, 762]]} from={s + 34} color={C.purple} w={3} head />
        <Wire pts={[[X.MDR + 102, BOT_Y], [MEM_X - 112, BOT_Y]]} from={s + 36} color={C.purple} w={3} head={false} />
        <Wire pts={[[X.CU, TOP_Y - 52], [X.CU, 300], [X.ALU, 300], [X.ALU, TOP_Y - 54]]} from={f2(0.12)} color={C.orange} dash="9 9" to={at(3, 0)} />
        <Wire pts={[[X.REG, 300], [X.REG, TOP_Y - 54]]} from={f2(0.16)} color={C.orange} dash="9 9" to={at(3, 0)} />
      </Svg>
      <Label x={200} y={BUS_Y - 30} from={s + 10} anchor="left" size={20} color={busGlow > 0 ? C.blue : C.muted} weight={650}>内部总线</Label>
      <Label x={MEM_X - 30} y={862} from={s + 36} size={18} color={C.purple}>地址</Label>
      <Label x={1530} y={BOT_Y - 22} from={s + 38} size={18} color={C.purple}>数据</Label>
      <Block x={X.PC} y={TOP_Y} w={200} h={104} from={at(0, 0.18)} title={<span style={{fontFamily: MONO}}>{pc}</span>} sub="PC 程序计数器" hl={hl('PC')} size={30} />
      <Block x={X.IR} y={TOP_Y} w={220} h={104} from={at(0, 0.36)} title={<span style={{fontFamily: MONO, fontSize: ir.length > 2 ? 24 : 30}}>{ir}</span>}
        sub="IR 指令寄存器" hl={hl('IR')} color={C.indigo} />
      <Block x={X.CU} y={TOP_Y} w={200} h={104} from={at(0, 0.5)} title="控制器" sub="CU" hl={hl('CU')} color={C.orange} />
      <Block x={X.REG} y={TOP_Y} w={200} h={104} from={at(0, 0.62)} title={<span style={{fontFamily: MONO, fontSize: 24}}>R1={r1} R2=7</span>}
        sub="通用寄存器" hl={hl('REG')} color={C.teal} />
      <Block x={X.ALU} y={TOP_Y} w={200} h={104} from={at(0, 0.72)} title="ALU" sub="运算" hl={hl('ALU')} color={C.blue} />
      <Block x={X.MAR} y={BOT_Y} w={200} h={100} from={at(0, 0.82)} title="MAR" sub="地址寄存器" hl={hl('MAR')} color={C.purple} />
      <Block x={X.MDR} y={BOT_Y} w={200} h={100} from={at(0, 0.86)} title="MDR" sub="数据寄存器" hl={hl('MDR')} color={C.purple} />
      <Pop from={at(0, 0.9)} x={MEM_X} y={560}>
        <div style={card({width: 220, height: 400, padding: '20px 16px', boxSizing: 'border-box'})}>
          <div style={{fontSize: 26, fontWeight: 700, color: C.ink, textAlign: 'center', marginBottom: 12}}>主存</div>
          {['0x0FC  …', '0x100  ADD', '0x104  SUB', '0x108  JMP'].map((r, i) => (
            <div key={r} style={{height: 54, marginTop: 10, borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: MONO, fontSize: 20, background: memRow && i === 1 ? C.purple : C.fill, color: memRow && i === 1 ? '#fff' : C.ink2}}>{r}</div>
          ))}
        </div>
      </Pop>
      <Pop from={f1(0.02)} to={at(3, 0)} x={960} y={190}>
        <div style={{display: 'flex', gap: 10, alignItems: 'center'}}>
          {STAGES.map((st, i) => (
            <React.Fragment key={st}>
              <span style={{padding: '8px 22px', borderRadius: 999, fontSize: 24, fontWeight: 650, background: i === stage ? C.blue : '#fff',
                color: i === stage ? '#fff' : i < stage ? C.ink2 : C.faint, boxShadow: SHADOW}}>{st}</span>
              {i < 3 && <span style={{color: C.faint}}>›</span>}
            </React.Fragment>
          ))}
        </div>
      </Pop>
      <Packet pts={[[X.PC, TOP_Y + 52], [X.PC, BUS_Y], [X.MAR, BUS_Y], [X.MAR, BOT_Y - 50]]} from={f1(0.1)} len={f1(0.3) - f1(0.1)} tag="0x100" color={C.blue} />
      <Packet pts={[[X.MAR, BOT_Y + 50], [X.MAR, 840], [MEM_X - 40, 840], [MEM_X - 40, 762]]} from={f1(0.32)} len={f1(0.44) - f1(0.32)} color={C.purple} />
      <Packet pts={[[MEM_X - 112, BOT_Y], [X.MDR + 100, BOT_Y]]} from={f1(0.5)} len={f1(0.58) - f1(0.5)} tag="ADD" color={C.purple} />
      <Packet pts={[[X.MDR, BOT_Y - 50], [X.MDR, BUS_Y], [X.IR, BUS_Y], [X.IR, TOP_Y + 52]]} from={f1(0.6)} len={f1(0.82) - f1(0.6)} tag="ADD" color={C.indigo} />
      <Label x={X.PC} y={TOP_Y - 80} from={f1(0.88)} to={f2(0)} size={24} weight={700} color={C.blue}>+4 指向下一条</Label>
      <Packet pts={[[X.IR + 110, TOP_Y], [X.CU - 100, TOP_Y]]} from={f2(0.04)} len={12} color={C.orange} r={9} />
      <Label x={X.CU} y={TOP_Y + 82} from={f2(0.1)} to={f2(0.35)} size={20} weight={650} color={C.orange}>译码：这是加法</Label>
      <Packet pts={[[X.REG + 100, TOP_Y], [X.ALU - 100, TOP_Y]]} from={f2(0.35)} len={16} tag="12, 7" color={C.teal} />
      <Packet pts={[[X.ALU, TOP_Y + 52], [X.ALU, 500], [X.REG, 500], [X.REG, TOP_Y + 52]]} from={f2(0.72)} len={18} tag="19" color={C.blue} />
      <Pop from={at(3, 0.35)} to={end} x={430} y={760}>
        <div style={card({padding: '20px 24px', display: 'flex', gap: 20})}>
          {(['单总线', '专用通路'] as const).map((t, k) => (
            <div key={t} style={{textAlign: 'center'}}>
              <svg width={200} height={110} viewBox="0 0 200 110">
                {k === 0 ? (
                  <>
                    <line x1={10} y1={70} x2={190} y2={70} stroke={C.blue} strokeWidth={6} strokeLinecap="round" />
                    {[30, 80, 130, 175].map((x) => <g key={x}><line x1={x} y1={34} x2={x} y2={70} stroke={C.blue} strokeWidth={3} />
                      <rect x={x - 16} y={14} width={32} height={22} rx={6} fill={tint(C.blue, 0.2)} /></g>)}
                  </>
                ) : (
                  <>
                    {[[30, 30], [170, 30], [30, 90], [170, 90]].map(([x, y]) => <rect key={`${x}${y}`} x={x - 18} y={y - 12} width={36} height={24} rx={6} fill={tint(C.green, 0.25)} />)}
                    {[[48, 30, 152, 30], [48, 90, 152, 90], [30, 42, 30, 78], [170, 42, 170, 78], [48, 38, 152, 82]].map(([a, b, c, d], i) =>
                      <line key={i} x1={a} y1={b} x2={c} y2={d} stroke={C.green} strokeWidth={3} />)}
                  </>
                )}
              </svg>
              <div style={{fontSize: 20, fontWeight: 650, color: k ? C.green : C.blue}}>{t}</div>
            </div>
          ))}
        </div>
      </Pop>
    </AbsoluteFill>
  );
};

const GATE = 'M0,0 h22 a22,22 0 0 1 0,44 h-22 Z';

/** Beat 4: hard-wired control. */
const Hardwired: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(4, 0), end = at(5, 0);
  const o = vis(frame, s, end);
  if (o <= 0) return null;
  const ins = ['操作码（来自 IR）', '时序节拍 T1–T4', '状态标志 ZF / CF…'];
  const outs = ['PCout', 'MARin', 'Read', 'MDRout', 'IRin', 'PC+1'];
  const lit = Math.floor((frame - at(4, 0.45)) / 7);
  return (
    <AbsoluteFill style={{opacity: o}}>
      <Svg>
        {ins.map((_, i) => <Wire key={i} pts={[[560, 380 + i * 120], [732, 380 + i * 120]]} from={s + 10 + i * 4} color={C.faint} />)}
        {outs.map((_, i) => <Wire key={i} pts={[[1190, 500], [1420, 310 + i * 76]]} from={at(4, 0.35) + i * 3} color={i <= lit ? C.orange : C.line} />)}
        <g transform="translate(790 360)" opacity={ip(frame, s + 14, 14)}>
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <g key={i} transform={`translate(${(i % 3) * 120} ${Math.floor(i / 3) * 140 + 20})`}>
              <path d={GATE} fill={tint(C.orange, 0.12)} stroke={C.orange} strokeWidth={3} />
              <line x1={-18} y1={12} x2={0} y2={12} stroke={C.orange} strokeWidth={3} />
              <line x1={-18} y1={32} x2={0} y2={32} stroke={C.orange} strokeWidth={3} />
              <line x1={44} y1={22} x2={66} y2={22} stroke={C.orange} strokeWidth={3} />
            </g>
          ))}
        </g>
      </Svg>
      <Pop from={s + 6} x={960} y={500}>
        <div style={{width: 440, height: 340, borderRadius: 30, border: `2px solid ${tint(C.orange, 0.5)}`, background: tint(C.orange, 0.03)}} />
      </Pop>
      <Label x={960} y={680} from={s + 12} size={24} weight={700} color={C.orange}>组合逻辑电路</Label>
      {ins.map((t, i) => <Pop key={t} from={s + 8 + i * 4} x={540} y={380 + i * 120} anchor="right"><Pill color={C.ink2} size={24}>{t}</Pill></Pop>)}
      {outs.map((t, i) => (
        <Pop key={t} from={at(4, 0.35) + i * 3} x={1440} y={310 + i * 76} anchor="left">
          <Pill solid={i <= lit} color={C.orange} size={22}><span style={{fontFamily: MONO}}>{t}</span></Pill>
        </Pop>
      ))}
      <Label x={1460} y={250} from={at(4, 0.35)} anchor="left" size={20} color={C.muted}>控制信号</Label>
      <Pop from={at(4, 0.7)} x={960} y={800}>
        <div style={{display: 'flex', gap: 16}}><Pill color={C.green} size={26}>速度快</Pill><Pill color={C.red} size={26}>修改困难</Pill></div>
      </Pop>
    </AbsoluteFill>
  );
};

const MICRO: [string, string[]][] = [
  ['μ0', ['PCout', 'MARin', 'Read']], ['μ1', ['MDRout', 'IRin', 'PC+1']], ['μ2', ['R1out', 'Yin']],
  ['μ3', ['R2out', 'ALU:ADD', 'Zin']], ['μ4', ['Zout', 'R1in']], ['μ5', ['→ 回到取指']],
];

/** Beat 5: micro-programmed control. */
const Micro: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(5, 0);
  if (frame < s - 2) return null;
  const step = Math.max(0, Math.min(5, Math.floor((frame - at(5, 0.3)) / 16)));
  const running = frame >= at(5, 0.3);
  const rowY = (i: number) => 330 + i * 76;
  return (
    <AbsoluteFill>
      <Pop from={s + 4} x={340} y={480}>
        <div style={card({padding: '22px 30px', textAlign: 'center'})}>
          <div style={{fontSize: 20, color: C.muted}}>IR 操作码</div>
          <div style={{fontFamily: MONO, fontSize: 40, fontWeight: 700, color: C.indigo, marginTop: 4}}>ADD</div>
        </div>
      </Pop>
      <Svg>
        <Wire pts={[[450, 480], [600, 480], [600, rowY(2)], [640, rowY(2)]]} from={s + 14} color={C.indigo} />
      </Svg>
      <Label x={560} y={440} from={s + 16} size={18} color={C.muted}>微地址</Label>
      <Label x={980} y={262} from={s + 6} size={24} weight={700} color={C.ink}>控制存储器 CM</Label>
      {MICRO.map(([n, sig], i) => {
        const on = running && i === step;
        return (
          <Pop key={n} from={s + 8 + i * 3} x={980} y={rowY(i)}>
            <div style={{width: 640, height: 60, borderRadius: 16, background: on ? C.indigo : '#fff', boxShadow: SHADOW, display: 'flex',
              alignItems: 'center', padding: '0 24px', gap: 22, boxSizing: 'border-box', color: on ? '#fff' : C.ink2}}>
              <span style={{fontFamily: MONO, fontSize: 22, opacity: 0.7, width: 40}}>{n}</span>
              <span style={{fontFamily: MONO, fontSize: 22}}>{sig.join('  ')}</span>
            </div>
          </Pop>
        );
      })}
      {running && (
        <div style={{position: 'absolute', left: 640, top: rowY(step), transform: 'translate(-100%, -50%)', fontFamily: FONT, fontSize: 22,
          fontWeight: 700, color: C.indigo}}>μPC ▸</div>
      )}
      <Label x={1530} y={300} from={at(5, 0.3)} size={20} color={C.muted}>本步发出的控制信号</Label>
      {running && MICRO[step][1].map((sig, k) => (
        <div key={`${step}${k}`} style={{position: 'absolute', left: 1530, top: 370 + k * 64, transform: `translate(-50%,-50%) scale(${0.8 + 0.2 * pop(frame, at(5, 0.3) + step * 16 + k * 2)})`}}>
          <Pill solid color={C.orange} size={22}><span style={{fontFamily: MONO}}>{sig}</span></Pill>
        </div>
      ))}
      <Pop from={at(5, 0.75)} x={960} y={820}>
        <div style={{display: 'flex', gap: 16}}><Pill color={C.green} size={26}>设计灵活</Pill><Pill color={C.green} size={26}>容易修改</Pill>
          <Pill color={C.orange} size={26}>速度稍慢</Pill></div>
      </Pop>
    </AbsoluteFill>
  );
};

export const CpuScene: React.FC = () => (
  <AbsoluteFill>
    <Datapath />
    <Hardwired />
    <Micro />
  </AbsoluteFill>
);