import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT, MONO, SHADOW, tint} from '../theme';
import {P, clamp, easeOut, ip, pop, prog, useScene, vis} from '../anim';
import {Label, Pill, Pop, Svg, Wire, card} from '../kit';
import {LAYERS, Mover, Router, Tag} from '../net';
import {Glyph} from './Intro';

const STAGES = ['DNS 查询', 'TCP 握手', 'TLS 握手', 'HTTP 请求', '逐跳转发', '响应 · 渲染'];
const LY = 560;
const BR: P = [210, LY], SW: P = [500, LY], RS: P[] = [[780, LY], [1060, LY], [1340, LY]], SV: P = [1680, LY], DNS: P = [640, 330];
const PATH: P[] = [BR, SW, ...RS, SV];
const inner = (pts: P[]): P[] => [[pts[0][0] + 80, pts[0][1]], ...pts.slice(1, -1), [pts[pts.length - 1][0] - 80, pts[pts.length - 1][1]]];
const STACK: Record<string, number> = {host: 5, sw: 2, rt: 3};

const Stack: React.FC<{x: number; n: number; from: number; hl: number}> = ({x, n, from, hl}) => (
  <Pop from={from} x={x} y={720} anchor="top">
    <div style={{display: 'flex', flexDirection: 'column', gap: 4, alignItems: 'center'}}>
      {LAYERS.slice(5 - n).map((l) => (
        <div key={l.id} style={{width: 120, height: 22, borderRadius: 6, background: tint(l.c, 0.18 + 0.4 * hl), border: `1px solid ${tint(l.c, 0.5 + 0.5 * hl)}`,
          fontSize: 13, color: C.ink2, fontFamily: FONT, display: 'flex', alignItems: 'center', justifyContent: 'center'}}>{l.name}</div>
      ))}
    </div>
  </Pop>
);

