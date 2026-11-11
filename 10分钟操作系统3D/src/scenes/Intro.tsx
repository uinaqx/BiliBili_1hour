import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Block, CurveArrow, Label, Orb, Ring, Stage, V3} from '../three';
import {bounce, camPath, clamp, easeInOut, easeOut, ip, lerp, prog, useScene, vis} from '../anim';
import {C, FONT, MONO} from '../theme';

const TOPICS = ['系统调用', '进程', '调度', '同步', '死锁', '内存', '虚拟内存', '文件', '设备'];
const APPS: {name: string; color: string; x: number}[] = [
  {name: '浏览器', color: C.cyan, x: -3.6},
  {name: '音乐', color: C.pink, x: 0},
  {name: '编辑器', color: C.gold, x: 3.6},
];
const HW = ['CPU', '内存', '硬盘', '外设'];

const ringPos = (k: number, spin: number): V3 => {
  const a = (k / TOPICS.length) * Math.PI * 2 + spin;
  return [Math.cos(a) * 8.2, Math.sin(a) * 3.0, Math.sin(a) * 2.6];
};

export const Intro: React.FC = () => {
  const {frame, at, b} = useScene();

  const layersOut = 1 - prog(frame, at(2, 0.02), 22);
  const hwIn = vis(frame, at(0, 0.62), 1e9, 18) * layersOut;
  const osDrop = ip(frame, at(1, 0.04), 30, bounce);
  const osOp = ip(frame, at(1, 0.04), 8) * layersOut;
  const spin = (frame - at(2, 0.1)) * 0.004;

  const cam = camPath(frame, [
    [0, [0, 6, 30], [0, 0.5, 0]],
    [b(0), [5, 5, 24], [0, 0.8, 0]],
    [at(1, 0.1), [-6, 4, 22], [0, 0, 0]],
    [at(1, 0.9), [6, 4.5, 22], [0, 0, 0]],
    [at(2, 0.2), [0, 3, 25], [0, 0, 0]],
    [at(2, 1) + 40, [0, 4, 23], [0, 0, 0]],
  ]);

  const titleIn = ip(frame, 18, 36, easeOut);
  const titleOut = prog(frame, at(0, 0.5), 24);
  const title = titleIn * (1 - titleOut);

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={null} bloom={1.3} fog={[30, 120]}>
        {/* 应用程序：同时运行，各自浮动，互不碰撞 */}
        {APPS.map((a, k) => {
          const t = at(0, 0.3 + k * 0.1);
          const o = ip(frame, t, 20, easeOut) * layersOut;
          const y = 4.3 + Math.sin(frame * 0.05 + k * 2) * 0.22 + (1 - ip(frame, t, 26, bounce)) * 4;
          return (
            <group key={a.name}>
              <Block position={[a.x, y, 0]} size={[2.6, 1.5, 2.2]} color={C.panel2} edge={a.color} opacity={o} glow={2} />
              <Label text={a.name} position={[a.x, y, 1.3]} size={0.42} bold opacity={o} depthTest={false} />
            </group>
          );
        })}
        <Label text="应用程序" position={[0, 6.2, 0]} size={0.5} bold color={C.cyan} opacity={vis(frame, at(0, 0.5)) * layersOut} />

        {/* 硬件 */}
        <Block position={[0, -2.8, 0]} size={[12, 0.5, 6]} color={C.panel} edge={C.violet} opacity={hwIn} />
        {HW.map((n, k) => {
          const t = at(0, 0.7 + k * 0.05);
          const o = ip(frame, t, 16) * layersOut;
          return (
            <group key={n}>
              <Block position={[-4.2 + k * 2.8, -2.0, 0]} size={[2.1, 1.0, 2.1]} color={C.panel2} edge={C.violet} opacity={o} glow={1.8} />
              <Label text={n} position={[-4.2 + k * 2.8, -2.0, 1.2]} size={0.38} bold opacity={o} depthTest={false} />
            </group>
          );
        })}
        <Label text="硬件" position={[0, -3.8, 2.4]} size={0.5} bold color={C.violet} opacity={hwIn} />

        {/* 操作系统：落在中间 */}
        <Block position={[0, lerp(8, 1.2, osDrop), 0]} size={[12, 0.6, 6]} color="#3a1b3e" edge={C.pink} opacity={osOp} glow={2.4} emissive={0.4} />
        <Label text="操作系统  Operating System" position={[0, lerp(8, 1.2, osDrop), 3.2]} size={0.5} bold mono color={C.pink} opacity={osOp}
          depthTest={false} />

        {/* 向下管理，向上提供接口 */}
        {[-5.3, -4.4, 4.4, 5.3].map((x, k) => (
          <CurveArrow key={x} from={k < 2 ? [x, 0.7, 2.2] : [x, 1.9, 2.2]} to={k < 2 ? [x, -0.9, 2.2] : [x, 3.3, 2.2]} color={k < 2 ? C.violet : C.cyan}
            radius={0.05} progress={ip(frame, at(1, 0.4 + (k % 2) * 0.08), 20)} opacity={layersOut} />
        ))}
        <Label text="管理" position={[-7.2, -0.1, 2.2]} size={0.38} color={C.violet} opacity={vis(frame, at(1, 0.5)) * layersOut} />
        <Label text="接口" position={[7.2, 2.6, 2.2]} size={0.38} color={C.cyan} opacity={vis(frame, at(1, 0.55)) * layersOut} />

        {/* 九个话题 */}
        <Orb position={[0, 0, 0]} radius={1.1} color={C.pink} glow={1.5} opacity={ip(frame, at(2, 0.1), 20)} scale={ip(frame, at(2, 0.1), 24, easeOut)} />
        <Label text="OS" position={[0, 0, 1.3]} size={0.7} bold mono opacity={ip(frame, at(2, 0.14), 16)} depthTest={false} />
        {TOPICS.map((n, k) => {
          const t = at(2, 0.28 + k * 0.06);
          const o = ip(frame, t, 12);
          const p = ringPos(k, spin);
          const col = k % 3 === 0 ? C.cyan : k % 3 === 1 ? C.pink : C.gold;
          const pl = 1 - prog(frame, t, 26);
          return (
            <group key={n}>
              <Orb position={p} radius={0.34} color={col} opacity={o} scale={o} />
              <Label text={n} position={[p[0], p[1] + 0.95, p[2]]} size={0.52} bold color={col} opacity={o} glow={1} />
              {pl > 0 && pl < 1 && <Ring position={p} radius={0.6 + (1 - pl) * 2} width={0.06} color={col} opacity={pl} />}
            </group>
          );
        })}
        {frame > at(2, 0.1) && frame < at(2, 0.1) + 40 && (
          <Ring position={[0, 0, 0]} radius={ip(frame, at(2, 0.1), 40, easeOut) * 14} width={0.08} color={C.cyan}
            opacity={1 - prog(frame, at(2, 0.1), 40)} rotation={[-Math.PI / 2, 0, 0]} />
        )}
      </Stage>

      {title > 0 && (
        <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', fontFamily: FONT}}>
          <div style={{opacity: title, transform: `translateY(${(1 - titleIn) * 30 - titleOut * 60}px) scale(${1 + titleOut * 0.08})`, textAlign: 'center'}}>
            <div style={{fontFamily: MONO, fontSize: 30, letterSpacing: 14, color: C.cyan, marginBottom: 18}}>OPERATING SYSTEM</div>
            <div style={{fontSize: 150, fontWeight: 800, letterSpacing: 26, color: C.text, textShadow: `0 0 40px ${C.cyan}66, 0 0 90px ${C.pink}44`}}>
              {'操作系统'.split('').map((ch, i) => (
                <span key={i} style={{opacity: clamp((frame - 22 - i * 6) / 14), display: 'inline-block',
                  transform: `translateY(${(1 - easeInOut(clamp((frame - 22 - i * 6) / 14))) * 26}px)`}}>{ch}</span>
              ))}
            </div>
            <div style={{marginTop: 18, fontSize: 36, color: C.muted, letterSpacing: 8}}>十分钟 · 3D 动画速览</div>
          </div>
        </AbsoluteFill>
      )}
    </AbsoluteFill>
  );
};
