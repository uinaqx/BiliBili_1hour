"""Exactly 90 seconds of existing narration over source/board/summary layouts."""
import json,pathlib,subprocess,wave
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build/preview';DEL=ROOT/'out'
def main():
 c=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));by={s['id']:dict(**s,chapter=ch['title']) for ch in c['chapters'] for s in ch['scenes']};specs=[('m01-001',0,12),('m01-012',1,26),('m03-004',1,26),('m04a-001',0,26)];rows=['ffconcat version 1.0'];pcm=bytearray();BUILD.mkdir(exist_ok=True);DEL.mkdir(parents=True,exist_ok=True)
 for n,(key,index,seconds) in enumerate(specs):
  s=by[key];s['beatFrames']=list(range(len(s['beats'])));path=BUILD/(key+'.png');draw.render(s,index).save(path);rows.extend([f"file '{path.as_posix()}'",'option framerate 30',f'duration {seconds}'])
  with wave.open(str(ROOT/'public/audio'/(s['beats'][index]['key']+'.wav'))) as w:data=w.readframes(w.getnframes())
  data=data[:seconds*48000];pcm.extend(data+bytes(max(0,seconds*48000-len(data))))
 rows.extend([f"file '{path.as_posix()}'",'option framerate 30']);listing=BUILD/'preview.ffconcat';listing.write_text('\n'.join(rows)+'\n',encoding='utf8');audio=BUILD/'preview.wav'
 with wave.open(str(audio),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm)
 subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(listing),'-i',str(audio),'-vf','fps=30','-af','loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000','-t','90','-frames:v','2700','-c:v','libx264','-preset','veryfast','-crf','19','-threads','3','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(DEL/'90秒内部试片.mp4')],check=True);print('PREVIEW_DONE',flush=True)
if __name__=='__main__':main()
