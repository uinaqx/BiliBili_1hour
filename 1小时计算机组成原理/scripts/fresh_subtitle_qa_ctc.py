"""Lexical acoustic review on fresh MP4 audio and new ASR only.

Uses an existing local CTC checkpoint; no downloads and no previous subtitles.
Each flagged transition receives a short context with actual preceding words,
so a next-caption boundary cannot be accepted simply because sound is present.
"""
import argparse,json,re,sys,warnings
from pathlib import Path
import numpy as np
from fresh_subtitle_qa import ROOT,ASR,OUT,read,write,symbols

def tokens(words,vocab,context=''):
    result=[]
    for owner,word in words:
        for char in symbols(word['word'],context):
            symbol=char.upper();idx=vocab.get(symbol)
            result.append({'text':char,'id':idx,'owner':owner,'wildcard':idx is None})
    return result

def viterbi(logp,tokens):
    ids=np.array([t['id'] if t['id'] is not None else logp.shape[1] for t in tokens])
    emit=np.concatenate([logp,np.max(logp[:,5:],axis=1,keepdims=True)],axis=1)
    labels=np.zeros(2*len(ids)+1,dtype=int);labels[1::2]=ids
    skip=np.zeros(len(labels),dtype=bool);skip[3::2]=ids[1:]!=ids[:-1]
    previous=np.full(len(labels),-1e20,dtype=np.float32);previous[0]=emit[0,0];previous[1]=emit[0,ids[0]]
    trace=np.zeros((len(logp),len(labels)),dtype=np.uint8)
    for t in range(1,len(logp)):
        one=np.r_[-1e20,previous[:-1]];two=np.r_[-1e20,-1e20,previous[:-2]];two[~skip]=-1e20
        scores=np.stack([previous,one,two]);direction=np.argmax(scores,axis=0)
        previous=scores[direction,np.arange(len(labels))]+emit[t,labels];trace[t]=direction
    state=len(labels)-1 if previous[-1]>=previous[-2] else len(labels)-2;path=np.zeros(len(logp),dtype=int)
    for t in range(len(logp)-1,-1,-1):
        path[t]=state
        if t:state-=int(trace[t,state])
    spans=[]
    for i,token in enumerate(tokens):
        frames=np.flatnonzero(path==2*i+1)
        if not len(frames):raise ValueError('no acoustic path')
        p=emit[frames,ids[i]]
        spans.append({**token,'start':float(frames[0]*.02),'end':float((frames[-1]+1)*.02),
            'peak':float(frames[np.argmax(p)]*.02),'confidence':float(np.exp(np.mean(p)))})
    return spans

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=100);ap.add_argument('--min-delta',type=float,default=.18);args=ap.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    import soundfile as sf,torch
    from transformers import Wav2Vec2ForCTC,Wav2Vec2FeatureExtractor
    torch.set_num_threads(2);torch.set_num_interop_threads(1)
    modelpath=ROOT/'build/subtitle-model/ctc-zh'
    with warnings.catch_warnings():
        warnings.simplefilter('ignore');model=Wav2Vec2ForCTC.from_pretrained(modelpath,local_files_only=True).eval()
        model=torch.ao.quantization.quantize_dynamic(model,{torch.nn.Linear},dtype=torch.qint8)
    extractor=Wav2Vec2FeatureExtractor.from_pretrained(modelpath,local_files_only=True)
    vocab=read(modelpath/'vocab.json');inv={v:k for k,v in vocab.items()}
    audio,rate=sf.read(ASR/'actual-video-audio-16k.wav',dtype='float32');assert rate==16000
    cues=read(ASR/'cues-draft.json');suspects=read(OUT/'suspect-cue-boundaries.json')
    suspects=[c for c in suspects if c['onset_delta']>=args.min_delta or 'caption_starts_while_previous_tail_remains' in c['reasons']]
    suspects.sort(key=lambda c:-c['onset_delta']);suspects=suspects[:args.limit]
    reports=[]
    for suspected in suspects:
        i=suspected['index']-1;current=cues[i];previous=cues[i-1] if i else None
        pairs=[]
        if previous:pairs.extend(('previous',w) for w in previous['words'][-8:])
        pairs.extend(('current',w) for w in current['words'])
        if i+1<len(cues):pairs.extend(('next',w) for w in cues[i+1]['words'][:3])
        start=max(0,pairs[0][1]['start']-.25);end=min(len(audio)/rate,pairs[-1][1]['end']+.3)
        chunk=audio[round(start*rate):round(end*rate)];tok=tokens(pairs,vocab,' '.join(w['word'] for _,w in pairs))
        if not tok:continue
        key=OUT/f'ctc-cue-{current["index"]:04}.json'
        if key.exists():reports.append(read(key));continue
        try:
            with torch.inference_mode():
                inp=extractor(chunk,sampling_rate=rate,return_tensors='pt',padding=False)
                logp=model(**inp).logits[0].float().log_softmax(dim=-1).numpy()
            spans=viterbi(logp,tok);current_spans=[s for s in spans if s['owner']=='current'];prev_spans=[s for s in spans if s['owner']=='previous']
            greedy=[];last=-1
            for idx in np.argmax(logp,axis=1):
                if idx!=last and idx!=0:greedy.append(inv[int(idx)])
                last=idx
            onset=start+current_spans[0]['start'];peak=start+current_spans[0]['peak']
            previous_end=start+prev_spans[-1]['end'] if prev_spans else None
            firstconf=current_spans[0]['confidence'];meanconf=float(np.mean([s['confidence'] for s in current_spans]))
            numeric_latin=bool(re.search(r'[A-Za-z0-9]',current['text'][:8]))
            recommendation='review_uncertain'
            if firstconf>=.3 and meanconf>=.2 and not numeric_latin:
                if onset-current['start']>=.12:recommendation='delay_to_ctc_onset'
                elif abs(onset-current['start'])<.12:recommendation='keep_fresh_asr_boundary'
            report={'index':current['index'],'text':current['text'],'asr_start':current['start'],'fa_start':suspected['fa_first_start'],
                'ctc_onset':round(onset,3),'ctc_peak':round(peak,3),'ctc_previous_end':round(previous_end,3) if previous_end else None,
                'first_confidence':firstconf,'mean_confidence':meanconf,'numeric_latin_initial':numeric_latin,
                'window_start':start,'window_end':end,'greedy_text':''.join(greedy),'tokens':spans,
                'recommendation':recommendation,'reads_old_timestamps':False,'source':'actual-video-audio-16k.wav'}
            write(key,report);reports.append(report)
            print('CTC_QA',current['index'],round(onset-current['start'],3),round(firstconf,3),recommendation,flush=True)
        except Exception as exc:reports.append({'index':current['index'],'error':str(exc)})
    write(OUT/'ctc-review.json',reports)
    from PIL import Image,ImageDraw,ImageFont
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21)
    small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
    for r in reports[:20]:
        if 'error' in r:continue
        center=r['asr_start'];lo=max(r['window_start'],center-1);hi=min(r['window_end'],center+2)
        w,h=1500,500;im=Image.new('RGB',(w,h),'white');d=ImageDraw.Draw(im)
        d.text((30,16),f"新字幕 {r['index']}: {r['text']}",font=font,fill='black')
        d.text((30,54),f"Whisper {center:.3f}s  |  FA {r['fa_start']:.3f}s  |  CTC {r['ctc_onset']:.3f}s  |  首字置信 {r['first_confidence']:.3f}",font=small,fill='black')
        left,right,top,bottom=60,w-30,125,365
        def px(t):return left+(t-lo)/(hi-lo)*(right-left)
        segment=audio[round(lo*rate):round(hi*rate)]
        stride=max(1,len(segment)//(right-left));n=len(segment)//stride
        levels=np.max(np.abs(segment[:n*stride].reshape(n,stride)),axis=1)
        scale=max(.05,float(np.max(levels)))
        for k,value in enumerate(levels):
            x=left+k/n*(right-left);a=value/scale*(bottom-top)/2
            d.line((x,(top+bottom)/2-a,x,(top+bottom)/2+a),fill='#4a5568')
        lines=[(center,'#e53e3e','新ASR起点',90),(r['fa_start'],'#d69e2e','FA音节边界',385),(r['ctc_onset'],'#3182ce','CTC词序边界',415)]
        if r['ctc_previous_end'] is not None:lines.append((r['ctc_previous_end'],'#38a169','上一字幕尾字结束',445))
        for t,color,label,y in lines:
            if lo<=t<=hi:
                x=px(t);d.line((x,top,x,bottom),fill=color,width=3)
                d.text((max(left,min(x-60,right-260)),y),f'{label} {t:.3f}',font=small,fill=color)
        for t in np.arange(np.ceil(lo*2)/2,hi,.5):
            x=px(float(t));d.text((x-20,365),f'{t:.1f}',font=small,fill='black')
        im.save(OUT/f'waveform-cue-{r["index"]:04}.png')
    print('CTC_QA_DONE',len(reports),flush=True)

if __name__=='__main__':main()
