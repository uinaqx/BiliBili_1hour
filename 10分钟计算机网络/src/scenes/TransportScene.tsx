import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT, MONO, SHADOW, tint} from '../theme';
import {P, clamp, ip, pop, prog, useScene, vis} from '../anim';
import {Label, Pill, Pop, Svg, Wire, card} from '../kit';
import {Mover, SeqDiagram, State, Tag} from '../net';

const APPS = [{n: '网页服务', p: 443, c: C.purple}, {n: 'DNS', p: 53, c: C.teal}, {n: 'SSH', p: 22, c: C.green}];
const AX = (k: number) => 860 + k * 290, AY = 660, GATE: P = [560, 540];

const Ports: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(0, f);
  const end = at(1, 0);
  if (frame > end + 14) return null;
  const go = (k: number) => t(0.25 + k * 0.14);
  return (
    <AbsoluteFill>
      <Pop from={t(0.02)} to={end} x={1150} y={540}>
        <div style={{width: 1000, height: 440, borderRadius: 36, background: tint(C.blue, 0.03), border: `2px solid ${C.line}`, position: 'relative'}}>
          <div style={{position: 'absolute', top: 24, left: 34, fontFamily: FONT}}>
            <span style={{fontSize: 28, fontWeight: 650, color: C.ink}}>主机</span>
            <span style={{fontSize: 22, color: C.muted, marginLeft: 14, fontFamily: MONO}}>203.0.113.8</span>
          </div>
        </div>
      </Pop>
      <Svg>
        <Wire pts={[[180, 540], [GATE[0] + 90, 540]]} from={t(0.06)} to={end} color={C.blue} w={3} />
        {APPS.map((a, k) => <Wire key={k} pts={[[GATE[0] + 110, 540], [AX(k), 540], [AX(k), AY - 62]]} from={t(0.12) + k * 4} to={end} color={C.line} w={2.5} />)}
      </Svg>
      {APPS.map((a, k) => (
        <Pop key={k} from={t(0.1) + k * 5} to={end} x={AX(k)} y={AY + 10}>
          <div style={{width: 230, height: 130, borderRadius: 22, background: C.card, boxShadow: SHADOW, border: `2px solid ${tint(a.c, 0.3 + 0.7 * prog(frame, go(k) + 30, 8))}`,
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', fontFamily: FONT}}>
            <div style={{fontSize: 28, fontWeight: 650, color: C.ink}}>{a.n}</div>
            <div style={{fontSize: 30, color: a.c, fontFamily: MONO, marginTop: 6, fontWeight: 600}}>:{a.p}</div>
          </div>
        </Pop>
      ))}
      {APPS.map((a, k) => (
        <React.Fragment key={k}>
          <Mover pts={[[180, 540], [GATE[0] + 100, 540]]} from={go(k)} len={16}><Tag color={C.blue} size={19}>IP · :{a.p}</Tag></Mover>
          <Mover pts={[[GATE[0] + 110, 540], [AX(k), 540], [AX(k), AY - 62]]} from={go(k) + 16} len={16}><Tag color={a.c} size={19}>:{a.p}</Tag></Mover>
        </React.Fragment>
      ))}
      <Label x={360} y={490} from={t(0.1)} to={end} size={22} color={C.blue}>IP 地址 → 找到主机</Label>
      <Label x={1150} y={440} from={t(0.2)} to={end} size={22} color={C.orange}>端口号 → 找到进程</Label>
    </AbsoluteFill>
  );
};

const PROTO = [
  {n: 'UDP', c: C.teal, x: 560, traits: ['无连接 · 尽力而为', '不保证可靠、有序', '首部只有 8 字节'], use: ['直播', '游戏', 'DNS']},
  {n: 'TCP', c: C.orange, x: 1360, traits: ['面向连接 · 可靠有序', '确认 · 重传 · 流量/拥塞控制', '首部 20 字节起'], use: ['网页', '文件', '邮件']},
];

const UdpTcp: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(1, f);
  const end = at(2, 0);
  if (frame < t(0) - 2 || frame > end + 14) return null;
  return (
    <AbsoluteFill>
      {PROTO.map((p, k) => {
        const s = t(0.04 + k * 0.4);
        const lane = 432;
        return (
          <React.Fragment key={p.n}>
            <Pop from={s} to={end} x={p.x} y={560}>
              <div style={card({width: 680, height: 560, padding: '30px 40px', boxSizing: 'border-box', fontFamily: FONT, border: `1.5px solid ${tint(p.c, 0.35)}`})}>
                <div style={{fontSize: 56, fontWeight: 700, color: p.c, letterSpacing: 2}}>{p.n}</div>
                <div style={{height: 110}} />
                {p.traits.map((x, i) => (
                  <div key={x} style={{fontSize: 28, color: C.ink, marginTop: 14, opacity: prog(frame, s + 30 + i * 8, 10)}}>
                    <span style={{color: p.c, marginRight: 14}}>●</span>{x}
                  </div>
                ))}
                <div style={{display: 'flex', gap: 12, marginTop: 30, opacity: prog(frame, s + 60, 10)}}>
                  {p.use.map((u) => <Pill key={u} color={p.c} size={22}>{u}</Pill>)}
                </div>
              </div>
            </Pop>
            <Svg style={{opacity: vis(frame, s + 10, end)}}>
              <line x1={p.x - 280} y1={lane} x2={p.x + 280} y2={lane} stroke={C.hair} strokeWidth={2} />
            </Svg>
            {[0, 1, 2, 3].map((i) => {
              const lost = k === 0 && i === 2;
              const from = s + 16 + i * 10;
              return <Mover key={i} pts={[[p.x - 280, lane], [p.x + 280 - i * 36, lane]]} from={from} len={40} stop={lost ? 0.5 : 1} drop={lost}
                hold={lost ? 0 : end - from - 40}>
                <div style={{width: 28, height: 20, borderRadius: 6, background: lost && frame > from + 20 ? C.red : p.c, boxShadow: `0 0 14px ${tint(p.c, 0.5)}`}} />
              </Mover>;
            })}
            {k === 0 && <Label x={p.x} y={lane + 36} from={s + 46} to={end} size={18} color={C.red}>丢了也不管</Label>}
            {k === 1 && <Label x={p.x} y={lane + 36} from={s + 66} to={end} size={18} color={C.green}>全部按序到达</Label>}
          </React.Fragment>
        );
      })}
    </AbsoluteFill>
  );
};

