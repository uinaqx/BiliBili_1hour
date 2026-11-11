export const C = {
  bg: '#09090b',
  card: '#1c1c1f',
  ink: '#f5f5f7',
  ink2: '#d1d1d6',
  muted: '#98989f',
  faint: '#636368',
  line: '#3a3a3e',
  hair: '#2a2a2e',
  fill: '#242428',
  blue: '#0a84ff',
  indigo: '#5e5ce6',
  purple: '#bf5af2',
  teal: '#64d2ff',
  green: '#30d158',
  orange: '#ff9f0a',
  red: '#ff453a',
  pink: '#ff375f',
};

export const FONT = '"Segoe UI Variable Display", "Segoe UI Variable Text", "Noto Sans SC", "Microsoft YaHei UI", sans-serif';
export const MONO = '"Cascadia Code", "SF Mono", Consolas, "Noto Sans SC", monospace';
export const SHADOW = 'inset 0 1px 0 rgba(255,255,255,0.05), 0 0 0 1px rgba(255,255,255,0.06), 0 14px 40px rgba(0,0,0,0.45)';
export const TITLE_GRAD = 'linear-gradient(90deg, #f5f5f7 0%, #f5f5f7 35%, #0a84ff 70%, #bf5af2 100%)';

/** `#rrggbb` with alpha. */
export const tint = (hex: string, a: number) => hex + Math.round(Math.max(0, Math.min(1, a)) * 255).toString(16).padStart(2, '0');
