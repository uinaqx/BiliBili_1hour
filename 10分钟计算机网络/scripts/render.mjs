// Renders frames with Remotion and encodes them with the system FFmpeg (the bundled one cannot write files on this machine).
// Work is split into chunks under build/chunks so an interrupted render resumes where it stopped.
// Usage: node scripts/render.mjs [output.mp4] [--frames=0-299] [--concurrency=6] [--fresh]
import {bundle} from '@remotion/bundler';
import {renderFrames, selectComposition} from '@remotion/renderer';
import {spawn, spawnSync} from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(import.meta.dirname, '..');
const args = process.argv.slice(2);
const opt = (k, d) => (args.find((a) => a.startsWith(`--${k}=`))?.split('=')[1] ?? d);
const output = path.resolve(args.find((a) => !a.startsWith('--')) ?? path.join(root, 'out', '计算机网络十分钟.mp4'));
const concurrency = Number(opt('concurrency', 6));
const CHUNK = 1500;
const tl = JSON.parse(fs.readFileSync(path.join(root, 'src/timeline.json'), 'utf8'));
const [f0, f1] = (opt('frames', `0-${tl.total - 1}`)).split('-').map(Number);
const count = f1 - f0 + 1;
const inputProps = {subtitles: true};

const srcHash = crypto.createHash('sha1');
for (const dir of ['src', 'src/scenes']) for (const f of fs.readdirSync(path.join(root, dir)).sort()) {
  const p = path.join(root, dir, f);
  if (fs.statSync(p).isFile()) srcHash.update(f).update(fs.readFileSync(p));
}
srcHash.update(JSON.stringify(inputProps));
const chunkDir = path.join(root, 'build', 'chunks', srcHash.digest('hex').slice(0, 10));
if (args.includes('--fresh')) fs.rmSync(chunkDir, {recursive: true, force: true});
fs.mkdirSync(chunkDir, {recursive: true});
fs.mkdirSync(path.dirname(output), {recursive: true});

const chunks = [];
for (let s = f0; s <= f1; s += CHUNK) chunks.push([s, Math.min(f1, s + CHUNK - 1)]);
const chunkFile = ([a, b]) => path.join(chunkDir, `${a}-${b}.mp4`);
const todo = chunks.filter((c) => !fs.existsSync(chunkFile(c)));
console.log(`chunks ${chunks.length - todo.length}/${chunks.length} already done`);

let rendered = 0;
const t0 = Date.now();
if (todo.length) {
  const serveUrl = await bundle({entryPoint: path.join(root, 'src/index.ts'), publicDir: path.join(root, 'public')});
  const composition = await selectComposition({serveUrl, id: 'NET', inputProps, chromiumOptions: {gl: 'angle'}});
  const total = todo.reduce((n, [a, b]) => n + b - a + 1, 0);

  for (const [a, b] of todo) {
    const tmp = chunkFile([a, b]).replace(/\.mp4$/, '.part.mp4');
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(tl.fps), '-c:v', 'mjpeg', '-i', '-',
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', tmp], {stdio: ['pipe', 'inherit', 'inherit']});
    const ffDone = new Promise((res, rej) => ff.on('close', (c) => (c === 0 ? res() : rej(new Error('ffmpeg exited ' + c)))));
    const pending = new Map();
    let next = a;
    const flush = async () => {
      while (pending.has(next)) {
        const buf = pending.get(next); pending.delete(next); next++;
        if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
        if (++rendered % 300 === 0) {
          const s = (Date.now() - t0) / 1000;
          console.log(`frames ${rendered}/${total}  ${(rendered / s).toFixed(1)} fps  eta ${Math.round(((total - rendered) / rendered) * s / 60)} min`);
        }
      }
    };
    await renderFrames({
      serveUrl, composition, inputProps, concurrency, imageFormat: 'jpeg', jpegQuality: 94, frameRange: [a, b],
      chromiumOptions: {gl: 'angle'}, outputDir: null, onStart: () => {},
      onFrameBuffer: async (buffer, frame) => { pending.set(frame, buffer); await flush(); },
    });
    await flush();
    ff.stdin.end();
    await ffDone;
    fs.renameSync(tmp, chunkFile([a, b]));
    console.log(`chunk ${a}-${b} done`);
  }
}

const list = path.join(chunkDir, 'list.txt');
fs.writeFileSync(list, chunks.map((c) => `file '${chunkFile(c).replace(/\\/g, '/')}'`).join('\n'));
const clips = [];
for (const s of tl.scenes) for (const b of s.beats) {
  const at = s.from + b.from - f0;
  if (b.audio && at >= 0 && at < count) clips.push({file: path.join(root, 'public', b.audio), ms: Math.round((at / tl.fps) * 1000)});
}
const inputs = clips.flatMap((c) => ['-i', c.file]);
const audioArgs = clips.length === 0 ? ['-map', '0:v'] : [
  '-filter_complex',
  clips.map((c, i) => `[${i + 1}:a]aresample=48000,adelay=${c.ms}|${c.ms}[a${i}]`).join(';') +
    `;${clips.map((_, i) => `[a${i}]`).join('')}amix=inputs=${clips.length}:normalize=0:dropout_transition=0,apad[aout]`,
  '-map', '0:v', '-map', '[aout]', '-c:a', 'aac', '-b:a', '192k', '-shortest',
];
const r = spawnSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, ...inputs, ...audioArgs,
  '-c:v', 'copy', '-movflags', '+faststart', output], {stdio: 'inherit'});
if (r.status !== 0) throw new Error('final mux failed');
console.log(`DONE ${clips.length ? `with ${clips.length} narration clips` : '(no narration yet)'} ${output}`);
