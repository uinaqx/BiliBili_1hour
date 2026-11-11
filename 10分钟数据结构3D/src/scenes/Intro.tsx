import React, {useLayoutEffect, useMemo} from 'react';
import * as THREE from 'three';
import {AbsoluteFill} from 'remotion';
import {Label, Ring, Stage} from '../three';
import {camPath, clamp, easeInOut, easeOut, ip, lerp, prog, rand, useScene} from '../anim';
import {C, FONT, MONO} from '../theme';

const N = 4096;
const NAMES = ['数组', '链表', '栈', '队列', '哈希表', '树', '堆', '图'];
const RING_R = 9.5;

let dotTexture: THREE.Texture | null = null;
const dot = () => {
  if (dotTexture) return dotTexture;
  const cv = document.createElement('canvas'); cv.width = cv.height = 64;
  const g = cv.getContext('2d')!;
  const grd = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  grd.addColorStop(0, 'rgba(255,255,255,1)'); grd.addColorStop(0.35, 'rgba(255,255,255,0.55)'); grd.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = grd; g.fillRect(0, 0, 64, 64);
  dotTexture = new THREE.CanvasTexture(cv);
  return dotTexture;
};

const ringPos = (k: number, spin: number): [number, number, number] => {
  const a = (k / 8) * Math.PI * 2 + spin - Math.PI / 2;
  return [Math.cos(a) * RING_R, Math.sin(a) * 3.6, Math.sin(a) * 3.2];
};

