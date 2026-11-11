"""Replace only the opening title frames, reusing all other video chapters and audio."""
import hashlib,json,pathlib,subprocess
import numpy as np
from PIL import Image
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build/title-revision';DEL=ROOT/'out'
SOURCE=DEL/'一小时学完JavaScript_零基础_无字幕.mp4';FINAL=DEL/'一小时学完JavaScript_零基础_无字幕_标题加大版.mp4'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def run(args,name):
    with (BUILD/name).open('w',encoding='utf8') as f:subprocess.run(['ffmpeg','-y','-v','warning',*args],stdout=f,stderr=subprocess.STDOUT,check=True)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_chapters','-of','json',str(p)]))
def ahash(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],encoding='utf8').strip()
def main():
    BUILD.mkdir(parents=True,exist_ok=True);t=load(ROOT/'public/timeline.json');s=t['scenes'][0];events=load(ROOT/'build/no-subtitles/01.events.json');updated=[]
    for e in events:
        if e['frame']<s['durationFrames']:
            image=draw.render(s,e['frame']);path=BUILD/pathlib.Path(e['path']).name
            with Image.open(e['path']) as old:
                a=np.asarray(image).copy();b=np.asarray(old.convert('RGB')).copy();a[200:565,80:1200]=0;b[200:565,80:1200]=0;assert np.array_equal(a,b)
            image.save(path);updated.append(dict(e,path=str(path)))
        else:updated.append(e)
    draw.render(s,0).save(DEL/'开头标题预览.png')
    rows=['ffconcat version 1.0'];c=t['chapters'][0]
    for i,e in enumerate(updated):
        end=updated[i+1]['frame'] if i+1<len(updated) else c['durationFrames'];rows.extend([f"file '{pathlib.Path(e['path']).as_posix()}'",'option framerate 30',f"duration {(end-e['frame'])/30:.9f}"])
    rows.extend([f"file '{pathlib.Path(updated[-1]['path']).as_posix()}'",'option framerate 30']);listing=BUILD/'first.ffconcat';listing.write_text('\n'.join(rows)+'\n',encoding='utf8')
    run(['-f','concat','-safe','0','-i',str(listing),'-an','-fps_mode','vfr','-enc_time_base','1:30','-t',str(c['durationFrames']/30),'-c:v','libx264','-preset','veryfast','-crf','19','-bf','0','-g','60','-threads','2','-pix_fmt','yuv420p','-video_track_timescale','30000',str(BUILD/'01.mp4')],'first.log')
    listing=BUILD/'chapters.ffconcat';listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{((BUILD if i==0 else ROOT/'build/no-subtitles')/(c['key']+'.mp4')).as_posix()}'\nduration {c['durationFrames']/30:.9f}\n" for i,c in enumerate(t['chapters'])),encoding='utf8')
    pending=FINAL.with_name(FINAL.stem+'.rendering.mp4')
    run(['-f','concat','-safe','0','-i',str(listing),'-i',str(SOURCE),'-map','0:v:0','-map','1:a:0','-map_metadata','1','-map_chapters','1','-c','copy','-sn','-video_track_timescale','30000','-movflags','+faststart',str(pending)],'mux.log')
    before=probe(SOURCE);after=probe(pending);assert before['chapters']==after['chapters'];assert abs(float(before['format']['duration'])-float(after['format']['duration']))<.002;assert ahash(SOURCE)==ahash(pending)
    subprocess.run(['ffmpeg','-v','error','-i',str(pending),'-f','null','-'],check=True,stdout=subprocess.DEVNULL);pending.replace(FINAL)
    (BUILD/'verification.json').write_text(json.dumps(dict(allPassed=True,titleSizes=[156,100],font='Microsoft YaHei Bold',titleOnlySourcePixelChange=True,audioIdentical=True,chaptersIdentical=True,duration=float(after['format']['duration']),fullDecode=True,videoSha256=hashlib.sha256(FINAL.read_bytes()).hexdigest()),indent=2),encoding='utf8');print('TITLE_REVISION_DONE',str(FINAL),flush=True)
if __name__=='__main__':main()
