"""Check actual rendered/encoded states against the authored targets, not only JSON."""
import argparse,bisect,hashlib,json,pathlib,subprocess,sys,wave
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def expected(s,local):
    meta=load(ROOT/'public'/s['audio'].replace('.wav','.json'));parts=[p for p in meta['parts'] if p['lines'] and local>=s['leadFrames']+__import__('math').ceil(p['onset']*30-1e-6)]
    return (s['parts'][parts[-1]['index']]['lines'] if parts else s['parts'][0]['lines']) if s['code'] else []
def pixels(path,s,local,lines=None):
    with Image.open(path) as im:
        assert im.size==(1920,1080),(path.name,im.size)
        if s['code']:
            actual=[]
            for line in range(1,len(s['code'].splitlines())+1):
                y=264+(line-1)*36+18
                found=any((lambda c:c[0]>200 and 125<c[1]<220 and 55<c[2]<170)(im.getpixel((x,y))[:3]) for x in range(72,77))
                if found:actual.append(line)
            target=expected(s,local) if lines is None else lines
            assert actual==target,('Actual highlight differs',path.name,s['key'],local,actual,target)
        band=im.crop((20,960,1900,1060)).convert('RGB')
        assert max(band.getextrema()[i][1] for i in range(3))<80,('Unexpected bottom text',path.name)
def main():
    p=argparse.ArgumentParser();p.add_argument('--final',action='store_true');p.add_argument('--partial',action='store_true');a=p.parse_args()
    t=load(ROOT/'public/timeline.json');by={s['key']:s for s in t['scenes']};frames=[]
    assert load(ROOT/'build/example-verification.json')['allPassed']
    for s in t['scenes']:
        path=ROOT/'public'/s['audio'];assert digest(path)==s['audioSha256']
        with wave.open(str(path)) as f:assert f.getnframes()<=s['speechFrames']*800 and f.getframerate()==24000
        assert s['kind']!='question' or (s['hold']==4 and s['output'] is None)
    for j in t['renderJobs']:
        path=ROOT/'public'/j['path']
        if a.partial and not path.exists():continue
        s=by[j['sceneKey']];local=j['frame']-s['startFrame'];pixels(path,s,local);frames.append(dict(frame=j['frame'],scene=s['key'],path=str(path)))
    final=DEL/'一小时学习Go_零基础.mp4';encoded=[]
    if a.final:
        meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(final)],text=True,encoding='utf8'))
        video=next(s for s in meta['streams'] if s['codec_type']=='video');audio=next(s for s in meta['streams'] if s['codec_type']=='audio')
        assert video['codec_name']=='h264' and video['width']==1920 and video['height']==1080 and audio['codec_name']=='aac'
        assert len(meta['chapters'])==10 and abs(float(meta['format']['duration'])-t['duration'])<.08
        for c,d in zip(t['chapters'],meta['chapters']):assert abs(float(d['start_time'])-c['startFrame']/30)<.002 and d['tags']['title']==c['title']
        out=ROOT/'build/final-frames';out.mkdir(parents=True,exist_ok=True)
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(final),'-map','0:v:0','-fps_mode','passthrough',str(out/'frame-%05d.png')],check=True)
        data=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(final)],text=True))['frames']
        starts=[s['startFrame'] for s in t['scenes']];pts=[float(f['best_effort_timestamp_time']) for f in data]
        for i,seconds in enumerate(pts,1):
            frame=round(seconds*30);s=t['scenes'][bisect.bisect_right(starts,frame)-1];path=out/f'frame-{i:05}.png'
            pixels(path,s,frame-s['startFrame']);encoded.append(dict(frame=frame,scene=s['key'],path=str(path)))
        actual={round(x*30) for x in pts}
        assert all(j['frame'] in actual for j in t['renderJobs']), 'Missing encoded display events'
        subprocess.run(['ffmpeg','-v','error','-i',str(final),'-f','null','-'],check=True)
        # One actual frame per page, plus each quiz countdown, for visual review.
        chosen=[]
        for s in t['scenes']:
            target=s['startFrame']+(s['resultFrame']+1 if s['resultFrame']<s['durationFrames'] else s['steps'][-1]+1)
            chosen.append(encoded[bisect.bisect_right([r['frame'] for r in encoded],target)-1])
            if s['kind']=='question':
                target=s['startFrame']+s['leadFrames']+s['speechFrames']+s['sentenceTailFrames']+30
                chosen.append(encoded[bisect.bisect_right([r['frame'] for r in encoded],target)-1])
        font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18);qa=ROOT/'build/qa';qa.mkdir(exist_ok=True)
        for begin in range(0,len(chosen),12):
            sheet=Image.new('RGB',(1440,1184),'#111827');draw=ImageDraw.Draw(sheet)
            for k,r in enumerate(chosen[begin:begin+12]):
                x=k%3*480;y=k//3*296
                with Image.open(r['path']) as im:sheet.paste(im.resize((480,270)),(x,y))
                draw.text((x+8,y+272),r['scene']+' '+str(round(r['frame']/30,2))+'s',font=font,fill='white')
            sheet.save(qa/f'pages-{begin//12+1:02}.jpg',quality=92)
    report=dict(allPassed=True,scope='encoded display states plus structural integrity; does not claim manual listening to every minute',timelineSha256=digest(ROOT/'public/timeline.json'),courseSha256=digest(ROOT/'public/course.json'),scenes=len(t['scenes']),renderedStatesChecked=len(frames),encodedStatesChecked=len(encoded),duration=t['duration'],videoSha256=digest(final) if a.final else None)
    (ROOT/'build'/('final-validation.json' if a.final else 'visual-validation.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
