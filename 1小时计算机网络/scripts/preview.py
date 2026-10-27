"""90-second internal edit of actual narration and continuously rendered diagrams."""
import json,pathlib,subprocess,wave
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out'
def clips(t):
    by={s['key']:s for s in t['scenes']}
    def move(key,index=0):return by[key]['units'][index]['motions'][0]['begin']-15
    specs=[('net-01-01',0,8),('net-01-07',by['net-01-07']['durationFrames']-300,10),('net-01-08',0,10),('net-02-02',move('net-02-02',1),12),('net-03-02',move('net-03-02',1),12),('net-04-03',move('net-04-03',1),12),('net-07-04',move('net-07-04',1),14),('net-09-02',move('net-09-02',1),12)]
    return [(k,max(0,min(b,by[k]['durationFrames']-seconds*30)),seconds) for k,b,seconds in specs]
def main():
    t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));assert t['scope']=='complete-course';draw.init(t);by={s['key']:s for s in t['scenes']};out=BUILD/'preview';out.mkdir(exist_ok=True);rows=['ffconcat version 1.0'];pcm=bytearray();total=0
    for clip,(key,start,seconds) in enumerate(clips(t)):
        s=by[key];count=seconds*30;assert 0<=start<start+count<=s['durationFrames'];points=sorted({start,*[f for f in s['renderFrames'] if start<f<start+count]})
        for i,f in enumerate(points):
            path=out/f'{clip}-{f:05}.png';draw.render(s,f).save(path,compress_level=1);end=points[i+1] if i+1<len(points) else start+count;rows.extend([f"file '{path.as_posix()}'",'option framerate 30',f'duration {(end-f)/30:.9f}']);total+=1
        with wave.open(str(ROOT/'public'/s['audio'])) as w:data=w.readframes(w.getnframes())
        full=bytes(s['leadFrames']*1600)+data;full+=bytes(max(0,s['durationFrames']*1600-len(full)));pcm.extend(full[start*1600:(start+count)*1600])
    assert len(pcm)==90*24000*2;rows.extend([f"file '{path.as_posix()}'",'option framerate 30']);listing=out/'preview.ffconcat';listing.write_text('\n'.join(rows)+'\n',encoding='utf8');audio=out/'preview.wav'
    with wave.open(str(audio),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm)
    subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(listing),'-i',str(audio),'-vf','fps=30','-af','loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000','-t','90','-frames:v','2700','-c:v','libx264','-preset','veryfast','-crf','19','-bf','0','-threads','4','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(DEL/'90秒内部试片.mp4')],check=True)
    print('PREVIEW_DONE',total,'source states, 90 seconds',flush=True)
if __name__=='__main__':main()
