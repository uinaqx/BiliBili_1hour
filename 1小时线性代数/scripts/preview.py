"""Ninety real-audio seconds covering vectors, elimination, eigendirections and surfaces."""
import bisect,json,pathlib,subprocess,wave
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build'
def main():
    t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));assert t['scope']=='complete-course';draw.init(t);by={s['key']:s for s in t['scenes']}
    a=by['la-04-03']['units'][0]['motions'][0]['begin'];b=by['la-09-02']['units'][0]['motions'][0]['begin']
    selected=[('la-01-03',0,18),('la-04-03',max(0,a-24),18),('la-07-01',0,14),('la-09-02',max(0,b-30),14),('la-10-01',0,10),('la-09-05',by['la-09-05']['durationFrames']-240,8),('la-09-06',0,8)]
    out=BUILD/'preview';out.mkdir(exist_ok=True);rows=['ffconcat version 1.0'];pcm=bytearray();count=0
    for clip,(key,start,seconds) in enumerate(selected):
        s=by[key];n=seconds*30;assert start+n<=s['durationFrames'];points=sorted({start,*[f for f in s['renderFrames'] if start<f<start+n]})
        for i,frame in enumerate(points):
            path=out/f'{clip}-{frame:05}.png';draw.render(s,frame).save(path,compress_level=1);end=points[i+1] if i+1<len(points) else start+n;rows.extend([f"file '{path.as_posix()}'",'option framerate 30',f'duration {(end-frame)/30:.9f}']);count+=1
        with wave.open(str(ROOT/'public'/s['audio'])) as f:data=f.readframes(f.getnframes())
        full=bytes(s['leadFrames']*1600)+data;full+=bytes(max(0,s['durationFrames']*1600-len(full)));pcm.extend(full[start*1600:(start+n)*1600])
        print('PREVIEW_CLIP_READY',key,len(points),flush=True)
    assert len(pcm)==90*24000*2
    rows.extend([f"file '{path.as_posix()}'",'option framerate 30']);listing=out/'preview.ffconcat';listing.write_text('\n'.join(rows)+'\n',encoding='utf8')
    audio=out/'preview.wav'
    with wave.open(str(audio),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(pcm)
    dest=ROOT/'out/90秒内部试片.mp4'
    subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(listing),'-i',str(audio),'-vf','fps=30','-af','loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000','-t','90','-frames:v','2700','-c:v','libx264','-preset','veryfast','-crf','19','-bf','0','-threads','4','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(dest)],check=True)
    print('PREVIEW_DONE',count,'source frames, 90 seconds',flush=True)
if __name__=='__main__':main()
