import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT, TITLE_GRAD} from '../theme';
import {easeOut, ip, prog, useScene} from '../anim';
import {Pop} from '../kit';
import {LAYERS, Slab} from '../net';

const SUM = [
  ['服务用户', 'HTTP · DNS · TLS'],
  ['端到端', '端口 · TCP · UDP'],
  ['选路转发', 'IP · 路由 · NAT'],
  ['成帧 · 局域网', 'MAC · 交换机 · CRC'],
  ['传比特', '电 · 光 · 无线'],
];

const Recap: React.FC = () => {
  const {frame, at} = useScene();
  const end = at(1, 0.05);
  if (frame > end + 14) return null;
  return (
    <AbsoluteFill>
      {LAYERS.map((l, i) => {
        const k = 4 - i;
        const on = at(0, 0.08 + k * 0.17);
        const hl = prog(frame, on, 10) * (1 - prog(frame, on + 40, 20) * 0.6);
        return (
          <React.Fragment key={l.id}>
            <Slab x={640} y={270 + i * 124} w={520} h={100} from={at(0, 0.02) + k * 4} to={end} color={l.c} name={l.name} en={l.en} hl={hl} />
            <Pop from={on} to={end} x={960} y={270 + i * 124} anchor="left">
              <div style={{fontFamily: FONT, display: 'flex', alignItems: 'baseline', gap: 24}}>
                <span style={{fontSize: 36, fontWeight: 650, color: C.ink}}>{SUM[i][0]}</span>
                <span style={{fontSize: 22, color: l.c}}>{SUM[i][1]}</span>
              </div>
            </Pop>
          </React.Fragment>
        );
      })}
    </AbsoluteFill>
  );
};

const Final: React.FC = () => {
  const {frame, at} = useScene();
  const start = at(1, 0.12);
  const t = ip(frame, start, 26, easeOut);
  if (t <= 0) return null;
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center', fontFamily: FONT, opacity: t}}>
      <div style={{textAlign: 'center', transform: `translateY(${(1 - t) * 30}px)`}}>
        <div style={{fontSize: 120, fontWeight: 700, letterSpacing: 8, display: 'inline-block', backgroundImage: TITLE_GRAD,
          WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent'}}>计算机网络</div>
        <div style={{fontSize: 34, color: C.ink2, marginTop: 14, letterSpacing: 10, opacity: prog(frame, start + 20, 16)}}>分层 · 封装 · 协作</div>
        <div style={{fontSize: 24, color: C.muted, marginTop: 48, letterSpacing: 4, opacity: prog(frame, at(1, 0.7), 16)}}>感谢观看</div>
      </div>
    </AbsoluteFill>
  );
};

export const Outro: React.FC = () => (
  <AbsoluteFill>
    <Recap />
    <Final />
  </AbsoluteFill>
);
