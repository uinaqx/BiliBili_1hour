"""Independent short-window timing review of the repeated long IPv4 phrase."""
import json,pathlib
import torch,whisper
from whisper.timing import find_alignment
from whisper.tokenizer import get_tokenizer
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    torch.set_num_threads(4)
    model=whisper.load_model(str(pathlib.Path.home()/'.cache/whisper/base.pt'),device='cpu')
    tokenizer=get_tokenizer(True,language='zh',task='transcribe')
    source=ROOT/'public/audio_original/net-06-02-p01.mp3'
    raw=whisper.load_audio(str(source));start=18.5;end=len(raw)/16000
    phrase='七十落在第二条里，这条前缀更长，所以走一九二点一六八点一点六四斜杠二十七那条。确定表项后从对应接口转发。'
    segment=raw[round(start*16000):round(end*16000)]
    found=find_alignment(model,tokenizer,tokenizer.encode(phrase),whisper.log_mel_spectrogram(whisper.pad_or_trim(segment)),len(segment)//160)
    report=dict(source=source.name,cropStart=start,cropEnd=end,reference=phrase,words=[dict(text=w.word,start=round(start+float(w.start),4),end=round(start+float(w.end),4),probability=float(w.probability)) for w in found])
    (ROOT/'build/route-anchor-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
