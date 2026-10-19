"""Align natural-rate narration; never stretch the voice to meet a target duration."""
import json,pathlib,sys,time
import audio_timing as engine
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1]
scenes=[s for c in json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'))['chapters'] for s in c['scenes']]
def main():
 import torch,whisper
 from whisper.tokenizer import get_tokenizer
 engine.PACE=1.0;engine.VERSION='co-natural-v1-no-tempo-change'
 torch.set_num_threads(4);model=whisper.load_model('base',device='cpu');tokenizer=get_tokenizer(True,language='zh',task='transcribe');records=[]
 for i,s in enumerate(scenes,1):
  path=ROOT/'public/audio_original'/(s['key']+'.json')
  while not path.exists():time.sleep(5)
  aligned,cached=engine.align_part(s,model,tokenizer);data=engine.clip(s)
  for j,c in enumerate(data['captions']):c['end']=data['captions'][j+1]['start'] if j+1<len(data['captions']) else data['duration']
  assert all(c['end']>c['start'] for c in data['captions'])
  clean=lambda text:''.join(ch for ch in text if ch.isalnum())
  assert clean(''.join(c['text'] for c in data['captions']))==clean(''.join(w['text'] for w in data['words']))
  engine.save(ROOT/'public/audio'/(s['key']+'.json'),data)
  records.append(dict(key=s['key'],seconds=data['duration'],captions=len(data['captions']),onsetsRefined=len(data['captionOnsetRefinements']),providerDeltaP95=aligned['providerDeltaP95']))
  print('AUDIO_ALIGNED',f'{i}/{len(scenes)}',s['key'],round(data['duration'],3),flush=True)
 raw=sum(engine.load(ROOT/'public/audio_original'/(s['key']+'.json'))['duration'] for s in scenes)
 engine.save(ROOT/'build/audio-settings.json',dict(wholeCourseTempo=1.0,serviceRate=1.0,rawSeconds=raw,sentencePauseSeconds=.1,tempoAdjusted=False,allowedDurationSeconds=[3000,4200]))
 engine.save(ROOT/'build/audio-alignment.json',dict(clips=len(records),wholeCourseTempo=1.0,method='natural speech; known-transcript acoustic alignment; waveform onset refinement; cues held until next cue',results=records))
 print('AUDIO_PREPARATION_DONE',round(sum(r['seconds'] for r in records),3),flush=True)
if __name__=='__main__':main()
