"""Read-only waveform check of cue onsets in the frozen narration."""
import wave
import numpy as np
from subtitle_sync_v2 import ROOT,OUT,load,save

def main():
    timeline=load(OUT/'timeline.json');bad=[];total=0
    for s in timeline['scenes']:
        with wave.open(str(ROOT/'public/audio'/f"{s['key']}.wav"),'rb') as f:
            y=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(float)/32768
        hop=120
        rms=np.sqrt(np.mean(y[:len(y)//hop*hop].reshape(-1,hop)**2,axis=1))
        active=rms>max(.0006,np.percentile(rms,90)*.015)
        for i,c in enumerate(s['captions']):
            total+=1;k=round(c['start']/.005)
            if not np.any(active[max(0,k-2):min(len(active),k+8)]):
                following=np.flatnonzero(active[k:min(len(active),k+100)])
                gap=following[0]*.005 if len(following) else None
                bad.append(dict(scene=s['key'],index=i,start=c['start'],text=c['text'],secondsUntilAudible=gap))
    save(OUT/'waveform-review.json',dict(checked=total,quietStarts=bad))
    print('WAVEFORM_START_CHECK',total,'quietStarts',bad,flush=True)
if __name__=='__main__':main()
