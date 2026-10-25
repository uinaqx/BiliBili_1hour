import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {bundle} from '@remotion/bundler';
import {openBrowser,selectComposition,renderStill} from '@remotion/renderer';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const timeline=JSON.parse(await fs.readFile(path.join(root,'public/timeline.json'),'utf8'));
const args=process.argv.slice(2);
const inputPaths=[...(await fs.readdir(path.join(root,'src'))).filter(n=>/\.tsx?$/.test(n)).sort().map(n=>path.join(root,'src',n)),path.join(root,'package-lock.json'),path.join(root,'tsconfig.json'),path.join(root,'public/timeline.json'),'C:/Windows/Fonts/consola.ttf','C:/Windows/Fonts/msyh.ttc'];
const files=[];const fingerprint=crypto.createHash('sha256');
for(const file of inputPaths){const bytes=await fs.readFile(file);const hash=crypto.createHash('sha256').update(bytes).digest('hex');files.push({path:file.startsWith(root)?path.relative(root,file).replaceAll('\\','/'):file,sha256:hash});fingerprint.update(hash);}
const sourceHash=fingerprint.digest('hex');
await fs.writeFile(path.join(root,'build/render-inputs.json'),JSON.stringify({sourceHash,files},null,2));
const cachePath=path.join(root,'build/still-cache.json');
let cache={};try{cache=JSON.parse(await fs.readFile(cachePath,'utf8'));}catch{}
let cacheWrites=Promise.resolve();
function saveCache(){
  cacheWrites=cacheWrites.then(async()=>{
    const temp=cachePath+'.tmp';
    await fs.writeFile(temp,JSON.stringify(cache));
    await fs.rename(temp,cachePath);
  });
  return cacheWrites;
}
let jobs=timeline.renderJobs;
if(args.includes('--preview'))jobs=jobs.filter(j=>j.frame<90*30);
if(args.includes('--qa'))jobs=timeline.scenes.map(s=>jobs.filter(j=>j.sceneKey===s.key).slice(-1)[0]);
if(args.includes('--scene'))jobs=jobs.filter(j=>args[args.indexOf('--scene')+1].split(',').includes(j.sceneKey));
const serveUrl=await bundle({entryPoint:path.join(root,'src/index.tsx'),webpackCache:true});
const browser=await openBrowser('chrome',{logLevel:'error'});
const inputProps={includeAudio:false,includeCaptions:false};
const composition=await selectComposition({serveUrl,id:'RustPracticeCourse',puppeteerInstance:browser,inputProps});
let next=0,done=0;
async function worker(){
  while(next<jobs.length){
    const job=jobs[next++],out=path.join(root,'public',job.path);
    let exists=false;try{exists=(await fs.stat(out)).size>1000;}catch{}
    if(cache[job.path]!==sourceHash||!exists){
      await fs.mkdir(path.dirname(out),{recursive:true});
      for(let attempt=0;attempt<4;attempt++){
        try{
          let dom=null;
          await renderStill({composition,serveUrl,puppeteerInstance:browser,frame:job.frame,output:out,imageFormat:'png',inputProps,logLevel:'error',onBrowserLog:log=>{if(process.env.RUST_PRACTICE_DEBUG)console.log('BROWSER_META_PROBE',log.text.slice(0,200));if(log.text.startsWith('PRACTICE_META:')){const m=JSON.parse(log.text.slice('PRACTICE_META:'.length));if(m.frame===job.frame)dom=m;}}});
          if(job.sceneKey!=='rp-overview'&&!dom)throw Error('Missing actual DOM evidence '+job.sceneKey);
          await fs.writeFile(out.replace(/\.png$/,'.json'),JSON.stringify({sourceHash,dom}));
          break;
        }
        catch(error){if(attempt===3)throw error;console.log(`RETRY ${job.path}: ${attempt+1}`);await new Promise(resolve=>setTimeout(resolve,1000));}
      }
      cache[job.path]=sourceHash;
    }
    done++;
    if(done%50===0||done===jobs.length){console.log(`VISUAL_FRAMES ${done}/${jobs.length}`);await saveCache();}
  }
}
try{
  const workers=Math.max(1,Number(process.env.REMOTION_STILL_WORKERS??6));
  const results=await Promise.allSettled(Array.from({length:workers},()=>worker()));
  const failed=results.find(r=>r.status==='rejected');
  if(failed){console.error('RENDER_ERROR: '+failed.reason.message);process.exitCode=1;}
}finally{
  await saveCache();
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
