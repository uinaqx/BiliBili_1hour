"""Recognize frozen audio, then map the unchanged transcript to acoustic tokens.

Unlike duration/character-count prediction, ASR anchors depend on the words that
are actually spoken. This handles consecutive number syllables and Latin names.
"""
import argparse, difflib, hashlib, pathlib, re, sys, time
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from subtitle_calibrate import ROOT, BUILD, BACKUP, load, save, clean, mapped_words
sys.stdout.reconfigure(encoding='utf-8')

def map_characters(expected,tokens,times):
    heard=[];timing=[]
    for token,(a,b) in zip(tokens,times):
        letters=clean(token.replace('@@','')).replace('幺','一')
        for k,c in enumerate(letters):
            heard.append(c);timing.append([a/1000+(b-a)/1000*k/len(letters),a/1000+(b-a)/1000*(k+1)/len(letters)])
    heard=''.join(heard);mapped={};blocks=[]
    # Global edit alignment prevents a common homophone from being greedily
    # attached to the NEXT sentence. Equal-length recognition substitutions
    # still have valid acoustic times, even if ASR spelled the word incorrectly.
    from pypinyin import lazy_pinyin
    sounds={c:lazy_pinyin(c)[0] for c in set(expected+heard)}
    n,m=len(expected),len(heard);trace=np.zeros((n+1,m+1),dtype=np.uint8)
    trace[0,1:]=2;trace[1:,0]=1;previous=list(range(m+1))
    for i,a in enumerate(expected,1):
        current=[float(i)]+[0.0]*m
        for j,b in enumerate(heard,1):
            diagonal=previous[j-1]+(0 if a==b else .25 if sounds[a]==sounds[b] else 1)
            deletion=previous[j]+1;insertion=current[j-1]+1
            if diagonal<=deletion and diagonal<=insertion:current[j]=diagonal;trace[i,j]=0
            elif deletion<=insertion:current[j]=deletion;trace[i,j]=1
            else:current[j]=insertion;trace[i,j]=2
        previous=current
    pairs=[];i,j=n,m
    while i or j:
        direction=trace[i,j]
        if direction==0:
            pairs.append((i-1,j-1));i-=1;j-=1
        elif direction==1:i-=1
        else:j-=1
    for a,b in reversed(pairs):
        mapped[a]=timing[b]
        kind='exact' if expected[a]==heard[b] else 'phonetic' if sounds[expected[a]]==sounds[heard[b]] else 'substitution'
        if blocks and blocks[-1]['kind']==kind and blocks[-1]['expected']+blocks[-1]['length']==a and blocks[-1]['heard']+blocks[-1]['length']==b:blocks[-1]['length']+=1
        else:blocks.append(dict(expected=a,heard=b,length=1,kind=kind))
    return heard,mapped,timing,blocks

