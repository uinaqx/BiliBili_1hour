export const C = {
  bg: '#060608',
  card: '#111116',
  card2: '#18181f',
  ink: '#f7f7fb',
  ink2: '#cfcfdb',
  muted: '#8e8ea3',
  faint: '#55556a',
  line: '#2b2b38',
  hair: '#1c1c25',
  violet: '#8a5cff',
  magenta: '#ff4fd8',
  cyan: '#27e1ff',
  lime: '#c8f53c',
  gold: '#ffd166',
  red: '#ff4d6d',
  blue: '#4d7cff',
  dark: '#0b0b10',
};

export const FONT = '"Segoe UI Variable Display", "Segoe UI Variable Text", "Noto Sans SC", "Microsoft YaHei UI", sans-serif';
export const MONO = '"Cascadia Code", "SF Mono", Consolas, "Noto Sans SC", monospace';
export const BORDER = '1px solid rgba(255,255,255,0.09)';
export const SHADOW = '0 30px 80px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.06)';
export const GRAD = 'linear-gradient(90deg, #8a5cff 0%, #ff4fd8 50%, #27e1ff 100%)';

/** `#rrggbb` with alpha. */
export const tint = (hex: string, a: number) => hex + Math.round(Math.max(0, Math.min(1, a)) * 255).toString(16).padStart(2, '0');

/** Neon glow box-shadow in `color`. */
export const glow = (color: string, k = 1) =>
  `0 0 ${18 * k}px ${tint(color, 0.55)}, 0 0 ${60 * k}px ${tint(color, 0.28)}`;
