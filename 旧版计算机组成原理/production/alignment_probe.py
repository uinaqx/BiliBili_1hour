"""Compare acoustic forced alignment with the provider's timestamp estimates."""
import json,pathlib,sys,time
import numpy as np
import torch,whisper
from whisper.timing import find_alignment
from whisper.tokenizer import get_tokenizer
sys.stdout.reconfigure(encoding='utf-8')
torch.set_num_threads(6)
P=pathlib.Path(__file__).resolve().parent
model=whisper.load_model('base',device='cpu')
tokenizer=get_tokenizer(True,language='zh',task='transcribe')
key=sys.argv[1] if len(sys.argv)>1 else 'S01-lesson'
m=json.loads((P/'audio_original'/(key+'.json')).read_text(encoding='utf-8'))
audio=whisper.load_audio(str(P/'audio_original'/(key+'.mp3')))
words=[w for w in m['words'] if w['begin_time']<21000]
text=''.join(w['text'] for w in words)
end=min(len(audio)/16000,words[-1]['end_time']/1000+1.5)
wave=audio[:round(end*16000)]
mel=whisper.log_mel_spectrogram(whisper.pad_or_trim(wave))
start=time.time()
aligned=find_alignment(model,tokenizer,tokenizer.encode(text),mel,len(wave)//160)
print('elapsed',time.time()-start,'audio',end)
for i,w in enumerate(aligned):
 print(w.word,round(w.start,3),round(w.end,3),round(w.probability,3))
(P/'alignment-probe.json').write_text(json.dumps([dict(text=w.word,start=float(w.start),end=float(w.end),probability=float(w.probability)) for w in aligned],ensure_ascii=False,indent=2),encoding='utf-8')
