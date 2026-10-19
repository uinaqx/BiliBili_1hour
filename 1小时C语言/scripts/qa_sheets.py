"""Review one completed state per scene and every quiz countdown."""
import json,pathlib
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path(__file__).resolve().parents[1]
t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf-8'))
out=ROOT/'build/qa';out.mkdir(exist_ok=True)
jobs={j['frame']:j for j in t['renderJobs']};chosen=[]
for s in t['scenes']:
    chosen.append(jobs[s['startFrame']+s['steps'][3]+12])
    if s['kind']=='question':chosen.append(jobs[s['startFrame']+s['leadFrames']+s['speechFrames']+s['sentenceTailFrames']+30])
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)
for start in range(0,len(chosen),12):
    sheet=Image.new('RGB',(1440,1176),'#111827');d=ImageDraw.Draw(sheet)
    for k,j in enumerate(chosen[start:start+12]):
        x=(k%3)*480;y=(k//3)*294
        with Image.open(ROOT/'public'/j['path']) as im:sheet.paste(im.resize((480,270)),(x,y))
        d.text((x+8,y+271),j['sceneKey']+' · '+str(j['frame']),font=font,fill='white')
    sheet.save(out/f'scenes-{start//12+1:02}.jpg',quality=92)
print('QA_SHEETS',len(chosen))
