"""Check layout-only PNGs. Synthetic timing cannot establish narration synchronization."""
import json,pathlib
from PIL import Image,ImageDraw,ImageFont
from check import pixels
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));assert t['scope']=='layout-only'
    by={s['key']:s for s in t['scenes']}
    for j in t['renderJobs']:
        s=by[j['sceneKey']];local=j['frame']-s['startFrame']
        begun=[c for c in s['codeCues'] if local>=c['beginFrame']]
        target=begun[-1]['lines'] if begun else s['initialCodeLines']
        pixels(ROOT/'public'/j['path'],s,local,target)
    qa=ROOT/'build/layout-qa';qa.mkdir(exist_ok=True);chosen=[]
    for s in t['scenes']:
        target=s['startFrame']+s['steps'][-1]
        chosen.append(next(j for j in t['renderJobs'] if j['frame']==target))
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    for begin in range(0,len(chosen),12):
        sheet=Image.new('RGB',(1440,1184),'#111827');draw=ImageDraw.Draw(sheet)
        for i,j in enumerate(chosen[begin:begin+12]):
            x=i%3*480;y=i//3*296
            with Image.open(ROOT/'public'/j['path']) as im:sheet.paste(im.resize((480,270)),(x,y))
            draw.text((x+8,y+272),j['sceneKey'],font=font,fill='white')
        sheet.save(qa/f'pages-{begin//12+1:02}.jpg',quality=92)
    report=dict(allPassed=True,pages=len(t['scenes']),states=len(t['renderJobs']),scope='layout-only synthetic event positions; does not validate audio timing')
    (ROOT/'build/layout-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report),flush=True)
if __name__=='__main__':main()
