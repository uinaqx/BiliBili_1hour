"""Inspect the actual 90-second preview and its visible motion states."""
import hashlib,json,pathlib,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'build/preview-review'
def main():
    OUT.mkdir(exist_ok=True);t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));draw.init(t);by={s['key']:s for s in t['scenes']}
    path=ROOT/'out/90秒内部试片.mp4'
    m=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],text=True,encoding='utf8'))
    video=next(s for s in m['streams'] if s['codec_type']=='video')
    assert abs(float(m['format']['duration'])-90)<.04 and int(video['nb_frames'])==2700
    a=by['la-04-03']['units'][0]['motions'][0]['begin'];b=by['la-09-02']['units'][0]['motions'][0]['begin']
    clips=[('la-01-03',0,18),('la-04-03',max(0,a-24),18),('la-07-01',0,14),('la-09-02',max(0,b-30),14),('la-10-01',0,10),('la-09-05',by['la-09-05']['durationFrames']-240,8),('la-09-06',0,8)]
    samples=[];cursor=0
    for key,start,seconds in clips:
        for local in [30,seconds*15,seconds*30-30]:samples.append((cursor+local,key,start+local))
        cursor+=seconds*30
    filt=OUT/'select.txt';filt.write_text("select='"+'+'.join(f'eq(n,{frame})' for frame,_,_ in samples)+"'",encoding='ascii')
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(path),'-filter_script:v',str(filt),'-fps_mode','passthrough',str(OUT/'sample-%02d.png')],check=True)
    errors=[]
    for i,(_,key,frame) in enumerate(samples,1):
        with Image.open(OUT/f'sample-{i:02}.png') as im:
            a=np.asarray(im.convert('RGB')).astype(np.int16);b=np.asarray(draw.render(by[key],frame)).astype(np.int16)
            error=float(np.mean(abs(a-b)));assert error<4,(key,frame,error);errors.append(error)
    sheet=Image.new('RGB',(1440,2072),draw.BG);d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    for i,(at,key,_) in enumerate(samples):
        x=i%3*480;y=i//3*296
        with Image.open(OUT/f'sample-{i+1:02}.png') as im:sheet.paste(im.resize((480,270)),(x,y))
        d.text((x+8,y+272),f'{key} · {at/30:.1f}s',font=font,fill='white')
    sheet.save(OUT/'contact.jpg',quality=93)
    r=dict(allPassed=True,seconds=90,frames=2700,sampledStates=len(samples),maxMAE=max(errors),videoSha256=hashlib.sha256(path.read_bytes()).hexdigest())
    (ROOT/'build/preview-validation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r),flush=True)
if __name__=='__main__':main()
