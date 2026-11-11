"""Resumeable chapter visuals + one continuous AAC encode, measured PCM throughout."""
import argparse,concurrent.futures,hashlib,json,pathlib,subprocess,wave
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build/spoken';DEL=ROOT/'out'
FINAL=DEL/'一小时讲完现代汇编_x86-64与AArch64_含字幕.mp4'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,log):
 with (BUILD/log).open('w',encoding='utf8') as f:r=subprocess.run(['ffmpeg','-y','-v','warning',*args],stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError((BUILD/log).read_text(encoding='utf8',errors='replace')[-2000:])
def source_hash():
 h=hashlib.sha256()
 for p in [ROOT/'scripts/render_spoken.py',ROOT/'scripts/draw.py',ROOT/'scripts/examples.py',ROOT/'build/execution-data.json',ROOT/'build/examples-verification.json',pathlib.Path('C:/Windows/Fonts/msyh.ttc'),pathlib.Path('C:/Windows/Fonts/consola.ttf')]:h.update(p.read_bytes())
 return h.hexdigest()
def chapter(c):
 key=c['key'];tag=BUILD/(key+'.renderhash');video=BUILD/(key+'.mp4');audio=BUILD/(key+'.wav')
 if video.exists() and audio.exists() and tag.exists() and tag.read_text()==c['fingerprint']:print('SPOKEN_CHAPTER_CACHED',key,flush=True);return
 folder=BUILD/'frames'/key/c['fingerprint'][:16];folder.mkdir(parents=True,exist_ok=True);events=[]
 with wave.open(str(audio),'wb') as target:
  target.setnchannels(1);target.setsampwidth(2);target.setframerate(24000)
  for s in c['scenes']:
   source=ROOT/'public'/s['audio'];assert digest(source)==s['audioSha256']
   with wave.open(str(source),'rb') as f:
    assert f.getframerate()==24000 and f.getsampwidth()==2 and f.getnchannels()==1;pcm=f.readframes(f.getnframes())
   tail=s['durationFrames']*800-s['leadFrames']*800-len(pcm)//2;assert tail>=0
   target.writeframes(bytes(s['leadFrames']*800*2)+pcm+bytes(tail*2))
   for f in s['renderFrames']:
    path=folder/f'{s["key"]}-{f:05}.png'
    if not path.exists():draw.render(s,f).save(path,compress_level=1)
    events.append((s['startFrame']-c['startFrame']+f,path))
   print('SPOKEN_PAGE_READY',s['key'],flush=True)
 rows=['ffconcat version 1.0']
 for i,(f,p) in enumerate(events):
  end=events[i+1][0] if i+1<len(events) else c['durationFrames'];rows.extend([f"file '{p.as_posix()}'",'option framerate 30',f'duration {(end-f)/30:.9f}'])
 rows.extend([f"file '{events[-1][1].as_posix()}'",'option framerate 30']);listing=BUILD/(key+'.ffconcat');listing.write_text('\n'.join(rows)+'\n',encoding='utf8')
 run(['-f','concat','-safe','0','-i',str(listing),'-an','-fps_mode','vfr','-enc_time_base','1:30','-t',f'{c["durationFrames"]/30:.9f}','-c:v','libx264','-preset','veryfast','-crf','19','-bf','0','-g','60','-pix_fmt','yuv420p','-threads','2','-video_track_timescale','30000','-movflags','+faststart',str(video)],key+'.video.log')
 with wave.open(str(audio),'rb') as f:assert f.getnframes()==c['durationFrames']*800
 tag.write_text(c['fingerprint']);print('SPOKEN_CHAPTER_DONE',key,len(events),flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=4);a=p.parse_args();BUILD.mkdir(parents=True,exist_ok=True);t=load(ROOT/'public/timeline.json');assert t['status']=='complete-spoken-course' and t['audio'];h=source_hash()
 for c in t['chapters']:c['fingerprint']=hashlib.sha256((h+json.dumps(c,ensure_ascii=False,sort_keys=True)).encode()).hexdigest()
 (BUILD/'render-manifest.json').write_text(json.dumps(dict(sourceHash=h,timelineSha256=digest(ROOT/'public/timeline.json'),chapters=t['chapters']),ensure_ascii=False,indent=2),encoding='utf8')
 with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as pool:list(pool.map(chapter,t['chapters']))
 for kind,suffix in [('videos','mp4'),('audio','wav')]:
  (BUILD/(kind+'.ffconcat')).write_text('ffconcat version 1.0\n'+''.join(f"file '{c['key']}.{suffix}'\nduration {c['durationFrames']/30:.9f}\n" for c in t['chapters']),encoding='utf8')
 pending=FINAL.with_name(FINAL.stem+'.rendering.mp4')
 run(['-f','concat','-safe','0','-i',str(BUILD/'videos.ffconcat'),'-f','concat','-safe','0','-i',str(BUILD/'audio.ffconcat'),'-f','ffmetadata','-i',str(ROOT/'build/chapters-spoken.ffmetadata'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','aac','-b:a','160k','-t',f'{t["duration"]:.9f}','-video_track_timescale','30000','-movflags','+faststart',str(pending)],'final-mux.log');pending.replace(FINAL);print('SPOKEN_FINAL_DONE',str(FINAL),FINAL.stat().st_size,flush=True)
if __name__=='__main__':main()
