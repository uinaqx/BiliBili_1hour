"""Verify rendered cue identity at every video packet, not merely cue presence."""
import bisect,json,pathlib,subprocess,sys
import numpy as np
from subtitle_sync_v2 import ROOT,BUILD,OUT,DEL,FINAL,load,save
from subtitle_calibrate import ass_time
sys.stdout.reconfigure(encoding='utf-8')
W,H=580,37

def main():
    t=load(OUT/'timeline.json');old=load(OUT/'previous-timeline.json')
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-show_chapters','-of','json',str(FINAL)]))
    assert abs(float(info['format']['duration'])-t['duration'])<.002
    assert len(info['chapters'])==12
    for c,a in zip(t['chapters'],info['chapters']):
        assert abs(c['startFrame']/30-float(a['start_time']))<.002
    assert t['renderJobs']==old['renderJobs'] and t['duration']==old['duration']
    for new,prior in zip(t['scenes'],old['scenes']):
        assert {k:v for k,v in new.items() if k!='captions'}=={k:v for k,v in prior.items() if k!='captions'}
    packets=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts_time,duration_time','-of','json',str(FINAL)]))['packets']
    expected=[(c['startFrame']+e['frame'],e['frames']) for c in t['chapters'] for e in c['images']]
    assert len(packets)==len(expected)
    for p,(f,d) in zip(packets,expected):
        assert abs(float(p['pts_time'])*30-f)<.002
        assert abs(float(p['duration_time'])*30-d)<.002
    # Construct a text-only reference strip for every caption, each occupying
    # a distinct frame. This catches a wrong next line even when subtitles
    # remain visible in both the intended and actual encoded frame.
    header=(OUT/'00.ass').read_text(encoding='utf-8-sig').split('Dialogue:')[0]
    lines=[f"Dialogue: 0,{ass_time(i)},{ass_time(i+1)},Default,,0,0,0,,{c['text']}" for i,c in enumerate(t['captions'])]
    (OUT/'reference.ass').write_text(header+'\n'.join(lines)+'\n',encoding='utf-8-sig')
    crop='crop=1740:110:90:955,scale=580:37,format=gray'
    data=subprocess.check_output(['ffmpeg','-v','error','-loop','1','-framerate','30','-i',str(ROOT/'public'/t['renderJobs'][0]['path']),'-frames:v',str(len(lines)),'-vf','format=yuv420p,ass=build/subtitle-sync-v2/reference.ass,'+crop,'-f','rawvideo','-pix_fmt','gray','-'],cwd=ROOT)
    refs=np.frombuffer(data,dtype=np.uint8).reshape(len(lines),H,W)
    starts=[c['startFrame'] for c in t['captions']]
    proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(FINAL),'-an','-vf',crop,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','gray','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    i=0;bad=[];ious=[];correlations=[];cue_seen=set()
    while True:
        raw=bytearray()
        while len(raw)<W*H:
            b=proc.stdout.read(W*H-len(raw))
            if not b:break
            raw.extend(b)
        if not raw:break
        assert len(raw)==W*H
        f=expected[i][0];j=bisect.bisect_right(starts,f)-1
        visible=j>=0 and f<t['captions'][j]['endFrame']
        gray=np.frombuffer(raw,dtype=np.uint8).reshape(H,W);actual=gray>170
        if visible:
            ref=refs[j]>170;union=np.count_nonzero(ref|actual)
            iou=np.count_nonzero(ref&actual)/max(1,union);ious.append(iou);cue_seen.add(j)
            # H.264 slightly changes antialiasing values across a hard white
            # threshold. Compare the complete centred grayscale text instead.
            correlation=float(np.corrcoef(refs[j].ravel(),gray.ravel())[0,1]);correlations.append(correlation)
            if correlation<.97:bad.append(dict(frame=f,cue=j,text=t['captions'][j]['text'],iou=iou,correlation=correlation))
        elif np.count_nonzero(actual)>5:bad.append(dict(frame=f,cue=None,unexpectedCaptionPixels=int(np.count_nonzero(actual))))
        i+=1
    err=proc.stderr.read().decode(errors='replace');assert proc.wait()==0,err
    report=dict(durationSeconds=t['duration'],chapters=len(t['chapters']),captions=len(t['captions']),encodedFramesChecked=i,captionIdentitiesChecked=len(cue_seen),minTextMaskIoU=min(ious),minTextImageCorrelation=min(correlations),bad=bad,audioProof=load(OUT/'audio-proof.json'),visualContentAndTimingUnchanged=True)
    save(OUT/'validation.json',report)
    print('ACTUAL_CUE_IDENTITY_CHECK',i,'captions',len(cue_seen),'minCorrelation',round(min(correlations),4),'mismatches',len(bad),flush=True)
    assert i==len(expected) and len(cue_seen)==len(lines) and not bad,bad[:8]
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(FINAL),'-map','0:v:0','-map','0:a:0','-f','null','-'],check=True)
    report.update(strictDecodePassed=True,allPassed=True);save(OUT/'validation.json',report)
    print('V2_VALIDATED',flush=True)
if __name__=='__main__':main()
