"""Check the actual 90-second internal sample before starting the full export."""
import bisect,json,pathlib,subprocess
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from check import ROOT,BUILD,DEL,load,digest,pixels,expected,write
def main():
    t=load(ROOT/'public/timeline.json');by={s['key']:s for s in t['scenes']};video=DEL/'90秒内部试片.mp4'
    meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],text=True))
    v=next(x for x in meta['streams'] if x['codec_type']=='video');assert v['r_frame_rate']=='30/1' and int(v['nb_frames'])==2700 and abs(float(meta['format']['duration'])-90)<.03
    clips=[('rp-25-a2',0,810),('rp-30-q',by['rp-30-q']['durationFrames']-240,240),('rp-30-a1',0,900),('rp-30-v',0,750)]
    chosen=[];cursor=0
    for key,start,count in clips:
        s=by[key];jobs=[j for j in t['renderJobs'] if j['sceneKey']==key];pts=[j['frame']-s['startFrame'] for j in jobs]
        targets={start,start+count-1,start+count//2}
        for f in pts:
            if start<=f<start+count:targets.update(x for x in [f-1,f,f+1] if start<=x<start+count)
        for f in sorted(targets):chosen.append(dict(previewFrame=cursor+f-start,local=f,scene=s,job=jobs[bisect.bisect_right(pts,f)-1]))
        cursor+=count
    out=BUILD/'preview-qa';out.mkdir(exist_ok=True)
    filt=BUILD/'preview-qa-filter.txt';filt.write_text("select='"+'+'.join(f"eq(n,{x['previewFrame']})" for x in chosen)+"'",encoding='ascii')
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(video),'-filter_script:v',str(filt),'-fps_mode','passthrough',str(out/'sample-%03d.png')],check=True)
    records=[]
    for i,r in enumerate(chosen,1):
        path=out/f'sample-{i:03}.png';s=r['scene'];local=r['job']['frame']-s['startFrame']
        assert expected(s,r['local'])==expected(s,local)
        pixels(path,s,local,expected(s,local))
        with Image.open(path) as im,Image.open(ROOT/'public'/r['job']['path']) as ref:
            a=np.asarray(im).astype(np.int16);b=np.asarray(ref).astype(np.int16);mae=float(np.mean(abs(a-b)))
            assert mae<4,('Preview image mismatch',s['key'],r['previewFrame'],mae)
        records.append(dict(previewFrame=r['previewFrame'],key=s['key'],sourceLocal=r['local'],mae=mae))
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    for first in range(0,len(chosen),12):
        sheet=Image.new('RGB',(1440,1184),'#111827');d=ImageDraw.Draw(sheet)
        for k,r in enumerate(chosen[first:first+12]):
            with Image.open(out/f'sample-{first+k+1:03}.png') as im:sheet.paste(im.resize((480,270)),(k%3*480,k//3*296))
            d.text((k%3*480+8,k//3*296+272),f"{r['scene']['key']} · {r['previewFrame']/30:.2f}s",fill='white',font=font)
        sheet.save(out/f'contact-{first//12+1:02}.jpg',quality=92)
    subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True)
    r=dict(allPassed=True,duration=90,frames=2700,actualSamples=len(records),videoSha256=digest(video),timelineSha256=digest(ROOT/'public/timeline.json'),records=records)
    write(BUILD/'preview-validation.json',r);print('INTERNAL_PREVIEW_CHECKED',len(records),'actual frames',flush=True)
if __name__=='__main__':main()
