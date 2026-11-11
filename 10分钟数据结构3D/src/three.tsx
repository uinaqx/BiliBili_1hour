import React, {useLayoutEffect, useMemo} from 'react';
import * as THREE from 'three';
import {useThree} from '@react-three/fiber';
import {ThreeCanvas} from '@remotion/three';
import {EffectComposer, Bloom, Vignette} from '@react-three/postprocessing';
import {RoundedBoxGeometry} from 'three/examples/jsm/geometries/RoundedBoxGeometry.js';
import {useCurrentFrame} from 'remotion';
import {C, FONT, MONO} from './theme';
import {rand} from './anim';

export type V3 = [number, number, number];

const CameraRig: React.FC<{pos: V3; target: V3; fov: number}> = ({pos, target, fov}) => {
  const camera = useThree((s) => s.camera) as THREE.PerspectiveCamera;
  useLayoutEffect(() => {
    camera.position.set(...pos);
    camera.fov = fov;
    camera.near = 0.1;
    camera.far = 400;
    camera.updateProjectionMatrix();
    camera.lookAt(...target);
  });
  return null;
};

const starGeometry = (() => {
  const n = 2600, p = new Float32Array(n * 3), c = new Float32Array(n * 3);
  const tint = [new THREE.Color(C.muted), new THREE.Color(C.text), new THREE.Color(C.orange), new THREE.Color(C.green)];
  for (let i = 0; i < n; i++) {
    const r = 45 + rand(i) * 90, th = rand(i + 9000) * Math.PI * 2, ph = Math.acos(2 * rand(i + 19000) - 1);
    p[i * 3] = r * Math.sin(ph) * Math.cos(th);
    p[i * 3 + 1] = r * Math.cos(ph) * 0.7 + 10;
    p[i * 3 + 2] = r * Math.sin(ph) * Math.sin(th);
    const k = rand(i + 7) < 0.88 ? (rand(i + 3) < 0.6 ? 0 : 1) : rand(i + 5) < 0.5 ? 2 : 3;
    const b = 0.35 + rand(i + 11) * 0.65;
    c[i * 3] = tint[k].r * b; c[i * 3 + 1] = tint[k].g * b; c[i * 3 + 2] = tint[k].b * b;
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(p, 3));
  g.setAttribute('color', new THREE.BufferAttribute(c, 3));
  return g;
})();

const Stars: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <points geometry={starGeometry} rotation={[0, frame * 0.0006, 0]}>
      <pointsMaterial size={0.35} vertexColors sizeAttenuation transparent opacity={0.9} depthWrite={false} />
    </points>
  );
};

export const Stage: React.FC<{
  pos: V3; target?: V3; fov?: number; floor?: number | null; bloom?: number; fog?: [number, number];
  children: React.ReactNode;
}> = ({pos, target = [0, 0, 0], fov = 42, floor = -3, bloom = 1.1, fog = [22, 85], children}) => (
  <ThreeCanvas width={1920} height={1080} gl={{antialias: true}} style={{position: 'absolute', inset: 0}}>
    <color attach="background" args={[C.bg]} />
    <fog attach="fog" args={[C.bg, fog[0], fog[1]]} />
    <CameraRig pos={pos} target={target} fov={fov} />
    <ambientLight intensity={0.55} />
    <directionalLight position={[8, 14, 10]} intensity={1.6} color={C.text} />
    <pointLight position={[-10, 6, 6]} intensity={60} distance={40} color={C.orange} />
    <pointLight position={[10, -2, 8]} intensity={40} distance={40} color={C.green} />
    <Stars />
    {floor !== null && <gridHelper args={[160, 80, C.border, '#17263a']} position={[0, floor, 0]} />}
    {children}
    <EffectComposer multisampling={4}>
      <Bloom mipmapBlur luminanceThreshold={0.82} luminanceSmoothing={0.2} intensity={bloom} radius={0.75} />
      <Vignette eskil={false} offset={0.25} darkness={0.7} />
    </EffectComposer>
  </ThreeCanvas>
);

