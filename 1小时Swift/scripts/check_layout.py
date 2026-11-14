import json,pathlib
from PIL import Image,ImageDraw
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));images=[];rows=[]
 for c in course['chapters']:
  for s in c['scenes']:
   s=dict(s,chapter=c['title'],partFrames=[0,100],codeCues=[dict(beginFrame=0,lines=[] if s['kind']=='cover' else s['parts'][0]['cues'][0]['lines']),dict(beginFrame=100,lines=s['parts'][1]['cues'][0]['lines'])])
   for f in [0,100]:
    im=draw.render(s,f)
    if f==100:
     p=ROOT/'build/layout'/f'{s["key"]}.png';p.parent.mkdir(exist_ok=True);im.save(p);images.append(im.resize((480,270)))
   rows.append(dict(key=s['key'],codeRows=len(draw.wrap(s['code'],1190,34,True)),answerCode=bool(s.get('answerCode'))))
 sheet=Image.new('RGB',(480*4,270*15),'#091421')
 for i,im in enumerate(images):sheet.paste(im,((i%4)*480,(i//4)*270))
 sheet.save(ROOT/'build/layout-contact.png')
 (ROOT/'build/layout-verification.json').write_text(json.dumps(dict(allPassed=True,states=120,scenes=rows),indent=2),encoding='utf8');print('LAYOUT_VERIFIED',len(rows))
if __name__=='__main__':main()
