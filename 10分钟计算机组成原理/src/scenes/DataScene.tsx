import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT, MONO, SHADOW, tint} from '../theme';
import {easeInOut, easeOut, ip, pop, prog, useScene, vis} from '../anim';
import {Bit, BitRow, Label, Pill, Pop, Svg, Wire, bitRowWidth, card} from '../kit';

const BITS = '10110110';
const WEIGHTS = [128, 64, 32, 16, 8, 4, 2, 1];

/** Beats 0–1: place values, then nibbles to hex. */
const Binary: React.FC = () => {
  const {frame, at} = useScene();
  const end = at(2, 0);
  const o = vis(frame, at(0, 0), end);
  if (o <= 0) return null;
  const size = 104, gap = 22;
  const split = ip(frame, at(1, 0.15), 24);
  const width = 8 * size + 7 * gap + split * 80;
  const x0 = 960 - width / 2;
  const lit0 = at(0, 0.5), litStep = 9;
  const ones = BITS.split('').map((b, i) => (b === '1' ? i : -1)).filter((i) => i >= 0);
  const litCount = Math.max(0, Math.min(ones.length, Math.floor((frame - lit0) / litStep) + 1));
  const sumO = vis(frame, lit0, at(1, 0.1));
  return (
    <AbsoluteFill style={{opacity: o}}>
      {BITS.split('').map((b, i) => {
        const s = pop(frame, at(0, 0) + i * 3);
        const x = x0 + i * (size + gap) + (i >= 4 ? split * 80 : 0);
        const lit = ones.indexOf(i) >= 0 && ones.indexOf(i) < litCount ? 1 : 0;
        const nib = i < 4 ? C.blue : C.indigo;
        return (
          <div key={i} style={{position: 'absolute', left: x, top: 380, opacity: Math.min(1, s * 1.5), transform: `translateY(${(1 - s) * 30}px)`}}>
            <Bit v={b} size={size} lit={Math.max(lit * (1 - split), split * (b === '1' ? 1 : 0))} color={split > 0.5 ? nib : C.blue} />
            <div style={{textAlign: 'center', marginTop: 16, fontFamily: FONT, fontSize: 24, color: lit ? C.blue : C.muted, fontWeight: 600,
              opacity: 1 - split}}>{WEIGHTS[i]}</div>
          </div>
        );
      })}
      <div style={{position: 'absolute', left: 0, right: 0, top: 600, textAlign: 'center', fontFamily: FONT, opacity: sumO}}>
        <span style={{fontSize: 44, color: C.ink2}}>
          {ones.slice(0, litCount).map((i) => WEIGHTS[i]).join(' + ')}
        </span>
        {litCount === ones.length && <span style={{fontSize: 64, fontWeight: 700, color: C.blue, marginLeft: 24}}>= 182</span>}
      </div>
      {[0, 1].map((k) => {
        const s = pop(frame, at(1, 0.35) + k * 8);
        const cx = x0 + (k === 0 ? 0 : 4 * (size + gap) + split * 80) + (4 * size + 3 * gap) / 2;
        return (
          <div key={k} style={{position: 'absolute', left: cx, top: 600, transform: `translateX(-50%) scale(${0.6 + 0.4 * s})`, opacity: Math.min(1, s * 1.4),
            textAlign: 'center', fontFamily: FONT}}>
            <div style={{fontSize: 20, color: C.muted, fontFamily: MONO}}>{k === 0 ? '1011' : '0110'}</div>
            <div style={{width: 120, height: 120, borderRadius: 30, marginTop: 10, background: k === 0 ? C.blue : C.indigo, color: '#fff',
              fontSize: 72, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: SHADOW}}>
              {k === 0 ? 'B' : '6'}
            </div>
          </div>
        );
      })}
      <Label x={960} y={830} from={at(1, 0.6)} size={34} color={C.ink} weight={650} mono>1011 0110₂ = 0xB6 = 182</Label>
      <Label x={960} y={300} from={at(1, 0.2)} size={24} color={C.muted}>4 位二进制 = 1 位十六进制</Label>
    </AbsoluteFill>
  );
};