const X1 = 640, X2 = 1280;

const Handshake: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(2, f);
  const end = at(3, 0);
  if (frame < t(0) - 2 || frame > end + 14) return null;
  return (
    <AbsoluteFill>
      <SeqDiagram x1={X1} x2={X2} top={240} bottom={860} from={t(0.02)} to={end} drop={90} msgs={[
        {dir: 'cs', y: 320, label: 'SYN  seq=x', from: t(0.16), color: C.blue},
        {dir: 'sc', y: 470, label: 'SYN+ACK  seq=y, ack=x+1', from: t(0.38), color: C.purple},
        {dir: 'cs', y: 620, label: 'ACK  ack=y+1', from: t(0.62), color: C.blue},
      ]} />
      <State x={X1 - 24} y={320} from={t(0.18)} to={end} color={C.blue}>SYN-SENT</State>
      <State x={X2 + 24} y={410} anchor="left" from={t(0.2)} to={end} color={C.purple}>SYN-RCVD</State>
      <State x={X1 - 24} y={560} from={t(0.45)} to={end} color={C.green}>ESTABLISHED</State>
      <State x={X2 + 24} y={710} anchor="left" from={t(0.68)} to={end} color={C.green}>ESTABLISHED</State>
      {[['①', '服务器知道：客户端能发'], ['②', '客户端知道：服务器能收能发'], ['③', '服务器知道：客户端能收']].map(([n, s], i) => (
        <Pop key={i} from={t(0.3 + i * 0.24)} to={end} x={1480} y={330 + i * 150} anchor="left">
          <span style={{fontFamily: FONT, fontSize: 21, color: C.muted}}><span style={{color: C.ink, marginRight: 8}}>{n}</span>{s}</span>
        </Pop>
      ))}
      <Pop from={t(0.82)} to={end} x={960} y={860}><Pill solid color={C.green} size={22}>连接建立 · 可以传数据了</Pill></Pop>
    </AbsoluteFill>
  );
};

