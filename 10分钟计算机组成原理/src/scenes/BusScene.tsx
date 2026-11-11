import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, MONO, SHADOW, tint} from '../theme';
import {P, clamp, ip, pointAt, useScene, vis} from '../anim';
import {Block, Label, Pill, Pop, Svg, Wire, card} from '../kit';

const LINES: [string, string, number][] = [['数据总线', C.blue, 560], ['地址总线', C.orange, 625], ['控制总线', C.purple, 690]];
const DEV: [string, string, number][] = [['CPU', '处理器', 420], ['主存', '内存条', 820], ['键盘接口', 'I/O', 1220], ['磁盘接口', 'I/O', 1620]];

/** Beat 0: three buses shared by every component. */
const Overview: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(0, 0), end = at(1, 0);
  const o = vis(frame, s, end);
  if (o <= 0) return null;
  const draw = ip(frame, s + 4, 30);
  const flows: [number, number, number, string][] = [[0, 420, 820, C.blue], [0, 820, 420, C.blue], [1, 420, 1620, C.orange], [2, 420, 1220, C.purple], [0, 1620, 820, C.blue]];
  return (
    <AbsoluteFill style={{opacity: o}}>
      <Svg>
        {LINES.map(([, col, y], i) => (
          <line key={i} x1={380} y1={y} x2={380 + 1400 * draw} y2={y} stroke={tint(col, 0.35)} strokeWidth={12} strokeLinecap="round" />
        ))}
        {DEV.map(([, , x], i) => (
          <g key={i} opacity={ip(frame, s + 20 + i * 4, 14)}>
            <line x1={x} y1={412} x2={x} y2={690} stroke={C.line} strokeWidth={4} />
            {LINES.map(([, col, y]) => <circle key={y} cx={x} cy={y} r={9} fill="#fff" stroke={col} strokeWidth={4} />)}
          </g>
        ))}
        {frame > at(0, 0.45) && flows.map(([li, a, b, col], k) => {
          const period = 70, t = ((frame - at(0, 0.45) + k * 17) % period) / period;
          const y = LINES[li][2];
          const {p} = pointAt([[a, y], [b, y]], t);
          return <rect key={k} x={p[0] - 20} y={y - 9} width={40} height={18} rx={9} fill={col} opacity={Math.min(1, t * 8, (1 - t) * 8)} />;
        })}
      </Svg>
      {DEV.map(([n, sub, x], i) => <Block key={n} x={x} y={360} w={240} h={104} from={s + 14 + i * 4} title={n} sub={sub} />)}
      {LINES.map(([n, col, y], i) => (
        <Label key={n} x={360} y={y} from={at(0, 0.3) + i * 6} anchor="right" size={24} weight={700} color={col}>{n}</Label>
      ))}
      <Pop from={at(0, 0.6)} x={960} y={820}>
        <div style={{display: 'flex', gap: 14}}>
          <Pill color={C.blue} size={22}>数据：双向</Pill><Pill color={C.orange} size={22}>地址：CPU 发出</Pill><Pill color={C.purple} size={22}>控制：读写、时序、请求</Pill>
        </div>
      </Pop>
    </AbsoluteFill>
  );
};

