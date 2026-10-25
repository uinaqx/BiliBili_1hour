import json,pathlib,time
from PIL import Image,ImageDraw,ImageFont
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));draw.prepare_formulas(course);draw.init(t)
    out=ROOT/'build/layout';out.mkdir(exist_ok=True);chosen=[];started=time.time()
    for s in t['scenes']:
        for u in s['units']:
            frame=u['motions'][-1]['end'] if u['motions'] else u['begin']
            if u['index']+1<len(s['units']):frame=min(frame,s['units'][u['index']+1]['begin']-1)
            path=out/f'{s["key"]}-p{u["index"]:02}.png';draw.render(s,frame).save(path,compress_level=1);chosen.append((s['key'],u['index'],path))
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    for begin in range(0,len(chosen),12):
        sheet=Image.new('RGB',(1440,1184),draw.BG);d=ImageDraw.Draw(sheet)
        for i,(key,index,p) in enumerate(chosen[begin:begin+12]):
            x=i%3*480;y=i//3*296
            with Image.open(p) as im:sheet.paste(im.resize((480,270)),(x,y))
            d.text((x+8,y+272),f'{key} · {index+1}',font=font,fill='white')
        sheet.save(out/f'contact-{begin//12+1:02}.jpg',quality=93)
    print('LAYOUT_READY',len(chosen),round(time.time()-started,2),'seconds',flush=True)
if __name__=='__main__':main()
