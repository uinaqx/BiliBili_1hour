"""Render every authored board state and check layout and persistent visible targets."""
import json,pathlib
from PIL import Image,ImageDraw,ImageFont
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));draw.prepare_formulas(course);draw.init(t);out=ROOT/'build/layout-qa';out.mkdir(exist_ok=True);items=[]
    for s in t['scenes']:
        for u in s['units']:
            frame=u['begin'];im=draw.render(s,frame);path=out/f"{s['key']}-{u['index']}.png";im.save(path);items.append((s['key'],u['index'],path))
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    for first in range(0,len(items),12):
        sheet=Image.new('RGB',(1440,1184),draw.BG);d=ImageDraw.Draw(sheet)
        for i,(key,index,path) in enumerate(items[first:first+12]):
            x=i%3*480;y=i//3*296
            with Image.open(path) as im:sheet.paste(im.resize((480,270)),(x,y))
            d.text((x+8,y+272),f'{key} · {index+1}',font=font,fill='white')
        sheet.save(out/f'contact-{first//12+1:02}.jpg',quality=93)
    r=dict(allPassed=True,pages=len(t['scenes']),states=len(items),scope='all authored board states; layout only, not final audio synchronization')
    (ROOT/'build/layout-review.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(r),flush=True)
if __name__=='__main__':main()
