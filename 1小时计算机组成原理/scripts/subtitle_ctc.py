"""Independent, transcript-constrained CTC alignment of frozen narration.

No TTS calls, no edits to audio. Short overlapping inference windows preserve
context; one monotonic Viterbi path aligns each whole scene to known text.
Unknown characters and whole English words get explicit wildcard emissions.
"""
import argparse, hashlib, json, pathlib, re, sys, time, warnings
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build'
MODEL=BUILD/'subtitle-model/ctc-zh';OUT=BUILD/'subtitle-ctc'
OUT.mkdir(exist_ok=True)
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')

def tokens_for(captions,vocab,phonetic=False):
    result=[]
    sounds={}
    if phonetic:
        from pypinyin import lazy_pinyin
        for char,idx in vocab.items():
            if len(char)==1 and '\u3400'<=char<='\u9fff':sounds.setdefault(lazy_pinyin(char)[0],[]).append(idx)
    for i,c in enumerate(captions):
        for m in re.finditer(r'[A-Za-z]+|[\u3400-\u9fff]|[0-9]+',c['text']):
            text=m.group();symbol=text.upper()
            # A non-speech wildcard handles an English word, digit string or
            # out-of-vocabulary character without fabricating its syllables.
            idx=vocab.get(symbol) if len(symbol)==1 else None
            item=dict(text=text,caption=i,id=idx,wildcard=idx is None)
            if phonetic and len(text)==1 and '\u3400'<=text<='\u9fff':
                sound='yao' if text=='一' and '一一' in c['text'] else lazy_pinyin(text)[0]
                item['alternatives']=sounds.get(sound,[idx] if idx is not None else [])
            result.append(item)
    return result