const RowLabel: React.FC<{x: number; y: number; from: number; to?: number; children: React.ReactNode; color?: string}> =
  ({x, y, from, to, children, color = C.ink}) => (
    <Label x={x} y={y} from={from} to={to} anchor="right" size={40} weight={650} color={color}>{children}</Label>
  );

/** Beat 2: sign-magnitude and its two zeros. */
const SignMag: React.FC = () => {
  const {at} = useScene();
  const end = at(3, 0);
  const X = 700, sign = (i: number) => (i === 0 ? C.orange : C.blue);
  const rows: [string, string, number][] = [['+5', '00000101', 0.12], ['−5', '10000101', 0.22], ['+0', '00000000', 0.55], ['−0', '10000000', 0.62]];
  return (
    <>
      <Label x={960} y={220} from={at(2, 0.05)} to={end} size={30} color={C.ink2} weight={600}>原码：最高位是符号位</Label>
      {rows.map(([n, bits, f], k) => (
        <React.Fragment key={k}>
          <RowLabel x={X - 40} y={330 + k * 120 + (k >= 2 ? 30 : 0)} from={at(2, f)} to={end}>{n}</RowLabel>
          <BitRow bits={bits} x={X} y={330 + k * 120 + (k >= 2 ? 30 : 0)} from={at(2, f)} to={end} size={76}
            lit={(i) => (i === 0 && bits[0] === '1' ? 1 : 0)} color={sign} ring={(i) => (i === 0 ? tint(C.orange, 0.6) : undefined)} />
        </React.Fragment>
      ))}
      <Pop from={at(2, 0.72)} to={end} x={1560} y={720}><Pill color={C.red} size={28}>0 有两种写法</Pill></Pop>
      <Pop from={at(2, 0.82)} to={end} x={1560} y={800}><Pill color={C.red} size={24}>加减还要判断符号</Pill></Pop>
      <Pop from={at(2, 0.25)} to={end} x={1560} y={390}><Pill color={C.orange} size={24}>符号位 0 正 · 1 负</Pill></Pop>
    </>
  );
};

/** Beat 3: two's complement by invert + 1. */
const TwosComp: React.FC = () => {
  const {frame, at} = useScene();
  const end = at(4, 0);
  const X = 560;
  const steps: [string, string, string, number][] = [
    ['+5', '00000101', C.blue, 0.05], ['取反', '11111010', C.indigo, 0.25], ['+1', '11111011', C.green, 0.42],
  ];
  return (
    <>
      <Label x={960} y={220} from={at(3, 0.02)} to={end} size={30} color={C.ink2} weight={600}>补码：取反，再加 1</Label>
      {steps.map(([n, bits, col, f], k) => (
        <React.Fragment key={k}>
          <RowLabel x={X - 40} y={360 + k * 170} from={at(3, f)} to={end} color={col}>{n}</RowLabel>
          <BitRow bits={bits} x={X} y={360 + k * 170} from={at(3, f)} to={end} size={72}
            lit={(i) => (bits[i] === '1' && k > 0 ? 0.85 : 0)} color={() => col} stagger={3} />
        </React.Fragment>
      ))}
      <Svg>
        <Wire pts={[[X + 330, 410], [X + 330, 476]]} from={at(3, 0.2)} to={end} color={C.faint} />
        <Wire pts={[[X + 330, 580], [X + 330, 646]]} from={at(3, 0.38)} to={end} color={C.faint} />
      </Svg>
      <Label x={X + 760} y={700} from={at(3, 0.48)} to={end} anchor="left" size={38} weight={700} color={C.green}>= −5</Label>
      <Pop from={at(3, 0.62)} to={end} x={1560} y={420}>
        <div style={card({padding: '28px 36px', textAlign: 'center'})}>
          <div style={{fontSize: 22, color: C.muted}}>减法变加法</div>
          <div style={{fontFamily: MONO, fontSize: 34, color: C.ink, marginTop: 12}}>A − B</div>
          <div style={{fontFamily: MONO, fontSize: 34, color: C.blue, marginTop: 6}}>= A + [−B]补</div>
          <div style={{marginTop: 18}}><Pill size={22} color={C.green}>只需一个加法器</Pill></div>
        </div>
      </Pop>
    </>
  );
};

