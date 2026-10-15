import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const timeline=JSON.parse(await fs.readFile(path.join(root,'public/timeline.json'),'utf8'));
process.stdout.write(crypto.createHash('sha256').update(await fs.readFile(path.join(root,'src/video.tsx'))).update(JSON.stringify(timeline)).digest('hex'));
