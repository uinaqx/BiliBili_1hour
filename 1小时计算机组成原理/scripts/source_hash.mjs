import fs from 'node:fs/promises';
import crypto from 'node:crypto';
const timeline=JSON.parse(await fs.readFile('public/timeline.json','utf8'));
const hash=crypto.createHash('sha256').update(await fs.readFile('src/video.tsx')).update(await fs.readFile('src/visuals.tsx')).update(JSON.stringify(timeline)).digest('hex');
await fs.writeFile('build/current-source-hash.txt',hash);
console.log('SOURCE_HASH_READY');
