"""Measured final PCM, known-transcript timing, sentence-only 100 ms pauses."""
import argparse,bisect,hashlib,json,pathlib,re,time,wave
import numpy as np
import audio_timing as acoustic
ROOT=pathlib.Path(__file__).resolve().parents[1];RATE=24000
def load(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def stops(meta):
 words=[w for w in meta['words'] if w['text'].strip()];out=[]
 for i,w in enumerate(words[:-1]):
  if '。' not in w['text']:continue
  if w['text'].lstrip('“”" ').startswith('。') and i:out.append((words[i-1]['end_time']+w['begin_time'])/2000)
  elif w['text'].rstrip('“”" ').endswith('。'):out.append((w['end_time']+words[i+1]['begin_time'])/2000)
 return sorted(set(out))
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--watch',action='store_true');a=parser.parse_args()
 import torch,whisper
 from whisper.tokenizer import get_tokenizer
 torch.set_num_threads(4);model=whisper.load_model(str(pathlib.Path.home()/'.cache/whisper/base.pt'),device='cpu');tok=get_tokenizer(True,language='zh',task='transcribe')
 course=load(ROOT/'public/course.json');out=ROOT/'public/audio';out.mkdir(exist_ok=True);reports=[]
 for c in course['chapters']:
  for s in c['scenes']:
   pcm=bytearray();parts=[];caps=[];refinements=[];think=[]
   for i,p in enumerate(s['parts']):
    key=s['key']+f'-p{i:02}';source=ROOT/'public/audio_original'/(key+'.mp3');meta=source.with_suffix('.json')
    while not (source.exists() and meta.exists()):
     if not a.watch:raise RuntimeError('Missing narration: '+key)
     print('WAIT_VOICE',key,flush=True);time.sleep(15)
    native=load(meta);assert native['narration']==p['text'] and native['rate']==1.05 and native['model']=='qwen-audio-3.1-tts-plus'
    aligned,_=acoustic.align_part(dict(key=key,narration=p['text']),model,tok)
    raw=acoustic.pcm_read(out/(key+'.scaled.wav'));signal=np.frombuffer(raw,dtype='<i2').astype(float)/32768;step=240
    rms=np.sqrt(np.mean(signal[:len(signal)//step*step].reshape(-1,step)**2,axis=1));threshold=max(.001,float(np.percentile(rms,90))*.025)
    cuts=[]
    for cut in stops(aligned):
     center=round(cut/.01);lo=max(1,center-25);hi=min(len(rms)-1,center+26);quiet=[k for k in range(lo,hi) if rms[k]<threshold]
     if not quiet:
      lo=max(1,center-60);hi=min(len(rms)-1,center+61);quiet=[k for k in range(lo,hi) if rms[k]<threshold]
     if not quiet:raise RuntimeError(f'No safe sentence boundary: {key} {cut}')
     pos=min(quiet,key=lambda k:abs(k-center))*step
     assert not cuts or pos>cuts[-1],(key,'Merged sentence pauses')
     cuts.append(pos)
    assert len(cuts)==p['text'].count('。')-1,(key,'Full stop count',len(cuts),p['text'].count('。')-1)
    chunks=[];cursor=0
    for pos in cuts:chunks.extend([raw[cursor*2:pos*2],bytes(2400*2)]);cursor=pos
    chunks.append(raw[cursor*2:]);part=b''.join(chunks);offset=len(pcm)/2/RATE
    voiced=np.flatnonzero(rms>threshold);assert len(voiced)>10
    onset=max(0,int(voiced[0])*.01-.055)
    words=[]
    for w in aligned['words']:
     w=dict(w);w['begin_time']+=bisect.bisect_right(cuts,round(w['begin_time']/1000*RATE))*100;w['end_time']+=bisect.bisect_left(cuts,round(w['end_time']/1000*RATE))*100;words.append(w)
    parts.append(dict(index=i,start=offset,onset=offset+onset,end=offset+len(part)/2/RATE,cue=p['text'],rawKey=key,rawSha256=hashlib.sha256(source.read_bytes()).hexdigest(),alignmentSha256=hashlib.sha256((ROOT/'build/alignment'/(key+'.json')).read_bytes()).hexdigest(),words=words,cutsSeconds=[x/RATE for x in cuts]))
    refinements.extend(dict(part=i,rawSeconds=x/RATE,addedSeconds=.1) for x in cuts);pcm.extend(part);pcm.extend(bytes(2400*2))
    if p.get('think'):
     think.append(dict(start=len(pcm)/2/RATE,end=len(pcm)/2/RATE+4));pcm.extend(bytes(4*RATE*2))
   # Validate the entire scene without clipping the previous spoken phrase.
   target=out/(s['key']+'.wav');acoustic.pcm_write(target,pcm);data=dict(key=s['key'],samples=len(pcm)//2,duration=len(pcm)/2/RATE,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),parts=parts,pauseRefinements=refinements,thinkIntervals=think,timeBase='final-audio',tempo=1.0,synthesisRate=1.05)
   save(target.with_suffix('.json'),data);reports.append(dict(key=s['key'],seconds=data['duration'],parts=len(parts),sentencePauses=len(refinements)));print('PREPARED',s['key'],round(data['duration'],3),flush=True)
 save(ROOT/'build/audio-preparation.json',dict(allPassed=True,scenes=reports,tempo=1.0,automaticTempoAdjustment=False,synthesisRate=1.05,model='qwen-audio-3.1-tts-plus',voice='xunanchuan_v3.1',fullStopExtraSeconds=.1,commaPauseUnchanged=True,method='Known-transcript acoustic alignment; sentence cuts in measured quiet intervals; sample-exact PCM assembly'))
 print('PREPARATION_DONE',len(reports),sum(x['seconds'] for x in reports),flush=True)
if __name__=='__main__':main()