export const JourneyScene: React.FC = () => {
  const {frame, at, b, dur} = useScene();
  const stageAt = [at(0, 0.1), at(1, 0.02), at(1, 0.42), at(1, 0.72), at(2, 0.05), at(3, 0.02)];
  const cur = stageAt.reduce((acc, f, k) => (frame >= f ? k : acc), -1);
  const page = at(3, 0.45);
  const mapO = 1 - ip(frame, page, 18);
  const trip = (from: number, to: number, a: P[], back = false) => ({pts: inner(back ? [...a].reverse() : a), from, len: to - from});
  const hop = Math.round((at(2, 0.9) - at(2, 0.1)) / 5);
  const fwd = PATH.map((_, k) => at(2, 0.1) + k * hop);
  const tcp = [0, 1, 2].map((k) => trip(at(1, 0.04) + k * Math.round(at(1, 0.12) - at(1, 0)), at(1, 0.04) + (k + 1) * Math.round(at(1, 0.12) - at(1, 0)), PATH, k === 1));
  const tls = [0, 1].map((k) => trip(at(1, 0.44) + k * Math.round(at(1, 0.12) - at(1, 0)), at(1, 0.44) + (k + 1) * Math.round(at(1, 0.12) - at(1, 0)), PATH, k === 1));
  const resp = trip(at(3, 0.04), at(3, 0.4), PATH, true);
  return (
    <AbsoluteFill>
      <Pop from={b(0) - 10} x={960} y={200}>
        <div style={{display: 'flex', alignItems: 'center', gap: 12}}>
          {STAGES.map((s, k) => {
            const on = k === cur, done = k < cur;
            return (
              <React.Fragment key={s}>
                <div style={{padding: '10px 22px', borderRadius: 999, fontFamily: FONT, fontSize: 22, fontWeight: 600, whiteSpace: 'nowrap',
                  background: on ? C.blue : done ? tint(C.blue, 0.16) : C.card, color: on ? '#fff' : done ? C.blue : C.muted,
                  boxShadow: on ? `0 0 30px ${tint(C.blue, 0.5)}` : SHADOW, transform: `scale(${on ? 1.06 : 1})`}}>{s}</div>
                {k < STAGES.length - 1 && <span style={{color: done ? C.blue : C.faint, fontSize: 20}}>›</span>}
              </React.Fragment>
            );
          })}
        </div>
      </Pop>
      <AbsoluteFill style={{opacity: mapO}}>
        <Svg>
          {PATH.slice(1).map((p, k) => <Wire key={k} pts={[PATH[k], p]} from={b(0) - 6 + k * 3} color={C.line} w={3} head={false} />)}
          {frame >= fwd[0] && frame < at(3, 0) + 10 && PATH.slice(1).map((p, k) => (
            <line key={k} x1={PATH[k][0]} y1={LY} x2={PATH[k][0] + (p[0] - PATH[k][0]) * ip(frame, fwd[k], hop)} y2={LY} stroke={C.blue} strokeWidth={5}
              strokeLinecap="round" opacity={1 - prog(frame, at(3, 0), 10)} />
          ))}
          <Wire pts={[[SW[0], LY - 50], [DNS[0] - 40, DNS[1] + 50]]} from={b(0)} to={at(1, 0)} color={C.line} w={2.5} head={false} dash="4 8" />
        </Svg>
        <Pop from={b(0) - 8} x={BR[0]} y={BR[1]}>
          <div style={{width: 150, height: 110, borderRadius: 24, background: C.card, boxShadow: SHADOW, border: `2px solid ${tint(C.blue, 0.6)}`,
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 10, fontFamily: FONT}}>
            <Glyph kind="browser" /><span style={{fontSize: 20, color: C.ink}}>浏览器</span>
          </div>
        </Pop>
        <Pop from={b(0) - 4} x={SV[0]} y={SV[1]}>
          <div style={{width: 150, height: 110, borderRadius: 24, background: C.card, boxShadow: SHADOW, border: `2px solid ${tint(C.purple, 0.6)}`,
            display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 10, fontFamily: FONT}}>
            <Glyph kind="server" color={C.purple} /><span style={{fontSize: 20, color: C.ink}}>服务器</span>
          </div>
        </Pop>
        <Pop from={b(0) - 6} x={SW[0]} y={SW[1]}>
          <div style={{width: 120, height: 64, borderRadius: 16, background: C.card, boxShadow: SHADOW, border: `2px solid ${tint(C.green, 0.6)}`,
            display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FONT, fontSize: 20, color: C.ink}}>交换机</div>
        </Pop>
        {RS.map((r, k) => <Router key={k} x={r[0]} y={r[1]} from={b(0) - 4 + k * 3} r={42}
          hl={frame >= fwd[k + 2] - 4 && frame < fwd[k + 2] + 20 ? 1 : 0} />)}
        <Pop from={b(0) + 4} to={at(1, 0)} x={DNS[0]} y={DNS[1]}>
          <div style={{padding: '14px 26px', borderRadius: 18, background: C.card, boxShadow: SHADOW, border: `2px solid ${tint(C.teal, 0.6)}`,
            fontFamily: FONT, fontSize: 22, color: C.teal, fontWeight: 650}}>DNS 服务器</div>
        </Pop>
        <Mover pts={[[BR[0] + 80, LY - 20], [SW[0], LY - 50], [DNS[0] - 40, DNS[1] + 40]]} from={at(0, 0.25)} len={24} hold={4}><Tag color={C.teal} size={17}>www.example.com ?</Tag></Mover>
        <Mover pts={[[DNS[0] - 40, DNS[1] + 40], [SW[0], LY - 50], [BR[0] + 80, LY - 20]]} from={at(0, 0.55)} len={24} hold={at(1, 0) - at(0, 0.55) - 24}>
          <Tag color={C.teal} size={17}>93.184.216.34</Tag></Mover>
        {tcp.map((m, k) => <Mover key={k} {...m}><Tag color={C.orange} size={17}>{['SYN', 'SYN+ACK', 'ACK'][k]}</Tag></Mover>)}
        {tls.map((m, k) => <Mover key={k} {...m}><Tag color={C.green} size={17}>{['ClientHello', '证书 · 密钥协商'][k]}</Tag></Mover>)}
        <Mover pts={inner(PATH)} from={at(1, 0.74)} len={Math.round(at(1, 0.12) - at(1, 0))}><Tag color={C.purple} size={17}>GET /</Tag></Mover>
        <Mover pts={PATH} from={fwd[0]} len={fwd[5] - fwd[0]}>
          <div style={{display: 'flex', gap: 3, transform: 'translateY(-60px)'}}>
            {[['帧', C.green], ['IP', C.blue], ['TCP', C.orange], ['HTTP', C.purple]].map(([n, c], i) => {
              const k = Math.max(0, fwd.findIndex((f) => frame < f) - 1);
              const flash = i === 0 ? 1 - prog(frame, fwd[k], 12) : 0;
              return <div key={n} style={{padding: '6px 10px', borderRadius: 8, background: tint(c, 0.25 + 0.5 * flash), border: `1.5px solid ${c}`,
                fontFamily: MONO, fontSize: 16, color: C.ink, fontWeight: 600}}>{n}</div>;
            })}
          </div>
        </Mover>
        <Mover pts={resp.pts} from={resp.from} len={resp.len}><Tag color={C.green} size={17}>200 OK · HTML</Tag></Mover>
        {[BR, SW, ...RS, SV].map((p, k) => {
          const kind = k === 0 || k === 5 ? 'host' : k === 1 ? 'sw' : 'rt';
          const hl = kind === 'rt' && frame >= fwd[k] - 4 && frame < fwd[k] + 24 ? 1 : 0;
          return <Stack key={k} x={p[0]} n={STACK[kind]} from={b(0) + 6 + k * 3} hl={hl} />;
        })}
        <Label x={960} y={680} from={at(2, 0.2)} to={at(3, 0)} size={20} color={C.muted}>路由器：拆帧 → 查转发表 → 重新成帧</Label>
      </AbsoluteFill>
      <Page from={page} />
    </AbsoluteFill>
  );
};

