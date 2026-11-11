"""Check actual encoded subtitle frames, chapters, audio alignment and complete decoding."""
import bisect,json,pathlib,subprocess,wave,hashlib
import numpy as np
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out';VIDEO=DEL/'一小时学完JavaScript_零基础_含字幕.mp4'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    t=load(ROOT/'public/timeline.json');assert t['scope']=='complete' and len(t['scenes'])==60 and len(t['chapters'])==10 and t['subtitles']
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-show_chapters','-of','json',str(VIDEO)]));assert abs(float(probe['format']['duration'])-t['duration'])<.06
    video=next(s for s in probe['streams'] if s['codec_type']=='video');audio=next(s for s in probe['streams'] if s['codec_type']=='audio');assert (video['width'],video['height'],video['codec_name'],audio['codec_name'])==(1920,1080,'h264','aac')
    assert len(probe['chapters'])==10
    for a,b in zip(probe['chapters'],t['chapters']):assert abs(float(a['start_time'])-b['startFrame']/30)<.002
    expected=[]
    for c in t['chapters']:
        expected.extend(dict(frame=c['startFrame']+v['frame'],path=v['path']) for v in load(ROOT/'build/render'/(c['key']+'.events.json')))
    ticks=[v['frame'] for v in expected]
    ff=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(VIDEO)]));pts=[round(float(f['best_effort_timestamp_time'])*30) for f in ff['frames']]
    assert set(ticks)<=set(pts),'Missing subtitle or visual event frame'
    proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(VIDEO),'-an','-vf','scale=480:270','-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    errors=[];ious=[];scene_seen=set();size=480*270*3;scene_starts=[s['startFrame'] for s in t['scenes']]
    for i,f in enumerate(pts):
        raw=bytearray()
        while len(raw)<size:
            chunk=proc.stdout.read(size-len(raw))
            if not chunk:break
            raw.extend(chunk)
        assert len(raw)==size,('Short decode',i)
        actual=np.frombuffer(raw,dtype=np.uint8).reshape(270,480,3).astype(float)
        ref=expected[bisect.bisect_right(ticks,f)-1]
        with Image.open(ref['path']) as im:target=np.array(im.convert('RGB').resize((480,270),Image.Resampling.BICUBIC)).astype(float)
        mae=float(np.mean(np.abs(actual-target)));errors.append(mae)
        a=np.min(actual[246:,:,:],axis=2)>180;b=np.min(target[246:,:,:],axis=2)>180
        union=np.logical_or(a,b).sum();iou=float(np.logical_and(a,b).sum()/union) if union else 1.
        if b.sum()>15:assert iou>.63,('Subtitle pixels',i,f,iou)
        else:assert a.sum()<20,('Stale subtitle',i,f,int(a.sum()))
        assert mae<8,(i,f,mae)
        ious.append(iou);scene_seen.add(t['scenes'][bisect.bisect_right(scene_starts,f)-1]['key'])
    proc.stdout.close();stderr=proc.stderr.read();assert proc.wait()==0,stderr.decode(errors='replace');assert len(scene_seen)==60
    wav=ROOT/'build/final-audio-8000.wav';subprocess.run(['ffmpeg','-y','-v','error','-i',str(VIDEO),'-vn','-ar','8000','-ac','1','-c:a','pcm_s16le',str(wav)],check=True)
    with wave.open(str(wav),'rb') as f:decoded=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(float)
    correlations=[]
    for c in t['chapters']:
        for s in [c['scenes'][0],c['scenes'][-1]]:
            with wave.open(str(ROOT/'public'/s['audio']),'rb') as f:source=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(float)[::3]
            offset=round((s['startFrame']+s['leadFrames'])/30*8000);a=source[8000:64000];b=decoded[offset+8000:offset+8000+len(a)];corr=float(np.corrcoef(a,b)[0,1]);assert corr>.90,(s['key'],corr);correlations.append(corr)
    plan=load(ROOT/'build/subtitles/subtitle-plan.json');assert all(c['end']>=c['spokenEnd'] for c in plan['cues'])
    out=dict(allPassed=True,duration=t['duration'],chapters=10,scenes=60,voiceClips=120,subtitles=len(plan['cues']),encodedFrames=len(pts),allSubtitleBoundaryFramesPresent=True,meanFrameMAE=float(np.mean(errors)),maxFrameMAE=max(errors),minSubtitleIoU=min(ious),audioComparisons=len(correlations),minAudioCorrelation=min(correlations),fullDecode=True,videoSha256=digest(VIDEO),timelineSha256=digest(ROOT/'public/timeline.json'),subtitlePlanSha256=digest(ROOT/'build/subtitles/subtitle-plan.json'),scope='Full encoded-state and subtitle-pixel comparison; 20 audio excerpts checked for timing; not a claim of listening to every sentence')
    (ROOT/'build/final-verification.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print('FINAL_VERIFIED',json.dumps(out),flush=True)
if __name__=='__main__':main()
