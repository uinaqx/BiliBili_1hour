// One-time cache reuse after two scene-specific diagram clarifications.
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
const t=JSON.parse(await fs.readFile('public/timeline.json','utf8'));
const video=await fs.readFile('src/video.tsx');
const before=await fs.readFile('build/diagrams-before-clarity.tsx','utf8');
const current=await fs.readFile('src/diagrams.tsx','utf8');
let expected=before.replace("type==='types'?'int  ·  整数'","type==='types'?(sceneKey==='c-01-4'?'char  ·  单个字符':'int  ·  整数')");
expected=expected.replace("type==='types'?'double  ·  带小数的数'","type==='types'?(sceneKey==='c-01-4'?\"单引号：'A'\":'double  ·  带小数的数')");
expected=expected.replace("box(12,142,366,'score：80',color.green)","box(12,142,366,sceneKey==='c-09-3'&&stage>=1?'score：85':'score：80',color.green)");
if(current!==expected||current===before)throw Error('Unexpected source difference; do not reuse cache');
const hash=d=>crypto.createHash('sha256').update(video).update(d).update(JSON.stringify(t)).digest('hex');
const oldHashes=[hash(before),hash(before.replace(/\r\n/g,'\n'))],newHash=hash(current),changed=new Set(['c-01-4','c-09-3']);
const cache=JSON.parse(await fs.readFile('build/still-cache.json','utf8'));let reused=0;
for(const j of t.renderJobs)if(!changed.has(j.sceneKey)&&oldHashes.includes(cache[j.path])){cache[j.path]=newHash;reused++;}
await fs.writeFile('build/still-cache.json',JSON.stringify(cache));
await fs.writeFile('build/visual-cache-migration.json',JSON.stringify({oldHashes,newHash,reused,rerenderScenes:[...changed],proof:'Exact guarded source replacements; other scene branches and all timeline scene data unchanged'},null,2));
console.log('UNCHANGED_VISUAL_CACHE_REUSED',reused,'frames; both changed scenes require fresh rendering');