/** Camera on a gentle orbit, useful for 3D parallax. */
export const orbit = (frame: number, radius: number, height: number, speed = 0.0018, phase = 0, center: V3 = [0, 0, 0]): V3 => [
  center[0] + Math.sin(frame * speed + phase) * radius,
  center[1] + height,
  center[2] + Math.cos(frame * speed + phase) * radius,
];

const textureCache = new Map<string, {tex: THREE.CanvasTexture; aspect: number}>();
const makeText = (text: string, color: string, bold: boolean, mono: boolean, bg: string | null, border: string | null) => {
  const key = [text, color, bold, mono, bg, border].join('|');
  const hit = textureCache.get(key);
  if (hit) return hit;
  const px = 96, pad = bg ? 44 : 12;
  const cv = document.createElement('canvas');
  const ctx = cv.getContext('2d')!;
  const font = `${bold ? 700 : 500} ${px}px ${mono ? MONO : FONT}`;
  ctx.font = font;
  const w = Math.ceil(ctx.measureText(text).width) + pad * 2;
  const h = Math.ceil(px * 1.45) + (bg ? 24 : 0);
  cv.width = w; cv.height = h;
  ctx.font = font;
  if (bg) {
    ctx.fillStyle = bg;
    const r = h / 2.6;
    ctx.beginPath();
    ctx.roundRect(4, 4, w - 8, h - 8, r);
    ctx.fill();
    if (border) { ctx.lineWidth = 6; ctx.strokeStyle = border; ctx.stroke(); }
  }
  ctx.fillStyle = color;
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(text, w / 2, h / 2 + px * 0.04);
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.anisotropy = 8;
  const out = {tex, aspect: w / h};
  textureCache.set(key, out);
  return out;
};

/** Camera-facing text sprite. `size` is world-space height. */
export const Label: React.FC<{
  text: string; position: V3; size?: number; color?: string; opacity?: number; bold?: boolean; mono?: boolean;
  bg?: string | null; border?: string | null; glow?: number; depthTest?: boolean;
}> = ({text, position, size = 0.5, color = C.text, opacity = 1, bold = false, mono = false, bg = null, border = null, glow = 0.86, depthTest = true}) => {
  const {tex, aspect} = makeText(text, color, bold, mono, bg, border);
  if (opacity <= 0.001) return null;
  const h = bg ? size * 1.35 : size * 1.45;
  return (
    <sprite position={position} scale={[h * aspect, h, 1]} renderOrder={10}>
      <spriteMaterial map={tex} transparent opacity={opacity} depthWrite={false} depthTest={depthTest}
        color={new THREE.Color(glow, glow, glow)} toneMapped={false} />
    </sprite>
  );
};