export const Intro: React.FC = () => {
  const {frame, at, b} = useScene();

  const seed = useMemo(() => {
    const colors = new Float32Array(N * 3);
    const pal = [C.muted, C.text, C.orange, C.green].map((c) => new THREE.Color(c));
    for (let i = 0; i < N; i++) {
      const r = rand(i * 3.1);
      const c = pal[r < 0.42 ? 0 : r < 0.6 ? 1 : r < 0.82 ? 2 : 3];
      const k = 0.9 + rand(i + 0.5) * 1.3;
      colors[i * 3] = c.r * k; colors[i * 3 + 1] = c.g * k; colors[i * 3 + 2] = c.b * k;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(N * 3), 3));
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    return geo;
  }, []);

  const toLattice = at(1, 0.12), toRing = at(2, 0.18);
  const spin = frame * 0.004;
  const ringSpin = (frame - toRing) * 0.0025;

  useLayoutEffect(() => {
    const p = seed.getAttribute('position') as THREE.BufferAttribute;
    const arr = p.array as Float32Array;
    for (let i = 0; i < N; i++) {
      // galaxy
      const arm = i % 3, r = 0.6 + Math.pow(rand(i + 1), 0.7) * 13;
      const ang = r * 0.42 + (arm * Math.PI * 2) / 3 + (rand(i + 2) - 0.5) * 0.7 + spin * (1.6 - r / 13);
      const gx = Math.cos(ang) * r, gz = Math.sin(ang) * r, gy = (rand(i + 3) - 0.5) * (1.6 - r / 13) * 1.4;
      const intro = ip(frame, rand(i + 4) * 30, 50, easeOut);
      const sx = (rand(i + 5) - 0.5) * 120, sy = (rand(i + 6) - 0.5) * 70, sz = (rand(i + 7) - 0.5) * 120;
      let x = lerp(sx, gx, intro), y = lerp(sy, gy, intro), z = lerp(sz, gz, intro);
      // lattice 16^3
      const lx = ((i % 16) - 7.5) * 0.62, ly = ((Math.floor(i / 16) % 16) - 7.5) * 0.62, lz = (Math.floor(i / 256) - 7.5) * 0.62;
      const d = Math.sqrt(lx * lx + ly * ly + lz * lz);
      const tl = ip(frame, toLattice + d * 3.2, 34);
      const rot = (frame - toLattice) * 0.006;
      const rx = lx * Math.cos(rot) - lz * Math.sin(rot), rz = lx * Math.sin(rot) + lz * Math.cos(rot);
      x = lerp(x, rx, tl); y = lerp(y, ly, tl); z = lerp(z, rz, tl);
      // ring of 8 clusters
      const k = i % 8;
      const c = ringPos(k, ringSpin);
      const u = rand(i + 8) * Math.PI * 2, v = Math.acos(2 * rand(i + 9) - 1), rr = Math.cbrt(rand(i + 10)) * 1.05;
      const tr = ip(frame, toRing + k * 3 + rand(i + 11) * 14, 40);
      x = lerp(x, c[0] + rr * Math.sin(v) * Math.cos(u + frame * 0.02), tr);
      y = lerp(y, c[1] + rr * Math.cos(v), tr);
      z = lerp(z, c[2] + rr * Math.sin(v) * Math.sin(u + frame * 0.02), tr);
      arr[i * 3] = x; arr[i * 3 + 1] = y; arr[i * 3 + 2] = z;
    }
    p.needsUpdate = true;
  });

  const cam = camPath(frame, [
    [0, [0, 9, 34], [0, 0, 0]],
    [b(0), [6, 6, 24], [0, 0, 0]],
    [at(1, 0.1), [-4, 5, 22], [0, 0, 0]],
    [at(1, 0.9), [9, 7, 17], [0, 0, 0]],
    [at(2, 0.2), [0, 7, 25], [0, 0, 0]],
    [at(2, 1) + 40, [0, 5.5, 23], [0, 0.4, 0]],
  ]);

  const nameT = (k: number) => at(2, 0.42 + k * 0.07);
  const titleIn = ip(frame, 18, 36, easeOut);
  const titleOut = prog(frame, at(0, 0.55), 24);
  const title = titleIn * (1 - titleOut);

  return (
    <AbsoluteFill>
      <Stage pos={cam.pos} target={cam.target} floor={null} bloom={1.35} fog={[30, 120]}>
        <points geometry={seed}>
          <pointsMaterial size={0.22} map={dot()} vertexColors transparent depthWrite={false} blending={THREE.AdditiveBlending}
            sizeAttenuation toneMapped={false} />
        </points>
        {frame > toLattice && frame < toRing + 30 && (
          <Ring position={[0, 0, 0]} radius={lerp(0, 18, ip(frame, toLattice + 10, 40, easeOut))} width={0.08} color={C.orange}
            opacity={1 - prog(frame, toLattice + 10, 40)} rotation={[-Math.PI / 2, 0, 0]} />
        )}
        {NAMES.map((n, k) => {
          const t = nameT(k);
          const o = ip(frame, t, 12);
          const pulse = 1 - prog(frame, t, 24);
          const c = ringPos(k, ringSpin);
          return (
            <group key={n}>
              <Label text={n} position={[c[0], c[1] + 1.75, c[2]]} size={0.7} bold color={k % 2 ? C.green : C.orange} opacity={o} glow={1} />
              {pulse < 1 && pulse > 0 && <Ring position={c} radius={1.2 + (1 - pulse) * 2.4} width={0.07} color={k % 2 ? C.green : C.orange}
                opacity={pulse} />}
            </group>
          );
        })}
      </Stage>

      {title > 0 && (
        <AbsoluteFill style={{justifyContent: 'center', alignItems: 'center', fontFamily: FONT}}>
          <div style={{opacity: title, transform: `translateY(${(1 - titleIn) * 30 - titleOut * 60}px) scale(${1 + titleOut * 0.08})`, textAlign: 'center'}}>
            <div style={{fontFamily: MONO, fontSize: 30, letterSpacing: 14, color: C.orange, marginBottom: 18}}>DATA STRUCTURES</div>
            <div style={{fontSize: 150, fontWeight: 800, letterSpacing: 26, color: C.text, textShadow: `0 0 40px ${C.orange}66, 0 0 90px #ffba7833`}}>
              {'数据结构'.split('').map((ch, i) => (
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
