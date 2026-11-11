import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT, MONO, SHADOW, tint} from '../theme';
import {P, clamp, curve, easeOut, ip, pop, prog, useScene, vis} from '../anim';
import {Block, Label, Pill, Pop, Svg, Wire, card} from '../kit';
import {Mover, Tag} from '../net';

const Translate: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(0, f);
  const end = at(1, 0);
  if (frame > end + 14) return null;
  const spin = frame / 40;
  return (
    <AbsoluteFill>
      <Pop from={t(0.06)} to={end} x={460} y={520}>
        <div style={{textAlign: 'center', fontFamily: FONT}}>
          <div style={card({padding: '26px 40px', fontFamily: MONO, fontSize: 44, color: C.ink, fontWeight: 600})}>www.example.com</div>
          <div style={{fontSize: 24, color: C.muted, marginTop: 20}}>人记得住的 · 域名</div>
        </div>
      </Pop>
      <Pop from={t(0.2)} to={end} x={960} y={520}>
        <div style={{width: 200, height: 200, borderRadius: 100, position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
          <svg width={200} height={200} style={{position: 'absolute', inset: 0}}>
            <circle cx={100} cy={100} r={96} fill={C.card} stroke={C.line} strokeWidth={2} />
            <circle cx={100} cy={100} r={96} fill="none" stroke={C.teal} strokeWidth={4} strokeDasharray="90 513" strokeLinecap="round"
              transform={`rotate(${spin * 180} 100 100)`} />
          </svg>
          <div style={{fontSize: 48, fontWeight: 700, color: C.teal, fontFamily: FONT, letterSpacing: 2, position: 'relative'}}>DNS</div>
        </div>
      </Pop>
      <Svg>
        <Wire pts={[[680, 520], [850, 520]]} from={t(0.3)} to={end} color={C.line} w={3} />
        <Wire pts={[[1070, 520], [1240, 520]]} from={t(0.5)} to={end} color={C.teal} w={3} />
      </Svg>
      <Pop from={t(0.56)} to={end} x={1480} y={520}>
        <div style={{textAlign: 'center', fontFamily: FONT}}>
          <div style={card({padding: '26px 40px', fontFamily: MONO, fontSize: 44, color: C.teal, fontWeight: 600, border: `1.5px solid ${tint(C.teal, 0.5)}`})}>93.184.216.34</div>
          <div style={{fontSize: 24, color: C.muted, marginTop: 20}}>机器需要的 · IP 地址</div>
        </div>
      </Pop>
      <Pop from={t(0.75)} to={end} x={960} y={790}><Pill color={C.teal} size={22}>互联网的“电话簿” · 分布式数据库</Pill></Pop>
    </AbsoluteFill>
  );
};

const HOST: P = [260, 560], LOCAL: P = [660, 560], ROOT: P = [1340, 300], TLD: P = [1480, 560], AUTH: P = [1340, 810];
const STEPS: {a: P; b: P; label?: string; c: string}[] = [
  {a: HOST, b: LOCAL, c: C.blue},
  {a: LOCAL, b: ROOT, c: C.blue},
  {a: ROOT, b: LOCAL, label: '去问 .com', c: C.ink2},
  {a: LOCAL, b: TLD, c: C.blue},
  {a: TLD, b: LOCAL, label: '去问 example.com', c: C.ink2},
  {a: LOCAL, b: AUTH, c: C.blue},
  {a: AUTH, b: LOCAL, label: '93.184.216.34', c: C.teal},
  {a: LOCAL, b: HOST, label: '93.184.216.34', c: C.teal},
];
const edge = (a: P, b: P): [P, P] => {
  const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy);
  const ra = 120, rb = 120;
  return [[a[0] + (dx / L) * ra, a[1] + (dy / L) * ra * 0.6], [b[0] - (dx / L) * rb, b[1] - (dy / L) * rb * 0.6]];
};

