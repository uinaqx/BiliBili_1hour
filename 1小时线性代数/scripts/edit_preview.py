"""Account-free layout preview; not a measured final audio timeline."""
import json,pathlib
from PIL import Image,ImageDraw,ImageFont
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));assert t['scope']=='layout-only','Use timeline.py --layout for silent editing'
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));draw.prepare_formulas(course);draw.init(t);out=ROOT/'out/edit-preview';out.mkdir(parents=True,exist_ok=True);items=[]
    for s in t['scenes']:
        for u in s['units']:
            frame=(u['motions'][-1]['end'] if u.get('motions') else u['begin']);path=out/(s['key']+'-p'+str(u['index'])+'.png');draw.render(s,frame).save(path);items.append((s['key'],u['index'],path))
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    for start in range(0,len(items),12):
        sheet=Image.new('RGB',(1440,1184),draw.BG);d=ImageDraw.Draw(sheet)
        for n,(key,part,path) in enumerate(items[start:start+12]):
            x=n%3*480;y=n//3*296
            with Image.open(path) as im:sheet.paste(im.resize((480,270)),(x,y))
            d.text((x+8,y+272),key+' / '+str(part+1),font=font,fill='white')
        sheet.save(out/('contact-'+str(start//12+1).zfill(2)+'.jpg'),quality=90)
    print('SILENT_LAYOUT_PREVIEW',len(items),'states; no audio or account; output out/edit-preview',flush=True)
if __name__=='__main__':main()
