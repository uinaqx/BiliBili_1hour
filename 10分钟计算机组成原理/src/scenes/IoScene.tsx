import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, MONO, SHADOW, tint} from '../theme';
import {P, clamp, ip, pointAt, useScene, vis} from '../anim';
import {Block, Label, Pill, Pop, Svg, Wire} from '../kit';

const Bar: React.FC<{x: number; y: number; w: number; segs: [number, number, string, string?][]; progress: number; h?: number}> =
  ({x, y, w, segs, progress, h = 54}) => (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, transform: 'translateY(-50%)', borderRadius: 16, background: '#fff',
      boxShadow: SHADOW, overflow: 'hidden'}}>
      {segs.map(([a, b, col, text], i) => {
        const r = Math.min(b, progress);
        if (r <= a) return null;
        return (
          <div key={i} style={{position: 'absolute', left: a * w, width: (r - a) * w, top: 0, bottom: 0, background: col, color: '#fff',
            fontSize: 22, fontWeight: 650, display: 'flex', alignItems: 'center', justifyContent: 'center', whiteSpace: 'nowrap', overflow: 'hidden'}}>
            {text}
          </div>
        );
      })}
    </div>
  );

/** Beat 0: programmed polling. */
const Polling: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(0, 0), end = at(1, 0);
  const o = vis(frame, s, end);
  if (o <= 0) return null;
  const t0 = at(0, 0.3);
  const period = 40;
  const ph = frame >= t0 ? ((frame - t0) % period) / period : -1;
  const p = ip(frame, at(0, 0.3), at(0, 0.9) - at(0, 0.3));
  const segs: [number, number, string, string?][] = [];
  for (let i = 0; i < 14; i++) segs.push([i * 0.06, i * 0.06 + 0.05, tint(C.orange, 0.85)]);
  segs.push([0.86, 1, C.blue, '传送']);
  return (
    <AbsoluteFill style={{opacity: o}}>
      <Svg>
        <line x1={500} y1={330} x2={1420} y2={330} stroke={C.line} strokeWidth={3} strokeDasharray="8 10" />
      </Svg>
      <Block x={380} y={330} w={240} h={110} from={s + 4} title="CPU" />
      <Block x={1540} y={330} w={240} h={110} from={s + 8} title="外设" sub="打印机" color={C.orange} hl={p >= 0.86 ? 1 : 0} />
      {ph >= 0 && p < 0.86 && (() => {
        const go = ph < 0.5, t = go ? ph * 2 : (ph - 0.5) * 2;
        const x = go ? 520 + 880 * t : 1400 - 880 * t;
        return (
          <div style={{position: 'absolute', left: x, top: go ? 300 : 360, transform: 'translate(-50%,-50%)'}}>
            <Pill solid color={go ? C.ink2 : C.orange} size={20}>{go ? '好了吗？' : '还没有'}</Pill>
          </div>
        );
      })()}
      <Label x={340} y={600} from={s + 10} anchor="right" size={24} weight={650} color={C.ink2}>CPU 时间</Label>
      <Bar x={380} y={600} w={1160} segs={segs} progress={p} />
      <Label x={380 + 0.42 * 1160} y={548} from={at(0, 0.4)} size={22} weight={650} color={C.orange}>反复查询、等待</Label>
      <Pop from={at(0, 0.7)} x={960} y={760}><Pill color={C.red} size={26}>CPU 大部分时间都在空等</Pill></Pop>
    </AbsoluteFill>
  );
};

/** Beat 1: interrupt request. */
const Interrupt: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(1, 0), end = at(2, 0);
  const o = vis(frame, s, end);
  if (o <= 0) return null;
  const p = ip(frame, at(1, 0.1), at(1, 0.9) - at(1, 0.1));
  const ready = 0.62;
  return (
    <AbsoluteFill style={{opacity: o}}>
      <Label x={340} y={420} from={s + 4} anchor="right" size={24} weight={650} color={C.ink2}>CPU</Label>
      <Label x={340} y={640} from={s + 6} anchor="right" size={24} weight={650} color={C.ink2}>外设</Label>
      <Bar x={380} y={420} w={1160} segs={[[0, ready, C.blue, '执行其他程序'], [ready, 0.8, C.green, '处理中断'], [0.8, 1, C.blue, '继续执行']]} progress={p} />
      <Bar x={380} y={640} w={1160} segs={[[0, ready, '#c7c7cc', '准备数据'], [ready, 1, C.green, '就绪']]} progress={p} />
      <Svg>
        <Wire pts={[[380 + 1160 * ready, 610], [380 + 1160 * ready, 452]]} from={at(1, 0.1) + (at(1, 0.9) - at(1, 0.1)) * ready} len={10} color={C.orange} w={5} />
      </Svg>
      <Label x={380 + 1160 * ready + 20} y={530} from={at(1, 0.1) + (at(1, 0.9) - at(1, 0.1)) * ready + 6} anchor="left" size={26} weight={700}
        color={C.orange}>中断请求 INTR</Label>
      <Pop from={s + 10} x={960} y={250}><Pill color={C.blue} size={26}>CPU 不用等，设备好了会“喊”它</Pill></Pop>
    </AbsoluteFill>
  );
};

