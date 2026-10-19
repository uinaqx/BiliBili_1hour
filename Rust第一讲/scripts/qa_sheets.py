import json, pathlib
from PIL import Image, ImageDraw, ImageFont
ROOT=pathlib.Path(__file__).resolve().parents[1]
timeline=json.loads((ROOT/'public'/'timeline.json').read_text(encoding='utf-8'))
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
scenes=timeline['scenes']
for offset in range(0,len(scenes),12):
    sheet=Image.new('RGB',(1920,930),(8,16,28)); draw=ImageDraw.Draw(sheet)
    for i,s in enumerate(scenes[offset:offset+12]):
        p=ROOT/'public'/'stills'/f"{s['key']}-{s['steps'][3]+12:05}.png"
        img=Image.open(p).convert('RGB').resize((480,270))
        x=(i%4)*480;y=(i//4)*310
        sheet.paste(img,(x,y));draw.text((x+8,y+274),s['key']+' · '+s['title'],font=font,fill=(220,230,244))
    path=ROOT/'build'/f'qa-sheet-{offset//12:02}.jpg';sheet.save(path,quality=92)
    print(path.name)
