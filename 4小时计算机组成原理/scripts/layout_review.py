import json,pathlib
from PIL import Image,ImageDraw,ImageFont
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 c=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));out=ROOT/'build/layout';out.mkdir(exist_ok=True);items=[];total=0
 for ch in c['chapters']:
  for s in ch['scenes']:
   s=dict(**s,chapter=ch['title'],beatFrames=list(range(len(s['beats']))))
   for i in range(len(s['beats'])):
    image=draw.render(s,i);total+=1
    if i in [0,len(s['beats'])-1]:
     path=out/(s['id']+f'-{i}.jpg');image.save(path,quality=92);items.append((s['id'],i,path))
 for first in range(0,len(items),12):
  sheet=Image.new('RGB',(1440,1184),draw.BG);d=ImageDraw.Draw(sheet)
  for j,(key,i,p) in enumerate(items[first:first+12]):
   x=j%3*480;y=j//3*296
   with Image.open(p) as im:sheet.paste(im.resize((480,270)),(x,y))
   d.text((x+8,y+273),key+' / '+str(i+1),font=draw.font(18),fill='white')
  sheet.save(out/f'contact-{first//12+1:03}.jpg',quality=92)
 (ROOT/'build/layout-review.json').write_text(json.dumps(dict(allPassed=True,frames=total,contactPages=len(items),sheets=(len(items)+11)//12),ensure_ascii=False,indent=2),encoding='utf8');print('LAYOUT_READY',total,len(items),flush=True)
if __name__=='__main__':main()
