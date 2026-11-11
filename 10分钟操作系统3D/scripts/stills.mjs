// Usage: node scripts/stills.mjs <scene>@<beat>.<fraction> ...   e.g. array@1.5 tree@3.8 graph@end
// A point may also be "f1234" for an absolute frame.
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const tl = JSON.parse(fs.readFileSync(path.join(root, 'src/timeline.json'), 'utf8'));
const jobs = process.argv.slice(2).map((tok) => {
  if (/^f\d+$/.test(tok)) return {name: tok, frame: Number(tok.slice(1))};
  const [id, p] = tok.split('@');
  const s = tl.scenes.find((x) => x.id === id);
  if (p === 'end') return {name: tok, frame: s.from + s.duration - 16};
  const [bi, frac] = p.split('.');
  const b = s.beats[Number(bi)];
  return {name: tok, frame: Math.round(s.from + b.from + b.dur * Number('0.' + (frac ?? '0')))};
});
const out = path.join(root, 'build/stills');
fs.mkdirSync(out, {recursive: true});
const serveUrl = await bundle({entryPoint: path.join(root, 'src/index.ts'), publicDir: path.join(root, 'public')});
const composition = await selectComposition({serveUrl, id: 'OS3D', inputProps: {subtitles: true}, chromiumOptions: {gl: 'angle'}});
for (const j of jobs) {
  const file = path.join(out, `${j.name.replace(/[@.]/g, '_')}.png`);
  await renderStill({serveUrl, composition, frame: j.frame, output: file, chromiumOptions: {gl: 'angle'}, inputProps: {subtitles: true}});
  console.log('STILL', j.frame, file);
}
