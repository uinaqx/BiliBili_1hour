"""Local acoustic timing and sample-accurate sentence pauses, independent of other projects."""
import bisect,copy,hashlib,json,math,pathlib,re,statistics,subprocess,wave
import numpy as np
import timing_utils as old
ROOT=pathlib.Path(__file__).resolve().parents[1];ORIGINAL=ROOT/'public';AUDIO=ROOT/'public/audio';ALIGN=ROOT/'build/alignment'
RATE=24000;SPF=800;PACE=1.0;VERSION='net-acoustic-v1'
for d in (AUDIO,ALIGN):d.mkdir(parents=True,exist_ok=True)
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')

def pcm_read(path):
    with wave.open(str(path),'rb') as f:
        assert f.getframerate()==RATE and f.getnchannels()==1 and f.getsampwidth()==2
        return f.readframes(f.getnframes())

def pcm_write(path,pcm):
    with wave.open(str(path),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(pcm)

def scaled(part):
    key=part['key'];source=ORIGINAL/'audio_original'/(key+'.mp3');meta=load(source.with_suffix('.json'))
    fingerprint=hashlib.sha256((meta['fingerprint']+VERSION).encode()).hexdigest()
    dest=AUDIO/(key+'.scaled.wav');tag=dest.with_suffix('.hash')
    if not dest.exists() or not tag.exists() or tag.read_text()!=fingerprint:
        assert PACE==1.0,'Changing original speech tempo requires prior user agreement'
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-ac','1','-ar',str(RATE),'-c:a','pcm_s16le',str(dest)],check=True)
        tag.write_text(fingerprint)
    return meta,dest,fingerprint

def align_part(part,model,tokenizer):
    import whisper
    from whisper.timing import find_alignment
    key=part['key'];meta,path,fingerprint=scaled(part);target=ALIGN/(key+'.json')
    if target.exists() and load(target).get('fingerprint')==fingerprint:return load(target),True
    audio=whisper.load_audio(str(path));duration=len(audio)/16000
    original=meta['words'];words=copy.deepcopy(original)
    spans=[];text=''
    for w in original:spans.append((len(text),len(text)+len(w['text'])));text+=w['text']
    char_times=[None]*len(text);groups=[];i=0
    while i<len(words):
        j=i+1
        while j<len(words) and (original[j]['end_time']-original[i]['begin_time'])/1000/PACE<19:j+=1
        choices=[k for k in range(i+1,j) if re.search(r'[。！？；，]',original[k-1]['text']) and (original[k-1]['end_time']-original[i]['begin_time'])/1000/PACE>13]
        if j<len(words) and choices:j=choices[-1]
        if j==i:j+=1
        groups.append((i,j));i=j
    chunks=[];seams=[]
    for first,last in groups:
        a=max(0,first-8);b=min(len(words),last+8)
        start=max(0,original[a]['begin_time']/1000/PACE-.4)
        end=min(duration,original[b-1]['end_time']/1000/PACE+.55)
        assert end-start<29.95,(key,start,end)
        start=round(start*16000)/16000;segment=audio[round(start*16000):round(end*16000)]
        phrase=text[spans[a][0]:spans[b-1][1]]
        mel=whisper.log_mel_spectrogram(whisper.pad_or_trim(segment))
        found=find_alignment(model,tokenizer,tokenizer.encode(phrase),mel,len(segment)//160)
        assert ''.join(w.word for w in found)==phrase,(key,phrase,''.join(w.word for w in found))
        pos=spans[a][0];probabilities=[]
        for w in found:
            for k,c in enumerate(w.word):
                x=pos+k
                timing=(start+float(w.start)+(float(w.end)-float(w.start))*k/len(w.word),start+float(w.start)+(float(w.end)-float(w.start))*(k+1)/len(w.word),float(w.probability))
                if c.isalnum():probabilities.append(float(w.probability))
                if spans[first][0]<=x<spans[last-1][1]:char_times[x]=timing
                elif char_times[x] is not None and c.isalnum():seams.append(abs(char_times[x][0]-timing[0]))
            pos+=len(w.word)
        chunks.append(dict(start=start,end=end,text=phrase,medianProbability=statistics.median(probabilities) if probabilities else 0))
    deltas=[]
    for w,raw,(a,b) in zip(words,original,spans):
        active=[char_times[k] for k in range(a,b) if text[k].isalnum()]
        if not active:active=[char_times[k] for k in range(a,b)]
        assert active and all(x is not None for x in active),(key,w)
        begin=max(0,min(x[0] for x in active));end=min(duration,max(x[1] for x in active))
        w['begin_time']=round(begin*1000,4);w['end_time']=round(max(begin,end)*1000,4)
        w['alignmentProbability']=statistics.mean(x[2] for x in active)
        if any(c.isalnum() for c in w['text']):deltas.append(begin-raw['begin_time']/1000/PACE)
    result=dict(key=key,fingerprint=fingerprint,method='Whisper-base known-transcript cross-attention DTW, audio already at final tempo',tempo=PACE,duration=duration,words=words,chunks=chunks,providerDeltaP95=float(np.percentile(np.abs(deltas),95)),providerDeltaMax=max(abs(x) for x in deltas),overlapAgreementP95=float(np.percentile(seams,95)) if seams else 0,narration=part['narration'])
    save(target,result);return result,False

def clip(part):
    key=part['key'];aligned=load(ALIGN/(key+'.json'));pcm=pcm_read(AUDIO/(key+'.scaled.wav'));words=copy.deepcopy(aligned['words'])
    cuts=old.boundaries(dict(words=words));cursor=0;pieces=[];positions=[]
    for t in cuts:
        pos=round(t/1000*RATE)*2
        assert cursor<=pos<=len(pcm)
        pieces.extend((pcm[cursor:pos],bytes(round(.1*RATE)*2)));positions.append(pos//2);cursor=pos
    pieces.append(pcm[cursor:]);pcm=b''.join(pieces)
    for w in words:
        w['begin_time']+=bisect.bisect_right(cuts,w['begin_time'])*100
        w['end_time']+=bisect.bisect_left(cuts,w['end_time'])*100
    caps=old.captions(words)
    # Caption starts follow the first spoken character, never punctuation in a pause.
    # Keep the caption briefly after the phrase, bounded by the next phrase start.
    for i,c in enumerate(caps):
        c['start']=max(0,c['start']-.035)
        c['end']=min(len(pcm)/2/RATE,c['end']+.10,caps[i+1]['start']-.035 if i+1<len(caps) else 1e9)
        assert c['end']>=c['start'],(key,c)
    # Keep short answers such as "不是。" with the explanation that follows.
    i=0
    while i<len(caps)-1:
        a,b=caps[i:i+2]
        if a['end']-a['start']<.55 and len(a['text']+b['text'])<=38 and b['end']-a['start']<=6.5:
            a.update(end=b['end'],text=a['text']+b['text']);caps.pop(i+1)
        else:i+=1
    # Attention alignment sometimes gives a phrase the middle of a long silence.
    # Refine only starts that are demonstrably quiet on both sides; leave starts
    # inside continuous speech alone. Keep 55ms for low-energy initial consonants.
    signal=np.frombuffer(pcm,dtype='<i2').astype(np.float64)/32768
    step=round(.01*RATE);rms=np.sqrt(np.mean(signal[:len(signal)//step*step].reshape(-1,step)**2,axis=1))
    voiced=rms>max(.001,float(np.percentile(rms,90))*.03);snaps=[]
    for c in caps:
        k=round(c['start']/.01)
        if np.any(voiced[max(0,k-4):min(len(voiced),k+8)]):continue
        candidates=np.flatnonzero(voiced[k:min(len(voiced),k+90)])
        if not len(candidates):continue
        onset=(k+int(candidates[0]))*.01;start=max(c['start'],onset-.055)
        if start<c['end']-.1 and start-c['start']>.075:
            snaps.append(dict(text=c['text'],oldStart=c['start'],newStart=start,onset=onset));c['start']=start
    fingerprint=hashlib.sha256((aligned['fingerprint']+json.dumps(words,sort_keys=True)+'pause100').encode()).hexdigest()
    pcm_write(AUDIO/(key+'.wav'),pcm)
    result=dict(key=key,fingerprint=fingerprint,tempo=PACE,duration=len(pcm)/2/RATE,frames=math.ceil(len(pcm)/2/SPF),samples=len(pcm)//2,words=words,captions=caps,captionOnsetRefinements=snaps,pauseCutsMs=cuts,insertedPauseSamples=positions,narration=part['narration'])
    save(AUDIO/(key+'.json'),result);return result
