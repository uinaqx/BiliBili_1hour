import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill} from '@remotion/renderer';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const timeline=JSON.parse(await fs.readFile(path.join(root,'public/timeline.json'),'utf8'));
const args=process.argv.slice(2);
const sourceHash=crypto.createHash('sha256').update(await fs.readFile(path.join(root,'src/video.tsx'))).update(JSON.stringify(timeline)).digest('hex');
const cachePath=path.join(root,'build/still-cache.json');
let cache={};try{cache=JSON.parse(await fs.readFile(cachePath,'utf8'));}catch{}
let jobs=timeline.renderJobs;
if(args.includes('--preview'))jobs=jobs.filter(j=>j.frame<90*30);
if(args.includes('--qa'))jobs=timeline.scenes.map(s=>jobs.find(j=>j.frame===s.startFrame+s.steps[3]+12)).filter(Boolean);
if(args.includes('--scene'))jobs=jobs.filter(j=>args[args.indexOf('--scene')+1].split(',').includes(j.sceneKey));
const serveUrl=await bundle({entryPoint:path.join(root,'src/index.tsx'),webpackCache:true});
const browser=await openBrowser('chrome',{logLevel:'error'});
const inputProps={includeAudio:false,includeCaptions:false};
const composition=await selectComposition({serveUrl,id:'RustReview',browser,inputProps});
let next=0,done=0;
async function worker(){
  while(next<jobs.length){
    const job=jobs[next++],out=path.join(root,'public',job.path);
    let exists=false;try{exists=(await fs.stat(out)).size>1000;}catch{}
    if(cache[job.path]!==sourceHash||!exists){
      await fs.mkdir(path.dirname(out),{recursive:true});
      for(let attempt=0;attempt<4;attempt++){
        try{await renderStill({composition,serveUrl,browser,frame:job.frame,output:out,imageFormat:'png',inputProps,logLevel:'error'});break;}
        catch(error){if(attempt===3)throw error;console.log(`RETRY ${job.path}: ${attempt+1}`);await new Promise(resolve=>setTimeout(resolve,1000));}
      }
      cache[job.path]=sourceHash;
    }
    done++;
    if(done%50===0||done===jobs.length){console.log(`VISUAL_FRAMES ${done}/${jobs.length}`);await fs.writeFile(cachePath,JSON.stringify(cache));}
  }
}
try{
  const results=await Promise.allSettled([worker(),worker(),worker()]);
  const failed=results.find(r=>r.status==='rejected');
  if(failed){console.error('RENDER_ERROR: '+failed.reason.message);process.exitCode=1;}
}finally{
  await fs.writeFile(cachePath,JSON.stringify(cache));
  let timer;
  const closed=await Promise.race([
    browser.close({silent:true}).then(()=>true),
    new Promise(resolve=>{timer=setTimeout(()=>resolve(false),10000);})
  ]);
  clearTimeout(timer);
  // A failed page retry may leave an unresolved page-disposal promise in Chrome.
  if(!closed){browser.disconnect();console.log('Browser cleanup timed out; rendered frames are safely cached.');}
}
process.exit(process.exitCode??0);
