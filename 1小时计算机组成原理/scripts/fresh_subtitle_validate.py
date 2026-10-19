"""Validate newly transcribed captions against their actual CFR video display.

Only the clean source MP4 and fresh recognition manifest are used. This is a
display/audio-integrity check, separate from the independent acoustic QA.
"""
import bisect,pathlib,subprocess,sys
import numpy as np
from fresh_subtitle_render import ROOT,BASE,OUT,DEL,SOURCE,FINAL,HEADER,load,save,probe,dialogue
sys.stdout.reconfigure(encoding='utf-8')
W,H=580,37

def selection_expr(numbers):
    if len(numbers)==1:return f'eq(n,{numbers[0]})'
    mid=len(numbers)//2
    return f'if(lt(n,{numbers[mid]}),{selection_expr(numbers[:mid])},{selection_expr(numbers[mid:])})'

def identity(m):
    caps=m['captions'];points={0,m['totalFrames']-1}
    for c in caps:points.update([max(0,c['startFrame']-1),c['startFrame'],c['endFrame']-1,min(m['totalFrames']-1,c['endFrame'])])
    points=sorted(points)
    image=OUT/'reference-background.png'
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(SOURCE),'-frames:v','1',str(image)],check=True)
    (OUT/'reference.ass').write_text(HEADER+'\n'.join(dialogue(c,i,i+1) for i,c in enumerate(caps))+'\n',encoding='utf-8-sig')
    crop='crop=1740:110:90:955,scale=580:37,format=gray'
    refraw=subprocess.check_output(['ffmpeg','-v','error','-loop','1','-framerate','30','-i',str(image),'-frames:v',str(len(caps)),'-vf','format=yuv420p,ass=build/fresh-subtitles-20261019/render/reference.ass,'+crop,'-f','rawvideo','-pix_fmt','gray','-'],cwd=ROOT)
    refs=np.frombuffer(refraw,dtype=np.uint8).reshape(len(caps),H,W)
    graph=OUT/'identity-select.filter';graph.write_text("select='"+selection_expr(points)+"',"+crop,encoding='utf-8')
    proc=subprocess.Popen(['ffmpeg','-v','error','-threads','4','-i',str(FINAL),'-an','-filter_script:v',str(graph),'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','gray','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    starts=[c['startFrame'] for c in caps];bad=[];ncc=[];seen=set();index=0
    while True:
        data=bytearray()
        while len(data)<W*H:
            b=proc.stdout.read(W*H-len(data))
            if not b:break
            data.extend(b)
        if not data:break
        assert len(data)==W*H and index<len(points)
        frame=points[index];j=bisect.bisect_right(starts,frame)-1
        wanted=j>=0 and frame<caps[j]['endFrame'];gray=np.frombuffer(data,dtype=np.uint8).reshape(H,W)
        if wanted:
            correlation=float(np.corrcoef(refs[j].ravel(),gray.ravel())[0,1]);ncc.append(correlation);seen.add(j)
            if correlation<.97:bad.append(dict(frame=frame,cue=j,text=caps[j]['text'],correlation=correlation))
        else:
            pixels=int(np.count_nonzero(gray>170))
            if pixels>5:bad.append(dict(frame=frame,cue=None,unexpectedCaptionPixels=pixels))
        index+=1
    err=proc.stderr.read().decode(errors='replace');assert proc.wait()==0,err
    report=dict(framesChecked=index,captionsChecked=len(seen),minimumCaptionImageCorrelation=min(ncc),unexpectedDisplayStates=bad)
    save(OUT/'display-check.json',report)
    assert index==len(points) and len(seen)==len(caps) and not bad,bad[:8]
    print('FRESH_DISPLAY_CHECK',index,'frames',len(seen),'distinct captions',flush=True)
    return report

def gray_at(path,at):
    return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-ss',f'{max(0,at):.8f}','-i',str(path),'-frames:v','1','-an','-vf','crop=1920:920:0:0,scale=480:230,format=gray','-f','rawvideo','-pix_fmt','gray','-']),dtype=np.uint8)

def visual(m):
    packets=probe(SOURCE,'-select_streams','v:0','-show_packets','-show_entries','packet=pts_time')['packets'];times=[float(p['pts_time']) for p in packets]
    comparisons=[]
    for chapter in m['chapters']:
        a=chapter['startFrame']/30;b=(chapter['startFrame']+chapter['durationFrames'])/30
        for at in [a,(a+b)/2,max(a,b-.1)]:
            held=times[bisect.bisect_right(times,at+1e-7)-1]
            original=gray_at(SOURCE,held-.00001);actual=gray_at(FINAL,math_floor_frame(at))
            score=float(np.corrcoef(original,actual)[0,1]);comparisons.append(dict(time=at,correlation=score))
            assert score>.995,(chapter['key'],at,score)
    save(OUT/'visual-check.json',comparisons)
    print('FRESH_VISUAL_CHECK',len(comparisons),'comparisons',flush=True)
    return comparisons

def math_floor_frame(at):return int(at*30+1e-6)/30
def main():
    m=load(OUT/'manifest.json');display=identity(m);visual_report=visual(m)
    with (OUT/'strict-decode.log').open('w',encoding='utf-8') as log:
        subprocess.run(['ffmpeg','-v','error','-xerror','-threads','4','-i',str(FINAL),'-map','0:v:0','-map','0:a:0','-f','null','-'],check=True,stdout=log,stderr=subprocess.STDOUT)
    report=dict(allPassed=True,durationSeconds=m['duration'],captionCount=len(m['captions']),displayCheck=display,visualComparisons=len(visual_report),minimumVisualCorrelation=min(x['correlation'] for x in visual_report),audioIntegrity=load(OUT/'audio-proof.json'),strictDecodePassed=True)
    save(OUT/'validation.json',report)
    print('FRESH_VALIDATION_PASSED',flush=True)
if __name__=='__main__':main()
