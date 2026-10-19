"""Read-only acoustic verification of frozen narration with FunASR fa-zh.

Install optional requirements-subtitles.txt in an isolated environment. Download
funasr/fa-zh (or iic/speech_timestamp_prediction-v1-16k-offline) to
build/subtitle-model/fa-zh. The output contains no synthesized or altered audio.
"""
import argparse, hashlib, json, pathlib, sys, time
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from subtitle_calibrate import ROOT, BUILD, BACKUP, load, save, clean, mapped_words
sys.stdout.reconfigure(encoding='utf-8')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--scene');args=parser.parse_args()
    from funasr import AutoModel
    from funasr.utils import postprocess_utils
    # Keep every character timestamp, including spelled English letters. Default
    # postprocessing joins Latin letters into words, losing caption boundaries.
    postprocess_utils.sentence_postprocess=lambda token,ts:(' '.join(token),ts,token)
    model=AutoModel(model=str(BUILD/'subtitle-model/fa-zh'),device='cpu',ncpu=4,disable_update=True,trust_remote_code=False,disable_pbar=True)
    out=BUILD/'subtitle-fa';out.mkdir(exist_ok=True)
    t=load(BACKUP/'timeline.json');started=time.time()
    for scene in t['scenes']:
        key=scene['key']
        if args.scene and args.scene!=key:continue
        path=ROOT/'public/audio'/f'{key}.wav';sha=hashlib.sha256(path.read_bytes()).hexdigest();dest=out/f'{key}.json'
        if dest.exists() and load(dest).get('audioSha256')==sha:
            print('FA_CACHED',key,flush=True);continue
        chars,meta=mapped_words(key);audio,rate=sf.read(str(path),dtype='float32');assert rate==24000
        audio=resample_poly(audio,2,3);text=' '.join(c['text'] for c in chars)
        result=model.generate(input=(audio,text),data_type=('sound','text'),fs=16000,disable_pbar=True)[0]
        times=result['timestamp'];assert len(times)==len(chars),(key,len(times),len(chars))
        caps=[];position=0
        for i,c in enumerate(meta['captions']):
            n=len(clean(c['text']));a,b=chars[position],chars[position+n-1]
            onset,offset=times[position][0]/1000,times[position+n-1][1]/1000
            caps.append(dict(index=i,text=c['text'],onset=onset,offset=offset,providerStart=a['start'],providerEnd=b['end'],delta=onset-a['start'],firstChar=position,lastChar=position+n-1))
            position+=n
        record=dict(scene=key,audioSha256=sha,method='FunASR 1.4.16 fa-zh MonotonicAligner on existing 16k resampled read-only audio; raw character times',captions=caps,charTimes=times)
        save(dest,record)
        print('FA_DONE',key,'maxDelta',round(max(abs(c['delta']) for c in caps),3),'elapsed',round(time.time()-started,1),flush=True)
    print('ACOUSTIC_CHECK_COMPLETE',flush=True)
if __name__=='__main__':main()