/** Beat 1: 32 address lines → 4 GB. */
const AddressWidth: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(1, 0), end = at(2, 0);
  const o = vis(frame, s, end);
  if (o <= 0) return null;
  const k = Math.round(32 * ip(frame, at(1, 0.15), at(1, 0.7) - at(1, 0.15)));
  const val = k === 0 ? 1 : Math.pow(2, k);
  const y = (i: number) => 668 - i * 12;
  return (
    <AbsoluteFill style={{opacity: o}}>
      <Svg>
        {Array.from({length: 32}, (_, i) => (
          <line key={i} x1={530} y1={y(i)} x2={530 + 860 * ip(frame, s + 8 + i * 0.6, 16)} y2={y(i)} stroke={i < k ? C.orange : C.line}
            strokeWidth={i < k ? 4 : 3} strokeLinecap="round" />
        ))}
      </Svg>
      <Block x={410} y={482} w={220} h={420} from={s + 2} title="CPU" />
      <Block x={1510} y={482} w={220} h={420} from={s + 4} title="主存" />
      <Label x={1440} y={y(0)} from={s + 20} anchor="left" size={18} color={C.muted} mono>A0</Label>
      <Label x={1440} y={y(31)} from={s + 20} anchor="left" size={18} color={C.muted} mono>A31</Label>
      <Pop from={at(1, 0.12)} x={960} y={800}>
        <div style={card({padding: '20px 40px', display: 'flex', alignItems: 'baseline', gap: 22})}>
          <span style={{fontFamily: MONO, fontSize: 44, fontWeight: 700, color: C.orange}}>2<sup style={{fontSize: 26}}>{k}</sup></span>
          <span style={{fontSize: 30, color: C.faint}}>=</span>
          <span style={{fontFamily: MONO, fontSize: 44, fontWeight: 700, color: C.ink}}>{val.toLocaleString('en-US')}</span>
          {k === 32 && <span style={{fontSize: 30, fontWeight: 700, color: C.blue}}>≈ 4 GB</span>}
        </div>
      </Pop>
      <Label x={960} y={240} from={s + 10} size={24} color={C.ink2} weight={600}>每多 1 根地址线，可寻址空间翻一倍</Label>
    </AbsoluteFill>
  );
};

/** Beat 2: bandwidth. */
const Bandwidth: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(2, 0), end = at(3, 0);
  const o = vis(frame, s, end);
  if (o <= 0) return null;
  const line = (y: number, from: number, children: React.ReactNode) => (
    <Pop from={from} x={960} y={y}><div style={{fontSize: 46, color: C.ink, whiteSpace: 'nowrap'}}>{children}</div></Pop>
  );
  return (
    <AbsoluteFill style={{opacity: o}}>
      {line(300, s + 6, <>带宽 = 总线宽度 × 传输频率</>)}
      {line(410, at(2, 0.4), <span style={{fontFamily: MONO}}><span style={{color: C.blue}}>64 bit</span> = 8 B，× <span style={{color: C.purple}}>100 MHz</span></span>)}
      {line(530, at(2, 0.7), <span style={{fontSize: 80, fontWeight: 700, color: C.blue}}>= 800 MB/s</span>)}
      <Svg>
        <line x1={300} y1={720} x2={1620} y2={720} stroke={C.line} strokeWidth={6} strokeLinecap="round" />
        {Array.from({length: 12}, (_, i) => <line key={i} x1={300 + i * 120} y1={736} x2={300 + i * 120} y2={748} stroke={C.faint} strokeWidth={3} />)}
      </Svg>
      {Array.from({length: 10}, (_, k) => {
        const t0 = s + 10 + k * 18, t = clamp((frame - t0) / 110);
        if (t <= 0 || t >= 1) return null;
        return (
          <div key={k} style={{position: 'absolute', left: 300 + 1320 * t, top: 720, transform: 'translate(-50%,-50%)', padding: '6px 14px',
            borderRadius: 10, background: C.blue, color: '#fff', fontFamily: MONO, fontSize: 20, fontWeight: 700, boxShadow: SHADOW,
            opacity: Math.min(1, t * 10, (1 - t) * 10)}}>8 B</div>
        );
      })}
      <Label x={960} y={790} from={s + 14} size={22} color={C.muted}>每个时钟周期传送一次</Label>
    </AbsoluteFill>
  );
};

