"""Capture the supplied SVG teaching states and encode a voiced chapter master."""
import argparse,asyncio,concurrent.futures,hashlib,json,math,pathlib,subprocess,sys,wave
from playwright.async_api import async_playwright
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'production';BUILD=P/'build';STILLS=P/'stills'
OUT=ROOT/'out';FPS=30
for d in (BUILD,STILLS,OUT):d.mkdir(parents=True,exist_ok=True)

def load():return json.loads((P/'timeline.json').read_text(encoding='utf-8'))
def make_html(t):
    html=(ROOT/'output/index.html').read_text(encoding='utf-8')
    html=html.replace("'Noto Sans Mono CJK SC','DejaVu Sans Mono',monospace", "'Cascadia Code',Consolas,monospace")
    html=html.replace("'Noto Sans CJK SC'", "'Noto Sans SC','Microsoft YaHei'")
    t={**t,'displayFrames':t['totalFrames'] if t['fullCourse'] else 216000}
    extra='const VOICED='+json.dumps(t,ensure_ascii=False).replace('</','<\\/')+';\n'+(P/'player_voice.js').read_text(encoding='utf-8')
    html=html.replace('</body>','<script>'+extra+'</script></body>')
    (P/'voiced.html').write_text(html,encoding='utf-8');return html

def events(s):
    n=int(s['id'][1:]);canonical={0,12,31,40,45,50,55,57,60,65,69,75,80,87,89.95}
    if n in (25,30,39):canonical.update(12+i*78/24 for i in range(24))
    if n in (51,52,53,55):canonical.update(12+i*15 for i in range(5))
    if n==10:canonical.update(12+i*10 for i in range(8))
    if n in (40,42,43,58):canonical.update(12+i*75/14 for i in range(15))
    points={0,s['lessonStart'],s['lessonEnd'],s['questionStart'],s['thinkStart'],s['answerStart'],s['answerEnd'],s['durationFrames']-1}
    points.update(s['lessonStart']+round(v/90*(s['lessonEnd']-s['lessonStart'])) for v in canonical)
    points.update(s['thinkStart']+i*30 for i in range(6))
    # Revisit mechanism states as the answer narration unfolds.
    points.update(s['answerStart']+round(f*(s['answerEnd']-s['answerStart'])) for f in (.25,.5,.75))
    for c in s['captions']:points.update((math.ceil(c['start']*30-1e-6),math.ceil(c['end']*30-1e-6)))
    return sorted(p for p in points if 0<=p<s['durationFrames'])