const Retransmit: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(3, f);
  const end = at(4, 0);
  if (frame < t(0) - 2 || frame > end + 14) return null;
  const lost = t(0.4), resend = t(0.68);
  const timer = ip(frame, lost, resend - lost, (x) => x);
  return (
    <AbsoluteFill>
      <SeqDiagram x1={X1} x2={X2} top={240} bottom={880} from={t(0.02)} to={end} drop={70} left="发送方" right="接收方" msgs={[
        {dir: 'cs', y: 290, label: 'seq=1 · 100 字节', from: t(0.1)},
        {dir: 'sc', y: 380, label: 'ack=101', from: t(0.24), color: C.green},
        {dir: 'cs', y: 480, label: 'seq=101', from: lost, lost: true, color: C.blue},
        {dir: 'cs', y: 660, label: 'seq=101 · 重传', from: resend, color: C.orange},
        {dir: 'sc', y: 760, label: 'ack=201', from: t(0.84), color: C.green},
      ]} />
      {frame >= lost && (
        <div style={{position: 'absolute', left: X1 - 70, top: 480, width: 14, height: 180, borderRadius: 7, background: C.fill, overflow: 'hidden',
          opacity: vis(frame, lost, end)}}>
          <div style={{width: '100%', height: `${timer * 100}%`, background: timer >= 1 ? C.red : C.orange}} />
        </div>
      )}
      <State x={X1 - 92} y={570} from={lost + 4} to={end} color={timer >= 1 ? C.red : C.orange}>{timer >= 1 ? '超时!' : '计时…'}</State>
      <Label x={1460} y={350} anchor="left" from={t(0.26)} to={end} size={21}>确认号 = 期望收到的下一个字节</Label>
      <Label x={1460} y={540} anchor="left" from={lost + 20} to={end} size={21} color={C.red}>报文段丢失，迟迟收不到确认</Label>
      <Label x={1460} y={720} anchor="left" from={resend} to={end} size={21} color={C.orange}>超时 → 重传</Label>
    </AbsoluteFill>
  );
};

const NW = 12, BW = 96, BG2 = 14, WX = 960 - (NW * BW + (NW - 1) * BG2) / 2, WY = 500, WIN = 4;
const wx = (i: number) => WX + i * (BW + BG2);

