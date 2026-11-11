import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Block, Label, Ring, Stage} from '../three';
import {camPath, clamp, easeOut, ip, lerp, prog, useScene} from '../anim';
import {C, FONT, MONO} from '../theme';

const ITEMS = [
  {t: '内核 · 系统调用', k: '用户态 / 内核态 · 陷入', c: C.cyan, beat: 0, f: 0.12},
  {t: '进程 · 线程', k: '进程分配资源 · 线程被调度', c: C.pink, beat: 0, f: 0.55},
  {t: 'CPU 调度', k: 'FCFS · SJF · RR · 多级反馈', c: C.gold, beat: 1, f: 0.06},
  {t: '同步 · 互斥', k: '互斥锁 · 信号量 P / V', c: C.cyan, beat: 1, f: 0.2},
  {t: '死锁', k: '四条件 · 预防 · 避免 · 检测', c: C.red, beat: 1, f: 0.34},
  {t: '内存管理', k: '分页 · 页表 · 碎片', c: C.pink, beat: 1, f: 0.5},
  {t: '虚拟内存', k: '缺页 · TLB · LRU', c: C.violet, beat: 1, f: 0.66},
  {t: '文件系统', k: 'inode · 日志', c: C.gold, beat: 2, f: 0.05},
  {t: '输入输出', k: '驱动 · 中断 · DMA', c: C.cyan, beat: 2, f: 0.2},
];
const COLS = [-7.2, 0, 7.2];
const ROWS = [2.8, 0, -2.8];

export const Outro: React.FC = () => {
  const {frame, at} = useScene();

  const dim = 1 - 0.985 * ip(frame, at(2, 0.6), 24);
  const final = ip(frame, at(2, 0.64), 36, easeOut);

  const cam = camPath(frame, [
    [0, [0, 3, 30], [0, 0, 0]],
    [at(0, 0.5), [-3, 3, 25], [0, 0, 0]],
    [at(1, 0.5), [3, 2, 24], [0, 0, 0]],
    [at(2, 0.5), [0, 2, 26], [0, 0, 0]],
    [at(2, 1) + 40, [0, 1, 31], [0, 0, 0]],
  ]);

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={-6} bloom={1.2}>
        {ITEMS.map((it, i) => {
          const x = COLS[i % 3], y = ROWS[Math.floor(i / 3)];
          const t = at(it.beat, it.f);
          const o = ip(frame, t, 18) * dim;
          const pop = ip(frame, t, 22, easeOut);
          const flash = Math.max(0, 1 - prog(frame, t, 34));
          return (
            <group key={it.t}>
              <Block position={[x, y + (1 - pop) * 2.5, 0]} size={[6.0, 2.3, 1.2]} color={C.panel2} edge={it.c} opacity={o} glow={2 + flash * 1.5} emissive={0.25 + flash * 0.5}
                scale={0.85 + 0.15 * pop} />
              <Label text={it.t} position={[x, y + 0.42 + (1 - pop) * 2.5, 0.7]} size={0.56} bold opacity={o} depthTest={false} />
              <Label text={it.k} position={[x, y - 0.5 + (1 - pop) * 2.5, 0.7]} size={0.28} color={C.muted} opacity={o} depthTest={false} />
              <Label text={String(i + 1).padStart(2, '0')} position={[x - 2.5, y + 0.8 + (1 - pop) * 2.5, 0.7]} size={0.3} mono bold color={it.c} opacity={o} depthTest={false} />
              {flash > 0 && flash < 1 && <Ring position={[x, y, 0.7]} radius={2.6 + (1 - flash) * 1.6} width={0.06} color={it.c} opacity={flash * 0.7} />}
            </group>
          );
        })}
        {final > 0 && <Ring position={[0, 0, 0]} radius={lerp(0, 22, final)} width={0.1} color={C.cyan} opacity={(1 - final) * 0.8} rotation={[-Math.PI / 2, 0, 0]} />}
      </Stage>

      {final > 0.01 && (
        <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', fontFamily: FONT}}>
          <div style={{opacity: final, transform: `translateY(${(1 - final) * 30}px)`, textAlign: 'center'}}>
            <div style={{fontFamily: MONO, fontSize: 28, letterSpacing: 12, color: C.cyan, marginBottom: 16}}>OPERATING SYSTEM</div>
            <div style={{fontSize: 120, fontWeight: 800, letterSpacing: 18, color: C.text, textShadow: `0 0 40px ${C.cyan}66, 0 0 90px ${C.pink}44`}}>
              {['高效', '公平', '安全'].map((w, i) => (
                <span key={w} style={{display: 'inline-block', margin: '0 22px', opacity: clamp((final - 0.15 - i * 0.18) * 4),
                  color: [C.cyan, C.pink, C.gold][i], textShadow: `0 0 34px ${[C.cyan, C.pink, C.gold][i]}88`}}>{w}</span>
              ))}
            </div>
            <div style={{marginTop: 22, fontSize: 34, color: C.muted, letterSpacing: 8}}>在有限的资源上，让众多程序共享 · 感谢观看</div>
          </div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