async def capture(t,ids=None,qa=False):
    html=make_html(t);scenes=[s for s in t['scenes'] if not ids or s['id'] in ids]
    source=(ROOT/'src/player.js').read_bytes()+(P/'player_voice.js').read_bytes()
    jobs=[];manifest={}
    if ids and not qa and (BUILD/'frame-manifest.json').exists():manifest=json.loads((BUILD/'frame-manifest.json').read_text())
    for s in scenes:
        digest=hashlib.sha256(source+json.dumps(s,ensure_ascii=False,sort_keys=True).encode()+str(t['totalFrames'] if t['fullCourse'] else 216000).encode()).hexdigest()
        allpoints=events(s);points=allpoints
        if qa:points=[s['lessonStart']+round((s['lessonEnd']-s['lessonStart'])*.65),s['thinkStart']+90,s['answerStart']+15]
        manifest[s['id']]=dict(hash=digest,points=allpoints)
        for f in points:
            target=STILLS/f"{s['id']}-{f:05}.png";tag=target.with_suffix('.hash')
            if not qa and target.exists() and tag.exists() and tag.read_text()==digest:continue
            jobs.append((s,f,target,digest))
    errors=[];audits=[];done=0
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True,args=['--disable-dev-shm-usage','--no-sandbox'])
        queue=asyncio.Queue()
        for job in jobs:queue.put_nowait(job)
        async def worker():
            nonlocal done
            page=await browser.new_page(viewport=dict(width=1920,height=1080),device_scale_factor=1)
            page.on('pageerror',lambda exc:errors.append(str(exc)))
            await page.set_content(html,wait_until='load');await page.evaluate("document.body.classList.add('export')");await page.evaluate('document.fonts.ready')
            while not queue.empty():
                try:s,f,target,digest=queue.get_nowait()
                except asyncio.QueueEmpty:break
                state=await page.evaluate('(t)=>window.renderVoicedAt(t)',(s['startFrame']+f)/30)
                if qa or f in (s['thinkStart'],s['answerStart'],s['lessonEnd']):
                    bad=await page.evaluate('window.auditVoicedLayout()');audits.append(dict(scene=s['id'],frame=f,issues=bad,state=state))
                    if bad:raise RuntimeError('LAYOUT '+json.dumps(audits[-1],ensure_ascii=False))
                await page.locator('#stage').screenshot(path=str(target),animations='disabled')
                target.with_suffix('.hash').write_text(digest)
                done+=1
                if done%100==0 or done==len(jobs):print(f'CAPTURE {done}/{len(jobs)}',flush=True)
            await page.close()
        try:await asyncio.gather(*[worker() for _ in range(3)])
        finally:await browser.close()
    assert not errors,errors
    (BUILD/('qa-layout.json' if qa else 'layout.json')).write_text(json.dumps(audits,ensure_ascii=False,indent=2),encoding='utf-8')
    if not qa:(BUILD/'frame-manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('CAPTURE_DONE',len(jobs),'frames; browser errors',len(errors),flush=True)

def run(cmd,log):
    with log.open('w',encoding='utf-8') as f:r=subprocess.run(cmd,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    if r.returncode:raise RuntimeError(log.read_text(encoding='utf-8',errors='replace')[-2500:])

def encode_chapter(ch,t):
    scenes=[s for s in t['scenes'] if s['id'] in ch['sceneIds']];key=ch['id'];duration=ch['durationFrames']/30
    manifest=json.loads((BUILD/'frame-manifest.json').read_text())
    digest=hashlib.sha256(json.dumps([[manifest[s['id']],s['audioHash']] for s in scenes],sort_keys=True).encode()+pathlib.Path(__file__).read_bytes()+b'no-b-frame-v1').hexdigest()
    video=BUILD/(key+'.mp4');audio=BUILD/(key+'.master.wav');tag=BUILD/(key+'.encodehash')
    if video.exists() and audio.exists() and tag.exists() and tag.read_text()==digest:print('CHAPTER_CACHED '+key,flush=True);return
    listing=[]
    for s in scenes:
        points=manifest[s['id']]['points']
        for i,f in enumerate(points):
            target=STILLS/f"{s['id']}-{f:05}.png"
            assert target.exists() and target.with_suffix('.hash').read_text()==manifest[s['id']]['hash'],'Render current frames first'
            stop=points[i+1] if i+1<len(points) else s['durationFrames']
            escaped=target.as_posix().replace("'","'\\''")
            listing.extend([f"file '{escaped}'",'option framerate 30',f'duration {(stop-f)/30:.9f}'])
    listing.extend([f"file '{target.as_posix()}'",'option framerate 30'])
    concat=BUILD/(key+'.ffconcat');concat.write_text('ffconcat version 1.0\n'+'\n'.join(listing)+'\n',encoding='utf-8')
    raw=BUILD/(key+'.raw.wav')
    with wave.open(str(raw),'wb') as dest:
        dest.setnchannels(1);dest.setsampwidth(2);dest.setframerate(24000)
        for s in scenes:
            with wave.open(str(BUILD/(s['id']+'.wav')),'rb') as f:dest.writeframes(f.readframes(f.getnframes()))
    run(['ffmpeg','-y','-hide_banner','-loglevel','warning','-i',str(raw),'-af','loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,apad', '-t',f'{duration:.9f}','-c:a','pcm_s16le',str(audio)],BUILD/(key+'.audio.log'))
    run(['ffmpeg','-y','-hide_banner','-loglevel','warning','-f','concat','-safe','0','-i',str(concat),'-an','-fps_mode','vfr','-enc_time_base','1:30','-t',f'{duration:.9f}','-c:v','libx264','-preset','fast','-crf','20','-bf','0','-g','30','-pix_fmt','yuv420p','-threads','4','-video_track_timescale','30000','-movflags','+faststart',str(video)],BUILD/(key+'.video.log'))
    tag.write_text(digest);print(f'CHAPTER_DONE {key} {duration:.3f}s',flush=True)

def encode(t,preview=False):
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda ch:encode_chapter(ch,t),t['chapters']))
    videos=BUILD/'videos.ffconcat';audios=BUILD/'audios.ffconcat'
    for output,suffix in [(videos,'.mp4'),(audios,'.master.wav')]:
        output.write_text('ffconcat version 1.0\n'+''.join(f"file '{ch['id']+suffix}'\nduration {ch['durationFrames']/30:.9f}\n" for ch in t['chapters']),encoding='utf-8')
    target=OUT/('配音试片.mp4' if preview else '两小时学习计算机组成原理.mp4')
    run(['ffmpeg','-y','-hide_banner','-loglevel','warning','-f','concat','-safe','0','-i',str(videos),'-f','concat','-safe','0','-i',str(audios),'-i',str(BUILD/'chapters.ffmetadata'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','aac','-b:a','128k','-ar','48000','-ac','1','-t',f"{t['duration']:.9f}",'-movflags','+faststart',str(target)],BUILD/'final-mux.log')
    print('FINAL_DONE '+str(target),flush=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--qa',action='store_true');parser.add_argument('--scenes');parser.add_argument('--encode-only',action='store_true');parser.add_argument('--preview',action='store_true');args=parser.parse_args();t=load()
    if not args.encode_only:asyncio.run(capture(t,set(args.scenes.split(',')) if args.scenes else None,args.qa))
    if not args.qa and not args.scenes:encode(t,args.preview)
if __name__=='__main__':main()
