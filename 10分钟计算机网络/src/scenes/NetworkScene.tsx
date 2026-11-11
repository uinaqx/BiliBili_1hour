import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT, MONO, tint} from '../theme';
import {P, clamp, ip, pop, prog, useScene, vis} from '../anim';
import {BitRow, Block, Label, Pill, Pop, Svg, Wire, bitRowWidth, card} from '../kit';
import {Mover, Router, Tag} from '../net';

const H1: P = [360, 540], R1: P = [700, 540], R3: P = [960, 380], R4: P = [960, 720], R2: P = [1220, 540], SV: P = [1560, 540];
const HOPS: P[] = [H1, R1, R3, R2, SV];

const Hops: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(0, f);
  const end = at(1, 0);
  if (frame > end + 14) return null;
  const go = t(0.35), step = Math.round((t(0.85) - go) / 4);
  const nets = [[230, 590, '网络 1'], [770, 1150, '网络 2'], [1290, 1690, '网络 3']] as const;
  return (
    <AbsoluteFill>
      {nets.map(([a, b, n], i) => (
        <Pop key={n} from={t(0.02) + i * 5} to={end} x={(a + b) / 2} y={540}>
          <div style={{width: b - a, height: 480, borderRadius: 44, border: `2px dashed ${C.line}`, background: tint(C.blue, 0.025), position: 'relative'}}>
            <div style={{position: 'absolute', bottom: 18, left: 0, right: 0, textAlign: 'center', fontSize: 20, color: C.faint, fontFamily: FONT}}>{n}</div>
          </div>
        </Pop>
      ))}
      <Svg>
        {[[R1, R3], [R1, R4], [R4, R2], [R3, R2], [H1, R1], [R2, SV]].map(([a, b], i) => (
          <Wire key={i} pts={[a, b]} from={t(0.12) + i * 3} to={end} color={C.line} w={3} head={false} />
        ))}
        {HOPS.slice(1).map((b, i) => (
          <Wire key={i} pts={[HOPS[i], b]} from={go + i * step} len={step} to={end} color={C.blue} w={5} head={false} />
        ))}
      </Svg>
      <Block x={H1[0]} y={H1[1]} w={190} h={100} from={t(0.08)} to={end} title="源主机" sub="192.168.1.10" color={C.blue} size={26} />
      <Block x={SV[0]} y={SV[1]} w={190} h={100} from={t(0.1)} to={end} title="目的主机" sub="203.0.113.8" color={C.blue} size={26}
        hl={prog(frame, go + step * 4, 10)} />
      {[R1, R3, R4, R2].map((r, i) => {
        const k = HOPS.indexOf(r);
        const hl = k > 0 ? prog(frame, go + (k - 1) * step + step - 6, 6) * (1 - prog(frame, go + k * step + 6, 12)) : 0;
        return <Router key={i} x={r[0]} y={r[1]} from={t(0.14) + i * 4} to={end} hl={hl} label={`R${i + 1}`} />;
      })}
      <Mover pts={HOPS} from={go} len={step * 4}>
        <Tag color={C.blue}>IP 数据报</Tag>
      </Mover>
      <Pop from={t(0.3)} to={end} x={960} y={860}><Pill color={C.blue} size={22}>源 192.168.1.10 → 目的 203.0.113.8 · 逐跳转发</Pill></Pop>
    </AbsoluteFill>
  );
};

const OCT = ['192', '168', '1', '10'];
const BITS = '11000000101010000000000100001010';
const BS = 40, BG = 6, BW = bitRowWidth(32, BS, BG), BX = 960 - BW / 2;
const bx = (i: number) => BX + i * (BS + BG) + Math.floor(i / 4) * BG * 2;

