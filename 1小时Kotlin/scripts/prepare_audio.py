"""Build measured, continuous narration from manually authored semantic units."""
import bisect,hashlib,json,math,pathlib,subprocess,sys,wave
import numpy as np
import audio_timing as acoustic
ROOT=pathlib.Path(__file__).resolve().parents[1];RATE=24000
def load(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def full_stops(meta,duration):
    words=[w for w in meta['words'] if w['text'].strip()];cuts=[]
    for i,w in enumerate(words):
        if '。' not in w['text']:continue
        if i==len(words)-1:continue
        if w['text'].lstrip('“”\" ').startswith('。') and i:t=(words[i-1]['end_time']+w['begin_time'])/2000
        elif w['text'].rstrip('“”\" ').endswith('。'):t=(w['end_time']+words[i+1]['begin_time'])/2000
        else:continue
        if .03<t<duration-.03:cuts.append(t)
    return sorted(set(cuts))
def main():
    course=load(ROOT/'public/course.json');scenes=[s for c in course['chapters'] for s in c['scenes']]
    clips=[(s,i,p,ROOT/'public/audio_original'/(s['key']+f'-p{i:02}.mp3')) for s in scenes for i,p in enumerate(s['parts'])]
    missing=[x[3].name for x in clips if not x[3].exists() or not x[3].with_suffix('.json').exists()]
    if missing:raise RuntimeError(f'Missing {len(missing)} narration clips; resume voice generation first')
    raw=sum(load(x[3].with_suffix('.json'))['duration'] for x in clips)
    fixed=sum(len(full_stops(load(x[3].with_suffix('.json')),load(x[3].with_suffix('.json'))['duration']))*.1 for x in clips)+len(clips)*.1+len(scenes)*.5+sum(s['hold'] for s in scenes)
    predicted=raw+fixed;pace=1.0 if 3480<=predicted<=3780 else raw/(3600-fixed)
    assert .90<=pace<=1.10,('Revise useful content if pace would be unnatural',pace,predicted)
    settings=dict(wholeCourseTempo=pace,rawSeconds=raw,predictedSeconds=predicted,sentencePauseSeconds=.1,commaPauseUnchanged=True,syncMethod='manually authored semantic narration units, measured PCM offsets plus acoustic onset',voice='longanlufeng',model='qwen-audio-3.0-tts-plus')
    save(ROOT/'build/audio-settings.json',settings)
    audio=ROOT/'public/audio';audio.mkdir(exist_ok=True);reports=[]
    import torch,whisper
    from whisper.tokenizer import get_tokenizer
    torch.set_num_threads(4)
    model_file=pathlib.Path.home()/'.cache/whisper/base.pt'
    if not model_file.exists():raise RuntimeError('Install Whisper base model for local sentence alignment')
    model=whisper.load_model(str(model_file),device='cpu');tokenizer=get_tokenizer(True,language='zh',task='transcribe')
    acoustic.PACE=pace;acoustic.VERSION=f'kotlin-semantic-units-v1-tempo={pace:.10f}'
    for s in scenes:
        pcm=bytearray();timings=[];refinements=[]
        for i,p in enumerate(s['parts']):
            key=s['key']+f'-p{i:02}';source=ROOT/'public/audio_original'/(key+'.mp3');meta=load(source.with_suffix('.json'));temp=audio/(key+'.scaled.wav')
            assert meta['narration']==p['text'],('Narration changed; regenerate this clip',key)
            aligned,_=acoustic.align_part(dict(key=key,narration=p['text']),model,tokenizer)
            with wave.open(str(temp),'rb') as f:part=f.readframes(f.getnframes())
            signal=np.frombuffer(part,dtype='<i2').astype(float)/32768;step=240
            rms=np.sqrt(np.mean(signal[:len(signal)//step*step].reshape(-1,step)**2,axis=1));threshold=max(.001,float(np.percentile(rms,90))*.025)
            positions=[]
            for cut in full_stops(aligned,aligned['duration']):
                center=round(cut/.01);lo=max(1,center-25);hi=min(len(rms)-1,center+26)
                quiet=[k for k in range(lo,hi) if rms[k]<threshold]
                if not quiet:
                    lo=max(1,center-60);hi=min(len(rms)-1,center+61)
                    quiet=[k for k in range(lo,hi) if rms[k]<threshold]
                if not quiet:raise RuntimeError(f'No safe acoustic pause near sentence boundary: {key} {cut:.3f}')
                k=min(quiet,key=lambda k:abs(k-center));pos=k*step
                if not positions or pos>positions[-1]:positions.append(pos)
                refinements.append(dict(part=i,alignedSeconds=cut,acousticSeconds=pos/RATE))
            chunks=[];cursor=0
            for pos in positions:chunks.extend([part[cursor*2:pos*2],bytes(2400*2)]);cursor=pos
            chunks.append(part[cursor*2:]);part=b''.join(chunks)
            voiced=np.flatnonzero(rms>threshold)
            assert len(voiced)>10,('No measurable narration',key)
            onset=max(0,(int(voiced[0])*.01-.055))
            offset=len(pcm)//2/RATE
            timings.append(dict(index=i,start=offset,onset=offset+onset,end=offset+len(part)/2/RATE,lines=p['lines'],cue=p['text'],result=p['result']))
            pcm.extend(part)
            if p['text'].endswith('。'):pcm.extend(bytes(2400*2))
        target=audio/(s['key']+'.wav')
        with wave.open(str(target),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(pcm)
        data=dict(key=s['key'],samples=len(pcm)//2,duration=len(pcm)/2/RATE,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),timeBase='final-audio',timeUnit='seconds',parts=timings,pauseRefinements=refinements)
        save(target.with_suffix('.json'),data);reports.append(dict(key=s['key'],seconds=data['duration'],parts=len(timings),pauses=len(refinements)))
        print('AUDIO_PREPARED',s['key'],round(data['duration'],3),flush=True)
    save(ROOT/'build/audio-preparation.json',dict(settings=settings,scenes=reports));print('AUDIO_PREPARATION_DONE',sum(r['seconds'] for r in reports),flush=True)
if __name__=='__main__':main()
