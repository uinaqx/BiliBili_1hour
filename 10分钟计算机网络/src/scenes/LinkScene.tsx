import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT, MONO, SHADOW, tint} from '../theme';
import {P, clamp, ip, pop, prog, useScene, vis} from '../anim';
import {BitRow, Block, Label, Pill, Pop, Svg, Wire, bitRowWidth, card} from '../kit';
import {Mover, Seg} from '../net';

const BITS = '10110010';
const BS = 84, BG = 14;
const bitsW = bitRowWidth(8, BS, BG);
const BX = 960 - bitsW / 2;
const bitX = (i: number) => BX + i * (BS + BG) + Math.floor(i / 4) * BG * 2;

const Signal: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(0, f);
  const end = at(1, 0);
  if (frame > end + 14) return null;
  const hi = 520, lo = 620;
  const pts: P[] = [];
  BITS.split('').forEach((v, i) => {
    const y = v === '1' ? hi : lo;
    const x0 = i === 0 ? BX - 30 : bitX(i) - (BG + (i % 4 === 0 ? BG * 2 : 0)) / 2, x1 = i === 7 ? bitX(i) + BS + 30 : bitX(i + 1) - (BG + ((i + 1) % 4 === 0 ? BG * 2 : 0)) / 2;
    pts.push([x0, y], [x1, y]);
  });
  const o = vis(frame, t(0.12), end);
  return (
    <AbsoluteFill>
      <BitRow bits={BITS} x={BX} y={330} from={t(0.04)} to={end} size={BS} gap={BG} lit={(i) => (BITS[i] === '1' ? 0.85 : 0)} color={() => C.teal} />
      <Svg style={{opacity: o}}>
        <line x1={BX - 40} y1={lo + 40} x2={BX + bitsW + 40} y2={lo + 40} stroke={C.hair} strokeWidth={2} />
        <Wire pts={pts} from={t(0.14)} len={50} color={C.teal} w={4} head={false} />
        {BITS.split('').map((_, i) => <line key={i} x1={bitX(i) + BS / 2} y1={388} x2={bitX(i) + BS / 2} y2={480} stroke={C.hair} strokeWidth={2} strokeDasharray="3 6"
          opacity={prog(frame, t(0.14) + i * 6, 8)} />)}
      </Svg>
      <Label x={BX - 60} y={hi} anchor="right" from={t(0.2)} to={end} size={20} mono>高电平</Label>
      <Label x={BX - 60} y={lo} anchor="right" from={t(0.22)} to={end} size={20} mono>低电平</Label>
      {[['双绞线', '电信号', C.teal], ['光纤', '光脉冲', C.blue], ['无线', '电磁波', C.indigo]].map(([a, b, c], i) => (
        <Pop key={a} from={t(0.5) + i * 6} to={end} x={660 + i * 300} y={790}>
          <div style={card({width: 250, padding: '18px 0', textAlign: 'center', fontFamily: FONT})}>
            <div style={{fontSize: 28, fontWeight: 650, color: C.ink}}>{a}</div>
            <div style={{fontSize: 20, color: c, marginTop: 4}}>{b}</div>
          </div>
        </Pop>
      ))}
    </AbsoluteFill>
  );
};

const FIELDS = [
  {t: '目的 MAC', sub: '6 字节', w: 260, c: C.green},
  {t: '源 MAC', sub: '6 字节', w: 260, c: C.green},
  {t: '类型', sub: '2 字节', w: 150, c: C.teal},
  {t: '数据', sub: '46 – 1500 字节', w: 560, c: C.blue},
  {t: 'CRC', sub: '4 字节', w: 180, c: C.orange},
];

const Frame: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(1, f);
  const end = at(2, 0);
  if (frame < t(0) - 2 || frame > end + 14) return null;
  const born = FIELDS.map((_, i) => t(0.06) + i * 6);
  const mac = pop(frame, t(0.45));
  return (
    <AbsoluteFill>
      <Label x={960} y={230} from={t(0.02)} to={end} size={24} color={C.ink2} weight={650}>以太网帧</Label>
      <Pop from={t(0.04)} to={end} x={960} y={330}><Seg fields={FIELDS} h={96} size={28} born={born} /></Pop>
      <Svg>
        <Wire pts={[[377, 380], [377, 470], [640, 548]]} from={t(0.42)} to={end} color={C.line} w={2} head={false} />
      </Svg>
      <Pop from={t(0.45)} to={end} x={960} y={600}>
        <div style={{display: 'flex', fontFamily: MONO, fontSize: 84, fontWeight: 600, letterSpacing: 2, transform: `scale(${0.96 + 0.04 * mac})`}}>
          <span style={{color: C.green}}>3C:22:FB</span><span style={{color: C.ink}}>:7A:91:0E</span>
        </div>
      </Pop>
      <Label x={790} y={690} from={t(0.58)} to={end} size={22} color={C.green}>厂商标识 · 24 位</Label>
      <Label x={1140} y={690} from={t(0.64)} to={end} size={22}>网卡序号 · 24 位</Label>
      <Pop from={t(0.72)} to={end} x={960} y={790}><Pill color={C.green} size={24}>MAC 地址 48 位 · 固化在网卡里</Pill></Pop>
    </AbsoluteFill>
  );
};

