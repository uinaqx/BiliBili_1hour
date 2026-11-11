"""Burn subtitles into every exact cue-boundary state, then encode sparse VFR frames."""
import argparse,bisect,concurrent.futures,hashlib,json,math,pathlib,subprocess,wave
from PIL import ImageDraw
import draw
from subtitle_sync import build_project,write_tracks,sha
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build/render';DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def run(args,path):
    with path.open('w',encoding='utf8') as log:
        subprocess.run(['ffmpeg','-y','-v','warning',*args],stdout=log,stderr=subprocess.STDOUT,check=True)
def caption_frame(s,f,caps):
    image=draw.render(s,f);d=ImageDraw.Draw(image)
    active=next((c for c in caps if c['startFrame']<=f<c['endFrame']),None)
    if active:
        text=active['text'];rows=draw.wrap(text,1730,38)
        assert len(rows)<=2,(s['key'],'caption too long',text)
        top=1000 if len(rows)==1 else 978
        d.rounded_rectangle((66,top-3,1854,top+len(rows)*45+5),9,fill='#07111c')
        for j,row in enumerate(rows):
            x=(1920-draw.font(38).getlength(row))/2;draw.label(d,(x,top+j*45),row,38)
    return image
def chapter(job):
    c,planhash=job;folder=BUILD/c['key']/c['fingerprint'][:16];folder.mkdir(parents=True,exist_ok=True);video=BUILD/(c['key']+'.mp4');tag=video.with_suffix('.hash')
    if video.exists() and tag.exists() and tag.read_text()==c['fingerprint']:return c
    events=[]
    for s in c['scenes']:
        caps=s['renderCaptions'];points=set(s['renderFrames'])
        for cap in caps:points.update([cap['startFrame'],cap['endFrame']])
        for f in sorted(x for x in points if 0<=x<s['durationFrames']):
            path=folder/f'{s["key"]}-{f:06}.png'
            if not path.exists():caption_frame(s,f,caps).save(path,compress_level=1)
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
    plan=build_project(ROOT);write_tracks(plan,ROOT/'build/subtitles')
    byscene={s['key']:[] for s in t['scenes']}
    for c in plan['cues']:
        byscene[c['scene']].append(c)
    sourcehash=hashlib.sha256(b''.join((ROOT/'scripts'/n).read_bytes() for n in ['draw.py','render.py','subtitle_sync.py'])).hexdigest()
    for c in t['chapters']:
        for s in c['scenes']:
            caps=[]
            for cap in byscene[s['key']]:
                caps.append(dict(text=cap['text'],startFrame=math.ceil(cap['start']*30-1e-6)-s['startFrame'],endFrame=math.ceil(cap['end']*30-1e-6)-s['startFrame']))
            s['renderCaptions']=caps
        c['fingerprint']=hashlib.sha256((sourcehash+json.dumps(c,ensure_ascii=False,sort_keys=True)).encode()).hexdigest()
    (BUILD/'manifest.json').write_text(json.dumps(dict(timelineSha256=sha(ROOT/'public/timeline.json'),subtitlePlanSha256=sha(ROOT/'build/subtitles/subtitle-plan.json'),chapters=t['chapters']),ensure_ascii=False,indent=2),encoding='utf8')
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
    name='内部试片_含字幕.mp4' if a.preview else '一小时学完JavaScript_零基础_含字幕.mp4';final=DEL/name;temp=final.with_name(final.stem+'.rendering.mp4')
    run(['-f','concat','-safe','0','-i',str(listing),'-i',str(audio),'-f','ffmetadata','-i',str(ROOT/'build/chapters.ffmetadata'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','aac','-b:a','160k','-t',str(total/30),'-video_track_timescale','30000','-movflags','+faststart',str(temp)],BUILD/'mux.log');temp.replace(final)
    if not a.preview:
        import shutil
        shutil.copy2(ROOT/'build/subtitles/subtitles.srt',DEL/'中文字幕.srt')
    print('VIDEO_RENDERED',str(final),total/30,flush=True)
if __name__=='__main__':main()
