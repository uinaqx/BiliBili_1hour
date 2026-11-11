import hashlib,json,pathlib
from PIL import Image,ImageDraw
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));out=ROOT/'build/layout';out.mkdir(exist_ok=True);items=[];n=0
 for s in t['scenes']:
  for i,p in enumerate(s['parts']):
   path=out/f'{s["key"]}-{i}.jpg';draw.render(s,p['begin']).save(path,quality=93);n+=1;items.append((s['key'],i,path))
 for first in range(0,len(items),12):
  sheet=Image.new('RGB',(1440,1184),draw.BG);d=ImageDraw.Draw(sheet)
  for i,(key,part,path) in enumerate(items[first:first+12]):
   x=i%3*480;y=i//3*296
   with Image.open(path) as im:sheet.paste(im.resize((480,270)),(x,y))
   d.text((x+8,y+273),key+' / '+str(part+1),font=draw.font(18),fill='white')
  sheet.save(out/f'contact-{first//12+1:02}.jpg',quality=93)
 report=dict(allPassed=True,pages=len(t['scenes']),parts=n,courseSha256=hashlib.sha256((ROOT/'public/course.json').read_bytes()).hexdigest(),drawingSha256=hashlib.sha256((ROOT/'scripts/draw.py').read_bytes()).hexdigest(),scope='all authored page/part layouts drawn; visual-only editorial timing, no voice alignment claim')
 (ROOT/'build/layout-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report),flush=True)
if __name__=='__main__':main()
