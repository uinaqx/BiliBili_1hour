"""Independently locate every semantic unit in the actual encoded AAC waveform."""
import hashlib,json,pathlib,subprocess,wave
import numpy as np
from scipy.signal import correlate
ROOT=pathlib.Path(__file__).resolve().parents[1];RATE=24000
def main():
    t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));assert t['scope']=='complete-course'
    video=ROOT/'out/一小时学完计算机网络_百炼3.1Plus许南川_1.05倍速.mp4'
    pcm=ROOT/'build/final-audio-placement.s16'
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-vn','-ac','1','-ar',str(RATE),'-c:a','pcm_s16le','-f','s16le',str(pcm)],check=True)
    actual=np.memmap(pcm,dtype='<i2',mode='r');records=[]
    for s in t['scenes']:
        source=ROOT/'public'/s['audio']
        with wave.open(str(source)) as f:assert f.getframerate()==RATE;reference=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2')
        meta=json.loads(source.with_suffix('.json').read_text(encoding='utf8'))
        for p in meta['parts']:
            for label,start in [('begin',p['onset']+.3),('end',p['end']-1.7)]:
                a=round(start*RATE);n=round(1.2*RATE);ref=reference[a:a+n].astype(np.float64)
                assert len(ref)==n and np.std(ref)>15,(s['key'],p['index'],label,'reference is silent')
                expected=round((s['startFrame']+s['leadFrames'])/30*RATE)+a
                radius=round(.35*RATE);lo=max(0,expected-radius);hi=min(len(actual),expected+n+radius)
                segment=actual[lo:hi].astype(np.float64);ref-=ref.mean()
                numerator=correlate(segment,ref,mode='valid',method='fft')
                sums=np.r_[0,np.cumsum(segment)];squares=np.r_[0,np.cumsum(segment**2)]
                energy=squares[n:]-squares[:-n]-(sums[n:]-sums[:-n])**2/n
                score=numerator/np.sqrt(np.maximum(energy,1)*np.dot(ref,ref))
                index=int(np.argmax(score));deviation=(lo+index-expected)/RATE;coefficient=float(score[index])
                assert abs(deviation)<=.06 and coefficient>=.8,(s['key'],p['index'],label,deviation,coefficient)
                records.append(dict(key=s['key'],part=p['index'],sample=label,secondsDeviation=deviation,correlation=coefficient))
    report=dict(allPassed=True,semanticUnits=sum(len(s['parts']) for s in t['scenes']),waveformSamples=len(records),maxSecondsDeviation=max(abs(x['secondsDeviation']) for x in records),minimumCorrelation=min(x['correlation'] for x in records),scope='beginning and end waveform match for every semantic unit in final AAC; does not independently judge teaching semantics',videoSha256=hashlib.sha256(video.read_bytes()).hexdigest(),timelineSha256=hashlib.sha256((ROOT/'public/timeline.json').read_bytes()).hexdigest(),samples=records)
    (ROOT/'build/audio-placement.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in report.items() if k!='samples'},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
