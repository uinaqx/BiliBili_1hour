"""A strict 90-second internal sample: long code, output, countdown and answer."""
import bisect,json,pathlib,subprocess,wave
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out'
def main():
    t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));by={s['key']:s for s in t['scenes']}
    assert t['scope']=='complete-course'
    selected=[('rp-25-a2',0,810),('rp-30-q',by['rp-30-q']['durationFrames']-240,240),('rp-30-a1',0,900),('rp-30-v',0,750)]
    images=[];pcm=bytearray()
    for key,start,count in selected:
        s=by[key];assert 0<=start<start+count<=s['durationFrames'];jobs=[j for j in t['renderJobs'] if j['sceneKey']==key];times=[j['frame']-s['startFrame'] for j in jobs]
        points=sorted({start,*[x for x in times if start<x<start+count]})
        for i,p in enumerate(points):
            job=jobs[bisect.bisect_right(times,p)-1];images.append((ROOT/'public'/job['path'],(points[i+1] if i+1<len(points) else start+count)-p))
        with wave.open(str(ROOT/'public'/s['audio'])) as f:data=f.readframes(f.getnframes())
        full=bytes(s['leadFrames']*800*2)+data
        full+=bytes(max(0,s['durationFrames']*800*2-len(full)))
        pcm.extend(full[start*800*2:(start+count)*800*2])
    assert len(pcm)==90*24000*2 and sum(n for _,n in images)==2700
    audio=BUILD/'preview.wav'
    with wave.open(str(audio),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(24000);f.writeframes(pcm)
    rows=['ffconcat version 1.0']
    for p,n in images:rows.extend([f"file '{p.as_posix()}'",'option framerate 30',f'duration {n/30:.9f}'])
    rows.extend([f"file '{images[-1][0].as_posix()}'",'option framerate 30'])
    listing=BUILD/'preview.ffconcat';listing.write_text('\n'.join(rows)+'\n',encoding='utf8')
    dest=DEL/'90秒内部试片.mp4'
    subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(listing),'-i',str(audio),'-map','0:v:0','-map','1:a:0','-vf','fps=30','-af','loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,atrim=end_sample=4320000','-frames:v','2700','-t','90','-c:v','libx264','-preset','fast','-crf','20','-bf','0','-threads','4','-c:a','aac','-b:a','128k','-movflags','+faststart',str(dest)],check=True)
    duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(dest)],text=True));assert abs(duration-90)<.03
    print('PREVIEW_DONE',duration,flush=True)
if __name__=='__main__':main()
