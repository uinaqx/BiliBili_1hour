"""Independent acoustic QA of freshly recognized subtitles, never old captions.

Uses the already installed 158 MB FunASR timestamp model and actual MP4-derived
PCM. FA is a syllable-count acoustic aligner, not lexical ground truth; warnings
remain explicit for Arabic numbers/English and suspect token counts. Results are
evidence/suggestions, never automatic changes to the primary subtitles.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys, time, wave
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'build/fresh-subtitles-20261019'
ASR=BASE/'asr'; OUT=BASE/'qa'; OUT.mkdir(parents=True,exist_ok=True)

def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def write(path,value):
    tmp=path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(path)

def chinese_number(raw):
    digits='零一二三四五六七八九'
    if len(raw)>1 and raw.startswith('0'):return ''.join(digits[int(c)] for c in raw)
    n=int(raw)
    if n<10:return digits[n]
    if n>=10000:
        if n>=100000000:return ''.join(digits[int(c)] for c in raw)
        high,low=divmod(n,10000)
        return chinese_number(str(high))+'万'+(('零' if low<1000 else '')+chinese_number(str(low)) if low else '')
    value='';zero=False
    for unit,label in [(1000,'千'),(100,'百'),(10,'十'),(1,'')]:
        digit,n=divmod(n,unit)
        if digit:
            if zero and value:value+='零'
            value+=('' if digit==1 and unit==10 and not value else digits[digit])+label;zero=False
        elif value and n:zero=True
    return value

def symbols(text,context=''):
    # FA consumes syllable counts. Arabic 256 must be five spoken syllables,
    # not three digits; binary bit strings are deliberately kept as digits.
    explicit_bits=bool(re.search(r'逐位|逐个|每一位|二进制串|比特串|位模式|零和一',context))
    def expand(m):
        value=m.group()
        if explicit_bits or (len(value)>=4 and set(value)<=set('01')):
            return ''.join('零一二三四五六七八九'[int(c)] if c.isdigit() else '点' for c in value)
        integer,dot,fraction=value.partition('.')
        return chinese_number(integer)+('点'+''.join('零一二三四五六七八九'[int(c)] for c in fraction) if dot else '')
    spoken=re.sub(r'\d+(?:\.\d+)?',expand,text)
    return re.findall(r'[\u3400-\u9fff]|[A-Za-z]',spoken)

def energy_evidence(audio,start,end):
    p=audio[max(0,round(start*16000)):min(len(audio),round(end*16000))]
    if len(p)<160:return {'peak':0,'rms':0}
    return {'peak':round(float(np.max(np.abs(p))),6),'rms':round(float(np.sqrt(np.mean(p*p))),6)}

def align_chunk(path,audio,model):
    chunk=read(path);dest=OUT/path.name
    digest=hashlib.sha256(path.read_bytes()+b'fresh-qa-spoken-numbers-v2').hexdigest()
    if dest.exists() and read(dest).get('freshAsrSha256')==digest:return read(dest)
    records=[];failures=[]
    for seg in chunk['segments']:
        words=seg['words']; tokens=[];spans=[]
        for w in words:
            start=len(tokens);tokens.extend(symbols(w['word'],seg['text']));spans.append((start,len(tokens)))
        if not tokens:continue
        start=max(chunk['clip_start'],min(seg['start'],words[0]['start'])-.25)
        end=min(chunk['clip_end'],max(seg['end'],words[-1]['end'])+.30)
        segment=audio[round(start*16000):round(end*16000)]
        try:
            aligned=model.generate(input=(segment,' '.join(tokens)),data_type=('sound','text'),fs=16000,disable_pbar=True)[0]
            times=aligned['timestamp']
            if len(times)!=len(tokens):raise ValueError(f'token count {len(tokens)} versus model {len(times)}')
            for i,(w,(a,b)) in enumerate(zip(words,spans)):
                if a==b:continue
                onset=start+times[a][0]/1000;offset=start+times[b-1][1]/1000
                records.append({'chunk':chunk['index'],'segment':seg['id'],'word_index':i,
                    'word':w['word'],'accepted':w['accepted'],'whisper_start':w['start'],'whisper_end':w['end'],
                    'fa_start':round(onset,3),'fa_end':round(offset,3),
                    'onset_delta':round(onset-w['start'],3),'offset_delta':round(offset-w['end'],3),
                    'probability':w['probability'],'numeric_or_latin':bool(re.search(r'[A-Za-z0-9]',w['word'])),
                    'leading_energy':energy_evidence(audio,w['start'],min(onset,w['start']+.4)),
                    'fa_duration':round(offset-onset,3),'segment_text':seg['text'],
                    'method':'independent existing fa-zh acoustic timestamp predictor; fresh transcript only'})
        except Exception as exc:
            failures.append({'segment':seg['id'],'start':start,'end':end,'text':seg['text'],'error':str(exc)})
    result={'index':chunk['index'],'freshAsrSha256':digest,'method':'new audio and fresh recognition only; no previous subtitle files',
            'words':records,'failures':failures}
    write(dest,result);print('QA_ALIGNED',chunk['index'],len(records),'failures',len(failures),flush=True)
    return result

def summarize(audio):
    files=sorted(OUT.glob('chunk-*.json'));words=[w for p in files for w in read(p)['words'] if w['accepted']]
    bykey={(w['chunk'],w['segment'],w['word'],w['whisper_start']):w for w in words}
    cues=read(ASR/'cues-draft.json') if (ASR/'cues-draft.json').exists() else []
    evidence=[];previous=None
    for cue in cues:
        raw=cue['words'];first=next((w for w in raw if symbols(w['word'])),None)
        last=next((w for w in reversed(raw) if symbols(w['word'])),None)
        if not first or not last:continue
        def lookup(w):return bykey.get((w['chunk'],w['segment'],w['word'],w['start']))
        a,b=lookup(first),lookup(last)
        if a is None or b is None:continue
        reasons=[];difference=a['fa_start']-cue['start']
        if difference>.15:reasons.append('next_caption_may_precede_new_utterance')
        if previous and previous['fa_last_end']>cue['start']+.10:reasons.append('caption_starts_while_previous_tail_remains')
        if cue['end']<b['fa_end']-.12:reasons.append('caption_ends_before_acoustic_tail')
        ev={'index':cue['index'],'start':cue['start'],'end':cue['end'],'text':cue['text'],
            'fa_first_start':a['fa_start'],'fa_last_end':b['fa_end'],'onset_delta':round(difference,3),
            'reasons':reasons,'first_word':a,'last_word':b,
            'caution':'Count-based FA can shift when recognized text omits/repeats syllables; numeric/Latin spans need independent review.'}
        if reasons:evidence.append(ev)
        previous=ev
    write(OUT/'suspect-cue-boundaries.json',evidence)
    summary={'aligned_chunks':len(files),'aligned_words':len(words),'fresh_cues_available':len(cues),
        'suspect_boundaries':len(evidence),'uses_previous_subtitles':False,'audio_modified':False,
        'warning':'Acoustic cross-check, not an assertion of perfect synchronization.',
        'failed_segments':[{'chunk':read(p)['index'],**f} for p in files for f in read(p)['failures']]}
    write(OUT/'summary.json',summary)
    # Numeric arrays at 10 ms resolution make the warning independently inspectable.
    hop=160;n=len(audio)//hop
    rms=np.sqrt(np.mean(audio[:n*hop].reshape(n,hop)**2,axis=1))
    np.savez_compressed(OUT/'actual-track-energy-10ms.npz',rms=rms,hop_seconds=.01)
    print('QA_SUMMARY',summary['aligned_chunks'],summary['aligned_words'],summary['suspect_boundaries'],flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--watch',action='store_true');ap.add_argument('--limit',type=int,default=0);ap.add_argument('--summarize',action='store_true');args=ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    path=ASR/'actual-video-audio-16k.wav'
    while not path.exists():
        if not args.watch:raise FileNotFoundError(path)
        time.sleep(5)
    with wave.open(str(path),'rb') as w:
        assert w.getframerate()==16000
        audio=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
    if args.summarize:summarize(audio);return
    import torch
    torch.set_num_threads(2);torch.set_num_interop_threads(1)
    from funasr import AutoModel
    from funasr.utils import postprocess_utils
    postprocess_utils.sentence_postprocess=lambda token,ts:(' '.join(token),ts,token)
    model=AutoModel(model=str(ROOT/'build/subtitle-model/fa-zh'),device='cpu',ncpu=2,disable_update=True,trust_remote_code=False,disable_pbar=True)
    seen=set()
    while True:
        paths=sorted(ASR.glob('chunk-*.json'))
        for path in paths:
            if path.name in seen:continue
            align_chunk(path,audio,model);seen.add(path.name)
            summarize(audio)
            if args.limit and len(seen)>=args.limit:return
        progress=read(ASR/'progress.json') if (ASR/'progress.json').exists() else {}
        complete=progress.get('complete_chunks')==progress.get('total_chunks') and bool(progress)
        if not args.watch or (complete and len(seen)>=progress['total_chunks']):break
        time.sleep(5)
    summarize(audio)

if __name__=='__main__':main()