def align(logp,tokens):
    """CTC Viterbi with mandatory blank between identical successive labels."""
    if any('alternatives' in x for x in tokens):
        groups={};columns=[logp[:,0]];target=[]
        for token in tokens:
            choices=tuple(token.get('alternatives') or ([token['id']] if token['id'] is not None else []))
            if choices not in groups:
                groups[choices]=len(columns)
                columns.append(np.max(logp[:,list(choices) if choices else slice(5,None)],axis=1))
            target.append(groups[choices])
        ids=np.array(target);emit=np.stack(columns,axis=1)
    else:
        ids=np.array([x['id'] if x['id'] is not None else logp.shape[1] for x in tokens])
        wildcard=np.max(logp[:,5:],axis=1,keepdims=True)
        emit=np.concatenate([logp,wildcard],axis=1)
    labels=np.zeros(2*len(ids)+1,dtype=int);labels[1::2]=ids
    skip=np.zeros(len(labels),dtype=bool)
    skip[3::2]=ids[1:]!=ids[:-1]
    previous=np.full(len(labels),-1e20,dtype=np.float32)
    previous[0]=emit[0,0];previous[1]=emit[0,ids[0]]
    trace=np.zeros((len(logp),len(labels)),dtype=np.uint8)
    for t in range(1,len(logp)):
        one=np.concatenate([[-1e20],previous[:-1]])
        two=np.concatenate([[-1e20,-1e20],previous[:-2]])
        two[~skip]=-1e20
        scores=np.stack([previous,one,two]);direction=np.argmax(scores,axis=0)
        previous=scores[direction,np.arange(len(labels))]+emit[t,labels]
        trace[t]=direction
    state=len(labels)-1 if previous[-1]>=previous[-2] else len(labels)-2
    path=np.zeros(len(logp),dtype=int)
    for t in range(len(logp)-1,-1,-1):
        path[t]=state
        if t:state-=int(trace[t,state])
    assert state in [0,1],('CTC path did not reach beginning',state)
    spans=[]
    for i,token in enumerate(tokens):
        frames=np.flatnonzero(path==2*i+1)
        assert len(frames),(i,token)
        prob=emit[frames,ids[i]]
        spans.append(dict(**token,start=float(frames[0]*.02),end=float((frames[-1]+1)*.02),confidence=float(np.exp(np.mean(prob))),peak=float(frames[np.argmax(prob)]*.02)))
    return spans

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--scene');parser.add_argument('--threads',type=int,default=4);parser.add_argument('--phonetic-review',action='store_true');args=parser.parse_args()
    out=BUILD/'subtitle-ctc-phonetic' if args.phonetic_review else OUT;out.mkdir(exist_ok=True)
    import torch
    from transformers import Wav2Vec2ForCTC,Wav2Vec2FeatureExtractor
    torch.set_num_threads(args.threads)
    torch.set_num_interop_threads(1)
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        model=Wav2Vec2ForCTC.from_pretrained(MODEL,local_files_only=True).eval()
        model=torch.ao.quantization.quantize_dynamic(model,{torch.nn.Linear},dtype=torch.qint8)
    extractor=Wav2Vec2FeatureExtractor.from_pretrained(MODEL,local_files_only=True)
    vocab=load(MODEL/'vocab.json');timeline=load(ROOT/'public/timeline.json');started=time.time()
    for scene in timeline['scenes']:
        key=scene['key']
        if args.scene and args.scene!=key:continue
        if args.phonetic_review:
            if not (OUT/f'{key}.json').exists():continue
            lexical=load(OUT/f'{key}.json');sem=load(BUILD/'subtitle-asr'/f'{key}.json')
            if not any(c['meanConfidence']<.15 or abs(c['onset']-b['onset'])>.22 or (c['firstConfidence']<.05 and abs(c['onset']-b['onset'])>.075) for c,b in zip(lexical['captions'],sem['captions'])):continue
        path=ROOT/'public/audio'/f'{key}.wav';sha=hashlib.sha256(path.read_bytes()).hexdigest();dest=out/f'{key}.json'
        if dest.exists() and load(dest).get('audioSha256')==sha:
            print('CTC_CACHED',key,flush=True);continue
        audio,rate=sf.read(path,dtype='float32');audio=resample_poly(audio,2,3)
        # Keep 12-second cores and two seconds of context either side. The
        # context is discarded, so every 20ms output tick has a single owner.
        length=int(np.ceil(len(audio)/320));logits=np.zeros((length,len(vocab)),dtype=np.float32);coverage=np.zeros(length,dtype=bool)
        with torch.inference_mode():
            for first in range(0,length,600):
                last=min(length,first+600);left=max(0,first-100);right=min(length,last+100)
                segment=audio[left*320:min(len(audio),right*320)]
                inputs=extractor(segment,sampling_rate=16000,return_tensors='pt',padding=False)
                result=model(**inputs).logits[0].float().log_softmax(dim=-1).numpy()
                a=first-left;b=min(last-left,len(result));n=b-a
                logits[first:first+n]=result[a:b];coverage[first:first+n]=True
        # Wav2vec's valid convolution consumes a few final samples. Extend the
        # final valid acoustic frame only; no spoken interval is dropped.
        if not coverage[-1]:
            end=np.flatnonzero(coverage)[-1]+1;logits[end:]=logits[end-1];coverage[end:]=True
        assert np.all(coverage),key
        tokens=tokens_for(scene['captions'],vocab,args.phonetic_review);spans=align(logits,tokens)
        inv={v:k for k,v in vocab.items()};greedy=[];previous=-1
        for idx in np.argmax(logits,axis=1):
            if idx!=previous and idx!=0:greedy.append(inv[int(idx)])
            previous=idx
        captions=[]
        for i,c in enumerate(scene['captions']):
            labels=[x for x in spans if x['caption']==i];assert labels
            captions.append(dict(index=i,text=c['text'],onset=labels[0]['start'],offset=labels[-1]['end'],firstPeak=labels[0]['peak'],lastPeak=labels[-1]['peak'],firstConfidence=labels[0]['confidence'],lastConfidence=labels[-1]['confidence'],meanConfidence=float(np.mean([x['confidence'] for x in labels])),wildcards=sum(x['wildcard'] for x in labels)))
        save(dest,dict(scene=key,audioSha256=sha,method='independent Chinese Wav2Vec2 XLSR CTC transcript-constrained Viterbi; 20ms grid; short overlapping acoustic contexts',phoneticReview=args.phonetic_review,captions=captions,tokens=spans,greedyText=''.join(greedy)))
        print('CTC_DONE',key,'seconds',round(len(audio)/16000,2),'elapsed',round(time.time()-started,1),'minConfidence',round(min(c['meanConfidence'] for c in captions),3),flush=True)
    print('CTC_ALIGNMENT_COMPLETE',flush=True)
if __name__=='__main__':main()
