"""Read the final MP4 and inspect actual selection colors at every encoded state."""
import bisect,hashlib,json,pathlib,subprocess
import numpy as np
import draw
from highlight_sync import selected_lines
ROOT=pathlib.Path(__file__).resolve().parents[1];VIDEO=ROOT/'out/一小时学完JavaScript_零基础_无字幕_动态高亮修正版.mp4'
def main():
    t=json.loads((ROOT/'public/timeline-highlighted.json').read_text(encoding='utf8'));starts=[s['startFrame'] for s in t['scenes']]
    data=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(VIDEO)]));pts=[round(float(v['best_effort_timestamp_time'])*30) for v in data['frames']]
    required={s['startFrame']+c['beginFrame'] for s in t['scenes'] for c in s['codeCues']};assert required<=set(pts)
    proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(VIDEO),'-an','-vf','scale=480:270','-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    seen=set();checks=0
    for frame in pts:
        buf=bytearray();size=480*270*3
        while len(buf)<size:
            chunk=proc.stdout.read(size-len(buf))
            if not chunk:break
            buf.extend(chunk)
        assert len(buf)==size
        image=np.frombuffer(buf,dtype=np.uint8).reshape(270,480,3).astype(float);s=t['scenes'][bisect.bisect_right(starts,frame)-1]
        if s['kind']=='cover':continue
        local=frame-s['startFrame'];selected=selected_lines(s,local);visual=0
        for logical,line in enumerate(s['code'].splitlines(),1):
            for _ in draw.wrap(line,1190,34,True) or ['']:
                rgb=image[int((247+visual*40+20)/4),338];expected=np.array([36,65,90] if logical in selected else [16,34,55]);assert np.max(np.abs(rgb-expected))<12,(s['key'],frame,logical,rgb.tolist(),selected)
                checks+=1;visual+=1
        seen.add(s['key'])
    proc.stdout.close();err=proc.stderr.read();assert proc.wait()==0,err;assert len(seen)==59
    report=dict(allPassed=True,videoSha256=hashlib.sha256(VIDEO.read_bytes()).hexdigest(),codedPagesChecked=len(seen),encodedStatesChecked=len(pts),linePixelChecks=checks,requiredHighlightFrames=len(required),allRequiredFramesPresent=True,method='decode actual MP4; inspect highlight/panel colors on every displayed code row and every encoded frame')
    (ROOT/'build/highlight-video-verification.json').write_text(json.dumps(report,indent=2),encoding='utf8');print('ACTUAL_VIDEO_HIGHLIGHTS_VERIFIED',json.dumps(report),flush=True)
if __name__=='__main__':main()