const Page: React.FC<{from: number}> = ({from}) => {
  const {frame} = useScene();
  const s = pop(frame, from, 16);
  if (frame < from) return null;
  const blk = (i: number) => clamp(prog(frame, from + 14 + i * 5, 10));
  return (
    <Pop from={from} x={960} y={560}>
      <div style={card({width: 1080, height: 560, overflow: 'hidden', transform: `scale(${0.9 + 0.1 * s})`, border: `1.5px solid ${C.line}`})}>
        <div style={{height: 56, background: C.fill, display: 'flex', alignItems: 'center', padding: '0 22px', gap: 10}}>
          {[C.red, C.orange, C.green].map((c) => <span key={c} style={{width: 14, height: 14, borderRadius: 7, background: c}} />)}
          <div style={{marginLeft: 20, flex: 1, height: 32, borderRadius: 10, background: C.bg, display: 'flex', alignItems: 'center', padding: '0 16px',
            fontFamily: MONO, fontSize: 18, color: C.ink2}}><span style={{color: C.green}}>https://</span>www.example.com</div>
        </div>
        <div style={{padding: 40, display: 'flex', flexDirection: 'column', gap: 20}}>
          <div style={{height: 54, width: 520, borderRadius: 12, background: tint(C.blue, 0.5), opacity: blk(0)}} />
          <div style={{display: 'flex', gap: 24, opacity: blk(1)}}>
            <div style={{flex: 2, height: 260, borderRadius: 18, background: `linear-gradient(135deg, ${tint(C.blue, 0.4)}, ${tint(C.purple, 0.4)})`}} />
            <div style={{flex: 1, display: 'flex', flexDirection: 'column', gap: 16}}>
              {[0, 1, 2, 3, 4].map((i) => <div key={i} style={{height: 22, borderRadius: 8, background: C.line, width: `${100 - i * 12}%`, opacity: blk(2 + i)}} />)}
            </div>
          </div>
          <div style={{display: 'flex', gap: 16, opacity: blk(4)}}>
            {[0, 1, 2].map((i) => <div key={i} style={{flex: 1, height: 22, borderRadius: 8, background: C.hair}} />)}
          </div>
        </div>
      </div>
    </Pop>
  );
};
