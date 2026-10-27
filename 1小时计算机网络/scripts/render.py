"""Render every motion tick, hold static states, encode chapters and mux measured narration."""
import argparse,concurrent.futures,hashlib,json,os,pathlib,subprocess,wave
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out';FINAL=DEL/'一小时学完计算机网络_百炼3.1Plus许南川_1.05倍速.mp4'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def command(args,log):
    with (BUILD/log).open('w',encoding='utf8') as f:r=subprocess.run(['ffmpeg','-y','-v','warning',*args],stdout=f,stderr=subprocess.STDOUT)
    if r.returncode:raise RuntimeError((BUILD/log).read_text(encoding='utf8',errors='replace')[-2000:])
def source_hash():
    h=hashlib.sha256((ROOT/'scripts/draw.py').read_bytes()+pathlib.Path(__file__).read_bytes())
    for p in [ROOT/'scripts/diagrams.py',ROOT/'scripts/examples.py',ROOT/'build/examples-verification.json',pathlib.Path('C:/Windows/Fonts/msyh.ttc')]:h.update(p.read_bytes())
    return h.hexdigest()
def image_path(c,s,frame):return BUILD/'frames'/c['key']/c['fingerprint'][:14]/f'{s["key"]}-{frame:05}.png'
def chapter(c):
    key=c['key'];tag=BUILD/(key+'.renderhash');video=BUILD/(key+'.mp4');audio=BUILD/(key+'.wav')
    if video.exists() and audio.exists() and tag.exists() and tag.read_text()==c['fingerprint']:print('CHAPTER_CACHED',key,flush=True);return
    total=sum(len(s['renderFrames']) for s in c['scenes']);done=0;events=[]
    for s in c['scenes']:
        for frame in s['renderFrames']:
            p=image_path(c,s,frame);p.parent.mkdir(parents=True,exist_ok=True)
            if not p.exists():draw.render(s,frame).save(p,compress_level=1)
            events.append((s['startFrame']-c['startFrame']+frame,p));done+=1
            if done%1000==0:print('MOTION_FRAMES',key,done,total,flush=True)
    rows=['ffconcat version 1.0']
    for i,(f,path) in enumerate(events):
        end=events[i+1][0] if i+1<len(events) else c['durationFrames'];rows.extend([f"file '{path.as_posix()}'",'option framerate 30',f'duration {(end-f)/30:.9f}'])
    rows.extend([f"file '{events[-1][1].as_posix()}'",'option framerate 30']);listing=BUILD/(key+'.ffconcat');listing.write_text('\n'.join(rows)+'\n',encoding='utf8')
    pcm=bytearray(c['durationFrames']*800*2)
    for s in c['scenes']:
        with wave.open(str(ROOT/'public'/s['audio'])) as f:assert f.getframerate()==24000;data=f.readframes(f.getnframes())
        at=(s['startFrame']-c['startFrame']+s['leadFrames'])*800*2;pcm[at:at+len(data)]=data
    raw=BUILD/(key+'.raw.wav')
    with wave.open(str(raw),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(pcm)
    command(['-i',str(raw),'-af',f'loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,asetpts=N/SR/TB,apad,atrim=end_sample={c["durationFrames"]*1600}','-c:a','pcm_s16le',str(audio)],key+'.audio.log')
    command(['-f','concat','-safe','0','-i',str(listing),'-an','-fps_mode','vfr','-enc_time_base','1:30','-t',f'{c["durationFrames"]/30:.9f}','-c:v','libx264','-preset','veryfast','-crf','19','-bf','0','-g','60','-pix_fmt','yuv420p','-threads','2','-video_track_timescale','30000','-movflags','+faststart',str(video)],key+'.video.log')
    tag.write_text(c['fingerprint']);print('CHAPTER_DONE',key,total,'frames',round(c['durationFrames']/30,2),'seconds',flush=True)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--chapter');parser.add_argument('--workers',type=int,default=4);a=parser.parse_args()
    t=read(ROOT/'public/timeline.json');assert t['scope']=='complete-course','Never export synthetic layout timings'
    draw.prepare_formulas(read(ROOT/'public/course.json'));fingerprint=source_hash()
    for c in t['chapters']:c['fingerprint']=hashlib.sha256((fingerprint+json.dumps(c,ensure_ascii=False,sort_keys=True)).encode()).hexdigest()
    (BUILD/'render-manifest.json').write_text(json.dumps(dict(sourceHash=fingerprint,chapters=t['chapters']),ensure_ascii=False,indent=2),encoding='utf8')
    selected=[c for c in t['chapters'] if not a.chapter or c['key']==a.chapter]
    with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers,initializer=draw.init,initargs=(t,)) as pool:
        list(pool.map(chapter,selected))
    if a.chapter:return
    for name,suffix in [('videos','.mp4'),('audios','.wav')]:
        (BUILD/(name+'.ffconcat')).write_text('ffconcat version 1.0\n'+''.join(f"file '{c['key']+suffix}'\nduration {c['durationFrames']/30:.9f}\n" for c in t['chapters']),encoding='utf8')
    staged=FINAL.with_name(FINAL.stem+'.rendering.mp4')
    command(['-f','concat','-safe','0','-i',str(BUILD/'videos.ffconcat'),'-f','concat','-safe','0','-i',str(BUILD/'audios.ffconcat'),'-f','ffmetadata','-i',str(BUILD/'chapters.ffmetadata'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-af',f'asetpts=N/SR/TB,apad,atrim=end_sample={t["totalFrames"]*1600}','-c:a','aac','-b:a','128k','-ar','48000','-ac','1','-t',f'{t["duration"]:.9f}','-video_track_timescale','30000','-movflags','+faststart',str(staged)],'final-mux.log')
    staged.replace(FINAL);print('FINAL_DONE',str(FINAL),flush=True)
if __name__=='__main__':main()