/** Beat 4: the 8-bit wheel. */
const Dial: React.FC = () => {
  const {frame, at} = useScene();
  const start = at(4, 0), end = at(5, 0);
  const o = vis(frame, start, end);
  if (o <= 0) return null;
  const cx = 700, cy = 540, R = 250;
  const ang = (u: number) => (u / 256) * Math.PI * 2 - Math.PI / 2;
  const pt = (u: number, r: number) => [cx + Math.cos(ang(u)) * r, cy + Math.sin(ang(u)) * r];
  const arc = (u0: number, u1: number, r: number) => {
    const [x0, y0] = pt(u0, r), [x1, y1] = pt(u1, r);
    return `M${x0},${y0} A${r},${r} 0 ${u1 - u0 > 128 ? 1 : 0} 1 ${x1},${y1}`;
  };
  let u = 0;
  const a1 = ip(frame, at(4, 0.15), at(4, 0.4) - at(4, 0.15), easeInOut);
  const a2 = ip(frame, at(4, 0.45), 12, easeOut);
  const a3 = ip(frame, at(4, 0.62), at(4, 0.85) - at(4, 0.62), easeInOut);
  u = a1 * 127 + a2 * 1 + a3 * (251 - 128);
  const ui = Math.round(u) & 255, v = ui < 128 ? ui : ui - 256;
  const draw = ip(frame, start + 4, 30);
  const [nx, ny] = pt(u, R - 50);
  const wrap = vis(frame, at(4, 0.42), at(4, 0.62));
  return (
    <AbsoluteFill style={{opacity: o}}>
      <Svg>
        <circle cx={cx} cy={cy} r={R + 40} fill="#fff" style={{filter: 'drop-shadow(0 12px 30px rgba(0,0,0,0.07))'}} />
        <path d={arc(0.5, 127.5, R)} stroke={C.blue} strokeWidth={22} fill="none" strokeLinecap="round"
          strokeDasharray={2000} strokeDashoffset={2000 * (1 - draw)} />
        <path d={arc(128.5, 255.5, R)} stroke={C.orange} strokeWidth={22} fill="none" strokeLinecap="round"
          strokeDasharray={2000} strokeDashoffset={2000 * (1 - draw)} />
        {Array.from({length: 32}, (_, i) => {
          const [x0, y0] = pt(i * 8, R - 26), [x1, y1] = pt(i * 8, R - (i % 4 === 0 ? 46 : 36));
          return <line key={i} x1={x0} y1={y0} x2={x1} y2={y1} stroke={C.line} strokeWidth={3} strokeLinecap="round" />;
        })}
        <line x1={cx} y1={cy} x2={nx} y2={ny} stroke={C.ink} strokeWidth={6} strokeLinecap="round" />
        <circle cx={cx} cy={cy} r={12} fill={C.ink} />
        {([[7, '0'], [64, '+64'], [119, '+127'], [137, '−128'], [192, '−64'], [249, '−1']] as [number, string][]).map(([k, t]) => {
          const [x, y] = pt(k, R + 78);
          return <text key={t} x={x} y={y + 9} textAnchor="middle" fontFamily={FONT} fontSize={26} fontWeight={600}
            fill={k < 128 ? C.blue : C.orange}>{t}</text>;
        })}
      </Svg>
      <div style={{position: 'absolute', left: cx, top: cy + 110, transform: 'translateX(-50%)', textAlign: 'center', fontFamily: FONT}}>
        <div style={{fontSize: 56, fontWeight: 700, color: v < 0 ? C.orange : C.blue}}>{v > 0 ? `+${v}` : v}</div>
        <div style={{fontFamily: MONO, fontSize: 26, color: C.ink2}}>{ui.toString(2).padStart(8, '0').replace(/(\d{4})(\d{4})/, '$1 $2')}</div>
      </div>
      <div style={{position: 'absolute', left: 1440, top: 560, transform: 'translate(-50%, -50%)', opacity: wrap}}>
        <Pill color={C.red} size={24}>+127 再加 1，绕回 −128</Pill>
      </div>
      <Pop from={at(4, 0.08)} x={1440} y={430}>
        <div style={{textAlign: 'center'}}>
          <div style={{fontSize: 24, color: C.muted}}>8 位补码范围</div>
          <div style={{fontSize: 72, fontWeight: 700, color: C.ink, marginTop: 6}}>−128 ~ +127</div>
        </div>
      </Pop>
      <Pop from={at(4, 0.65)} x={1440} y={660}>
        <div style={card({padding: '22px 34px', display: 'flex', gap: 22, alignItems: 'center'})}>
          <span style={{fontSize: 40, fontWeight: 700, color: C.orange}}>−5</span>
          <span style={{fontSize: 30, color: C.faint}}>=</span>
          <span style={{fontFamily: MONO, fontSize: 40, color: C.ink}}>1111 1011</span>
        </div>
      </Pop>
    </AbsoluteFill>
  );
};

