"""Cache and encode source-based scenes in chapters, with exact measured narration."""
import argparse,concurrent.futures,hashlib,json,pathlib,subprocess,wave
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out';FINAL=DEL/'计算机组成原理_课件全知识点与考题精讲_无字幕.mp4'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def run(args,log):
 with log.open('w',encoding='utf8') as f:subprocess.run(['ffmpeg','-y','-v','warning',*args],stdout=f,stderr=subprocess.STDOUT,check=True)
def chapter(c):
 key=c['key'];fingerprint=c['fingerprint'];tag=BUILD/(key+'.renderhash');video=BUILD/(key+'.mp4');audio=BUILD/(key+'.wav')
 if tag.exists() and tag.read_text()==fingerprint and video.exists() and audio.exists():print('CHAPTER_CACHED',key,flush=True);return
 folder=BUILD/'frames'/key/fingerprint[:16];folder.mkdir(parents=True,exist_ok=True);rows=['ffconcat version 1.0'];pcm=bytearray(c['durationFrames']*1600)
 for s in c['scenes']:
  for i,f in enumerate(s['renderFrames']):
   path=folder/(s['id']+f'-{f:06}.png')
   if not path.exists():draw.render(s,f).save(path,compress_level=1)
   end=s['renderFrames'][i+1] if i+1<len(s['renderFrames']) else s['durationFrames']
   rows.extend([f"file '{path.as_posix()}'",'option framerate 30',f'duration {(end-f)/30:.9f}'])
  with wave.open(str(ROOT/'public'/s['audio'])) as w:data=w.readframes(w.getnframes())
  at=(s['startFrame']-c['startFrame']+s['leadFrames'])*1600;pcm[at:at+len(data)]=data
 rows.extend([f"file '{path.as_posix()}'",'option framerate 30']);listing=BUILD/(key+'.ffconcat');listing.write_text('\n'.join(rows)+'\n',encoding='utf8')
 raw=BUILD/(key+'.raw.wav')
 with wave.open(str(raw),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm)
 run(['-i',str(raw),'-af',f'loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,apad,atrim=end_sample={c["durationFrames"]*1600}','-c:a','pcm_s16le',str(audio)],BUILD/(key+'.audio.log'))
 run(['-f','concat','-safe','0','-i',str(listing),'-an','-fps_mode','vfr','-enc_time_base','1:30','-t',f'{c["durationFrames"]/30:.9f}','-c:v','libx264','-preset','veryfast','-crf','18','-bf','0','-g','60','-pix_fmt','yuv420p','-threads','2','-video_track_timescale','30000','-movflags','+faststart',str(video)],BUILD/(key+'.video.log'))
 tag.write_text(fingerprint);print('CHAPTER_DONE',key,round(c['durationFrames']/30,2),'seconds',flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--workers',type=int,default=3);p.add_argument('--chapter');p.add_argument('--partial',action='store_true');a=p.parse_args();t=load(ROOT/'public/timeline.json');course=load(ROOT/'public/course.json');assert t['scope']=='complete' or a.partial
 for s in t['scenes']:
  source=ROOT/'public'/s['audio'];assert hashlib.sha256(source.read_bytes()).hexdigest()==s['audioSha256'],('Audio changed after timeline',s['id'])
 h=hashlib.sha256((ROOT/'scripts/draw.py').read_bytes()+pathlib.Path(__file__).read_bytes())
 h.update(pathlib.Path('C:/Windows/Fonts/msyh.ttc').read_bytes())
 for item in course['sourceAssets'].values():h.update(item['sha256'].encode())
 for c in t['chapters']:c['fingerprint']=hashlib.sha256((h.hexdigest()+json.dumps(c,ensure_ascii=False,sort_keys=True)).encode()).hexdigest()
 (BUILD/'render-manifest.json').write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf8');selected=[c for c in t['chapters'] if not a.chapter or c['key']==a.chapter]
 with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as pool:list(pool.map(chapter,selected))
 if a.chapter or a.partial:return
 for kind,ext in [('videos','.mp4'),('audios','.wav')]:
  (BUILD/(kind+'.ffconcat')).write_text('ffconcat version 1.0\n'+''.join(f"file '{c['key']+ext}'\nduration {c['durationFrames']/30:.9f}\n" for c in t['chapters']),encoding='utf8')
 staged=FINAL.with_name(FINAL.stem+'.rendering.mp4')
 run(['-f','concat','-safe','0','-i',str(BUILD/'videos.ffconcat'),'-f','concat','-safe','0','-i',str(BUILD/'audios.ffconcat'),'-f','ffmetadata','-i',str(BUILD/'chapters.ffmetadata'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-af',f'asetpts=N/SR/TB,apad,atrim=end_sample={t["totalFrames"]*1600}','-c:a','aac','-b:a','128k','-ar','48000','-t',f'{t["duration"]:.9f}','-video_track_timescale','30000','-movflags','+faststart',str(staged)],BUILD/'final-mux.log')
 staged.replace(FINAL);print('FINAL_DONE',str(FINAL),FINAL.stat().st_size,flush=True)
if __name__=='__main__':main()
