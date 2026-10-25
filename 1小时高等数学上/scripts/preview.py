"""Strict 90 seconds of actual narration, formula changes, countdown and answers."""
import json,pathlib,subprocess,wave
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out'
def clips(t):
    by={s['key']:s for s in t['scenes']}
    return [('ca-01-03',0,25),('ca-01-08',by['ca-01-08']['durationFrames']-240,8),('ca-01-09',0,15),('ca-04-02',by['ca-04-02']['units'][1]['begin']-45,17),('ca-07-06',0,15),('ca-10-06',by['ca-10-06']['units'][1]['begin']-30,10)]
def main():
    t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));assert t['scope']=='complete-course';draw.init(t);by={s['key']:s for s in t['scenes']};out=BUILD/'preview';out.mkdir(exist_ok=True);rows=['ffconcat version 1.0'];pcm=bytearray();total=0
    for clip,(key,start,seconds) in enumerate(clips(t)):
        s=by[key];count=seconds*30;assert 0<=start<start+count<=s['durationFrames'];points=sorted({start,*[f for f in s['renderFrames'] if start<f<start+count]})
        for i,f in enumerate(points):
            path=out/f'{clip}-{f:05}.png';draw.render(s,f).save(path);end=points[i+1] if i+1<len(points) else start+count;rows.extend([f"file '{path.as_posix()}'",'option framerate 30',f'duration {(end-f)/30:.9f}']);total+=1
        with wave.open(str(ROOT/'public'/s['audio'])) as w:data=w.readframes(w.getnframes())
        full=bytes(s['leadFrames']*1600)+data;full+=bytes(max(0,s['durationFrames']*1600-len(full)));pcm.extend(full[start*1600:(start+count)*1600])
    assert len(pcm)==90*24000*2;rows.extend([f"file '{path.as_posix()}'",'option framerate 30']);listing=out/'preview.ffconcat';listing.write_text('\n'.join(rows)+'\n',encoding='utf8');audio=out/'preview.wav'
    with wave.open(str(audio),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm)
    subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(listing),'-i',str(audio),'-vf','fps=30','-af','loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000','-t','90','-frames:v','2700','-c:v','libx264','-preset','veryfast','-crf','19','-bf','0','-threads','4','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(DEL/'90秒内部试片.mp4')],check=True)
    print('PREVIEW_DONE',total,'source states, 90 seconds',flush=True)
if __name__=='__main__':main()