/** Beat 5: IEEE 754 single precision. */
const Float: React.FC = () => {
  const {frame, at} = useScene();
  const start = at(5, 0);
  if (frame < start) return null;
  const bits = '1' + '10000001' + '10100000000000000000000';
  const w = 40, g = 5, x0 = 960 - (32 * w + 31 * g + 2 * 18) / 2;
  const segColor = (i: number) => (i === 0 ? C.pink : i < 9 ? C.orange : C.blue);
  const xAt = (i: number) => x0 + i * (w + g) + (i >= 1 ? 18 : 0) + (i >= 9 ? 18 : 0);
  const groups: [number, number, string, string][] = [[0, 0, '符号 S', '1 位'], [1, 8, '阶码 E', '8 位'], [9, 31, '尾数 M', '23 位']];
  return (
    <AbsoluteFill>
      {bits.split('').map((b, i) => {
        const s = pop(frame, start + 6 + i * 1.2);
        const c = segColor(i);
        return (
          <div key={i} style={{position: 'absolute', left: xAt(i), top: 400, width: w, height: 74, borderRadius: 10,
            background: tint(c, 0.12), color: c, fontFamily: MONO, fontSize: 26, fontWeight: 600, display: 'flex',
            alignItems: 'center', justifyContent: 'center', opacity: Math.min(1, s * 1.5), transform: `translateY(${(1 - s) * 24}px)`}}>
            {b}
          </div>
        );
      })}
      {groups.map(([a, b, name, n], k) => {
        const c = segColor(a);
        const l = xAt(a), r = xAt(b) + w;
        const o = vis(frame, at(5, 0.25 + k * 0.08));
        return (
          <div key={k} style={{position: 'absolute', left: l, width: r - l, top: 300, opacity: o, textAlign: 'center', fontFamily: FONT}}>
            <div style={{fontSize: 28, fontWeight: 700, color: c, whiteSpace: 'nowrap'}}>{name}</div>
            <div style={{fontSize: 20, color: C.muted}}>{n}</div>
            <div style={{height: 10, borderTop: `3px solid ${c}`, borderLeft: `3px solid ${c}`, borderRight: `3px solid ${c}`, borderRadius: '6px 6px 0 0', marginTop: 8}} />
          </div>
        );
      })}
      <Pop from={at(5, 0.55)} x={960} y={620}>
        <div style={{fontFamily: MONO, fontSize: 52, color: C.ink, whiteSpace: 'nowrap'}}>
          (−1)<sup style={{color: C.pink, fontSize: 30}}>S</sup> × 1.<span style={{color: C.blue}}>M</span> × 2<sup style={{color: C.orange, fontSize: 30}}>E − 127</sup>
        </div>
      </Pop>
      <Pop from={at(5, 0.72)} x={960} y={750}>
        <div style={{display: 'flex', gap: 16, alignItems: 'center', fontSize: 26, color: C.ink2}}>
          <Pill color={C.ink2} size={24}>例</Pill>
          <span style={{fontFamily: MONO}}>−6.5 = −1.101₂ × 2²</span>
          <span style={{color: C.faint}}>→</span>
          <span>S = 1，E = 2 + 127 = 129</span>
        </div>
      </Pop>
    </AbsoluteFill>
  );
};

export const DataScene: React.FC = () => (
  <AbsoluteFill>
    <Binary />
    <SignMag />
    <TwosComp />
    <Dial />
    <Float />
  </AbsoluteFill>
);