const A: P = [380, 520], B: P = [1540, 520];

const Crc: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(2, f);
  const end = at(3, 0);
  if (frame < t(0) - 2 || frame > end + 14) return null;
  const go = t(0.1), hit = t(0.3), arrive = t(0.5);
  const flash = clamp(1 - Math.abs(frame - hit) / 10);
  const bad = frame >= hit;
  const path: P[] = [[A[0] + 260, A[1]], [B[0] - 270, B[1]]];
  return (
    <AbsoluteFill>
      <Block x={A[0]} y={A[1]} w={220} h={120} from={t(0.02)} to={end} title="主机 A" sub="发送" color={C.green} />
      <Block x={B[0]} y={B[1]} w={220} h={120} from={t(0.04)} to={end} title="主机 B" sub="接收" color={C.green} hl={prog(frame, arrive, 10) * (1 - prog(frame, end - 10, 10))} />
      <Svg>
        <Wire pts={path} from={t(0.06)} to={end} color={C.line} w={3} head={false} />
        {flash > 0 && (
          <path d="M970,330 L940,420 L975,420 L945,505" fill="none" stroke={C.red} strokeWidth={6} strokeLinejoin="round" strokeLinecap="round"
            opacity={flash} style={{filter: `drop-shadow(0 0 12px ${C.red})`}} />
        )}
      </Svg>
      <Label x={960} y={300} from={hit - 4} to={end} size={22} color={C.red}>噪声干扰 · 一位翻转</Label>
      <Mover pts={path} from={go} len={arrive - go} drop hold={t(0.7) - arrive}>
        <div style={{transform: `translateX(${flash * Math.sin(frame * 3) * 8}px)`}}>
          <Seg size={20} h={50} fields={[{t: '帧头', w: 80, c: C.green}, {t: bad ? '1001' : '1011', w: 110, c: bad ? C.red : C.blue}, {t: 'CRC', w: 80, c: C.orange}]} />
        </div>
      </Mover>
      <Pop from={arrive + 4} to={end} x={B[0]} y={760}>
        <div style={card({width: 440, padding: '22px 30px', boxSizing: 'border-box', fontFamily: FONT})}>
          <div style={{fontSize: 22, color: C.muted, marginBottom: 12}}>接收方重新计算 CRC</div>
          {[['帧尾携带', '7A3F', C.ink], ['重新计算', '1C92', C.red]].map(([k, v, c], i) => (
            <div key={k} style={{display: 'flex', justifyContent: 'space-between', fontSize: 28, marginTop: i ? 8 : 0, opacity: prog(frame, arrive + 8 + i * 10, 8)}}>
              <span style={{color: C.ink2}}>{k}</span><span style={{fontFamily: MONO, color: c, fontWeight: 600}}>{v}</span>
            </div>
          ))}
        </div>
      </Pop>
      <Pop from={t(0.72)} to={end} x={B[0]} y={360}><Pill color={C.red} solid size={24}>不一致 → 丢弃</Pill></Pop>
      <Label x={A[0]} y={690} from={t(0.12)} to={end} size={20}>发送前按内容算出 CRC</Label>
    </AbsoluteFill>
  );
};

const SW: P = [760, 400];
const PORT_X = [640, 720, 800, 880];
const HOSTS = [{n: 'A', x: 330, y: 760}, {n: 'B', x: 610, y: 800}, {n: 'C', x: 910, y: 800}, {n: 'D', x: 1190, y: 760}];
const hostPath = (k: number): P[] => [[PORT_X[k], SW[1] + 56], [PORT_X[k], 560], [HOSTS[k].x, 640], [HOSTS[k].x, HOSTS[k].y - 52]];