const Address: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(1, f);
  const end = at(2, 0);
  if (frame < t(0) - 2 || frame > end + 14) return null;
  const split = ip(frame, t(0.5), 16);
  return (
    <AbsoluteFill>
      <Pop from={t(0.04)} to={end} x={960} y={300}>
        <div style={{fontFamily: MONO, fontSize: 104, fontWeight: 600, letterSpacing: 2, display: 'flex'}}>
          {OCT.map((o, i) => (
            <React.Fragment key={i}>
              <span style={{color: split > 0.5 ? (i < 3 ? C.blue : C.green) : C.ink, opacity: clamp(pop(frame, t(0.06) + i * 5) * 1.5)}}>{o}</span>
              {i < 3 && <span style={{color: C.faint}}>.</span>}
            </React.Fragment>
          ))}
          <span style={{color: C.orange, opacity: prog(frame, t(0.46), 10)}}>/24</span>
        </div>
      </Pop>
      <BitRow bits={BITS} x={BX} y={500} from={t(0.18)} to={end} size={BS} gap={BG} stagger={1}
        lit={(i) => split * 0.85} color={(i) => (i < 24 ? C.blue : C.green)} />
      {[0, 1, 2, 3].map((k) => (
        <Label key={k} x={(bx(k * 8) + bx(k * 8 + 7) + BS) / 2} y={446} from={t(0.22) + k * 4} to={end} size={18} mono color={C.faint}>{OCT[k]}</Label>
      ))}
      <Svg style={{opacity: split * vis(frame, 0, end)}}>
        {[[0, 23, C.blue], [24, 31, C.green]].map(([a, b, c]) => {
          const x1 = bx(a as number), x2 = bx(b as number) + BS;
          return <path key={String(a)} d={`M${x1},548 L${x1},562 L${x2},562 L${x2},548`} fill="none" stroke={c as string} strokeWidth={2.5} />;
        })}
      </Svg>
      <Label x={(bx(0) + bx(23) + BS) / 2} y={600} from={t(0.55)} to={end} size={26} color={C.blue} weight={650}>网络号 · 前 24 位</Label>
      <Label x={(bx(24) + bx(31) + BS) / 2} y={600} from={t(0.6)} to={end} size={26} color={C.green} weight={650}>主机号 · 8 位</Label>
      <Pop from={t(0.72)} to={end} x={960} y={740}>
        <div style={{display: 'flex', gap: 18}}>
          <Pill color={C.ink2} size={22}>32 位 · 约 43 亿个地址</Pill>
          <Pill color={C.orange} size={22}>子网掩码 255.255.255.0</Pill>
        </div>
      </Pop>
    </AbsoluteFill>
  );
};

const TABLE = [
  {p: '0.0.0.0/0', i: '0', m: true, n: 0},
  {p: '10.0.0.0/8', i: '1', m: true, n: 8},
  {p: '192.168.0.0/16', i: '2', m: false, n: 16},
  {p: '10.1.0.0/16', i: '3', m: true, n: 16},
  {p: '10.1.2.0/24', i: '4', m: true, n: 24},
];

const Lpm: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(2, f);
  const end = at(3, 0);
  if (frame < t(0) - 2 || frame > end + 14) return null;
  const pick = t(0.62);
  const RT: P = [1330, 560];
  const ifY = (k: number) => 300 + k * 130;
  return (
    <AbsoluteFill>
      <Pop from={t(0.02)} to={end} x={700} y={226}>
        <div style={{display: 'flex', alignItems: 'center', gap: 16, fontFamily: FONT}}>
          <span style={{fontSize: 24, color: C.muted}}>目的地址</span>
          <Tag color={C.blue} size={26}>10.1.2.7</Tag>
        </div>
      </Pop>
      <Pop from={t(0.04)} to={end} x={700} y={300} anchor="top">
        <div style={card({width: 760, padding: '22px 28px 26px', boxSizing: 'border-box', fontFamily: FONT})}>
          <div style={{display: 'flex', justifyContent: 'space-between', fontSize: 20, color: C.muted, padding: '0 20px 6px'}}>
            <span>目的网络前缀</span><span>出接口</span>
          </div>
          {TABLE.map((r, k) => {
            const chk = t(0.14) + k * Math.round((pick - t(0.14)) / 5);
            const on = frame >= chk;
            const win = r.n === 24 && frame >= pick;
            const lose = frame >= pick && !win;
            const c = win ? C.green : r.m ? C.blue : C.red;
            return (
              <div key={r.p} style={{height: 64, marginTop: 10, borderRadius: 14, display: 'flex', alignItems: 'center', padding: '0 20px',
                background: on ? tint(c, win ? 0.2 : 0.1) : C.fill, border: `2px solid ${on ? tint(c, win ? 1 : 0.5) : 'transparent'}`,
                opacity: lose ? 0.45 : 1, boxShadow: win ? `0 0 30px ${tint(C.green, 0.3)}` : 'none'}}>
                <span style={{fontFamily: MONO, fontSize: 28, color: C.ink, flex: 1}}>{r.p}</span>
                {on && <span style={{fontSize: 22, color: c, marginRight: 36, fontWeight: 600, opacity: prog(frame, chk, 6)}}>
                  {r.m ? `✓ 匹配 ${r.n} 位` : '✕ 不匹配'}</span>}
                <span style={{fontFamily: MONO, fontSize: 28, color: win ? C.green : C.ink2, width: 30, textAlign: 'right'}}>{r.i}</span>
              </div>
            );
          })}
        </div>
      </Pop>
      <Pop from={pick + 4} to={end} x={1100} y={300 + 52 + 4 * 74 + 36} anchor="left"><Pill solid color={C.green} size={20}>最长前缀</Pill></Pop>
      <Svg>
        {[0, 1, 2, 3, 4].map((k) => (
          <Wire key={k} pts={[[RT[0] + 40, RT[1]], [1520, ifY(k)], [1700, ifY(k)]]} from={t(0.08) + k * 3} to={end}
            color={k === 4 && frame >= pick ? C.green : C.line} w={k === 4 && frame >= pick ? 4 : 2} head={false} />
        ))}
      </Svg>
      {[0, 1, 2, 3, 4].map((k) => <Label key={k} x={1720} y={ifY(k)} anchor="left" from={t(0.1) + k * 3} to={end} size={20} mono
        color={k === 4 && frame >= pick ? C.green : C.muted}>{k}</Label>)}
      <Router x={RT[0]} y={RT[1]} from={t(0.06)} to={end} r={54} hl={prog(frame, pick, 10)} label="路由器" />
      <Mover pts={[[RT[0] + 40, RT[1]], [1520, ifY(4)], [1700, ifY(4)]]} from={pick + 14} len={30} hold={20}>
        <div style={{width: 16, height: 16, borderRadius: 8, background: C.green, boxShadow: `0 0 24px ${C.green}`}} />
      </Mover>
    </AbsoluteFill>
  );
};