const Resolve: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(1, f);
  const end = at(2, 0);
  if (frame < t(0) - 2 || frame > end + 14) return null;
  const stepAt = (k: number) => t(0.06 + k * 0.095);
  return (
    <AbsoluteFill>
      <Svg>
        {STEPS.map((s, k) => {
          const [a, b] = edge(s.a, s.b);
          return <Wire key={k} pts={curve(a, b, 30)} from={stepAt(k)} len={14} to={end} color={tint(s.c === C.blue ? C.blue : C.teal, 0.6)} w={2.5} />;
        })}
      </Svg>
      <Block x={HOST[0]} y={HOST[1]} w={200} h={110} from={t(0.02)} to={end} title="主机" sub="浏览器" size={28} />
      <Block x={LOCAL[0]} y={LOCAL[1]} w={240} h={110} from={t(0.03)} to={end} title="本地 DNS" sub="运营商 / 路由器" color={C.teal} size={28}
        hl={0.4 + 0.2 * Math.sin(frame / 12)} />
      <Block x={ROOT[0]} y={ROOT[1]} w={240} h={100} from={t(0.12)} to={end} title="根域名服务器" sub="." size={26} color={C.indigo}
        hl={vis(frame, stepAt(1) + 12, stepAt(2) + 6, 6)} />
      <Block x={TLD[0]} y={TLD[1]} w={240} h={100} from={t(0.3)} to={end} title="顶级域名服务器" sub=".com" size={26} color={C.indigo}
        hl={vis(frame, stepAt(3) + 12, stepAt(4) + 6, 6)} />
      <Block x={AUTH[0]} y={AUTH[1]} w={260} h={100} from={t(0.48)} to={end} title="权威域名服务器" sub="example.com" size={26} color={C.indigo}
        hl={vis(frame, stepAt(5) + 12, stepAt(6) + 6, 6)} />
      {STEPS.map((s, k) => {
        const [a, b] = edge(s.a, s.b);
        const pts = curve(a, b, 30);
        const mid = pts[Math.floor(pts.length / 2)];
        return (
          <React.Fragment key={k}>
            <Mover pts={pts} from={stepAt(k)} len={18}>
              <div style={{width: 14, height: 14, borderRadius: 7, background: s.c === C.ink2 ? C.ink2 : s.c, boxShadow: `0 0 18px ${s.c}`}} />
            </Mover>
            <Pop from={stepAt(k) + 4} to={end} x={mid[0]} y={mid[1]}>
              <div style={{width: 34, height: 34, borderRadius: 17, background: C.bg, border: `1.5px solid ${s.c}`, color: s.c, fontSize: 18,
                fontFamily: MONO, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{k + 1}</div>
            </Pop>
            {s.label && k !== 7 && <Label x={mid[0] + (k === 6 ? -60 : 20)} y={mid[1] + (k === 2 ? -40 : k === 6 ? 40 : 40)} anchor={k === 6 ? 'right' : 'left'}
              from={stepAt(k) + 8} to={stepAt(k + 1) + 30} size={19} mono color={s.c}>{s.label}</Label>}
          </React.Fragment>
        );
      })}
      <Pop from={stepAt(7) + 10} to={end} x={HOST[0]} y={680}><Tag color={C.teal} size={18}>93.184.216.34</Tag></Pop>
      <Pop from={t(0.85)} to={end} x={LOCAL[0]} y={700}><Pill color={C.green} size={20}>结果缓存 · TTL 内直接用</Pill></Pop>
    </AbsoluteFill>
  );
};

const REQ = [['GET', ' /index.html HTTP/1.1'], ['Host:', ' www.example.com'], ['Accept:', ' text/html']];
const RES = [['HTTP/1.1', ' 200 OK'], ['Content-Type:', ' text/html'], ['Content-Length:', ' 1256'], ['', ''], ['<html>', '…</html>']];
const CODES = [['200', 'OK · 成功', C.green], ['301', '永久重定向', C.blue], ['404', 'Not Found', C.orange], ['500', '服务器错误', C.red]];

const Http: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(2, f);
  const end = at(3, 0);
  if (frame < t(0) - 2 || frame > end + 14) return null;
  const code = (lines: string[][], color: string, from: number) => lines.map(([k, v], i) => (
    <div key={i} style={{fontFamily: MONO, fontSize: 26, lineHeight: '42px', whiteSpace: 'pre', opacity: prog(frame, from + i * 5, 8), minHeight: 42}}>
      <span style={{color}}>{k}</span><span style={{color: C.ink2}}>{v}</span>
    </div>
  ));
  return (
    <AbsoluteFill>
      <Pop from={t(0.04)} to={end} x={520} y={250} anchor="top">
        <div style={card({width: 660, padding: '26px 34px', boxSizing: 'border-box'})}>
          <div style={{fontFamily: FONT, fontSize: 22, color: C.muted, marginBottom: 12}}>请求 Request</div>
          {code(REQ, C.blue, t(0.08))}
        </div>
      </Pop>
      <Pop from={t(0.36)} to={end} x={1400} y={250} anchor="top">
        <div style={card({width: 660, padding: '26px 34px', boxSizing: 'border-box'})}>
          <div style={{fontFamily: FONT, fontSize: 22, color: C.muted, marginBottom: 12}}>响应 Response</div>
          {code(RES, C.green, t(0.4))}
        </div>
      </Pop>
      <Svg>
        <Wire pts={[[860, 340], [1060, 340]]} from={t(0.24)} to={end} color={C.blue} w={3} />
        <Wire pts={[[1060, 420], [860, 420]]} from={t(0.42)} to={end} color={C.green} w={3} />
      </Svg>
      <Mover pts={[[860, 340], [1060, 340]]} from={t(0.24)} len={18}><Tag color={C.blue} size={17}>GET</Tag></Mover>
      <Mover pts={[[1060, 420], [860, 420]]} from={t(0.42)} len={18}><Tag color={C.green} size={17}>200</Tag></Mover>
      <Pop from={t(0.58)} to={end} x={960} y={770}>
        <div style={{display: 'flex', gap: 22}}>
          {CODES.map(([c, n, col], i) => {
            const s = pop(frame, t(0.58) + i * 5);
            const hot = (c === '200' && frame > t(0.62)) || (c === '404' && frame > t(0.78));
            return (
              <div key={c} style={{width: 250, padding: '18px 0', borderRadius: 20, textAlign: 'center', background: hot ? tint(col, 0.16) : C.card,
                border: `1.5px solid ${tint(col, hot ? 0.9 : 0.3)}`, boxShadow: SHADOW, opacity: clamp(s * 1.5), transform: `translateY(${(1 - s) * 16}px)`}}>
                <div style={{fontFamily: MONO, fontSize: 40, fontWeight: 700, color: col}}>{c}</div>
                <div style={{fontFamily: FONT, fontSize: 20, color: C.ink2, marginTop: 4}}>{n}</div>
              </div>
            );
          })}
        </div>
      </Pop>
    </AbsoluteFill>
  );
};

