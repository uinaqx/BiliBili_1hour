"""Independent local recognition samples for human comparison with the source lecture."""
import json,pathlib,sys
import torch,whisper
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1]
torch.set_num_threads(3);model=whisper.load_model('base',device='cpu');out=[]
course=json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'));scenes={s['key']:s for c in course['chapters'] for s in c['scenes']}
for key,start in [('python-00-1',0),('python-01-1',0),('python-04-3',18),('python-08-1',0),('python-09-q',0),('python-11-a',0)]:
    audio=whisper.load_audio(str(ROOT/'public/audio_original'/(key+'.mp3')))[int(start*16000):int((start+25)*16000)]
    result=model.transcribe(audio,language='zh',fp16=False,temperature=0,verbose=False)
    out.append(dict(key=key,startSeconds=start,seconds=len(audio)/16000,recognized=result['text'],source=scenes[key]['sourceNarration']));print(key,result['text'],flush=True)
(ROOT/'build/speech-spotcheck.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
