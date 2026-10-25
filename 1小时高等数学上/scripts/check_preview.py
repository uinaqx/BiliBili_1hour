import bisect,json,pathlib,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import draw
from preview import clips
from check import ROOT,BUILD,DEL,load,digest,write,pixel_check
def main():
    t=load(ROOT/'public/timeline.json');draw.init(t);by={s['key']:s for s in t['scenes']};video=DEL/'90秒内部试片.mp4';meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],text=True));v=next(s for s in meta['streams'] if s['codec_type']=='video');assert abs(float(meta['format']['duration'])-90)<.04 and int(v['nb_frames'])==2700
    samples=[];cursor=0
    for key,start,seconds in clips(t):
        s=by[key];targets={start,start+seconds*15,start+seconds*30-1}
        for u in s['units']:
            targets.update(f for f in [u['begin']-1,u['begin'],u['begin']+1,u['end']+1] if start<=f<start+seconds*30)
        for f in s['renderFrames']:
            if start<=f<start+seconds*30:targets.add(f)
        for f in sorted(targets):samples.append((cursor+f-start,key,f))
        cursor+=seconds*30
    out=BUILD/'preview-review';out.mkdir(exist_ok=True);filt=out/'select.txt';filt.write_text("select='"+'+'.join(f'eq(n,{f})' for f,_,_ in samples)+"'",encoding='ascii');subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-filter_script:v',str(filt),'-fps_mode','passthrough',str(out/'sample-%03d.png')],check=True);errors=[]
    for i,(_,key,frame) in enumerate(samples,1):
        with Image.open(out/f'sample-{i:03}.png') as im:
            pixel_check(im,by[key],frame);a=np.asarray(im).astype(np.int16);b=np.asarray(draw.render(by[key],frame)).astype(np.int16);error=float(np.mean(abs(a-b)));assert error<4,(key,frame,error);errors.append(error)
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    for first in range(0,len(samples),12):
        sheet=Image.new('RGB',(1440,1184),draw.BG);d=ImageDraw.Draw(sheet)
        for i,(f,key,_) in enumerate(samples[first:first+12]):
            x=i%3*480;y=i//3*296
            with Image.open(out/f'sample-{first+i+1:03}.png') as im:sheet.paste(im.resize((480,270)),(x,y))
            d.text((x+8,y+272),f'{key} · {f/30:.2f}s',font=font,fill='white')
        sheet.save(out/f'contact-{first//12+1:02}.jpg',quality=93)
    subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
    r=dict(allPassed=True,duration=90,frames=2700,actualSamples=len(samples),maxMAE=max(errors),videoSha256=digest(video),timelineSha256=digest(ROOT/'public/timeline.json'));write(BUILD/'preview-validation.json',r);print(json.dumps(r),flush=True)
if __name__=='__main__':main()