const CL: P = [330, 560], SV: P = [1590, 560];
const Key: React.FC<{c: string}> = ({c}) => (
  <svg width={46} height={24} viewBox="0 0 46 24">
    <circle cx={12} cy={12} r={9} fill="none" stroke={c} strokeWidth={3.5} />
    <path d="M21,12 L44,12 M36,12 L36,20 M42,12 L42,18" stroke={c} strokeWidth={3.5} strokeLinecap="round" fill="none" />
  </svg>
);

const Tls: React.FC = () => {
  const {frame, at} = useScene();
  const t = (f: number) => at(3, f);
  if (frame < t(0) - 2) return null;
  const s1 = t(0.12), s2 = t(0.34), s3 = t(0.54), s4 = t(0.68);
  const scramble = (seed: number) => Array.from({length: 10}, (_, i) => '0123456789abcdef'[(seed * 7 + i * 13 + Math.floor(frame / 3)) % 16]).join('');
  const keyS = pop(frame, s3);
  return (
    <AbsoluteFill>
      <Pop from={t(0.02)} x={960} y={210}>
        <div style={{display: 'flex', alignItems: 'center', gap: 14, fontFamily: FONT}}>
          <Pill color={C.purple} size={24}>HTTP</Pill><span style={{color: C.faint, fontSize: 24}}>+</span>
          <Pill color={C.green} size={24}>TLS</Pill><span style={{color: C.faint, fontSize: 24}}>=</span>
          <Pill solid color={C.green} size={24}>HTTPS</Pill>
        </div>
      </Pop>
      <Block x={CL[0]} y={CL[1]} w={220} h={140} from={t(0.04)} title="浏览器" sub="客户端" size={30} />
      <Block x={SV[0]} y={SV[1]} w={220} h={140} from={t(0.06)} title="服务器" sub="持有私钥" size={30} />
      <Svg>
        {[330, 460, 700].map((y, i) => <Wire key={i} pts={[[CL[0] + 130, y], [SV[0] - 130, y]]} from={t(0.08) + i * 3} color={C.hair} w={2} head={false} />)}
      </Svg>
      <Label x={960} y={292} from={s1} size={21} color={C.green} weight={600}>① 证书 + 公钥</Label>
      <Mover pts={[[SV[0] - 130, 330], [CL[0] + 130, 330]]} from={s1} len={30} hold={s2 - s1}>
        <Tag color={C.green} mono={false} size={19}>证书 · 公钥</Tag>
      </Mover>
      <Label x={960} y={422} from={s2} size={21} color={C.orange} weight={600}>② 用公钥加密密钥材料，只有私钥能解</Label>
      <Mover pts={[[CL[0] + 130, 460], [SV[0] - 130, 460]]} from={s2} len={30} hold={10}>
        <Tag color={C.orange} size={19}>{scramble(3)}</Tag>
      </Mover>
      {[CL, SV].map((p, i) => (
        <Pop key={i} from={s3 + i * 4} x={p[0]} y={p[1] + 120}>
          <div style={{display: 'flex', alignItems: 'center', gap: 10, padding: '10px 18px', borderRadius: 14, background: tint(C.green, 0.14),
            border: `1.5px solid ${C.green}`, boxShadow: `0 0 ${30 * keyS}px ${tint(C.green, 0.4)}`, fontFamily: FONT, fontSize: 21, color: C.ink, whiteSpace: 'nowrap'}}>
            <Key c={C.green} />会话密钥 K
          </div>
        </Pop>
      ))}
      <Label x={960} y={600} from={s3 + 6} size={21} color={C.green} weight={600}>③ 双方得到同一把会话密钥</Label>
      {[0, 1, 2, 3].map((k) => (
        <Mover key={k} pts={k % 2 ? [[SV[0] - 210, 700], [CL[0] + 210, 700]] : [[CL[0] + 210, 700], [SV[0] - 210, 700]]} from={s4 + k * 22} len={36}>
          <Tag color={C.blue} size={18}>{scramble(k)}</Tag>
        </Mover>
      ))}
      <Label x={960} y={760} from={s4} size={21} color={C.blue} weight={600}>④ 之后的数据都用 K 对称加密 · 快</Label>
      <Pop from={t(0.85)} x={960} y={860}><Pill color={C.ink2} size={22}>非对称负责“安全地交换钥匙”，对称负责“快速加密数据”</Pill></Pop>
    </AbsoluteFill>
  );
};

export const AppScene: React.FC = () => (
  <AbsoluteFill>
    <Translate />
    <Resolve />
    <Http />
    <Tls />
  </AbsoluteFill>
);
