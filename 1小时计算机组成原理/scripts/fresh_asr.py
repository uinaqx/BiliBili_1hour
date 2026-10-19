"""Independent local ASR of the delivered clean MP4; never reads former subtitles."""
from __future__ import annotations
import argparse, dataclasses, hashlib, importlib.metadata, json, math, os, re, subprocess, sys, time, wave
from pathlib import Path
import numpy as np
try:
    from opencc import OpenCC
except ImportError:
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'build/fresh-subtitles-20261019/asr/vendor'))
    from opencc import OpenCC

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/fresh-subtitles-20261019/asr'
INPUT = ROOT/'out/一小时学习计算机组成原理_无字幕版.mp4'
CC = OpenCC('t2s')

def dump(path, value):
    path = Path(path)
    tmp = path.with_suffix(path.suffix + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=lambda x:x.item() if isinstance(x,np.generic) else str(x)), encoding='utf-8')
    tmp.replace(path)

def log(text):
    line = time.strftime('%Y-%m-%d %H:%M:%S') + ' ' + text
    print(line, flush=True)
    with (OUT/'run.log').open('a', encoding='utf-8') as f:
        f.write(line+'\n')

def prepare_audio():
    audio = OUT/'actual-video-audio-16k.wav'
    try:
        with wave.open(str(audio),'rb') as probe:
            valid=probe.getframerate()==16000 and probe.getnchannels()==1 and probe.getnframes()>4000*16000
    except (OSError,EOFError,wave.Error):valid=False
    if not valid:
        temporary=OUT/'actual-video-audio-16k.tmp.wav'
        subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-i', str(INPUT),
                        '-map', '0:a:0', '-vn', '-ac', '1', '-ar', '16000', '-c:a', 'pcm_s16le', str(temporary)], check=True)
        temporary.replace(audio)
    with wave.open(str(audio),'rb') as w:
        assert w.getframerate()==16000 and w.getnchannels()==1
        pcm = np.frombuffer(w.readframes(w.getnframes()), dtype='<i2').astype(np.float32)/32768
    return audio, pcm

def boundaries(pcm):
    # Put independent windows in real silence near two-minute marks, never script scene times.
    sr=16000
    hop=320
    n=len(pcm)//hop
    energy=np.sqrt(np.mean(pcm[:n*hop].reshape(n,hop)**2, axis=1))
    points=[0.0]
    total=len(pcm)/sr
    while points[-1]+140 < total:
        target=points[-1]+120
        lo=int((target-10)/.02)
        hi=min(n-25,int((target+10)/.02))
        # 500ms rolling energy favors a true gap, tie-break toward the center.
        x=np.convolve(energy[lo:hi+25],np.ones(25)/25,mode='valid')
        cost=x+np.abs(np.arange(len(x))*.02+(lo+12)*.02-target)*.000015
        index=lo+12+int(np.argmin(cost))
        points.append(round(index*.02,3))
    points.append(total)
    return points

def correct_text(text):
    text=CC.convert(text)
    text=re.sub(r'\bC\s*P\s*U\b','CPU',text,flags=re.I)
    text=re.sub(r'\bA\s*L\s*U\b','ALU',text,flags=re.I)
    text=re.sub(r'\bR\s*A\s*M\b','RAM',text,flags=re.I)
    text=re.sub(r'\bR\s*O\s*M\b','ROM',text,flags=re.I)
    text=re.sub(r'\bI\s*R\b','IR',text)
    text=re.sub(r'\bP\s*C\b','PC',text)
    text=re.sub(r'\bD\s*M\s*A\b','DMA',text,flags=re.I)
    text=re.sub(r'\bI\s*/\s*O\b','I/O',text,flags=re.I)
    return text.strip()

def srt_time(x):
    ms=round(max(0,x)*1000)
    h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

