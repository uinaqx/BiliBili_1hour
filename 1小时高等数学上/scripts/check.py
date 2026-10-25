"""Check authored formula states, measured audio and every encoded display event."""
import argparse,bisect,hashlib,json,math,pathlib,subprocess,wave
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out';FINAL=DEL/'一小时学完高等数学上_期末基础题型.mp4'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
    return h.hexdigest()
def write(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
def capture(args):return subprocess.check_output(args,text=True,encoding='utf8')
def expected(s,frame):
    m=load(ROOT/'public/audio'/(s['key']+'.json'));index=0
    for i,p in enumerate(m['parts']):
        if frame>=s['leadFrames']+math.ceil(p['onset']*30-1e-6):index=i
    return index
def pixel_check(im,s,frame):
    a=np.asarray(im.convert('RGB'));assert im.size==(1920,1080)
    if s['kind']=='overview':return
    p=s['parts'][expected(s,frame)]
    for i,r in enumerate(s['rows'],1):
        y=230+(i-1)*133;rgb=a[y+60,81].astype(int);orange=rgb[0]>200 and 125<rgb[1]<220 and 55<rgb[2]<170
        assert orange==(i in p['focus']),('Wrong encoded highlight',s['key'],frame,i,rgb.tolist())
        if i>p['show']:
            # Undisclosed answer steps must remain blank, not merely dimmed.
            crop=a[y+2:y+125,90:1238].astype(np.int16);bg=np.array([16,36,58]);assert np.max(abs(crop-bg))<18,('Future step leaked',s['key'],frame,i)
    assert np.max(a[980:1060,20:1900])<80,('Unexpected subtitles',s['key'],frame)
def structure(t):
    assert t['scope']=='complete-course' and not t['subtitles'] and 3480<=t['duration']<=3780 and len(t['chapters'])==10
    course=load(ROOT/'public/course.json');manual={s['key']:s for c in course['chapters'] for s in c['scenes']};draw.prepare_formulas(course);draw.init(t)
    verified=load(BUILD/'math-verification.json');assert verified['allPassed'] and verified['courseSha256']==digest(ROOT/'public/course.json')
    assert load(BUILD/'formula-review.json')['allPassed'];coverage=load(ROOT/'docs/考点覆盖.json');assert len(coverage)==39 and all(coverage.values())
    cursor=0;count=0;questions=0;boundary=0
    for c in t['chapters']:
        assert c['startFrame']==cursor and sum(s['kind']=='question' for s in c['scenes'])==1
        for i,s in enumerate(c['scenes']):
            assert s['startFrame']==cursor and s['parts']==manual[s['key']]['parts'] and s['rows']==manual[s['key']]['rows'];path=ROOT/'public'/s['audio'];m=load(path.with_suffix('.json'))
            assert digest(path)==m['sha256']==s['audioSha256'] and m['timeBase']=='final-audio'
            with wave.open(str(path)) as f:assert f.getframerate()==24000 and f.getsampwidth()==2 and f.getnchannels()==1 and f.getnframes()==m['samples']
            assert len(s['parts'])==len(m['parts'])==len(s['units'])
            for u,p,audio in zip(s['units'],s['parts'],m['parts']):
                count+=1;assert audio['cue']==p['text'];assert u['begin']==s['leadFrames']+math.ceil(audio['onset']*30-1e-6)
                assert draw.state(s,u['begin'])[0]==u['index'] and p['focus'] and max(p['focus'])<=p['show']<=len(s['rows'])
                next_start=s['units'][u['index']+1]['begin'] if u['index']+1<len(s['units']) else s['durationFrames']
                for f in [u['begin'],next_start-1,min(next_start-1,u['end']+1)]:assert draw.state(s,f)[0]==u['index'];boundary+=1
            assert s['parts'][-1]['show']==len(s['rows']),('Last step omitted',s['key'])
            if s['kind']=='question':
                questions+=1;assert s['hold']==4 and c['scenes'][i+1]['kind']=='answer'
                begin=s['leadFrames']+s['speechFrames']+s['sentenceTailFrames'];assert all(begin+j*30 in s['renderFrames'] for j in range(4))
            cursor+=s['durationFrames']
    assert cursor==t['totalFrames'] and count==136 and questions==10
    # Exercise the actual renderer state implementation with silent gaps and a fresh page.
    sample=dict(units=[dict(index=0,begin=12,end=20),dict(index=1,begin=60,end=70)])
    for f,index in [(0,0),(12,0),(20,0),(59,0),(60,1),(100,1)]:assert draw.state(sample,f)[0]==index
    assert draw.state(dict(units=[dict(index=0,begin=12,end=20)]),100)[0]==0
    return dict(chapters=10,topics=39,pages=len(t['scenes']),semanticParts=count,questions=questions,mathChecks=verified['checks'],formulaExpressions=load(BUILD/'formula-review.json')['formulas'],persistentBoundaryChecks=boundary,plannedStates=t['renderedFrames'])
def encoded(t,r):
    meta=json.loads(capture(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(FINAL)]));v=next(s for s in meta['streams'] if s['codec_type']=='video');a=next(s for s in meta['streams'] if s['codec_type']=='audio')
    assert v['codec_name']=='h264' and (v['width'],v['height'])==(1920,1080) and a['codec_name']=='aac' and int(a['sample_rate'])==48000
    assert abs(float(meta['format']['duration'])-t['duration'])<.08 and len(meta['chapters'])==10 and not any(s['codec_type']=='subtitle' for s in meta['streams'])
    for c,mc in zip(t['chapters'],meta['chapters']):assert abs(float(mc['start_time'])-c['startFrame']/30)<.002 and mc['tags']['title']==c['title']
    fs=json.loads(capture(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(FINAL)]))['frames'];pts=[float(f['best_effort_timestamp_time']) for f in fs];ticks=[round(x*30) for x in pts]
    assert all(abs(p-f/30)<.0001 for p,f in zip(pts,ticks)) and all(x<y for x,y in zip(ticks,ticks[1:]))
    jobs={s['startFrame']+f:(s,f) for s in t['scenes'] for f in s['renderFrames']};assert set(jobs)<=set(ticks)
    chosen=[i for i,f in enumerate(ticks) if f in jobs];out=BUILD/'final-frames';out.mkdir(exist_ok=True);filt=BUILD/'qa-filter.txt';filt.write_text("select='"+'+'.join(f'eq(n,{i})' for i in chosen)+"'",encoding='ascii')
    subprocess.run(['ffmpeg','-y','-v','error','-threads','2','-i',str(FINAL),'-filter_script:v',str(filt),'-fps_mode','passthrough',str(out/'sample-%04d.png')],check=True)
    records=[];files={}
    for ordinal,index in enumerate(chosen,1):
        tick=ticks[index];s,frame=jobs[tick];path=out/f'sample-{ordinal:04}.png';files[index]=path
        with Image.open(path) as im:
            assert draw.state(s,frame)[0]==expected(s,frame);pixel_check(im,s,frame);a=np.asarray(im.convert('RGB')).astype(np.int16);b=np.asarray(draw.render(s,frame)).astype(np.int16);errors=[]
            for x,y,xx,yy in [(70,225,1250,915),(1290,235,1855,915)]:
                error=float(np.mean(abs(a[y:yy,x:xx]-b[y:yy,x:xx])));assert error<4,(s['key'],frame,error);errors.append(error)
        records.append(dict(key=s['key'],frame=tick,seconds=tick/30,part=expected(s,frame),focus=s['parts'][expected(s,frame)]['focus'],formulaMAE=errors[0],notesMAE=errors[1]))
    contacts=[];held=0
    for s in t['scenes']:
        targets={0,s['durationFrames']-1}
        for u in s['units']:
            targets.update([max(0,u['begin']-1),u['begin'],min(s['durationFrames']-1,u['begin']+1),min(s['durationFrames']-1,u['end']+1)])
            contacts.append((s,s['units'][u['index']+1]['begin']-1 if u['index']+1<len(s['units']) else s['durationFrames']-1))
        for frame in targets:
            index=bisect.bisect_right(ticks,s['startFrame']+frame)-1;ss,f=jobs[ticks[index]];assert ss['key']==s['key'] and expected(s,frame)==expected(s,f),('Wrong held state',s['key'],frame);held+=1
    qa=BUILD/'qa';qa.mkdir(exist_ok=True);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    for first in range(0,len(contacts),12):
        sheet=Image.new('RGB',(1440,1184),draw.BG);d=ImageDraw.Draw(sheet)
        for i,(s,f) in enumerate(contacts[first:first+12]):
            x=i%3*480;y=i//3*296;index=bisect.bisect_right(ticks,s['startFrame']+f)-1
            with Image.open(files[index]) as im:sheet.paste(im.resize((480,270)),(x,y))
            d.text((x+8,y+272),f"{s['key']} · {expected(s,f)+1} · {(s['startFrame']+f)/30:.1f}s",font=font,fill='white')
        sheet.save(qa/f'contact-{first//12+1:02}.jpg',quality=93)
    subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(FINAL),'-fps_mode','passthrough','-f','null','-'],check=True)
    write(BUILD/'encoded-frame-checks.json',dict(allPassed=True,records=records));r.update(videoSha256=digest(FINAL),videoBytes=FINAL.stat().st_size,encodedStatesChecked=len(records),heldStateSamples=held,maxFormulaMAE=max(x['formulaMAE'] for x in records),maxNotesMAE=max(x['notesMAE'] for x in records),fullDecodePassed=True,chaptersEmbedded=10)
def main():
    p=argparse.ArgumentParser();p.add_argument('--final',action='store_true');a=p.parse_args();t=load(ROOT/'public/timeline.json');r=structure(t)
    if a.final:encoded(t,r)
    r.update(allPassed=True,duration=t['duration'],courseSha256=digest(ROOT/'public/course.json'),timelineSha256=digest(ROOT/'public/timeline.json'),drawingSourceSha256=digest(ROOT/'scripts/draw.py'),scope='authored targets, all mathematical examples, final audio files and persistent steps; final mode checks every planned encoded display state and full A/V decoding; no claim of minute-by-minute manual listening')
    write(BUILD/('final-validation.json' if a.final else 'preflight-validation.json'),r);print(json.dumps(r,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
