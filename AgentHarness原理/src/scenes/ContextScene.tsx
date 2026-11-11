import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, FONT, MONO, glow, tint} from '../theme';
import {easeOut, ip, lerp, pop, prog, useScene, vis} from '../anim';
import {Block, Burst, Code, Comet, Orb, Packet, Pill, Pop, Shock, Svg, Wire, shake} from '../kit';

const LAYERS: [string, string][] = [['系统提示', C.gold], ['工具说明', C.magenta], ['对话历史', C.cyan], ['工具结果', C.violet]];
const OUTSIDE: [string, number, number][] = [['上一次会话', 1580, 270], ['整个代码库', 1640, 500], ['你没说出口的想法', 1560, 730]];

/** Beat 0: the model only sees what is inside the window. */
const Window: React.FC = () => {
  const {frame, at} = useScene();
  const end = at(1, 0.02);
  const o = vis(frame, at(0, 0), end, 16);
  if (o <= 0) return null;
  const cone = ip(frame, at(0, 0.15), 20, easeOut);
  return (
    <>
      <Svg style={{opacity: o}}>
        <defs>
          <linearGradient id="cone" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stopColor={C.violet} stopOpacity={0.55} />
            <stop offset="1" stopColor={C.cyan} stopOpacity={0.05} />
          </linearGradient>
        </defs>
        <polygon points={`380,500 ${lerp(380, 620, cone)},${lerp(500, 270, cone)} ${lerp(380, 620, cone)},${lerp(500, 730, cone)}`} fill="url(#cone)" />
      </Svg>
      <Orb x={330} y={500} r={80} from={at(0, 0)} to={end} />
      <Pop from={at(0, 0.08)} to={end} x={960} y={500} fx="zoom">
        <div style={{width: 680, height: 460, borderRadius: 30, boxSizing: 'border-box', padding: '58px 40px 30px', position: 'relative',
          border: `2px solid ${tint(C.cyan, 0.7)}`, boxShadow: `${glow(C.cyan, 0.7)}, inset 0 0 60px ${tint(C.cyan, 0.12)}`,
          background: tint(C.card, 0.85)}}>
          <div style={{position: 'absolute', top: 16, left: 30, fontFamily: MONO, fontSize: 18, letterSpacing: 6, color: C.cyan}}>CONTEXT WINDOW · 本次调用</div>
          {LAYERS.map(([t, c], i) => {
            const k = pop(frame, at(0, 0.2) + i * 6, 12);
            return (
              <div key={t} style={{height: 74, marginTop: i ? 16 : 0, borderRadius: 14, display: 'flex', alignItems: 'center', padding: '0 26px',
                background: `linear-gradient(90deg, ${tint(c, 0.4)}, ${tint(c, 0.08)})`, border: `1px solid ${tint(c, 0.6)}`,
                transform: `translateX(${(1 - k) * 200}px)`, opacity: k, fontSize: 28, fontWeight: 800, color: C.ink}}>{t}</div>
            );
          })}
        </div>
      </Pop>
      {OUTSIDE.map(([t, x, y], i) => {
        const f = at(0, 0.45 + i * 0.1);
        const jit = Math.sin(frame / 5 + i) * 4;
        const fade = ip(frame, f + 14, 30);
        return (
          <Pop key={t} from={f} to={end} x={x} y={y + jit} fx="right">
            <div style={{padding: '14px 26px', borderRadius: 16, border: `1.5px dashed ${C.faint}`, color: C.muted, fontSize: 26, fontWeight: 700,
              opacity: 1 - fade * 0.6, filter: `blur(${fade * 2.5}px) grayscale(1)`, whiteSpace: 'nowrap'}}>
              {t} <span style={{color: C.red, marginLeft: 8}}>看不见</span>
            </div>
          </Pop>
        );
      })}
    </>
  );
};

const X0 = 210, W = 1500, LIMIT = 200, BAR_Y = 440;

