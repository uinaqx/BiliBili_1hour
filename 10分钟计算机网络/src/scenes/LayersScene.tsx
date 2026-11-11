import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT} from '../theme';
import {clamp, ip, pop, prog, useScene, vis} from '../anim';
import {BitRow, Label, Pill, Pop, Svg, Wire, bitRowWidth} from '../kit';
import {Field, LAYERS, Mover, Seg, Slab, segWidth} from '../net';

const OSI = ['应用层', '表示层', '会话层', '传输层', '网络层', '数据链路层', '物理层'];
const RH = 72, RG = 12, TOP = 206;
const rowY = (i: number) => TOP + i * (RH + RG) + RH / 2;

const Compare: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(0, f);
  const end = at(1, 0);
  if (frame > end + 14) return null;
  const five = [
    {l: LAYERS[0], a: 0, b: 2}, {l: LAYERS[1], a: 3, b: 3}, {l: LAYERS[2], a: 4, b: 4}, {l: LAYERS[3], a: 5, b: 5}, {l: LAYERS[4], a: 6, b: 6},
  ];
  const osiC = (i: number) => (i <= 2 ? C.purple : five.find((f) => f.a === i)!.l.c);
  return (
    <AbsoluteFill>
      <Label x={560} y={164} from={t(0.04)} to={end} size={24} color={C.ink2} weight={650}>OSI 参考模型 · 7 层</Label>
      {OSI.map((n, i) => <Slab key={n} x={560} y={rowY(i)} w={380} h={RH} from={t(0.06) + i * 4} to={end} color={osiC(i)} name={n} size={26} />)}
      <Label x={1360} y={164} from={t(0.42)} to={end} size={24} color={C.ink2} weight={650}>教学五层模型</Label>
      {five.map(({l, a, b}, k) => {
        const y1 = rowY(a) - RH / 2, y2 = rowY(b) + RH / 2;
        return <Slab key={l.id} x={1360} y={(y1 + y2) / 2} w={380} h={y2 - y1} from={t(0.44) + k * 6} to={end} color={l.c} name={l.name} en={l.en} size={28} />;
      })}
      <Svg>
        {OSI.map((_, i) => <Wire key={i} pts={[[756, rowY(i)], [1164, rowY(i <= 2 ? 1 : i)]]} from={t(0.5) + i * 3} to={end} color={C.line} w={2} dash="4 8" head={false} />)}
      </Svg>
      <Pop from={t(0.72)} to={end} x={960} y={850}>
        <div style={{display: 'flex', gap: 16, alignItems: 'center'}}>
          <Pill color={C.blue} size={22}>TCP/IP：实际使用最广</Pill>
          <span style={{color: C.muted, fontSize: 22, fontFamily: FONT}}>应用 · 传输 · 网际 · 网络接口</span>
        </div>
      </Pop>
    </AbsoluteFill>
  );
};

const DUTY = [
  ['为应用程序提供服务', 'HTTP · DNS · SMTP'],
  ['进程到进程 · 端到端', 'TCP · UDP'],
  ['主机到主机 · 选路转发', 'IP · 路由协议'],
  ['相邻节点之间 · 成帧', '以太网 · Wi-Fi'],
  ['传输比特 · 信号', '双绞线 · 光纤 · 无线'],
];

const Duties: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(1, f);
  const end = at(2, 0);
  if (frame < t(0) - 2 || frame > end + 14) return null;
  const focus = ip(frame, t(0.55), 14);
  return (
    <AbsoluteFill>
      {LAYERS.map((l, i) => {
        const y = 250 + i * 128;
        const hl = i === 1 ? focus : 0, dim = i === 1 ? 0 : focus * 0.6;
        return (
          <React.Fragment key={l.id}>
            <Slab x={500} y={y} w={460} h={104} from={t(0.04) + i * 5} to={end} color={l.c} name={l.name} en={l.en} hl={hl} dim={dim} />
            <Pop from={t(0.12) + i * 6} to={end} x={800} y={y} anchor="left">
              <div style={{fontFamily: FONT, opacity: 1 - dim * 0.6}}>
                <div style={{fontSize: 30, color: C.ink, fontWeight: 600}}>{DUTY[i][0]}</div>
                <div style={{fontSize: 22, color: l.c, marginTop: 4, fontWeight: 500}}>{DUTY[i][1]}</div>
              </div>
            </Pop>
            {i < 4 && <Label x={238} y={y + 64} from={t(0.3) + i * 4} to={end} size={20} color={C.faint}>▲ 服务</Label>}
          </React.Fragment>
        );
      })}
      <Pop from={t(0.62)} to={end} x={1480} y={378}><Pill color={C.orange} size={22}>只管端到端，不管走哪条路</Pill></Pop>
    </AbsoluteFill>
  );
};

