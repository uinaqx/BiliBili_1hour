"""Sample actual encoded chapter starts/middles/ends, answers and joins for visual QA."""
import bisect,concurrent.futures,json,pathlib,subprocess
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out';FINAL=DEL/'一小时学习Java_零基础.mp4'
T=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf-8'));out=ROOT/'build/final-qa';out.mkdir(exist_ok=True)
packets=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts_time','-of','json',str(FINAL)]))['packets'];pts=[float(p['pts_time']) for p in packets]
samples=[]
for c in T['chapters']:
    start=c['startFrame']/30;duration=c['durationFrames']/30
    for label,seconds in [('start',start+2),('middle',start+duration/2),('end',start+duration-2)]:samples.append((c['key']+'-'+label,seconds))
    if start: samples.extend([(c['key']+'-join-before',start-.05),(c['key']+'-join-after',start+.05)])
for s in T['scenes']:
    if s['kind']=='answer':samples.append((s['key'],(s['startFrame']+s['steps'][3]+12)/30))
def one(x):
    label,seconds=x;p=out/(label+'.png');held=pts[max(0,bisect.bisect_right(pts,seconds)-1)]
    # A VFR held frame may begin several seconds before the requested point.
    subprocess.run(['ffmpeg','-y','-v','error','-ss',str(max(0,held-.00001)),'-i',str(FINAL),'-frames:v','1',str(p)],check=True)
    return p
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(one,samples))
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',19)
for first in range(0,len(samples),12):
    sheet=Image.new('RGB',(1440,1176),'#111827');d=ImageDraw.Draw(sheet)
    for k,(label,seconds) in enumerate(samples[first:first+12]):
        x=(k%3)*480;y=(k//3)*294
        with Image.open(out/(label+'.png')) as im:sheet.paste(im.resize((480,270)),(x,y))
        d.text((x+8,y+271),f'{label} · {seconds:.2f}s',font=font,fill='white')
    sheet.save(out/f'contact-{first//12+1:02}.jpg',quality=93)
print('FINAL_QA_FRAMES',len(samples),flush=True)