const Window: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(4, f);
  const end = at(5, 0);
  if (frame < t(0) - 2 || frame > end + 14) return null;
  const base = ip(frame, t(0.35), t(0.85) - t(0.35), (x) => x) * 6;
  const sent = Math.min(NW, Math.floor(ip(frame, t(0.12), 30, (x) => x) * WIN + 0.001) + Math.floor(base));
  const acked = Math.floor(base);
  const legend = [[C.green, '已确认'], [C.blue, '已发送 · 未确认'], [C.faint, '允许发送'], [C.hair, '不能发送']];
  return (
    <AbsoluteFill>
      {Array.from({length: NW}, (_, i) => {
        const st = i < acked ? 0 : i < sent ? 1 : i < acked + WIN ? 2 : 3;
        const c = [C.green, C.blue, C.faint, C.hair][st];
        const s = pop(frame, t(0.02) + i * 2);
        return (
          <div key={i} style={{position: 'absolute', left: wx(i), top: WY - 45, width: BW, height: 90, borderRadius: 16, boxSizing: 'border-box',
            background: st < 2 ? tint(c, 0.25) : C.card, border: `2px ${st === 2 ? 'dashed' : 'solid'} ${st === 3 ? C.hair : c}`,
            display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: MONO, fontSize: 30, fontWeight: 600,
            color: st === 3 ? C.faint : C.ink, opacity: clamp(s * 1.5) * vis(frame, 0, end), transform: `translateY(${(1 - s) * 20}px)`}}>{i + 1}</div>
        );
      })}
      {frame >= t(0.08) && (
        <div style={{position: 'absolute', left: wx(0) - 10 + base * (BW + BG2), top: WY - 60, width: WIN * BW + (WIN - 1) * BG2 + 20, height: 120,
          borderRadius: 22, border: `3px solid ${C.orange}`, boxShadow: `0 0 30px ${tint(C.orange, 0.35)}`, opacity: prog(frame, t(0.08), 10) * vis(frame, 0, end)}}>
          <div style={{position: 'absolute', top: -44, left: 0, right: 0, textAlign: 'center', fontFamily: FONT, fontSize: 22, color: C.orange, fontWeight: 600}}>发送窗口 = 4</div>
        </div>
      )}
      {[0, 1, 2, 3, 4, 5].map((k) => (
        <Mover key={k} pts={[[wx(k) + BW / 2, 700], [wx(k) + BW / 2, WY + 70]]} from={t(0.35) + Math.round(((k + 0.5) / 6) * (t(0.85) - t(0.35))) - 16} len={16}>
          <Tag color={C.green} size={17}>ACK</Tag>
        </Mover>
      ))}
      <Label x={960} y={740} from={t(0.36)} to={end} size={22} color={C.green}>每收到一个确认，窗口就向右滑动</Label>
      <Pop from={t(0.05)} to={end} x={960} y={830}>
        <div style={{display: 'flex', gap: 30, fontFamily: FONT, fontSize: 20, color: C.ink2}}>
          {legend.map(([c, n]) => <span key={n} style={{display: 'flex', alignItems: 'center', gap: 10}}>
            <span style={{width: 22, height: 22, borderRadius: 6, background: tint(c, 0.4), border: `2px solid ${c}`}} />{n}</span>)}
        </div>
      </Pop>
      <Pop from={t(0.7)} to={end} x={960} y={300}><Pill color={C.purple} size={22}>接收方在确认里通告 rwnd：“我还能收多少”</Pill></Pop>
    </AbsoluteFill>
  );
};

const CW = [1, 2, 4, 8, 16, 17, 18, 19, 20, 21, 22, 11, 12, 13, 14, 15, 16];
const OX = 380, OY = 820, SXR = 70, SYV = 21;
const cx = (r: number) => OX + r * SXR, cy = (v: number) => OY - v * SYV;

