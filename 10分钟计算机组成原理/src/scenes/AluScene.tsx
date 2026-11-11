import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT, MONO, tint} from '../theme';
import {pop, useScene, vis} from '../anim';
import {BitRow, Block, Label, Pill, Pop, Svg, Wire, card} from '../kit';

const Val: React.FC<{x: number; y: number; from: number; to?: number; v: string; color?: string; name: string}> = ({x, y, from, to, v, color = C.blue, name}) => (
  <Pop from={from} to={to} x={x} y={y}>
    <div style={{display: 'flex', alignItems: 'center', gap: 10}}>
      <span style={{fontSize: 26, color: C.ink2, fontWeight: 600, fontFamily: MONO}}>{name}</span>
      <span style={{width: 46, height: 46, borderRadius: 23, background: color, color: '#fff', fontFamily: MONO, fontSize: 26, fontWeight: 700,
        display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{v}</span>
    </div>
  </Pop>
);

/** Beat 0: one full adder. */
const FullAdder: React.FC = () => {
  const {at} = useScene();
  const s = at(0, 0), end = at(1, 0);
  return (
    <>
      <Svg>
        <Wire pts={[[880, 270], [880, 366]]} from={s + 10} to={end} color={C.faint} />
        <Wire pts={[[1040, 270], [1040, 366]]} from={s + 12} to={end} color={C.faint} />
        <Wire pts={[[1330, 470], [1124, 470]]} from={s + 14} to={end} color={C.faint} />
        <Wire pts={[[960, 572], [960, 680]]} from={at(0, 0.55)} to={end} color={C.blue} />
        <Wire pts={[[796, 470], [600, 470]]} from={at(0, 0.6)} to={end} color={C.orange} />
      </Svg>
      <Block x={960} y={470} w={320} h={200} from={s} to={end} title="全加器" sub="Full Adder" size={44} />
      <Val x={880} y={240} from={s + 10} to={end} name="A" v="1" />
      <Val x={1040} y={240} from={s + 14} to={end} name="B" v="1" />
      <Val x={1400} y={470} from={s + 18} to={end} name="Cin" v="1" color={C.orange} />
      <Val x={960} y={720} from={at(0, 0.58)} to={end} name="S" v="1" color={C.green} />
      <Val x={520} y={470} from={at(0, 0.64)} to={end} name="Cout" v="1" color={C.orange} />
      <Pop from={at(0, 0.7)} to={end} x={1520} y={720}>
        <div style={card({padding: '22px 32px', fontFamily: MONO, fontSize: 28, color: C.ink, lineHeight: 1.7, whiteSpace: 'nowrap'})}>
          <div>S = A ⊕ B ⊕ Cin</div>
          <div>Cout = AB + (A ⊕ B)·Cin</div>
        </div>
      </Pop>
      <Label x={960} y={178} from={at(0, 0.3)} to={end} size={22}>1 + 1 + 1 = 11₂ → 本位 1，进位 1</Label>
    </>
  );
};

const XS = [420, 760, 1100, 1440];
const A = '0111', B = '0001', SUM = '1000', CARRY = [1, 1, 1, 0];

/** Beats 1–2: ripple carry, then carry look-ahead. */
const Adders: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(1, 0), end = at(3, 0);
  const r0 = at(1, 0.32), step = 22, cla = at(2, 0.32);
  const inCla = frame >= at(2, 0);
  return (
    <>
      <Svg>
        <Wire pts={[[1660, 470], [1544, 470]]} from={s + 10} to={end} color={C.faint} />
        {[0, 1, 2, 3].map((bit) => {
          const x = XS[3 - bit];
          const done = r0 + (bit + 1) * step;
          const carryOn = !inCla && frame >= done && CARRY[bit] === 1;
          const to = bit < 3 ? [XS[3 - bit - 1] + 102, 470] : [220, 470];
          return (
            <g key={bit}>
              <Wire pts={[[x - 102, 470], to as [number, number]]} from={s + 10} to={end} color={carryOn ? C.orange : C.line} w={carryOn ? 4 : 3}
                opacity={inCla ? 0.35 : 1} />
              <Wire pts={[[x, 537], [x, 606]]} from={inCla ? cla + 8 : done} to={inCla ? end : at(2, 0)} color={C.green} />
              <Wire pts={[[x, 330], [x, 402]]} from={cla} to={end} color={C.purple} len={14} />
            </g>
          );
        })}
      </Svg>
      {[0, 1, 2, 3].map((bit) => {
        const x = XS[3 - bit];
        const active = inCla ? (frame >= cla && frame < cla + 30 ? 1 : 0) : frame >= r0 + bit * step && frame < r0 + (bit + 1) * step ? 1 : 0;
        const done = r0 + (bit + 1) * step;
        return (
          <React.Fragment key={bit}>
            <Block x={x} y={470} w={204} h={130} from={s + bit * 4} to={end} title={`FA${bit}`} size={32} hl={active}
              color={inCla ? C.purple : C.orange} sub={`A=${A[3 - bit]}  B=${B[3 - bit]}`} />
            <Label x={x} y={650} from={inCla ? cla + 8 : done} to={inCla ? end : at(2, 0)} size={30} weight={700} color={C.green} mono>
              S{bit}={SUM[3 - bit]}
            </Label>
            {!inCla && <Label x={x - 170} y={436} from={done} to={at(2, 0)} size={22} weight={700}
              color={CARRY[bit] ? C.orange : C.muted} mono>{CARRY[bit]}</Label>}
          </React.Fragment>
        );
      })}
      <Label x={1660} y={436} from={s + 12} to={end} size={22} weight={700} color={C.muted} mono>0</Label>
      <Pop from={at(1, 0.78)} to={at(2, 0)} x={960} y={790}>
        <div style={{display: 'flex', gap: 24, alignItems: 'center'}}>
          <span style={{fontFamily: MONO, fontSize: 34, color: C.ink}}>0111 + 0001 = 1000</span>
          <Pill color={C.orange} size={24}>进位逐级传递 · 延迟随位数增长</Pill>
        </div>
      </Pop>
      <Pop from={at(2, 0.12)} to={end} x={930} y={292}>
        <div style={{width: 1300, height: 72, borderRadius: 20, background: tint(C.purple, 0.1), border: `2px solid ${tint(C.purple, 0.5)}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 30, fontWeight: 700, color: C.purple}}>
          超前进位逻辑 CLA
        </div>
      </Pop>
      <Pop from={at(2, 0.5)} to={end} x={960} y={790}>
        <div style={{display: 'flex', gap: 28, alignItems: 'center'}}>
          <span style={{fontFamily: MONO, fontSize: 32, color: C.ink}}>C<sub>i+1</sub> = G<sub>i</sub> + P<sub>i</sub>·C<sub>i</sub></span>
          <span style={{fontFamily: MONO, fontSize: 24, color: C.muted}}>G = A·B　P = A ⊕ B</span>
          <Pill color={C.purple} size={24}>所有进位同时得到</Pill>
        </div>
      </Pop>
    </>
  );
};

/** Beat 3: overflow. */
const Overflow: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(3, 0), end = at(4, 0);
  const X = 640, size = 64, gap = 10;
  const colX = (i: number) => X + i * (size + gap) + (i >= 4 ? gap * 2 : 0) + size / 2;
  const hi = vis(frame, at(3, 0.45), end);
  return (
    <>
      <Pop from={at(3, 0.45)} to={end} x={colX(0)} y={505}>
        <div style={{width: 92, height: 430, borderRadius: 26, background: tint(C.red, 0.07), border: `2px solid ${tint(C.red, 0.35)}`}} />
      </Pop>
      {Array.from({length: 7}, (_, i) => (
        <Label key={i} x={colX(i)} y={330} from={at(3, 0.3) + (6 - i) * 3} to={end} size={24} weight={700} mono
          color={i === 0 ? C.red : C.orange}>1</Label>
      ))}
      <Label x={colX(0) - 92} y={330} from={at(3, 0.5)} to={end} size={24} weight={700} mono color={C.red}>0</Label>
      <Label x={colX(0) - 92} y={296} from={at(3, 0.55)} to={end} size={18} color={C.red}>进位输出</Label>
      <Label x={colX(0)} y={296} from={at(3, 0.55)} to={end} size={18} color={C.red}>进位输入</Label>
      <BitRow bits="01111111" x={X} y={410} from={s + 4} to={end} size={size} gap={gap} />
      <BitRow bits="00000001" x={X} y={510} from={s + 10} to={end} size={size} gap={gap} />
      <Label x={X - 40} y={510} from={s + 10} to={end} size={44} color={C.ink2} anchor="right">+</Label>
      <Pop from={at(3, 0.2)} to={end} x={X} y={578} anchor="left">
        <div style={{width: 602, height: 3, background: C.ink, borderRadius: 2}} />
      </Pop>
      <BitRow bits="10000000" x={X} y={650} from={at(3, 0.25)} to={end} size={size} gap={gap}
        lit={(i) => (i === 0 ? hi : 0)} color={() => C.red} />
      <Label x={1290} y={410} from={s + 4} to={end} anchor="left" size={34} weight={650} color={C.ink}>+127</Label>
      <Label x={1290} y={510} from={s + 10} to={end} anchor="left" size={34} weight={650} color={C.ink}>+1</Label>
      <Label x={1290} y={650} from={at(3, 0.25)} to={end} anchor="left" size={34} weight={700} color={C.red}>= −128 ?!</Label>
      <Pop from={at(3, 0.62)} to={end} x={960} y={800}>
        <Pill color={C.red} size={28}>符号位：进位输入 1 ≠ 进位输出 0 → 溢出</Pill>
      </Pop>
    </>
  );
};

/** Beat 4: the ALU. */
const Alu: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(4, 0);
  if (frame < s - 2) return null;
  const sp = pop(frame, s + 2);
  const shape = '770,330 910,330 960,385 1010,330 1150,330 1060,600 860,600';
  const parts: [string, string][] = [['加法器', C.blue], ['逻辑运算', C.indigo], ['移位器', C.teal]];
  return (
    <>
      <Svg>
        <Wire pts={[[840, 220], [840, 326]]} from={s + 14} color={C.faint} />
        <Wire pts={[[1080, 220], [1080, 326]]} from={s + 16} color={C.faint} />
        <Wire pts={[[960, 602], [960, 708]]} from={s + 20} color={C.blue} />
        <Wire pts={[[620, 465], [812, 465]]} from={s + 22} color={C.orange} dash="9 9" />
        <Wire pts={[[1110, 465], [1290, 465]]} from={at(4, 0.4)} color={C.purple} />
        <g opacity={Math.min(1, sp * 1.5)} transform={`translate(960,465) scale(${0.9 + 0.1 * sp}) translate(-960,-465)`}>
          <polygon points={shape} fill="#fff" stroke={tint(C.blue, 0.5)} strokeWidth={3} strokeLinejoin="round"
            style={{filter: 'drop-shadow(0 12px 28px rgba(0,0,0,0.08))'}} />
          <text x={960} y={500} textAnchor="middle" fontFamily={FONT} fontSize={64} fontWeight={700} fill={C.ink}>ALU</text>
        </g>
      </Svg>
      <Label x={840} y={196} from={s + 14} size={28} color={C.ink2} weight={650} mono>A</Label>
      <Label x={1080} y={196} from={s + 16} size={28} color={C.ink2} weight={650} mono>B</Label>
      <Label x={960} y={740} from={s + 20} size={28} color={C.blue} weight={650} mono>F</Label>
      <Label x={600} y={465} from={s + 22} size={24} color={C.orange} weight={600} anchor="right">ALUop 控制</Label>
      {parts.map(([t, c], i) => (
        <Pop key={t} from={at(4, 0.08) + i * 8} x={300} y={385 + i * 80}><Pill color={c} size={26}>{t}</Pill></Pop>
      ))}
      <Pop from={at(4, 0.42)} x={1450} y={465}>
        <div style={card({padding: '20px 24px'})}>
          <div style={{fontSize: 20, color: C.muted, marginBottom: 12}}>标志寄存器</div>
          <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10}}>
            {[['ZF', '零'], ['SF', '符号'], ['CF', '进位'], ['OF', '溢出']].map(([f, n]) => (
              <Pill key={f} color={C.purple} size={22}>{f} {n}</Pill>
            ))}
          </div>
        </div>
      </Pop>
      <Pop from={at(4, 0.7)} x={960} y={820}>
        <div style={{display: 'flex', gap: 16}}>
          <Pill color={C.ink2} size={26}>乘法 = 加法 + 移位</Pill>
          <Pill color={C.ink2} size={26}>除法 = 减法 + 移位</Pill>
        </div>
      </Pop>
    </>
  );
};

export const AluScene: React.FC = () => (
  <AbsoluteFill>
    <FullAdder />
    <Adders />
    <Overflow />
    <Alu />
  </AbsoluteFill>
);
