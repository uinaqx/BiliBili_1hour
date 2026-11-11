export const C = {
  bg: '#f5f5f7',
  card: '#ffffff',
  ink: '#1d1d1f',
  ink2: '#424245',
  muted: '#86868b',
  faint: '#aeaeb2',
  line: '#d2d2d7',
  hair: '#e8e8ed',
  fill: '#f2f2f5',
  blue: '#0071e3',
  indigo: '#5e5ce6',
  purple: '#af52de',
  teal: '#30b0c7',
  green: '#28a745',
  orange: '#ff9500',
  red: '#ff3b30',
  pink: '#ff2d55',
};

export const FONT = '"Segoe UI Variable Display", "Segoe UI Variable Text", "Noto Sans SC", "Microsoft YaHei UI", sans-serif';
export const MONO = '"Cascadia Code", "SF Mono", Consolas, "Noto Sans SC", monospace';
export const SHADOW = '0 1px 2px rgba(0,0,0,0.04), 0 10px 36px rgba(0,0,0,0.07)';

/** `#rrggbb` with alpha. */
export const tint = (hex: string, a: number) => hex + Math.round(Math.max(0, Math.min(1, a)) * 255).toString(16).padStart(2, '0');
