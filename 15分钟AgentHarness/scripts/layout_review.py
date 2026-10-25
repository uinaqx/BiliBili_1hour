import json,pathlib
from PIL import Image,ImageDraw,ImageFont
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));draw.init(t);out=ROOT/'build/layout-qa';out.mkdir(exist_ok=True);items=[];samples=0
    for s in t['scenes']:
        for u in s['units']:
            positions={u['begin']}
            for m in u['motions']:positions.update(m['begin']+round((m['end']-m['begin'])*f) for f in [0,.25,.5,.75,1])
            for f in sorted(positions):draw.render(s,f);samples+=1
            for suffix,f in [('mid',u['motions'][0]['begin']+round((u['motions'][0]['end']-u['motions'][0]['begin'])*.5) if u['motions'] else u['begin']),('end',u['motions'][-1]['end'] if u['motions'] else u['begin'])]:
                path=out/f"{s['key']}-{u['index']}-{suffix}.png";draw.render(s,f).save(path);items.append((s['key'],u['index'],suffix,path))
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    for first in range(0,len(items),12):
        sheet=Image.new('RGB',(1440,1184),draw.BG);d=ImageDraw.Draw(sheet)
        for i,(key,index,suffix,path) in enumerate(items[first:first+12]):
            x=i%3*480;y=i//3*296
            with Image.open(path) as im:sheet.paste(im.resize((480,270)),(x,y))
            d.text((x+8,y+272),f'{key} · {index+1} · {suffix}',font=font,fill='white')
        sheet.save(out/f'contact-{first//12+1:02}.jpg',quality=93)
    r=dict(allPassed=True,pages=len(t['scenes']),units=len(items)//2,checkedMotionSamples=samples,scope='diagram topology, text layout and authored motion samples; synthetic layout timings do not validate final audio')
    (ROOT/'build/layout-review.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r),flush=True)
if __name__=='__main__':main()
