"""Independent speech recognition for the two largest provider/alignment disagreements."""
import json,pathlib,sys
import torch,whisper
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1]
torch.set_num_threads(4);model=whisper.load_model('base',device='cpu');rows=[]
for key in ('c-07-5','c-08-3'):
    path=ROOT/'public/audio'/(key+'.scaled.wav')
    result=model.transcribe(str(path),language='zh',fp16=False,word_timestamps=True,temperature=0,verbose=False,condition_on_previous_text=False)
    row=dict(key=key,segments=[dict(start=s['start'],end=s['end'],text=s['text'],words=s['words']) for s in result['segments']]);rows.append(row)
    print('RECOGNIZED',key,json.dumps([dict(start=s['start'],end=s['end'],text=s['text']) for s in row['segments']],ensure_ascii=False),flush=True)
(ROOT/'build/subtitle-recognition-spotcheck.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