def build_subtitles(chunks):
    words=[]
    for chunk in chunks:
        for seg in chunk['segments']:
            for w in seg['words']:
                if w['accepted'] and w['word'].strip():
                    words.append(w)
    words.sort(key=lambda w:(w['start'],w['end']))
    for index,word in enumerate(words):word['word_index']=index
    groups=[]; group=[]
    for word in words:
        if group:
            text=correct_text(''.join(x['word'] for x in group))
            proposed=correct_text(text+word['word'])
            silence=word['start']-group[-1]['end']
            if len(proposed)>36 or word['end']-group[0]['start']>8.0 or silence>.65:
                groups.append(group);group=[]
        group.append(word)
        text=correct_text(''.join(x['word'] for x in group))
        if re.search(r'[。！？.!?]$', text) or (len(text)>=12 and re.search(r'[，,；;：:]$',text)):
            groups.append(group);group=[]
    if group: groups.append(group)
    cues=[]
    for i,group in enumerate(groups):
        start=group[0]['start']
        end=max(w['end'] for w in group)
        next_start=groups[i+1][0]['start'] if i+1<len(groups) else end+1
        # Never advance the next cue. Keep a previous cue across short pauses.
        hold=next_start if next_start-end<=.7 else end+.25
        end=min(next_start,max(end,hold))
        text=correct_text(''.join(w['word'] for w in group))
        cues.append({'index':i+1,'start':round(start,3),'end':round(end,3),'text':text,
                     'first_word_start':group[0]['start'],'last_word_end':max(w['end'] for w in group),
                     'word_count':len(group),'min_probability':min(w['probability'] for w in group),
                     'word_indices':[w['word_index'] for w in group],'words':group})
    dump(OUT/'words.json',words)
    dump(OUT/'cues-draft.json',cues)
    dump(OUT/'captions.json',{'captions':cues,'source':'independent-local-whisper-actual-mp4-audio',
                            'status':'draft-unreviewed','word_count':len(words)})
    srt='\n\n'.join(f"{c['index']}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{c['text']}" for c in cues)+'\n'
    (OUT/'fresh-whisper-draft.srt').write_text(srt,encoding='utf-8-sig')
    (OUT/'fresh-transcript.txt').write_text('\n'.join(c['text'] for c in cues),encoding='utf-8')
    dump(OUT/'low-confidence.json',[w for w in words if w['probability']<.45 or w['end']-w['start']>1.6 or w['end']<=w['start']])
    return words,cues

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=0);ap.add_argument('--rebuild',action='store_true');ap.add_argument('--backend',choices=['base','small','base-ct2'],default='base');args=ap.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
    audio,pcm=prepare_audio();points=boundaries(pcm)
    dump(OUT/'source.json',{'input':str(INPUT),'duration':len(pcm)/16000,
                          'audio_sha256':hashlib.sha256(audio.read_bytes()).hexdigest(),
                          'boundaries':points,'model':'openai/whisper-base' if args.backend.startswith('base') else 'Systran/faster-whisper-small',
                          'model_source':'https://github.com/openai/whisper' if args.backend=='base' else 'https://huggingface.co/Systran/faster-whisper-small',
                          'implementation':'https://github.com/openai/whisper' if args.backend=='base' else 'https://github.com/SYSTRAN/faster-whisper',
                          'reads_previous_transcripts':False,'voice_modified':False})
    model=None;all_chunks=[];t0=time.monotonic()
    count=len(points)-1
    for i,(start,end) in enumerate(zip(points,points[1:])):
        if args.limit and i>=args.limit: break
        path=OUT/f'chunk-{i:03}.json'
        if path.exists():
            all_chunks.append(json.loads(path.read_text(encoding='utf-8')));continue
        if args.rebuild:continue
        if model is None:
            log(f'Loading multilingual {args.backend} model, CPU, 6 threads')
            if args.backend=='base':
                import whisper, torch
                torch.set_num_threads(6)
                model=whisper.load_model('base',device='cpu')
            else:
                from faster_whisper import WhisperModel
                local=ROOT/'build/fresh-subtitles-20261019/base-ct2' if args.backend=='base-ct2' else OUT/'small-model'
                model=WhisperModel(str(local) if (local/'model.bin').exists() else 'small',device='cpu',compute_type='int8',cpu_threads=6,num_workers=1,download_root=str(OUT/'model-cache'))
            log('Model ready')
        begin=time.monotonic();clip_start=max(0,start-.6);clip_end=min(len(pcm)/16000,end+.6)
        clip=pcm[round(clip_start*16000):round(clip_end*16000)]
        prompt='以下是普通话计算机组成原理课程，使用简体中文。CPU，ALU，Cache，RAM，ROM，PC，IR，DMA，I/O，补码，高速缓存，流水线。'
        if args.backend=='base':
            decoded=model.transcribe(clip,language='zh',task='transcribe',beam_size=5,fp16=False,
                                     word_timestamps=True,condition_on_previous_text=False,
                                     initial_prompt=prompt,temperature=0.0,verbose=False)
            result=[]
            for seg in decoded['segments']:
                result.append({'id':seg['id'],'start':round(clip_start+seg['start'],3),'end':round(clip_start+seg['end'],3),
                               'text':seg['text'],'avg_logprob':seg['avg_logprob'],'no_speech_prob':seg['no_speech_prob'],
                               'compression_ratio':seg['compression_ratio'],
                               'words':[{'word':CC.convert(w['word']),'start':round(clip_start+w['start'],3),
                                         'end':round(clip_start+w['end'],3),'probability':w['probability'],
                                         'accepted':start<=(clip_start+(w['start']+w['end'])/2)<end,
                                         'chunk':i,'segment':seg['id']} for w in seg.get('words',[])]})
            language='zh';language_probability=1.0
        else:
            segs,info=model.transcribe(clip,language='zh',task='transcribe',beam_size=5,
                                 word_timestamps=True,condition_on_previous_text=False,
                                 vad_filter=True,vad_parameters={'min_silence_duration_ms':300,'speech_pad_ms':220},
                                 initial_prompt=prompt,
                                 temperature=0.0,hallucination_silence_threshold=1.0)
            result=[]
            for seg in segs:
                result.append({'id':seg.id,'start':round(clip_start+seg.start,3),'end':round(clip_start+seg.end,3),
                           'text':seg.text,'avg_logprob':seg.avg_logprob,'no_speech_prob':seg.no_speech_prob,
                           'compression_ratio':seg.compression_ratio,
                           'words':[{'word':CC.convert(w.word),'start':round(clip_start+w.start,3),
                                     'end':round(clip_start+w.end,3),'probability':w.probability,
                                     'accepted':start<=(clip_start+(w.start+w.end)/2)<end,
                                     'chunk':i,'segment':seg.id} for w in (seg.words or [])]})
            language=info.language;language_probability=info.language_probability
        elapsed=time.monotonic()-begin
        chunk={'index':i,'core_start':start,'core_end':end,'clip_start':clip_start,'clip_end':clip_end,
               'elapsed_seconds':elapsed,'segments':result,'backend':args.backend,'language':language,'language_probability':language_probability}
        dump(path,chunk);all_chunks.append(chunk)
        log(f'Chunk {i+1}/{count}: {start:.2f}..{end:.2f}s audio in {elapsed:.1f}s, real-time-factor={elapsed/(end-start):.3f}')
        build_subtitles(all_chunks)
        dump(OUT/'progress.json',{'complete_chunks':i+1,'total_chunks':count,'recognized_through':end,'elapsed_seconds':time.monotonic()-t0})
    words,cues=build_subtitles(all_chunks)
    dump(OUT/'transcript-raw.json',{'chunks':all_chunks,'word_count':len(words),'cue_count':len(cues)})
    log(f'FINISHED {len(all_chunks)} chunks; {len(words)} words, {len(cues)} cues; elapsed {time.monotonic()-t0:.1f}s')

if __name__=='__main__':main()