const Switch: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(3, f);
  if (frame < t(0) - 2) return null;
  const up = (k: number) => [...hostPath(k)].reverse();
  const flood = t(0.3), reply = t(0.56), fwd = t(0.72);
  const rows = [{m: 'A', p: '1', at: t(0.22), c: C.green}, {m: 'C', p: '3', at: t(0.66), c: C.green}];
  return (
    <AbsoluteFill>
      <Svg>
        {HOSTS.map((_, k) => <Wire key={k} pts={hostPath(k)} from={t(0.04) + k * 3} color={C.line} w={3} head={false} />)}
      </Svg>
      <Pop from={t(0.02)} x={SW[0]} y={SW[1]}>
        <div style={{width: 400, height: 112, borderRadius: 24, background: C.card, boxShadow: SHADOW, border: `2px solid ${tint(C.green, 0.5)}`,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', fontFamily: FONT, position: 'relative'}}>
          <div style={{fontSize: 30, fontWeight: 650, color: C.ink}}>交换机</div>
          <div style={{position: 'absolute', bottom: 8, left: 0, right: 0}}>
            {PORT_X.map((x, k) => <span key={k} style={{position: 'absolute', left: x - SW[0] + 200, transform: 'translateX(-50%)', fontSize: 16,
              color: C.muted, fontFamily: MONO}}>{k + 1}</span>)}
          </div>
        </div>
      </Pop>
      {HOSTS.map((h, k) => {
        const reject = (k === 1 || k === 3) && frame > flood + 30;
        return <Block key={h.n} x={h.x} y={h.y} w={150} h={96} from={t(0.04) + k * 4} title={h.n} sub={reject ? '不是我 · 丢弃' : '主机'}
          color={C.green} hl={k === 2 ? prog(frame, flood + 30, 8) * (1 - prog(frame, reply + 20, 10)) : k === 0 ? prog(frame, fwd + 30, 8) : 0} />;
      })}
      <Mover pts={up(0)} from={t(0.08)} len={26}><TagFrame c={C.blue}>A → C</TagFrame></Mover>
      {[1, 2, 3].map((k) => <Mover key={k} pts={hostPath(k)} from={flood} len={30} drop={k !== 2}><TagFrame c={C.orange}>A → C</TagFrame></Mover>)}
      <Label x={SW[0]} y={SW[1] - 92} from={flood} to={reply} size={22} color={C.orange} weight={600}>表里没有 C → 广播到其他所有端口</Label>
      <Mover pts={up(2)} from={reply} len={26}><TagFrame c={C.blue}>C → A</TagFrame></Mover>
      <Mover pts={hostPath(0)} from={fwd} len={30}><TagFrame c={C.green}>C → A</TagFrame></Mover>
      <Label x={SW[0]} y={SW[1] - 92} from={fwd} size={22} color={C.green} weight={600}>表里有 A → 只发端口 1</Label>
      <Pop from={t(0.1)} x={1560} y={470}>
        <div style={card({width: 420, padding: '24px 30px 28px', boxSizing: 'border-box', fontFamily: FONT})}>
          <div style={{fontSize: 28, fontWeight: 700, color: C.ink, marginBottom: 14}}>交换表</div>
          <div style={{display: 'flex', justifyContent: 'space-between', fontSize: 20, color: C.muted, padding: '0 16px 8px'}}><span>MAC 地址</span><span>端口</span></div>
          {rows.map((r) => {
            const s = pop(frame, r.at);
            return (
              <div key={r.m} style={{height: 58, marginTop: 8, borderRadius: 14, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '0 16px', background: frame >= r.at ? tint(r.c, 0.12 * (1 - prog(frame, r.at + 30, 30)) + 0.06) : C.fill,
                border: `1.5px solid ${frame >= r.at ? tint(r.c, 0.6) : 'transparent'}`}}>
                <span style={{fontFamily: MONO, fontSize: 24, color: C.ink, opacity: clamp(s * 1.5)}}>主机 {r.m} 的 MAC</span>
                <span style={{fontFamily: MONO, fontSize: 24, color: r.c, opacity: clamp(s * 1.5)}}>{r.p}</span>
              </div>
            );
          })}
        </div>
      </Pop>
      <Label x={1560} y={690} from={t(0.26)} size={20}>从哪个端口进来，就记下来</Label>
    </AbsoluteFill>
  );
};

const TagFrame: React.FC<{c: string; children: React.ReactNode}> = ({c, children}) => (
  <div style={{padding: '6px 14px', borderRadius: 10, background: tint(c, 0.25), border: `1.5px solid ${c}`, color: C.ink, fontFamily: MONO,
    fontSize: 19, fontWeight: 600, whiteSpace: 'nowrap', boxShadow: `0 0 20px ${tint(c, 0.4)}`}}>{children}</div>
);

export const LinkScene: React.FC = () => (
  <AbsoluteFill>
    <Signal />
    <Frame />
    <Crc />
    <Switch />
  </AbsoluteFill>
);
