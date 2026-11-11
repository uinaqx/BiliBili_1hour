"""Render authored persistent highlights and measured audio without subtitles."""
import argparse,bisect,concurrent.futures,hashlib,json,math,pathlib,subprocess,wave
from PIL import ImageDraw
import draw
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build/render';DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def run(args,path):
    with path.open('w',encoding='utf8') as log:
        subprocess.run(['ffmpeg','-y','-v','warning',*args],stdout=log,stderr=subprocess.STDOUT,check=True)
def chapter(job):
    c,planhash=job;folder=BUILD/c['key']/c['fingerprint'][:16];folder.mkdir(parents=True,exist_ok=True);video=BUILD/(c['key']+'.mp4');tag=video.with_suffix('.hash')
    if video.exists() and tag.exists() and tag.read_text()==c['fingerprint']:return c
    events=[]
    for s in c['scenes']:
        points=set(s['renderFrames'])
        for f in sorted(x for x in points if 0<=x<s['durationFrames']):
            path=folder/f'{s["key"]}-{f:06}.png'
            if not path.exists():draw.render(s,f).save(path,compress_level=1)
            events.append(dict(frame=s['startFrame']-c['startFrame']+f,path=str(path)))
        print('PAGE_RENDERED',s['key'],flush=True)
    rows=['ffconcat version 1.0']
    for i,event in enumerate(events):
        end=events[i+1]['frame'] if i+1<len(events) else c['durationFrames']
        rows.extend([f"file '{pathlib.Path(event['path']).as_posix()}'",'option framerate 30',f"duration {(end-event['frame'])/30:.9f}"])
    rows.extend([f"file '{pathlib.Path(events[-1]['path']).as_posix()}'",'option framerate 30'])
    listing=BUILD/(c['key']+'.ffconcat');listing.write_text('\n'.join(rows)+'\n',encoding='utf8')
    run(['-f','concat','-safe','0','-i',str(listing),'-an','-fps_mode','vfr','-enc_time_base','1:30','-t',str(c['durationFrames']/30),'-c:v','libx264','-preset','veryfast','-crf','19','-bf','0','-g','60','-pix_fmt','yuv420p','-threads','2','-video_track_timescale','30000',str(video)],BUILD/(c['key']+'.log'))
    (BUILD/(c['key']+'.events.json')).write_text(json.dumps(events),encoding='utf8');tag.write_text(c['fingerprint']);return c
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');a=parser.parse_args();t=load(ROOT/'public/timeline.json');assert a.preview or t['scope']=='complete'
    BUILD.mkdir(parents=True,exist_ok=True);DEL.mkdir(parents=True,exist_ok=True)
    sourcehash=hashlib.sha256(b''.join((ROOT/'scripts'/n).read_bytes() for n in ['draw.py','render.py','highlight_sync.py'])).hexdigest()
    for c in t['chapters']:
        c['fingerprint']=hashlib.sha256((sourcehash+json.dumps(c,ensure_ascii=False,sort_keys=True)).encode()).hexdigest()
    (BUILD/'manifest.json').write_text(json.dumps(dict(timelineSha256=sha(ROOT/'public/timeline.json'),subtitles=False,chapters=t['chapters']),ensure_ascii=False,indent=2),encoding='utf8')
    chapters=t['chapters'][:1] if a.preview else t['chapters']
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:list(pool.map(chapter,[(c,sourcehash) for c in chapters]))
    total=chapters[-1]['startFrame']+chapters[-1]['durationFrames'];audio=BUILD/'course.wav'
    with wave.open(str(audio),'wb') as target:
        target.setnchannels(1);target.setsampwidth(2);target.setframerate(24000)
        for s in [s for c in chapters for s in c['scenes']]:
            src=ROOT/'public'/s['audio'];assert sha(src)==s['audioSha256']
            with wave.open(str(src),'rb') as f:pcm=f.readframes(f.getnframes())
            tail=s['durationFrames']*800-s['leadFrames']*800-len(pcm)//2;assert tail>=0
            target.writeframes(bytes(s['leadFrames']*1600)+pcm+bytes(tail*2))
    listing=BUILD/'chapters.ffconcat';listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{c['key']}.mp4'\nduration {c['durationFrames']/30:.9f}\n" for c in chapters),encoding='utf8')
    name='内部试片_无字幕.mp4' if a.preview else '一小时学完TypeScript_零基础_无字幕.mp4';final=DEL/name;temp=final.with_name(final.stem+'.rendering.mp4')
    run(['-f','concat','-safe','0','-i',str(listing),'-i',str(audio),'-f','ffmetadata','-i',str(ROOT/'build/chapters.ffmetadata'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','aac','-b:a','160k','-t',str(total/30),'-video_track_timescale','30000','-movflags','+faststart',str(temp)],BUILD/'mux.log');temp.replace(final)
    print('VIDEO_RENDERED',str(final),total/30,flush=True)
if __name__=='__main__':main()
