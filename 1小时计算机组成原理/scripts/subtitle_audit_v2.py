"""Audit the *delivered* audio clock and independent caption boundaries read-only."""
import json, pathlib, subprocess, sys, wave
import numpy as np
from scipy.signal import correlate, resample_poly
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1]
BUILD=ROOT/'build'
DEL=ROOT/'out'

def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def main():
    t=load(ROOT/'public/timeline.json')
    video=DEL/'一小时学习计算机组成原理_字幕校准版.mp4'
    pcm=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-vn','-ac','1','-ar','8000','-f','f32le','-']),dtype='<f4')
    clocks=[];boundaries=[]
    for s in t['scenes']:
        key=s['key'];origin=(s['startFrame']+s['leadFrames'])/30
        with wave.open(str(ROOT/'public/audio'/f'{key}.wav'),'rb') as f:
            signal=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(float)/32768
        signal=resample_poly(signal,1,3)
        for at in [2.,len(signal)/8000*.5,len(signal)/8000-4.]:
            ref=signal[round(at*8000):round((at+2)*8000)]
            actual=pcm[round((origin+at-.6)*8000):round((origin+at+2.6)*8000)]
            best=int(np.argmax(correlate(actual,ref,mode='valid',method='fft')))
            chosen=actual[best:best+len(ref)]
            score=float(np.dot(ref,chosen)/(np.linalg.norm(ref)*np.linalg.norm(chosen)))
            clocks.append(dict(scene=key,local=at,lagSeconds=best/8000-.6,correlation=score))
        sem=load(BUILD/'subtitle-asr'/f'{key}.json')
        count=load(BUILD/'subtitle-fa'/f'{key}.json')
        for i,c in enumerate(s['captions']):
            a=sem['captions'][i]; b=count['captions'][i]
            boundaries.append(dict(scene=key,index=i,text=c['text'],globalStart=origin+c['start'],display=c['start'],semantic=a['onset'],independent=b['onset'],disagreement=b['onset']-a['onset'],previousSpokenEnd=sem['captions'][i-1]['offset'] if i else None))
    report=dict(audioClockChecks=clocks,maxAudioLag=max(abs(c['lagSeconds']) for c in clocks),minAudioCorrelation=min(c['correlation'] for c in clocks),captionBoundaryChecks=boundaries)
    (BUILD/'subtitle-audit-v2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('AUDIO_CLOCK',len(clocks),report['maxAudioLag'],report['minAudioCorrelation'],flush=True)
    print('LARGEST_INDEPENDENT_DISAGREEMENTS',flush=True)
    for b in sorted(boundaries,key=lambda x:abs(x['disagreement']),reverse=True)[:24]:print(json.dumps(b,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