export const ContextScene: React.FC = () => {
  const {frame, at} = useScene();
  const show = vis(frame, at(1, 0.02), at(3, 0.02), 16);

  const grow = (f0: number, f1: number) => ip(frame, f0, f1 - f0, easeOut);
  const cut = ip(frame, at(2, 0.06), 18), sum = ip(frame, at(2, 0.36), 18), rag = ip(frame, at(2, 0.66), 14);
  const seg = {
    sys: 8 * grow(at(1, 0.08), at(1, 0.16)),
    tools: 14 * grow(at(1, 0.18), at(1, 0.28)),
    hist: lerp(60 * grow(at(1, 0.3), at(1, 0.7)), 8, sum),
    res: lerp(106 * grow(at(1, 0.45), at(1, 0.92)), 38, cut),
    rag: 6 * rag,
  };
  const total = seg.sys + seg.tools + seg.hist + seg.res + seg.rag;
  const hot = Math.min(1, Math.max(0, (total - 150) / 30));
  const alarm = hot > 0 ? 0.5 + 0.5 * Math.sin(frame / 3) : 0;
  const px = (v: number) => (v / LIMIT) * W;
  const parts: [keyof typeof seg, string, string][] = [
    ['sys', '系统', C.gold], ['tools', '工具', C.magenta], ['hist', sum > 0.5 ? '摘要' : '对话历史', C.cyan], ['res', '工具结果', C.violet], ['rag', '检索', C.lime],
  ];
  const segX = (k: keyof typeof seg) => {
    let x = X0;
    for (const [p] of parts) { if (p === k) return x; x += px(seg[p]); }
    return x;
  };
  const sh = [shake(frame, at(1, 0.85), 10, 30), shake(frame, at(2, 0.08), 12), shake(frame, at(2, 0.38), 12)].find((s) => s !== 'none') ?? 'none';
  const tech: [string, string, string, number][] = [
    ['截断', '过长的输出只留头尾', C.violet, at(2, 0.04)],
    ['摘要压缩', '早期对话压成一段摘要', C.cyan, at(2, 0.34)],
    ['按需检索', '用到时再读，不全塞进去', C.lime, at(2, 0.64)],
  ];
  const curTech = tech.reduce((a, t, i) => (frame >= t[3] ? i : a), -1);

  const mem = at(3, 0);
  return (
    <AbsoluteFill style={{transform: sh}}>
      <Window />
      {show > 0 && (
        <div style={{position: 'absolute', inset: 0, opacity: show}}>
          <div style={{position: 'absolute', left: X0, top: BAR_Y - 110, fontFamily: FONT, fontSize: 26, fontWeight: 800, color: C.ink2}}>上下文预算</div>
          <div style={{position: 'absolute', right: 1920 - X0 - W, top: BAR_Y - 128, fontFamily: MONO, fontSize: 52, fontWeight: 800,
            color: hot > 0.2 && cut < 0.5 ? C.red : total < 100 && cut > 0.5 ? C.lime : C.ink, textShadow: hot > 0.2 && cut < 0.5 ? glow(C.red, 0.8) : 'none'}}>
            {Math.round(total)}K <span style={{fontSize: 28, color: C.muted}}>/ {LIMIT}K tokens</span>
          </div>
          <div style={{position: 'absolute', left: X0 - 6, top: BAR_Y - 6, width: W + 12, height: 102, borderRadius: 22, boxSizing: 'border-box',
            border: `2px solid ${hot > 0 && cut < 0.5 ? tint(C.red, 0.4 + 0.6 * alarm) : C.line}`,
            boxShadow: hot > 0 && cut < 0.5 ? glow(C.red, alarm) : 'none', background: tint(C.card, 0.8)}} />
          {parts.map(([k, label, c]) => {
            const w = px(seg[k]);
            if (w < 1) return null;
            return (
              <div key={k} style={{position: 'absolute', left: segX(k), top: BAR_Y, width: w, height: 90, boxSizing: 'border-box',
                background: `linear-gradient(180deg, ${tint(c, 0.85)}, ${tint(c, 0.45)})`, borderRight: `2px solid ${C.bg}`,
                display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', borderRadius: k === 'sys' ? '16px 0 0 16px' : 0}}>
                {w > label.length * 22 + 10 && <span style={{fontSize: 22, fontWeight: 800, color: C.dark, whiteSpace: 'nowrap'}}>{label}</span>}
              </div>
            );
          })}
          {[50, 100, 150, 200].map((v) => (
            <div key={v} style={{position: 'absolute', left: X0 + px(v), top: BAR_Y + 104, transform: 'translateX(-50%)', fontFamily: MONO,
              fontSize: 17, color: v === 200 ? C.red : C.faint}}>{v === 200 ? '上限 200K' : `${v}K`}</div>
          ))}
        </div>
      )}
      <Svg style={{opacity: show}}>
        <Burst x={segX('res') + px(seg.res)} y={BAR_Y + 45} at={at(2, 0.08)} color={C.violet} n={30} dist={220} seed={3} />
        <Shock x={segX('hist') + px(seg.hist) / 2} y={BAR_Y + 45} at={at(2, 0.4)} color={C.cyan} r1={300} />
        <Burst x={segX('rag')} y={BAR_Y + 45} at={at(2, 0.7)} color={C.lime} n={22} dist={160} seed={7} />
      </Svg>
      <Pop from={at(1, 0.86)} to={at(2, 0.1)} x={960} y={BAR_Y - 70} fx="slam">
        <Pill color={C.red} solid size={28}>⚠ 快要溢出</Pill>
      </Pop>
      {tech.map(([t, sub, c, f], i) => (
        <Block key={t} x={560 + i * 400} y={760} w={350} h={150} from={at(2, 0) + i * 4} to={at(3, 0.02)} title={t} sub={sub} color={c}
          hl={curTech === i ? 1 : 0} size={34} fx="rise" />
      ))}
      <Pop from={at(2, 0.1)} to={at(2, 0.34)} x={segX('res') + px(seg.res) / 2} y={BAR_Y + 150} fx="drop">
        <span style={{fontFamily: MONO, fontSize: 20, color: C.violet, fontWeight: 700}}>✂ … 省略 4,812 行 …</span>
      </Pop>
      <Svg>
        <Comet pts={[[1360, 690], [segX('rag') + 20, BAR_Y + 90]]} from={at(2, 0.62)} len={14} color={C.lime} />
      </Svg>

      <Block x={360} y={500} w={300} h={170} from={mem + 2} title="会话 1" sub="今天" color={C.faint} size={36} fx="left" />
      <Code x={960} y={500} w={540} from={mem + 10} lines={['# 项目记忆', '- 包管理用 pnpm', '- 提交前先跑测试', '- 回答使用中文']}
        title="AGENTS.md" size={24} fx="zoom" hl={frame > at(3, 0.32) && frame < at(3, 0.6) ? [1, 2, 3] : []} hlColor={C.gold} />
      <Block x={1560} y={500} w={300} h={170} from={at(3, 0.55)} title="会话 2" sub="明天 · 新开始" color={C.gold} size={36} fx="right"
        hl={Math.min(prog(frame, at(3, 0.78), 8), 1 - prog(frame, at(3, 0.95), 12))} />
      <Svg>
        <Wire pts={[[510, 500], [690, 500]]} from={at(3, 0.22)} len={12} color={C.gold} flow />
        <Wire pts={[[1230, 500], [1410, 500]]} from={at(3, 0.66)} len={12} color={C.gold} flow />
        <Burst x={1560} y={500} at={at(3, 0.78)} color={C.gold} n={30} dist={240} seed={13} />
        <Shock x={1560} y={500} at={at(3, 0.78)} color={C.gold} r1={320} />
      </Svg>
      <Packet pts={[[440, 500], [740, 500]]} from={at(3, 0.25)} len={22} color={C.gold} tag="写入" />
      <Packet pts={[[1180, 500], [1480, 500]]} from={at(3, 0.68)} len={22} color={C.gold} tag="启动时注入" />
      <Pop from={at(3, 0.8)} x={960} y={760} fx="rise">
        <span style={{fontSize: 30, fontWeight: 800, color: C.ink}}>记忆跨会话保留</span>
      </Pop>
    </AbsoluteFill>
  );
};