const DATA: Field = {t: '数据', w: 220, c: C.purple};
const TCP: Field = {t: 'TCP', w: 110, c: C.orange};
const IP: Field = {t: 'IP', w: 110, c: C.blue};
const FH: Field = {t: '帧头', w: 100, c: C.green};
const FT: Field = {t: '帧尾', w: 84, c: C.green};
const UNITS: {fields: Field[]; name: string}[] = [
  {fields: [DATA], name: '应用数据'},
  {fields: [TCP, DATA], name: '报文段 Segment'},
  {fields: [IP, TCP, DATA], name: '数据报 Datagram'},
  {fields: [FH, IP, TCP, DATA, FT], name: '帧 Frame'},
];
const BITS = '0110100111010010';
const ER = (i: number) => 286 + i * 132;
const SX = 480, RX = 1440;

const Encap: React.FC = () => {
  const {frame, at} = useScene();
  const t2 = (f: number) => at(2, f), t3 = (f: number) => at(3, f);
  if (frame < t2(0) - 2) return null;
  const sendAt = (i: number) => t2(0.06 + i * 0.2);
  const recvAt = (i: number) => t3(0.22 + (4 - i) * 0.16);
  const bitsW = bitRowWidth(16, 30, 4);
  return (
    <AbsoluteFill>
      <Label x={SX} y={190} from={t2(0.02)} size={26} color={C.ink} weight={650}>发送方 · 封装 ↓</Label>
      <Label x={RX} y={190} from={t3(0.02)} size={26} color={C.ink} weight={650}>接收方 · 解封装 ↑</Label>
      {LAYERS.map((l, i) => (
        <Pop key={l.id} from={t2(0.02) + i * 3} x={960} y={ER(i)}>
          <Pill color={l.c} size={20}>{l.name}</Pill>
        </Pop>
      ))}
      {UNITS.map((u, i) => {
        const s = sendAt(i), w = segWidth(u.fields);
        const born = u.fields.map((f) => (i > 0 && !UNITS[i - 1].fields.includes(f) ? s + 4 : undefined));
        return (
          <React.Fragment key={i}>
            <Pop from={s} x={SX} y={ER(i)}><Seg fields={u.fields} born={born} /></Pop>
            <Label x={SX - w / 2} y={ER(i) - 46} anchor="left" from={s + 8} size={19}>{u.name}</Label>
          </React.Fragment>
        );
      })}
      <BitRow bits={BITS} x={SX - bitsW / 2} y={ER(4)} from={sendAt(4)} size={30} gap={4} stagger={1}
        lit={() => 0.5} color={() => C.teal} />
      <Svg>
        <Wire pts={[[SX + bitsW / 2 + 16, ER(4)], [870, ER(4)]]} from={t3(0)} len={8} color={C.teal} w={3} head={false} />
        <Wire pts={[[1050, ER(4)], [RX - bitsW / 2 - 16, ER(4)]]} from={t3(0) + 8} len={8} color={C.teal} w={3} />
      </Svg>
      <Mover pts={[[SX + bitsW / 2 + 16, ER(4)], [RX - bitsW / 2 - 16, ER(4)]]} from={t3(0.02)} len={22}>
        <div style={{width: 16, height: 16, borderRadius: 8, background: C.teal, boxShadow: `0 0 24px ${C.teal}`}} />
      </Mover>
      <BitRow bits={BITS} x={RX - bitsW / 2} y={ER(4)} from={recvAt(4)} size={30} gap={4} stagger={1} lit={() => 0.5} color={() => C.teal} />
      {UNITS.map((u, i) => {
        const s = recvAt(i);
        const peeled = i < 3 ? UNITS[i + 1].fields.filter((f) => !u.fields.includes(f)) : [];
        const fly = ip(frame, s, 18);
        return (
          <React.Fragment key={i}>
            <Pop from={s} x={RX} y={ER(i)}><Seg fields={u.fields} /></Pop>
            {frame >= s && fly < 1 && peeled.map((f, k) => (
              <div key={k} style={{position: 'absolute', left: RX + (k === 0 ? -segWidth(u.fields) / 2 - 70 : segWidth(u.fields) / 2 + 60),
                top: ER(i) + 40 - fly * 50, transform: 'translate(-50%,-50%)', opacity: clamp(1 - fly)}}>
                <Seg fields={[f]} h={44} size={18} />
              </div>
            ))}
          </React.Fragment>
        );
      })}
      <Pop from={recvAt(0) + 12} x={RX + 200} y={ER(0)} anchor="left">
        <span style={{color: C.green, fontSize: 24, fontWeight: 650, fontFamily: FONT, opacity: Math.min(1, prog(frame, recvAt(0) + 12, 10))}}>✓ 交给应用</span>
      </Pop>
      <Label x={SX} y={ER(4) + 52} from={t2(0.92)} size={20}>每层加一个头部，最后变成比特流</Label>
    </AbsoluteFill>
  );
};

export const LayersScene: React.FC = () => (
  <AbsoluteFill>
    <Compare />
    <Duties />
    <Encap />
  </AbsoluteFill>
);