const Congestion: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(5, f);
  const end = at(6, 0);
  if (frame < t(0) - 2 || frame > end + 14) return null;
  const draw = ip(frame, t(0.1), t(0.8) - t(0.1), (x) => x) * (CW.length - 1);
  const n = Math.floor(draw), f = draw - n;
  const pts: P[] = CW.slice(0, n + 1).map((v, r) => [cx(r), cy(v)]);
  if (n < CW.length - 1) pts.push([cx(n + f), cy(CW[n] + (CW[n + 1] - CW[n]) * f)]);
  const o = vis(frame, t(0.02), end);
  return (
    <AbsoluteFill style={{opacity: o}}>
      <Svg>
        <line x1={OX} y1={OY} x2={cx(16) + 60} y2={OY} stroke={C.line} strokeWidth={2} />
        <line x1={OX} y1={OY} x2={OX} y2={cy(24)} stroke={C.line} strokeWidth={2} />
        {[0, 4, 8, 12, 16].map((r) => <text key={r} x={cx(r)} y={OY + 34} textAnchor="middle" fontSize={18} fill={C.faint} fontFamily={MONO}>{r}</text>)}
        {[8, 16, 24].map((v) => <text key={v} x={OX - 16} y={cy(v) + 6} textAnchor="end" fontSize={18} fill={C.faint} fontFamily={MONO}>{v}</text>)}
        <line x1={OX} y1={cy(16)} x2={cx(10)} y2={cy(16)} stroke={C.purple} strokeWidth={2} strokeDasharray="8 8" opacity={prog(frame, t(0.08), 10)} />
        <line x1={cx(10)} y1={cy(11)} x2={cx(16) + 40} y2={cy(11)} stroke={C.purple} strokeWidth={2} strokeDasharray="8 8" opacity={draw > 10.5 ? 1 : 0} />
        <polyline points={pts.map((p) => p.join(',')).join(' ')} fill="none" stroke={C.blue} strokeWidth={5} strokeLinejoin="round" strokeLinecap="round"
          style={{filter: `drop-shadow(0 0 10px ${tint(C.blue, 0.6)})`}} />
        {CW.map((v, r) => r <= n && <circle key={r} cx={cx(r)} cy={cy(v)} r={r === 10 ? 10 : 6} fill={r === 10 ? C.red : r < 5 ? C.teal : C.blue} />)}
      </Svg>
      <Label x={OX} y={cy(24) - 30} from={t(0.04)} size={20} color={C.muted}>拥塞窗口 cwnd</Label>
      <Label x={cx(16) + 60} y={OY + 70} anchor="right" from={t(0.04)} size={20} color={C.muted}>传输轮次 →</Label>
      <Label x={cx(6)} y={cy(16) + 26} anchor="left" from={t(0.1)} size={19} color={C.purple}>ssthresh = 16</Label>
      <Label x={cx(2)} y={cy(10)} from={t(0.22)} size={24} color={C.teal} weight={650}>慢开始 · ×2</Label>
      <Label x={cx(7)} y={cy(22)} from={t(0.45)} size={24} color={C.blue} weight={650}>拥塞避免 · +1</Label>
      <Pop from={t(0.6)} x={cx(10) + 30} y={cy(22) - 50} anchor="left"><Pill solid color={C.red} size={20}>丢包 → 窗口减半</Pill></Pop>
      <Label x={cx(16) + 50} y={cy(11) - 26} anchor="right" from={t(0.62)} size={19} color={C.purple}>新 ssthresh = 11</Label>
    </AbsoluteFill>
  );
};

const Teardown: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(6, f);
  if (frame < t(0) - 2) return null;
  return (
    <AbsoluteFill>
      <SeqDiagram x1={X1} x2={X2} top={240} bottom={880} from={t(0.02)} drop={70} msgs={[
        {dir: 'cs', y: 290, label: 'FIN', from: t(0.12), color: C.orange},
        {dir: 'sc', y: 390, label: 'ACK', from: t(0.26), color: C.green},
        {dir: 'sc', y: 560, label: 'FIN', from: t(0.48), color: C.orange},
        {dir: 'cs', y: 660, label: 'ACK', from: t(0.62), color: C.green},
      ]} />
      <Label x={960} y={500} from={t(0.34)} size={20} color={C.faint}>服务器还能继续发送剩余数据</Label>
      <State x={X1 - 24} y={330} from={t(0.14)} color={C.orange}>FIN-WAIT</State>
      <State x={X2 + 24} y={430} anchor="left" from={t(0.28)} color={C.muted}>CLOSE-WAIT</State>
      <State x={X1 - 24} y={760} from={t(0.66)} color={C.purple}>TIME-WAIT · 2MSL</State>
      <State x={X2 + 24} y={730} anchor="left" from={t(0.7)} color={C.green}>CLOSED</State>
      <Pop from={t(0.78)} x={960} y={870}><Pill color={C.ink2} size={22}>两个方向各自关闭 → 四次挥手</Pill></Pop>
    </AbsoluteFill>
  );
};

export const TransportScene: React.FC = () => (
  <AbsoluteFill>
    <Ports />
    <UdpTcp />
    <Handshake />
    <Retransmit />
    <Window />
    <Congestion />
    <Teardown />
  </AbsoluteFill>
);