def remap_all():
    """Reuse cached ASR tokens without another neural inference pass."""
    for path in sorted((BUILD/'subtitle-asr').glob('*.json')):
        if path.name.endswith('.raw.json'):continue
        rec=load(path);key=rec['scene'];chars,meta=mapped_words(key)
        heard,mapped,_,blocks=map_characters(rec['expected'],rec['tokens'],rec['tokenTimes'])
        position=0;caps=[];edges=[]
        for i,c in enumerate(meta['captions']):
            n=len(clean(c['text']));a,b=chars[position],chars[position+n-1]
            anchors=[k for k in range(position,position+n) if k in mapped]
            result=dict(index=i,text=c['text'],providerStart=a['start'],providerEnd=b['end'],firstChar=position,lastChar=position+n-1)
            if not anchors:
                ref=load(BUILD/'subtitle-fa'/f'{key}.json')['captions'][i]
                result.update(onset=ref['onset'],offset=ref['offset'],firstMatchedChar=None,lastMatchedChar=None,startExact=False,endExact=False,matchedFraction=0,noAnchors=True)
            else:
                first,last=anchors[0],anchors[-1]
                prefix=rec['expected'][position:first+1]
                suffix=rec['expected'][last:position+n]
                lead=0 if len(set(prefix))==1 else chars[first]['start']-a['start']
                tail=0 if len(set(suffix))==1 else b['end']-chars[last]['end']
                result.update(onset=max(0,mapped[first][0]-lead),offset=mapped[last][1]+tail,firstMatchedChar=first,lastMatchedChar=last,startExact=first==position,endExact=last==position+n-1,matchedFraction=len(anchors)/n)
            result['delta']=result['onset']-a['start']
            if not result['startExact'] or not result['endExact']:edges.append(i)
            caps.append(result);position+=n
        rec.update(mappingVersion=2,captions=caps,recognized=heard,characterMatches={str(k):v for k,v in mapped.items()},matchingBlocks=blocks,matchedFraction=len(mapped)/len(rec['expected']),edgeReview=edges)
        save(path,rec)
        print('REMAPPED',key,round(rec['matchedFraction'],3),edges,flush=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--scene');parser.add_argument('--remap',action='store_true');args=parser.parse_args()
    if args.remap:return remap_all()
    from funasr import AutoModel
    from funasr.utils import postprocess_utils
    postprocess_utils.sentence_postprocess=lambda token,ts:(' '.join(token),ts,token)
    model=AutoModel(model=str(BUILD/'subtitle-model/paraformer-timestamp'),device='cpu',ncpu=4,disable_update=True,trust_remote_code=False,disable_pbar=True)
    out=BUILD/'subtitle-asr';out.mkdir(exist_ok=True);started=time.time()
    t=load(BACKUP/'timeline.json')
    for scene in t['scenes']:
        key=scene['key']
        if args.scene and args.scene!=key:continue
        path=ROOT/'public/audio'/f'{key}.wav';sha=hashlib.sha256(path.read_bytes()).hexdigest();dest=out/f'{key}.json'
        if dest.exists() and load(dest).get('audioSha256')==sha:
            print('ASR_CACHED',key,flush=True);continue
        chars,meta=mapped_words(key);audio,rate=sf.read(str(path),dtype='float32');assert rate==24000
        audio=resample_poly(audio,2,3)
        rawdest=out/f'{key}.raw.json'
        if rawdest.exists():result=load(rawdest)
        else:
            result=model.generate(input=audio,fs=16000,disable_pbar=True)[0]
            save(rawdest,result)
        tokens=result['text'].split();times=result['timestamp'];assert len(times)==len(tokens),(key,len(times),len(tokens))
        expected=''.join(c['text'] for c in chars)
        heard,mapped,heardtimes,blocks=map_characters(expected,tokens,times)
        caps=[];position=0;unmatched=[]
        for i,c in enumerate(meta['captions']):
            n=len(clean(c['text']));a,b=chars[position],chars[position+n-1]
            anchors=[k for k in range(position,position+n) if k in mapped]
            if not anchors:
                reference=load(BUILD/'subtitle-fa'/f'{key}.json')['captions'][i]
                caps.append(dict(index=i,text=c['text'],onset=reference['onset'],offset=reference['offset'],providerStart=a['start'],providerEnd=b['end'],firstChar=position,lastChar=position+n-1,firstMatchedChar=None,lastMatchedChar=None,startExact=False,endExact=False,matchedFraction=0,delta=reference['onset']-a['start'],noAnchors=True))
                unmatched.append(i);position+=n;continue
            first,last=anchors[0],anchors[-1]
            # Estimate unmatched edge syllables from nearby recognized syllables;
            # every such estimate remains explicitly marked for review.
            onset=mapped[first][0]-(chars[first]['start']-a['start'])
            offset=mapped[last][1]+(b['end']-chars[last]['end'])
            start_exact=first==position;end_exact=last==position+n-1
            if not start_exact or not end_exact:unmatched.append(i)
            caps.append(dict(index=i,text=c['text'],onset=max(0,onset),offset=offset,providerStart=a['start'],providerEnd=b['end'],firstChar=position,lastChar=position+n-1,firstMatchedChar=first,lastMatchedChar=last,startExact=start_exact,endExact=end_exact,matchedFraction=len(anchors)/n,delta=onset-a['start']))
            position+=n
        record=dict(scene=key,audioSha256=sha,method='Paraformer semantic ASR character timestamps mapped to unchanged narration; no audio writing',captions=caps,tokens=tokens,tokenTimes=times,expected=expected,recognized=heard,characterMatches={str(k):v for k,v in mapped.items()},matchingBlocks=blocks,matchedFraction=len(mapped)/len(expected),edgeReview=unmatched)
        save(dest,record)
        print('ASR_DONE',key,'matched',round(record['matchedFraction'],3),'edges',unmatched,'elapsed',round(time.time()-started,1),flush=True)
    print('ASR_CHECK_COMPLETE',flush=True)
if __name__=='__main__':main()