const STEPS = ['执行完当前指令', '保存断点', '保存现场', '中断服务程序', '恢复现场', '返回断点'];
const FLOW: P[] = [[300, 600], [760, 600], [840, 760], [1240, 760], [1320, 600], [1640, 600]];

/** Beat 2: interrupt handling sequence. */
const Handling: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(2, 0), end = at(3, 0);
  const o = vis(frame, s, end);
  if (o <= 0) return null;
  const p = ip(frame, at(2, 0.08), at(2, 0.92) - at(2, 0.08));
  const step = Math.min(5, Math.floor(p * 6));
  const {p: dot} = pointAt(FLOW, p);
  return (
    <AbsoluteFill style={{opacity: o}}>
      <div style={{position: 'absolute', left: 960, top: 300, transform: 'translate(-50%,-50%)', display: 'flex', alignItems: 'center', gap: 10}}>
        {STEPS.map((t, i) => (
          <React.Fragment key={t}>
            <span style={{padding: '12px 20px', borderRadius: 16, fontSize: 23, fontWeight: 650, whiteSpace: 'nowrap', boxShadow: SHADOW,
              background: i === step ? (i === 3 ? C.green : C.blue) : '#fff', color: i === step ? '#fff' : i < step ? C.ink2 : C.faint,
              opacity: vis(frame, s + 4 + i * 4)}}>{t}</span>
            {i < 5 && <span style={{color: C.faint, fontSize: 22}}>›</span>}
          </React.Fragment>
        ))}
      </div>
      <Svg>
        <polyline points={FLOW.slice(0, 2).map((v) => v.join(',')).join(' ')} fill="none" stroke={tint(C.blue, 0.5)} strokeWidth={6} strokeLinecap="round" />
        <polyline points={FLOW.slice(1, 5).map((v) => v.join(',')).join(' ')} fill="none" stroke={tint(C.green, 0.6)} strokeWidth={6} strokeLinecap="round"
          strokeLinejoin="round" />
        <polyline points={FLOW.slice(4).map((v) => v.join(',')).join(' ')} fill="none" stroke={tint(C.blue, 0.5)} strokeWidth={6} strokeLinecap="round" />
        <circle cx={dot[0]} cy={dot[1]} r={14} fill={p > 0.33 && p < 0.67 ? C.green : C.blue} />
      </Svg>
      <Label x={530} y={560} from={s + 8} size={22} weight={650} color={C.blue}>主程序</Label>
      <Label x={760} y={560} from={s + 10} size={20} weight={650} color={C.orange}>断点</Label>
      <Label x={1040} y={810} from={s + 12} size={22} weight={650} color={C.green}>中断服务程序</Label>
      <Label x={1480} y={560} from={s + 14} size={22} weight={650} color={C.blue}>回到断点继续</Label>
    </AbsoluteFill>
  );
};

const NEST: P[] = [[320, 760], [560, 760], [560, 600], [860, 600], [860, 440], [1160, 440], [1160, 600], [1380, 600], [1380, 760], [1640, 760]];

/** Beat 3: priorities and nesting. */
const Nesting: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(3, 0), end = at(4, 0);
  const o = vis(frame, s, end);
  if (o <= 0) return null;
  const p = ip(frame, at(3, 0.08), at(3, 0.9) - at(3, 0.08));
  const {p: dot} = pointAt(NEST, p);
  const levels: [string, number, string][] = [['主程序', 760, C.blue], ['低优先级中断', 600, C.orange], ['高优先级中断', 440, C.red]];
  return (
    <AbsoluteFill style={{opacity: o}}>
      <Svg>
        {levels.map(([, y]) => <line key={y} x1={320} y1={y} x2={1640} y2={y} stroke={C.hair} strokeWidth={2} strokeDasharray="6 10" />)}
        <Wire pts={NEST} from={at(3, 0.08)} len={at(3, 0.9) - at(3, 0.08)} color={C.ink2} w={5} head={false} />
        <circle cx={dot[0]} cy={dot[1]} r={13} fill={dot[1] < 500 ? C.red : dot[1] < 700 ? C.orange : C.blue} />
      </Svg>
      {levels.map(([n, y, col], i) => <Label key={n} x={300} y={y} from={s + 4 + i * 4} anchor="right" size={22} weight={650} color={col}>{n}</Label>)}
      <Label x={560} y={810} from={at(3, 0.15)} size={20} color={C.orange} weight={650}>低级中断到来</Label>
      <Label x={860} y={660} from={at(3, 0.35)} size={20} color={C.red} weight={650}>更高级的打断它</Label>
      <Label x={1160} y={390} from={at(3, 0.6)} size={20} color={C.muted} weight={650}>处理完，逐层返回</Label>
      <Pop from={at(3, 0.2)} x={1500} y={260}><Pill solid color={C.red} size={24}>优先级：高 &gt; 低</Pill></Pop>
      <Pop from={at(3, 0.5)} x={560} y={260}><Pill color={C.ink2} size={24}>中断嵌套</Pill></Pop>
    </AbsoluteFill>
  );
};