/** Beat 3: arbitration, then synchronous vs asynchronous timing. */
const Arbitration: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(3, 0);
  if (frame < s - 2) return null;
  const devY = [340, 480, 620];
  const grant = frame >= at(3, 0.25);
  const wave = (pts: P[], from: number, color: string) => {
    const p = ip(frame, from, 40);
    const d = pts.map((v, i) => `${i ? 'L' : 'M'}${v[0]},${v[1]}`).join(' ');
    return <path d={d} fill="none" stroke={color} strokeWidth={4} strokeLinejoin="round" strokeDasharray={2400} strokeDashoffset={2400 * (1 - p)} />;
  };
  const sq = (x0: number, y: number, n: number, w: number, h: number): P[] => {
    const out: P[] = [[x0, y]];
    for (let i = 0; i < n; i++) { const x = x0 + i * w; out.push([x, y], [x, y - h], [x + w / 2, y - h], [x + w / 2, y]); }
    out.push([x0 + n * w, y]);
    return out;
  };
  const sx = 1060, ax = 1060;
  return (
    <AbsoluteFill>
      <Label x={450} y={240} from={s + 2} size={28} weight={700} color={C.ink}>总线仲裁</Label>
      <Svg>
        {devY.map((y, i) => <Wire key={i} pts={[[352, y], [540, 480]]} from={s + 10 + i * 3} color={tint(C.orange, 0.8)} />)}
        <Wire pts={[[640, 542], [640, 640], [352, devY[1] + 18]]} from={at(3, 0.25)} color={C.green} w={4} />
        {wave(sq(sx, 400, 8, 80, 50), at(3, 0.45), C.blue)}
        {wave([[sx, 460], [sx + 80, 460], [sx + 96, 430], [sx + 304, 430], [sx + 320, 460], [sx + 400, 460], [sx + 416, 430], [sx + 624, 430], [sx + 640, 460]], at(3, 0.5), C.indigo)}
        {wave([[ax, 700], [ax + 100, 700], [ax + 100, 650], [ax + 380, 650], [ax + 380, 700], [ax + 640, 700]], at(3, 0.65), C.orange)}
        {wave([[ax, 790], [ax + 220, 790], [ax + 220, 740], [ax + 500, 740], [ax + 500, 790], [ax + 640, 790]], at(3, 0.7), C.green)}
        <Wire pts={[[ax + 110, 662], [ax + 210, 752]]} from={at(3, 0.78)} color={C.ink2} w={2} />
        <Wire pts={[[ax + 230, 742], [ax + 370, 660]]} from={at(3, 0.82)} color={C.ink2} w={2} />
        <Wire pts={[[ax + 390, 690], [ax + 490, 780]]} from={at(3, 0.86)} color={C.ink2} w={2} />
      </Svg>
      {['设备 A', '设备 B', '设备 C'].map((n, i) => (
        <Block key={n} x={260} y={devY[i]} w={180} h={80} from={s + 4 + i * 3} title={n} size={24} hl={grant && i === 1 ? 1 : 0} color={C.green} />
      ))}
      <Block x={640} y={480} w={200} h={120} from={s + 8} title="仲裁器" sub="谁先用总线" color={C.orange} />
      <Label x={500} y={680} from={at(3, 0.3)} size={22} weight={700} color={C.green}>B 获得总线</Label>
      <Label x={sx} y={300} from={at(3, 0.42)} anchor="left" size={26} weight={700} color={C.blue}>同步：按统一时钟节拍</Label>
      <Label x={sx - 20} y={380} from={at(3, 0.45)} anchor="right" size={20} color={C.muted} mono>CLK</Label>
      <Label x={sx - 20} y={445} from={at(3, 0.5)} anchor="right" size={20} color={C.muted} mono>DATA</Label>
      <Label x={sx} y={590} from={at(3, 0.62)} anchor="left" size={26} weight={700} color={C.orange}>异步：请求 ↔ 应答 握手</Label>
      <Label x={ax - 20} y={675} from={at(3, 0.65)} anchor="right" size={20} color={C.muted} mono>REQ</Label>
      <Label x={ax - 20} y={765} from={at(3, 0.7)} anchor="right" size={20} color={C.muted} mono>ACK</Label>
    </AbsoluteFill>
  );
};

export const BusScene: React.FC = () => (
  <AbsoluteFill>
    <Overview />
    <AddressWidth />
    <Bandwidth />
    <Arbitration />
  </AbsoluteFill>
);