/** A tube that grows along a quadratic curve from `from` to `to`, with an arrow head. */
export const CurveArrow: React.FC<{
  from: V3; to: V3; bend?: V3; progress?: number; color?: string; radius?: number; opacity?: number;
  head?: boolean; glow?: number; trimStart?: number; trimEnd?: number;
}> = ({from, to, bend = [0, 0, 0], progress = 1, color = C.muted, radius = 0.05, opacity = 1, head = true, glow = 1.4, trimStart = 0, trimEnd = 0}) => {
  const key = [...from, ...to, ...bend, progress.toFixed(3), radius, trimStart, trimEnd].join(',');
  const data = useMemo(() => {
    const a = new THREE.Vector3(...from), b = new THREE.Vector3(...to);
    const mid = a.clone().add(b).multiplyScalar(0.5).add(new THREE.Vector3(...bend));
    const curve = new THREE.QuadraticBezierCurve3(a, mid, b);
    const len = curve.getLength();
    const t0 = Math.min(0.45, trimStart / len), t1 = Math.max(0.55, 1 - trimEnd / len);
    const tEnd = t0 + (t1 - t0) * progress;
    if (tEnd - t0 < 0.01) return null;
    const pts: THREE.Vector3[] = [];
    const n = 24;
    for (let i = 0; i <= n; i++) pts.push(curve.getPoint(t0 + ((tEnd - t0) * i) / n));
    const headLen = radius * 6;
    const tip = curve.getPoint(tEnd);
    const tan = curve.getTangent(tEnd).normalize();
    const body = new THREE.CatmullRomCurve3(head ? pts.map((p, i) => (i === n ? p.clone().addScaledVector(tan, -headLen * 0.8) : p)) : pts);
    const geo = new THREE.TubeGeometry(body, 40, radius, 10, false);
    const q = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 1, 0), tan);
    const headPos = tip.clone().addScaledVector(tan, -headLen / 2);
    return {geo, q, headPos, headLen};
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);
  if (!data || opacity <= 0.001) return null;
  const col = new THREE.Color(color).multiplyScalar(glow);
  return (
    <group>
      <mesh geometry={data.geo}>
        <meshBasicMaterial color={col} transparent opacity={opacity} toneMapped={false} />
      </mesh>
      {head && (
        <mesh position={data.headPos} quaternion={data.q}>
          <coneGeometry args={[radius * 2.6, data.headLen, 16]} />
          <meshBasicMaterial color={col} transparent opacity={opacity} toneMapped={false} />
        </mesh>
      )}
    </group>
  );
};

const boxGeoCache = new Map<string, THREE.BufferGeometry>();
const roundedBox = (w: number, h: number, d: number, r: number) => {
  const k = [w, h, d, r].join(',');
  if (!boxGeoCache.has(k)) boxGeoCache.set(k, new RoundedBoxGeometry(w, h, d, 4, r));
  return boxGeoCache.get(k)!;
};
const edgeCache = new Map<string, THREE.EdgesGeometry>();
const edges = (w: number, h: number, d: number) => {
  const k = [w, h, d].join(',');
  if (!edgeCache.has(k)) edgeCache.set(k, new THREE.EdgesGeometry(new THREE.BoxGeometry(w, h, d)));
  return edgeCache.get(k)!;
};

/** Translucent rounded block with glowing edges. */
export const Block: React.FC<{
  position: V3; size?: V3; color?: string; edge?: string; opacity?: number; glow?: number; scale?: number;
  rotation?: V3; emissive?: number;
}> = ({position, size = [1.6, 1.6, 1.6], color = C.panel, edge = C.muted, opacity = 1, glow = 1.6, scale = 1, rotation = [0, 0, 0], emissive = 0.15}) => {
  if (opacity <= 0.001 || scale <= 0.001) return null;
  const [w, h, d] = size;
  return (
    <group position={position} scale={scale} rotation={rotation}>
      <mesh geometry={roundedBox(w, h, d, Math.min(w, h, d) * 0.14)}>
        <meshStandardMaterial color={color} emissive={color} emissiveIntensity={emissive} metalness={0.35} roughness={0.32}
          transparent opacity={0.88 * opacity} />
      </mesh>
      <lineSegments geometry={edges(w * 1.005, h * 1.005, d * 1.005)}>
        <lineBasicMaterial color={new THREE.Color(edge).multiplyScalar(glow)} transparent opacity={opacity} toneMapped={false} />
      </lineSegments>
    </group>
  );
};

/** Faint transparent volume with bright edges (selection boxes, containers). */
export const GlassBox: React.FC<{size: V3; position?: V3; color?: string; opacity?: number; fill?: number; glow?: number}> =
  ({size, position = [0, 0, 0], color = C.green, opacity = 1, fill = 0.08, glow = 1.6}) => {
    if (opacity <= 0.001) return null;
    return (
      <group position={position}>
        <mesh>
          <boxGeometry args={size} />
          <meshBasicMaterial color={color} transparent opacity={fill * opacity} depthWrite={false} />
        </mesh>
        <lineSegments geometry={edges(...size)}>
          <lineBasicMaterial color={new THREE.Color(color).multiplyScalar(glow)} toneMapped={false} transparent opacity={opacity} />
        </lineSegments>
      </group>
    );
  };

