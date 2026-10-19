"""Offline base-model pilot of the clean MP4, independent of all past timings."""
import json, subprocess, time
from pathlib import Path
import whisper, torch
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/fresh-subtitles-20261019/asr'
SOURCE=ROOT/'out/一小时学习计算机组成原理_无字幕版.mp4'
OUT.mkdir(parents=True,exist_ok=True)
audio=OUT/'actual-video-audio-16k.wav'
if not audio.exists():
    subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(SOURCE),'-map','0:a:0','-vn','-ac','1','-ar','16000','-c:a','pcm_s16le',str(audio)],check=True)
torch.set_num_threads(6)
t=time.time()
print('Loading local base model',flush=True)
model=whisper.load_model('base',device='cpu')
print('Model ready; transcribing first 60 seconds',flush=True)
pcm=whisper.load_audio(str(audio))[:60*16000]
result=model.transcribe(pcm,language='zh',fp16=False,word_timestamps=True,beam_size=5,
                        condition_on_previous_text=False,verbose=False,
                        initial_prompt='普通话计算机组成原理课程，简体中文。CPU，ALU，Cache，补码，寄存器，流水线。')
result['elapsed_seconds']=time.time()-t
(OUT/'base-pilot-60s.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print('DONE',result['elapsed_seconds'],result['text'],flush=True)