/** Beat 4: DMA. */
const Dma: React.FC = () => {
  const {frame, at} = useScene();
  const s = at(4, 0);
  if (frame < s - 2) return null;
  const BUS = 520;
  const req = at(4, 0.15), yield_ = at(4, 0.25), x0 = at(4, 0.3), x1 = at(4, 0.8), done = at(4, 0.85);
  const moved = Math.round(512 * clamp((frame - x0) / (x1 - x0)));
  const cpuDim = frame >= yield_ && frame < done + 10;
  const path: P[] = [[1560, 384], [1560, BUS], [820, BUS], [820, 384]];
  return (
    <AbsoluteFill>
      <Svg>
        <line x1={240} y1={BUS} x2={1700} y2={BUS} stroke={C.line} strokeWidth={10} strokeLinecap="round" />
        {[380, 820, 1560].map((x) => <line key={x} x1={x} y1={384} x2={x} y2={BUS} stroke={C.line} strokeWidth={4} />)}
        <line x1={1180} y1={BUS} x2={1180} y2={666} stroke={C.line} strokeWidth={4} />
        <Wire pts={[[1070, 720], [300, 720], [300, 386]]} from={req} len={16} color={C.orange} dash="9 9" to={done} />
        <Wire pts={[[1070, 740], [320, 740], [320, 386]]} from={done} len={14} color={C.green} w={4} />
      </Svg>
      <div style={{opacity: cpuDim ? 0.35 : 1}}><Block x={380} y={330} w={240} h={104} from={s + 4} title="CPU" sub={cpuDim ? '让出总线，去做别的' : '处理器'} /></div>
      <Block x={820} y={330} w={240} h={104} from={s + 8} title="主存" color={C.purple} hl={frame >= x0 && frame < x1 ? 1 : 0} />
      <Block x={1560} y={330} w={240} h={104} from={s + 12} title="磁盘" color={C.teal} hl={frame >= x0 && frame < x1 ? 1 : 0} />
      <Block x={1180} y={720} w={240} h={104} from={s + 16} title="DMA 控制器" size={26} color={C.orange} hl={frame >= req && frame < done ? 1 : 0} />
      <Label x={680} y={700} from={req + 4} to={done} size={20} weight={650} color={C.orange}>请求总线</Label>
      {Array.from({length: 9}, (_, k) => {
        const t0 = x0 + k * ((x1 - x0 - 40) / 8);
        const t = clamp((frame - t0) / 40);
        if (t <= 0 || t >= 1) return null;
        const {p} = pointAt(path, t);
        return (
          <div key={k} style={{position: 'absolute', left: p[0], top: p[1], transform: 'translate(-50%,-50%)', width: 34, height: 24, borderRadius: 7,
            background: C.teal, boxShadow: `0 4px 12px ${tint(C.teal, 0.5)}`}} />
        );
      })}
      <Pop from={x0} x={1190} y={440}>
        <div style={{fontFamily: MONO, fontSize: 26, color: C.ink2, background: '#fff', padding: '8px 18px', borderRadius: 12, boxShadow: SHADOW}}>
          已传送 <b style={{color: C.teal}}>{moved}</b> / 512 字
        </div>
      </Pop>
      <Label x={680} y={790} from={done + 4} size={22} weight={700} color={C.green}>整块传完，只中断一次</Label>
      <Pop from={at(4, 0.9)} x={1260} y={850}>
        <div style={{display: 'flex', gap: 12}}>
          <Pill color={C.ink2} size={20}>查询：CPU 一直等</Pill><Pill color={C.ink2} size={20}>中断：每次都要 CPU</Pill><Pill solid color={C.teal} size={20}>DMA：CPU 几乎不参与</Pill>
        </div>
      </Pop>
    </AbsoluteFill>
  );
};

export const IoScene: React.FC = () => (
  <AbsoluteFill>
    <Polling />
    <Interrupt />
    <Handling />
    <Nesting />
    <Dma />
  </AbsoluteFill>
);