/** Glowing sphere node. */
export const Orb: React.FC<{position: V3; radius?: number; color?: string; glow?: number; opacity?: number; scale?: number}> =
  ({position, radius = 0.55, color = C.orange, glow = 1.2, opacity = 1, scale = 1}) => {
    if (opacity <= 0.001 || scale <= 0.001) return null;
    return (
      <group position={position} scale={scale}>
        <mesh>
          <sphereGeometry args={[radius, 40, 28]} />
          <meshStandardMaterial color={color} emissive={color} emissiveIntensity={glow * 0.55} metalness={0.2} roughness={0.25}
            transparent opacity={opacity} />
        </mesh>
        <mesh scale={1.35}>
          <sphereGeometry args={[radius, 24, 16]} />
          <meshBasicMaterial color={new THREE.Color(color).multiplyScalar(glow)} transparent opacity={0.12 * opacity}
            depthWrite={false} toneMapped={false} />
        </mesh>
      </group>
    );
  };

/** Glowing tube through `points`, drawn up to `progress` (0..1) of its length. */
export const PolyTube: React.FC<{points: V3[]; progress?: number; color?: string; radius?: number; glow?: number; opacity?: number}> =
  ({points, progress = 1, color = C.orange, radius = 0.07, glow = 1.6, opacity = 1}) => {
    const key = points.length + ':' + points[0].join(',') + points[points.length - 1].join(',') + ':' + progress.toFixed(3) + radius;
    const geo = useMemo(() => {
      const full = new THREE.CatmullRomCurve3(points.map((p) => new THREE.Vector3(...p)));
      if (progress < 0.005) return null;
      const n = Math.max(2, Math.ceil(points.length * 2 * progress));
      const pts = Array.from({length: n + 1}, (_, i) => full.getPointAt((progress * i) / n));
      return new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), n * 2, radius, 10, false);
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [key]);
    if (!geo || opacity <= 0.001) return null;
    return (
      <mesh geometry={geo}>
        <meshBasicMaterial color={new THREE.Color(color).multiplyScalar(glow)} transparent opacity={opacity} toneMapped={false} />
      </mesh>
    );
  };

/** Thin straight glowing line. */
export const Line: React.FC<{from: V3; to: V3; color?: string; opacity?: number; glow?: number}> = ({from, to, color = C.border, opacity = 1, glow = 1}) => {
  const geo = useMemo(() => new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(...from), new THREE.Vector3(...to)]),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [from.join(','), to.join(',')]);
  if (opacity <= 0.001) return null;
  return (
    <lineSegments geometry={geo}>
      <lineBasicMaterial color={new THREE.Color(color).multiplyScalar(glow)} transparent opacity={opacity} toneMapped={false} />
    </lineSegments>
  );
};

/** Expanding ring shockwave lying in a plane facing +z unless rotated. */
export const Ring: React.FC<{position: V3; radius: number; width?: number; color?: string; opacity?: number; rotation?: V3; glow?: number}> =
  ({position, radius, width = 0.06, color = C.orange, opacity = 1, rotation = [0, 0, 0], glow = 1.8}) => {
    if (opacity <= 0.001 || radius <= 0.001) return null;
    return (
      <mesh position={position} rotation={rotation}>
        <ringGeometry args={[Math.max(0, radius - width), radius, 96]} />
        <meshBasicMaterial color={new THREE.Color(color).multiplyScalar(glow)} transparent opacity={opacity} side={THREE.DoubleSide}
          depthWrite={false} toneMapped={false} />
      </mesh>
    );
  };
