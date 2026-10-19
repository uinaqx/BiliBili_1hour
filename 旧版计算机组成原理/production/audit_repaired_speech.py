"""Spot-check the repaired acoustic timing using free ASR, without transcript input."""
import argparse,difflib,json,pathlib,statistics,sys,time
import numpy as np
import torch,whisper
sys.stdout.reconfigure(encoding='utf-8');torch.set_num_threads(4)
P=pathlib.Path(__file__).resolve().parent/'repair_sync';B=P/'build'
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def normalize(s):return ''.join(c.lower() for c in s if c.isalnum())
def flatten(words):
    out=[]
    for w in words:
        letters=normalize(w['text']);n=len(letters)
        if not n:continue
        for k,c in enumerate(letters):out.append(dict(char=c,start=w['start']+(w['end']-w['start'])*k/n))
    return out
def main():
    args=argparse.ArgumentParser();args.add_argument('--all',action='store_true');args=args.parse_args()
    t=load(P/'timeline.json');model=whisper.load_model('base',device='cpu');jobs=[]
    # Each chapter, plus the largest discrepancies seen in the old provider timings.
    selected=[]
    for ch in t['chapters']:
        group=[s for s in t['scenes'] if s['id'] in ch['sceneIds']];selected.append(group[len(group)//2]['id'])
    selected=list(dict.fromkeys(selected+['S04','S20','S22']))
    if args.all:selected=[s['id'] for s in t['scenes']]
    results=[];start=time.time()
    for sid in selected:
        key=sid+'-lesson';meta=load(P/'audio'/(key+'.json'));audio=whisper.load_audio(str(P/'audio'/(key+'.wav')))
        # Start on a real caption boundary, well inside each narration.
        caps=[c for c in meta['captions'] if 10<c['start']<meta['duration']-12]
        c=caps[len(caps)//2] if caps else meta['captions'][0]
        offset=max(0,c['start']-.2);length=min(11.,len(audio)/16000-offset)
        snippet=audio[round(offset*16000):round((offset+length)*16000)]
        out=model.transcribe(snippet,language='zh',task='transcribe',fp16=False,temperature=0,word_timestamps=True,condition_on_previous_text=False,verbose=None)
        recognized=[dict(text=w['word'],start=w['start'],end=w['end']) for s in out['segments'] for w in s['words']]
        reference=[dict(text=w['text'],start=w['begin_time']/1000-offset,end=w['end_time']/1000-offset) for w in meta['words'] if w['begin_time']/1000>=offset-.2 and w['end_time']/1000<=offset+length+.2]
        a=flatten(reference);b=flatten(recognized);matcher=difflib.SequenceMatcher(None,''.join(w['char'] for w in a),''.join(w['char'] for w in b),autojunk=False)
        differences=[];matches=[]
        for block in matcher.get_matching_blocks():
            for k in range(block.size):
                x=a[block.a+k];y=b[block.b+k]
                if .4<x['start']<length-.4:
                    differences.append(y['start']-x['start']);matches.append(dict(char=x['char'],reference=x['start'],recognized=y['start'],difference=y['start']-x['start']))
        result=dict(scene=sid,clip=key,offset=offset,length=length,reference=''.join(w['text'] for w in reference),recognition=out['text'],matchedCharacters=len(differences),matchedFraction=2*sum(m.size for m in matcher.get_matching_blocks())/max(1,len(a)+len(b)),medianTimingDifference=float(np.median(differences)) if differences else None,p95AbsoluteTimingDifference=float(np.percentile(np.abs(differences),95)) if differences else None,matches=matches)
        results.append(result);print('FREE_ASR_CHECK',sid,'matched',len(differences),'p95',result['p95AbsoluteTimingDifference'],'ratio',round(result['matchedFraction'],3),flush=True)
        (B/'speech-spotchecks.json').write_text(json.dumps(dict(method='Free Whisper ASR on actual repaired clip audio, no supplied transcript',seconds=time.time()-start,results=results),ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
