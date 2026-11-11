"""Rebuild the original base frames; preserve source audio and chapters byte-for-byte."""
import bisect,concurrent.futures,hashlib,json,pathlib,subprocess
import numpy as np
from PIL import Image
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build/no-subtitles';DEL=ROOT/'out'
SOURCE=DEL/'一小时学完JavaScript_零基础_含字幕.mp4';FINAL=DEL/'一小时学完JavaScript_零基础_无字幕.mp4'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,log):
    with log.open('w',encoding='utf8') as f:subprocess.run(['ffmpeg','-y','-v','warning',*args],stdout=f,stderr=subprocess.STDOUT,check=True)
def chapter(c):
    folder=BUILD/c['key'];folder.mkdir(parents=True,exist_ok=True);events=[];old=load(ROOT/'build/render'/(c['key']+'.events.json'));ticks=[x['frame'] for x in old]
    for s in c['scenes']:
        for f in s['renderFrames']:
            image=draw.render(s,f);global_frame=s['startFrame']-c['startFrame']+f
            reference=old[bisect.bisect_right(ticks,global_frame)-1]
            with Image.open(reference['path']) as original:
                assert np.array_equal(np.asarray(image)[:975],np.asarray(original.convert('RGB'))[:975]),('Non-subtitle area changed',s['key'],f)
            path=folder/f'{s["key"]}-{f:06}.png';image.save(path,compress_level=1);events.append(dict(frame=global_frame,path=str(path)))
    rows=['ffconcat version 1.0']
    for i,v in enumerate(events):
        end=events[i+1]['frame'] if i+1<len(events) else c['durationFrames']
        rows.extend([f"file '{pathlib.Path(v['path']).as_posix()}'",'option framerate 30',f"duration {(end-v['frame'])/30:.9f}"])
    rows.extend([f"file '{pathlib.Path(events[-1]['path']).as_posix()}'",'option framerate 30']);listing=BUILD/(c['key']+'.ffconcat');listing.write_text('\n'.join(rows)+'\n',encoding='utf8')
    run(['-f','concat','-safe','0','-i',str(listing),'-an','-fps_mode','vfr','-enc_time_base','1:30','-t',str(c['durationFrames']/30),'-c:v','libx264','-preset','veryfast','-crf','19','-bf','0','-g','60','-pix_fmt','yuv420p','-threads','2','-video_track_timescale','30000',str(BUILD/(c['key']+'.mp4'))],BUILD/(c['key']+'.log'))
    (BUILD/(c['key']+'.events.json')).write_text(json.dumps(events),encoding='utf8');print('NO_SUBTITLE_CHAPTER',c['key'],len(events),flush=True)
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-show_chapters','-of','json',str(p)]))
def audio_hash(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],encoding='utf8').strip()
def main():
    BUILD.mkdir(parents=True,exist_ok=True);t=load(ROOT/'public/timeline.json');original_timeline=sha(ROOT/'public/timeline.json');manifest=load(ROOT/'build/render/manifest.json');assert manifest['timelineSha256']==original_timeline
    before=probe(SOURCE)
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:list(pool.map(chapter,manifest['chapters']))
    listing=BUILD/'chapters.ffconcat';listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{c['key']}.mp4'\nduration {c['durationFrames']/30:.9f}\n" for c in t['chapters']),encoding='utf8')
    pending=FINAL.with_name(FINAL.stem+'.rendering.mp4')
    run(['-f','concat','-safe','0','-i',str(listing),'-i',str(SOURCE),'-map','0:v:0','-map','1:a:0','-map_metadata','1','-map_chapters','1','-c:v','copy','-c:a','copy','-sn','-video_track_timescale','30000','-movflags','+faststart',str(pending)],BUILD/'mux.log')
    after=probe(pending);assert abs(float(before['format']['duration'])-float(after['format']['duration']))<.01;assert before['chapters']==after['chapters'];assert audio_hash(SOURCE)==audio_hash(pending);assert not any(s['codec_type']=='subtitle' for s in after['streams'])
    events=[]
    for c in t['chapters']:events.extend(dict(frame=c['startFrame']+v['frame'],path=v['path']) for v in load(BUILD/(c['key']+'.events.json')))
    ticks=[e['frame'] for e in events]
    frames=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(pending)]))['frames'];pts=[round(float(f['best_effort_timestamp_time'])*30) for f in frames];assert set(ticks)<=set(pts)
    proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(pending),'-an','-vf','scale=480:270','-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE);maes=[]
    for i,f in enumerate(pts):
        raw=bytearray();size=480*270*3
        while len(raw)<size:
            b=proc.stdout.read(size-len(raw))
            if not b:break
            raw.extend(b)
        assert len(raw)==size
        actual=np.frombuffer(raw,dtype=np.uint8).reshape(270,480,3).astype(float)
        with Image.open(events[bisect.bisect_right(ticks,f)-1]['path']) as im:expected=np.array(im.convert('RGB').resize((480,270),Image.Resampling.BICUBIC)).astype(float)
        mae=float(np.mean(np.abs(actual-expected)));assert mae<8,(i,mae);maes.append(mae)
        assert np.max(actual[249:,:,:])<60,('Burned subtitle remains',i)
    proc.stdout.close();errors=proc.stderr.read();assert proc.wait()==0,errors
    subprocess.run(['ffmpeg','-v','error','-i',str(pending),'-f','null','-'],check=True,stdout=subprocess.DEVNULL)
    assert sha(ROOT/'public/timeline.json')==original_timeline;pending.replace(FINAL)
    report=dict(allPassed=True,subtitles=False,duration=float(after['format']['duration']),chaptersPreserved=True,audioBitstreamIdentical=True,nonSubtitleSourcePixelsIdentical=True,allEncodedFramesChecked=len(pts),maxFrameMAE=max(maes),bottomBandClear=True,fullDecode=True,sourceSha256=sha(SOURCE),videoSha256=sha(FINAL),timelineSha256=original_timeline)
    (BUILD/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('NO_SUBTITLE_FINAL',str(FINAL),json.dumps(report),flush=True)
if __name__=='__main__':main()
