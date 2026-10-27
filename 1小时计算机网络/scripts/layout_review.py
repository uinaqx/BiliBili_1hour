"""Render every formula state and sample every authored geometric interval."""
import hashlib,json,pathlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));draw.prepare_formulas(json.loads((ROOT/'public/course.json').read_text(encoding='utf8')));draw.init(t);out=ROOT/'build/layout-qa';out.mkdir(exist_ok=True);items=[];samples=0;motion=[]
    for s in t['scenes']:
        for u in s['units']:
            positions={u['begin']}
            for m in u['motions']:
                frames=[m['begin']+round((m['end']-m['begin'])*q) for q in [0,.25,.5,.75,1]];positions.update(frames);images=[np.asarray(draw.render(s,f).crop((78,603,1243,913))).astype(np.int16) for f in frames[1:4]];diffs=[float(np.mean(abs(a-b))) for a,b in zip(images,images[1:])];assert min(diffs)>.003,('Motion is static',s['key'],u['index'],diffs);motion.append(dict(key=s['key'],part=u['index'],changes=diffs))
            for f in sorted(positions):draw.render(s,f);samples+=1
            final=u['motions'][-1]['end'] if u['motions'] else u['begin'];path=out/f"{s['key']}-{u['index']}.png";draw.render(s,final).save(path);items.append((s['key'],u['index'],path))
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    for first in range(0,len(items),12):
        sheet=Image.new('RGB',(1440,1184),draw.BG);d=ImageDraw.Draw(sheet)
        for i,(key,index,path) in enumerate(items[first:first+12]):
            x=i%3*480;y=i//3*296
            with Image.open(path) as im:sheet.paste(im.resize((480,270)),(x,y))
            d.text((x+8,y+272),f'{key} / {index+1}',font=font,fill='white')
        sheet.save(out/f'contact-{first//12+1:02}.jpg',quality=93)
    r=dict(allPassed=True,pages=len(t['scenes']),parts=len(items),checkedSourceFrames=samples,motionIntervals=len(motion),courseSha256=hashlib.sha256((ROOT/'public/course.json').read_bytes()).hexdigest(),drawingSourceSha256=hashlib.sha256((ROOT/'scripts/draw.py').read_bytes()).hexdigest(),diagramSourceSha256=hashlib.sha256((ROOT/'scripts/diagrams.py').read_bytes()).hexdigest(),scope='actual rendered layouts and quarter/half/three-quarter geometric changes; not final audio or codec verification',motion=motion)
    (ROOT/'build/layout-review.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in r.items() if k!='motion'},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