const G: Record<string, P> = {A: [480, 540], B: [740, 360], C: [740, 720], D: [1060, 340], E: [1060, 700], F: [1380, 540]};
const EDGES: [string, string, number][] = [['A', 'B', 2], ['A', 'C', 5], ['B', 'C', 1], ['B', 'D', 4], ['C', 'E', 3], ['D', 'E', 1], ['D', 'F', 5], ['E', 'F', 2]];
const SETTLE: [string, number, string | null][] = [['A', 0, null], ['B', 2, 'A'], ['C', 3, 'B'], ['D', 6, 'B'], ['E', 6, 'C'], ['F', 8, 'E']];
const BEST = ['A', 'B', 'C', 'E', 'F'];

const Dijkstra: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(3, f);
  const end = at(4, 0);
  if (frame < t(0) - 2 || frame > end + 14) return null;
  const sAt = (k: number) => t(0.18 + k * 0.1);
  const best = t(0.82);
  const settled = (n: string) => {
    const k = SETTLE.findIndex((s) => s[0] === n);
    return frame >= sAt(k);
  };
  const tree = (a: string, b: string) => SETTLE.some(([n, , p], k) => frame >= sAt(k) && ((n === a && p === b) || (n === b && p === a)));
  const onBest = (a: string, b: string) => frame >= best && BEST.some((n, i) => i > 0 && ((BEST[i - 1] === a && n === b) || (BEST[i - 1] === b && n === a)));
  return (
    <AbsoluteFill>
      <Svg>
        {EDGES.map(([a, b], i) => {
          const c = onBest(a, b) ? C.green : tree(a, b) ? C.blue : C.line;
          return <Wire key={i} pts={[G[a], G[b]]} from={t(0.04) + i * 3} to={end} color={c} w={onBest(a, b) ? 6 : tree(a, b) ? 4 : 2.5} head={false} />;
        })}
      </Svg>
      {EDGES.map(([a, b, w], i) => (
        <Pop key={i} from={t(0.08) + i * 3} to={end} x={(G[a][0] + G[b][0]) / 2} y={(G[a][1] + G[b][1]) / 2}>
          <div style={{width: 40, height: 40, borderRadius: 20, background: C.bg, border: `1.5px solid ${C.line}`, display: 'flex', alignItems: 'center',
            justifyContent: 'center', fontFamily: MONO, fontSize: 20, color: C.muted}}>{w}</div>
        </Pop>
      ))}
      {Object.entries(G).map(([n, p], i) => {
        const k = SETTLE.findIndex((s) => s[0] === n);
        const on = settled(n);
        const s = pop(frame, sAt(k));
        const c = frame >= best && BEST.includes(n) ? C.green : C.blue;
        return (
          <Pop key={n} from={t(0.02) + i * 4} to={end} x={p[0]} y={p[1]}>
            <div style={{position: 'relative'}}>
              <div style={{width: 84, height: 84, borderRadius: 42, background: on ? tint(c, 0.25) : C.card, border: `2.5px solid ${on ? c : C.line}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 34, fontWeight: 700, color: C.ink, fontFamily: FONT,
                boxShadow: on ? `0 0 ${30 * s}px ${tint(c, 0.4)}` : 'none'}}>{n}</div>
              <div style={{position: 'absolute', top: p[1] < 540 ? -46 : 96, left: '50%', transform: 'translateX(-50%)', fontFamily: MONO, fontSize: 24,
                fontWeight: 600, color: on ? c : C.faint, whiteSpace: 'nowrap'}}>{on ? `d=${SETTLE[k][1]}` : 'd=∞'}</div>
            </div>
          </Pop>
        );
      })}
      <Pop from={t(0.1)} to={end} x={1660} y={430}>
        <div style={card({width: 340, padding: '22px 26px', boxSizing: 'border-box', fontFamily: FONT})}>
          <div style={{fontSize: 22, color: C.ink, fontWeight: 650, marginBottom: 10}}>Dijkstra</div>
          {['选出距离最小的未确定节点', '把它标记为已确定', '用它更新邻居的距离'].map((s, i) => (
            <div key={i} style={{fontSize: 19, color: C.ink2, marginTop: 8, display: 'flex', gap: 10}}>
              <span style={{color: C.blue, fontFamily: MONO}}>{i + 1}</span>{s}
            </div>
          ))}
        </div>
      </Pop>
      <Pop from={best + 4} to={end} x={930} y={880}><Pill solid color={C.green} size={24}>A → F 最短路径 = 8 · 写入转发表</Pill></Pop>
    </AbsoluteFill>
  );
};

const LAN = [
  {n: 'A', ip: '192.168.1.10', x: 420},
  {n: 'B', ip: '192.168.1.11', x: 780},
  {n: 'C', ip: '192.168.1.20', x: 1140},
  {n: 'D', ip: '192.168.1.30', x: 1500},
];
const BUS = 640, HY = 470;

const Arp: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(4, f);
  const end = at(5, 0);
  if (frame < t(0) - 2 || frame > end + 14) return null;
  const ask = t(0.2), ans = t(0.55);
  const up = (x: number): P[] => [[x, HY + 52], [x, BUS]];
  return (
    <AbsoluteFill>
      <Svg>
        <Wire pts={[[300, BUS], [1620, BUS]]} from={t(0.04)} to={end} color={C.line} w={4} head={false} len={22} />
        {LAN.map((h, i) => <Wire key={i} pts={up(h.x)} from={t(0.08) + i * 3} to={end} color={C.line} w={3} head={false} />)}
        {frame >= ask && frame < ans && [0, 1, 2].map((k) => {
          const ph = ((frame - ask) / 40 + k / 3) % 1;
          return <ellipse key={k} cx={420} cy={BUS} rx={60 + ph * 1100} ry={18 + ph * 60} fill="none" stroke={C.orange}
            strokeWidth={3} opacity={(1 - ph) * 0.6 * (1 - prog(frame, ans - 10, 10))} />;
        })}
      </Svg>
      {LAN.map((h, i) => {
        const no = (i === 1 || i === 3) && frame > ask + 26;
        return <Block key={h.n} x={h.x} y={HY} w={250} h={104} from={t(0.06) + i * 4} to={end} title={`主机 ${h.n}`} sub={h.ip} size={26}
          color={i === 2 ? C.green : C.blue} hl={i === 2 ? prog(frame, ask + 26, 8) : i === 0 ? prog(frame, ans + 30, 8) : 0} />;
      })}
      <Pop from={ask} to={ans + 30} x={420} y={300}><Tag color={C.orange} mono={false}>谁是 192.168.1.20？（广播）</Tag></Pop>
      {[1, 3].map((i) => <Label key={i} x={LAN[i].x} y={HY - 82} from={ask + 30} to={end} size={20} color={C.faint}>不是我，忽略</Label>)}
      <Mover pts={[[1140, BUS], [420, BUS]]} from={ans} len={34} hold={6}><Tag color={C.green}>3C:22:FB:7A:91:0E</Tag></Mover>
      <Pop from={ans} to={end} x={1140} y={300}><Tag color={C.green} mono={false}>是我（单播回复）</Tag></Pop>
      <Pop from={t(0.78)} to={end} x={600} y={800}>
        <div style={card({padding: '18px 30px', fontFamily: FONT, display: 'flex', alignItems: 'center', gap: 22})}>
          <span style={{fontSize: 22, color: C.muted}}>A 的 ARP 缓存</span>
          <span style={{fontFamily: MONO, fontSize: 26, color: C.ink}}>192.168.1.20</span>
          <span style={{color: C.faint, fontSize: 24}}>→</span>
          <span style={{fontFamily: MONO, fontSize: 26, color: C.green}}>3C:22:FB:7A:91:0E</span>
        </div>
      </Pop>
      <Label x={1440} y={800} from={t(0.8)} to={end} size={22}>IP 地址 → MAC 地址</Label>
    </AbsoluteFill>
  );
};

const DEV = [{n: '手机', ip: '192.168.1.2', y: 360, c: C.blue}, {n: '电脑', ip: '192.168.1.3', y: 540, c: C.teal}, {n: '平板', ip: '192.168.1.4', y: 720, c: C.purple}];
const NAT: P = [800, 540], WEB: P = [1600, 540];

const Nat: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(5, f);
  if (frame < t(0) - 2) return null;
  const send = (k: number) => t(0.22 + k * 0.17);
  return (
    <AbsoluteFill>
      <Pop from={t(0.02)} x={490} y={540}>
        <div style={{width: 560, height: 600, borderRadius: 44, border: `2px dashed ${C.line}`, background: tint(C.blue, 0.025), position: 'relative'}}>
          <div style={{position: 'absolute', top: 18, left: 30, fontSize: 20, color: C.faint, fontFamily: FONT}}>家庭内网 · 私有地址</div>
        </div>
      </Pop>
      <Svg>
        {DEV.map((d, k) => <Wire key={k} pts={[[440, d.y], [NAT[0] - 60, NAT[1]]]} from={t(0.06) + k * 3} color={C.line} w={3} head={false} />)}
        <Wire pts={[[NAT[0] + 60, NAT[1]], [WEB[0] - 110, WEB[1]]]} from={t(0.1)} color={C.line} w={3} head={false} />
      </Svg>
      {DEV.map((d, k) => <Block key={k} x={330} y={d.y} w={220} h={100} from={t(0.04) + k * 4} title={d.n} sub={d.ip} color={d.c} size={26}
        hl={prog(frame, send(k), 6) * (1 - prog(frame, send(k) + 30, 12))} />)}
      <Router x={NAT[0]} y={NAT[1]} from={t(0.08)} r={58} color={C.orange} label="NAT 路由器" hl={0.4 + 0.3 * Math.sin(frame / 10)} />
      <Block x={WEB[0]} y={WEB[1]} w={210} h={110} from={t(0.12)} title="服务器" sub="公网" size={28} />
      <Label x={1200} y={590} from={t(0.14)} size={20} mono color={C.orange}>公网 IP 203.0.113.5</Label>
      {DEV.map((d, k) => (
        <React.Fragment key={k}>
          <Mover pts={[[440, d.y], [NAT[0] - 60, NAT[1]]]} from={send(k)} len={20}>
            <div style={{width: 16, height: 16, borderRadius: 8, background: d.c, boxShadow: `0 0 20px ${d.c}`}} />
          </Mover>
          <Mover pts={[[NAT[0] + 60, NAT[1]], [WEB[0] - 110, WEB[1]]]} from={send(k) + 22} len={30}>
            <Tag color={d.c} size={18}>:{40001 + k}</Tag>
          </Mover>
        </React.Fragment>
      ))}
      <Pop from={t(0.16)} x={1200} y={290}>
        <div style={card({width: 640, padding: '20px 26px 24px', boxSizing: 'border-box', fontFamily: FONT})}>
          <div style={{display: 'flex', justifyContent: 'space-between', fontSize: 19, color: C.muted, padding: '0 14px 4px'}}>
            <span>内网地址 : 端口</span><span>公网地址 : 端口</span>
          </div>
          {DEV.map((d, k) => {
            const s = pop(frame, send(k) + 20);
            return (
              <div key={k} style={{height: 48, marginTop: 8, borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '0 14px', background: C.fill, fontFamily: MONO, fontSize: 21, opacity: clamp(s * 1.5), transform: `translateX(${(1 - s) * 20}px)`}}>
                <span style={{color: C.ink}}>{d.ip}:5000</span>
                <span style={{color: C.faint}}>↔</span>
                <span style={{color: d.c}}>203.0.113.5:{40001 + k}</span>
              </div>
            );
          })}
        </div>
      </Pop>
      <Pop from={t(0.8)} x={1200} y={800}><Pill color={C.orange} size={22}>多台设备共享一个公网 IP · 用端口区分</Pill></Pop>
    </AbsoluteFill>
  );
};

export const NetworkScene: React.FC = () => (
  <AbsoluteFill>
    <Hops />
    <Address />
    <Lpm />
    <Dijkstra />
    <Arp />
    <Nat />
  </AbsoluteFill>
);
