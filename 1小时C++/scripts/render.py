"""Encode the approved Remotion states at exact 30fps time ticks and mux sample-exact audio."""
import argparse,concurrent.futures,hashlib,json,pathlib,subprocess,sys,wave
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out';FINAL=DEL/'一小时学习C++_基础与面向对象.mp4'
T=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf-8'))
if T.get('previewOnly'):raise SystemExit('Editing preview only. Generate narration, prepare_audio.py and timeline.py before final export.')
def run(args,name):
    with (BUILD/name).open('w',encoding='utf-8') as f:r=subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','warning',*args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    if r.returncode:raise RuntimeError((BUILD/name).read_text(encoding='utf-8',errors='replace')[-2200:])
def chapter(c):
    key=c['key'];duration=c['durationFrames']/30;video=BUILD/(key+'.mp4');audio=BUILD/(key+'.wav');tag=BUILD/(key+'.renderhash')
    cache=json.loads((BUILD/'still-cache.json').read_text(encoding='utf-8'))
    assert all((ROOT/'public'/v['path']).exists() and v['path'] in cache for v in c['images'])
    fingerprint=hashlib.sha256(json.dumps([c,[(v['path'],cache[v['path']]) for v in c['images']]],ensure_ascii=False).encode()+pathlib.Path(__file__).read_bytes()).hexdigest()
    if video.exists() and audio.exists() and tag.exists() and tag.read_text()==fingerprint:print('CHAPTER_CACHED',key,flush=True);return
    raw=BUILD/(key+'.raw.wav');pcm=bytearray(c['durationFrames']*800*2)
    for s in c['scenes']:
        with wave.open(str(ROOT/'public'/s['audio']),'rb') as f:
            assert f.getframerate()==24000 and f.getnchannels()==1;data=f.readframes(f.getnframes())
        start=(s['startFrame']-c['startFrame']+s['leadFrames'])*800*2;pcm[start:start+len(data)]=data
    with wave.open(str(raw),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(pcm)
    samples=c['durationFrames']*1600
    run(['-i',str(raw),'-af',f'loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,asetpts=N/SR/TB,apad,atrim=end_sample={samples}','-c:a','pcm_s16le',str(audio)],key+'.audio.log')
    with wave.open(str(audio),'rb') as f:assert f.getframerate()==48000 and f.getnframes()==samples
    rows=['ffconcat version 1.0']
    for event in c['images']:rows.extend([f"file '{(ROOT/'public'/event['path']).as_posix()}'",'option framerate 30',f"duration {event['frames']/30:.9f}"])
    rows.extend([f"file '{(ROOT/'public'/c['images'][-1]['path']).as_posix()}'",'option framerate 30'])
    listing=BUILD/(key+'.ffconcat');listing.write_text('\n'.join(rows)+'\n',encoding='utf-8')
    run(['-f','concat','-safe','0','-i',str(listing),'-an','-fps_mode','vfr','-enc_time_base','1:30','-t',f'{duration:.9f}','-c:v','libx264','-preset','fast','-crf','20','-bf','0','-g','30','-pix_fmt','yuv420p','-threads','4','-video_track_timescale','30000','-movflags','+faststart',str(video)],key+'.video.log')
    tag.write_text(fingerprint);print('CHAPTER_DONE',key,round(duration,3),flush=True)
def mux():
    for name,suffix in [('videos','.mp4'),('audios','.wav')]:
        (BUILD/(name+'.ffconcat')).write_text('ffconcat version 1.0\n'+''.join(f"file '{c['key']+suffix}'\nduration {c['durationFrames']/30:.9f}\n" for c in T['chapters']),encoding='utf-8')
    staged=FINAL.with_name(FINAL.stem+'.rendering.mp4')
    run(['-f','concat','-safe','0','-i',str(BUILD/'videos.ffconcat'),'-f','concat','-safe','0','-i',str(BUILD/'audios.ffconcat'),'-f','ffmetadata','-i',str(BUILD/'chapters.ffmetadata'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-af',f"asetpts=N/SR/TB,apad,atrim=end_sample={T['totalFrames']*1600}",'-c:a','aac','-b:a','128k','-ar','48000','-ac','1','-t',f"{T['duration']:.9f}",'-video_track_timescale','30000','-movflags','+faststart',str(staged)],'final-mux.log')
    staged.replace(FINAL);print('FINAL_DONE',str(FINAL),flush=True)
def main():
    p=argparse.ArgumentParser();p.add_argument('--chapter');p.add_argument('--preview',action='store_true');args=p.parse_args()
    if args.preview:
        c=next(x for x in T['chapters'] if x['key']=='01');chapter(c)
        run(['-i',str(BUILD/'01.mp4'),'-i',str(BUILD/'01.wav'),'-map','0:v:0','-map','1:a:0','-vf','fps=30,trim=duration=90,setpts=PTS-STARTPTS','-af','atrim=duration=90,asetpts=PTS-STARTPTS','-t','90','-c:v','libx264','-preset','fast','-crf','20','-bf','0','-threads','4','-c:a','aac','-b:a','128k','-movflags','+faststart',str(DEL/'90秒内部试片.mp4')],'preview.log');print('PREVIEW_DONE',flush=True);return
    selected=[c for c in T['chapters'] if not args.chapter or c['key']==args.chapter]
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(chapter,selected))
    if not args.chapter:mux()
if __name__=='__main__':main()
