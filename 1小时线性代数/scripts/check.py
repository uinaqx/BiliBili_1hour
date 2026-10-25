"""Validate the mathematical course, then independently inspect encoded video frames."""
import argparse,bisect,hashlib,json,math,pathlib,subprocess,wave
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out'
FINAL=DEL/'一小时学习线性代数_动态可视化.mp4'

def load(p):return json.loads(p.read_text(encoding='utf8'))
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def capture(args):return subprocess.check_output(args,text=True,encoding='utf8')
def write(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')

def structure(t):
    assert t['scope']=='complete-course' and t['subtitles'] is False
    assert len(t['chapters'])==10 and t['chapters'][0]['startFrame']==0
    assert 3480<=t['duration']<=3900
    course=load(ROOT/'public/course.json');draw.prepare_formulas(course);draw.init(t)
    assert load(BUILD/'math-verification.json')['allPassed']
    covered={tag.split('-')[0] for s in t['scenes'] for tag in s['tags']}
    expected={f'{c}.{s}' for c,n in [(1,5),(2,5),(3,3),(4,3),(5,4),(6,3)] for s in range(1,n+1)}
    assert expected<=covered,('Missing PDF subsections',expected-covered)
    manual=0;motions=0;animated=0;cursor=0;questions=0;units=0
    for ci,c in enumerate(t['chapters']):
        assert c['startFrame']==cursor
        assert sum(s['kind']=='question' for s in c['scenes'])==1
        for si,s in enumerate(c['scenes']):
            assert s['startFrame']==cursor
            cursor+=s['durationFrames'];path=ROOT/'public'/s['audio'];meta=load(path.with_suffix('.json'))
            assert digest(path)==s['audioSha256']==meta['sha256'],('Stale audio',s['key'])
            with wave.open(str(path)) as f:
                assert f.getframerate()==24000 and f.getnchannels()==1 and f.getsampwidth()==2
                assert f.getnframes()==meta['samples']<=s['speechFrames']*800
            assert len(s['parts'])==len(s['units'])==len(meta['parts'])
            assert all(p['text']==a['cue'] for p,a in zip(s['parts'],meta['parts']))
            assert s['renderFrames']==sorted(set(s['renderFrames']))
            ticks=set(s['renderFrames'])
            for u in s['units']:
                units+=1;audio=meta['parts'][u['index']]
                assert u['begin']==s['leadFrames']+math.ceil(audio['onset']*30-1e-6)
                assert draw.state(s,u['begin'])[0]==u['index']
                previous=u['begin']
                for m in u['motions']:
                    assert previous<=m['begin']<m['end']<=u['end'],('Motion outside spoken unit',s['key'],u['index'],previous,m,u['end'])
                    assert set(range(m['begin'],m['end']+1))<=ticks,('Motion sampled instead of animated',s['key'])
                    assert draw.state(s,m['end'])[0]==u['index']
                    assert abs(draw.state(s,m['end'])[1]-m['toProgress'])<1e-8
                    if m['method'].startswith('authored-phrase'):manual+=1
                    animated+=m['end']-m['begin'];motions+=1;previous=m['end']
                if u['motions']:
                    hold_end=s['units'][u['index']+1]['begin']-1 if u['index']+1<len(s['units']) else s['durationFrames']-1
                    assert abs(draw.state(s,hold_end)[1]-u['motions'][-1]['toProgress'])<1e-8,('State did not persist',s['key'])
            if s['kind']=='question':
                questions+=1
                assert s['hold']==4 and s['answer']
                assert c['scenes'][si+1]['title'].startswith('答案')
                pause=s['leadFrames']+s['speechFrames']+s['sentenceTailFrames']
                assert all(pause+n*30 in ticks for n in range(4))
    assert cursor==t['totalFrames']
    return dict(pdfSubsections=len(expected),chapters=10,pages=len(t['scenes']),semanticUnits=units,questions=questions,mathematicalChecks=49,motionIntervals=motions,phraseAnchoredIntervals=manual,continuousMotionSeconds=animated/30,plannedDisplayEvents=t['renderedFrames'])

def selection(t):
    # Every unit: before/on/after motion, held state, and exact page boundaries.
    # Also check all four countdown values and first frame of each answer page.
    targets=set();contacts=[]
    for s in t['scenes']:
        local={0,s['durationFrames']-1}
        for u in s['units']:
            local.update([u['begin'],max(0,u['begin']-1)])
            for m in u['motions']:
                local.update([max(0,m['begin']-1),m['begin'],(m['begin']+m['end'])//2,m['end'],min(s['durationFrames']-1,m['end']+15)])
                local.update(m['begin']+round((m['end']-m['begin'])*f) for f in [.25,.5,.75])
            end=s['units'][u['index']+1]['begin']-1 if u['index']+1<len(s['units']) else s['durationFrames']-1
            local.add(end);contacts.append(dict(frame=s['startFrame']+end,key=s['key'],part=u['index']+1))
        if s['kind']=='question':
            pause=s['leadFrames']+s['speechFrames']+s['sentenceTailFrames']
            local.update(pause+n*30 for n in range(4))
        targets.update(s['startFrame']+x for x in local if 0<=x<s['durationFrames'])
    return sorted(targets),contacts

def encoded(t,report):
    meta=json.loads(capture(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(FINAL)]))
    video=next(s for s in meta['streams'] if s['codec_type']=='video');audio=next(s for s in meta['streams'] if s['codec_type']=='audio')
    assert video['codec_name']=='h264' and video['width']==1920 and video['height']==1080
    assert audio['codec_name']=='aac' and int(audio['sample_rate'])==48000
    assert not any(s['codec_type']=='subtitle' for s in meta['streams'])
    assert abs(float(meta['format']['duration'])-t['duration'])<.08
    assert len(meta['chapters'])==10
    for c,m in zip(t['chapters'],meta['chapters']):
        assert abs(float(m['start_time'])-c['startFrame']/30)<.002 and m['tags']['title']==c['title']
    data=json.loads(capture(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(FINAL)]))['frames']
    pts=[float(f['best_effort_timestamp_time']) for f in data];ticks=[round(p*30) for p in pts]
    assert all(abs(p-k/30)<.0001 for p,k in zip(pts,ticks))
    assert all(a<b for a,b in zip(ticks,ticks[1:]))
    actual=set(ticks);planned={s['startFrame']+f for s in t['scenes'] for f in s['renderFrames']}
    assert planned<=actual,('Encoded motion/display events are missing',len(planned-actual),sorted(planned-actual)[:12])
    targets,contacts=selection(t)
    chosen=sorted({bisect.bisect_right(ticks,f)-1 for f in targets})
    out=BUILD/'final-frames';out.mkdir(exist_ok=True)
    # Filter graph is a file so it also works below the Windows command limit.
    filt=BUILD/'qa-filter.txt';filt.write_text("select='"+'+'.join(f'eq(n,{i})' for i in chosen)+"'",encoding='ascii')
    subprocess.run(['ffmpeg','-y','-v','error','-threads','2','-i',str(FINAL),'-filter_script:v',str(filt),'-fps_mode','passthrough','-threads','2',str(out/'sample-%04d.png')],check=True)
    starts=[s['startFrame'] for s in t['scenes']];record=[];files={}
    for ordinal,index in enumerate(chosen,1):
        tick=ticks[index];s=t['scenes'][bisect.bisect_right(starts,tick)-1];local=tick-s['startFrame'];path=out/f'sample-{ordinal:04}.png';files[index]=path
        with Image.open(path) as im:
            assert im.size==(1920,1080)
            a=np.asarray(im.convert('RGB')).astype(np.int16);b=np.asarray(draw.render(s,local)).astype(np.int16)
            maes=[]
            for box in [(70,225,1235,915),(1290,235,1855,915)]:
                x,y,xx,yy=box;mae=float(np.mean(abs(a[y:yy,x:xx]-b[y:yy,x:xx])));maes.append(mae)
                assert mae<4.0,('Encoded frame differs from the planned visible state',s['key'],tick,mae)
            assert np.max(a[980:1060,20:1900])<80,('Unexpected bottom subtitles',s['key'],tick)
        record.append(dict(key=s['key'],frame=tick,videoSeconds=tick/30,diagramMAE=maes[0],notesMAE=maes[1]))
        if ordinal%150==0:print('ENCODED_SAMPLES_CHECKED',ordinal,len(chosen),flush=True)
    qa=BUILD/'qa';qa.mkdir(exist_ok=True);font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    for first in range(0,len(contacts),12):
        sheet=Image.new('RGB',(1440,1184),draw.BG);d=ImageDraw.Draw(sheet)
        for n,c in enumerate(contacts[first:first+12]):
            i=bisect.bisect_right(ticks,c['frame'])-1;x=n%3*480;y=n//3*296
            with Image.open(files[i]) as im:sheet.paste(im.resize((480,270)),(x,y))
            d.text((x+8,y+272),f"{c['key']} · {c['part']} · {c['frame']/30:.2f}s",font=font,fill='white')
        sheet.save(qa/f'encoded-{first//12+1:02}.jpg',quality=92)
    # These examples require true geometric change, rather than a sequence of
    # repeated stills. Compare actual encoded quarter/half/three-quarter states.
    moving=[('la-01-03',0),('la-01-03',1),('la-02-02',0),('la-02-05',0),('la-03-01',0),('la-04-01',0),('la-04-03',0),('la-06-04',0),('la-07-01',0),('la-08-02',0),('la-09-02',0),('la-09-03',0),('la-10-01',0)]
    by={s['key']:s for s in t['scenes']};motion_evidence=[]
    for key,part in moving:
        s=by[key];m=s['units'][part]['motions'][0];images=[]
        for f in [.25,.5,.75]:
            tick=s['startFrame']+m['begin']+round((m['end']-m['begin'])*f);i=bisect.bisect_right(ticks,tick)-1
            with Image.open(files[i]) as im:images.append(np.asarray(im.crop((70,225,1235,915))).astype(np.int16))
        differences=[float(np.mean(abs(x-y))) for x,y in zip(images,images[1:])]
        assert min(differences)>.02,('Expected geometric motion is static in actual video',key,part,differences)
        motion_evidence.append(dict(key=key,part=part,successiveDiagramDifferences=differences))
    write(BUILD/'encoded-motion-checks.json',dict(allPassed=True,examples=motion_evidence))
    subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(FINAL),'-fps_mode','passthrough','-f','null','-'],check=True)
    report.update(videoSha256=digest(FINAL),videoBytes=FINAL.stat().st_size,encodedDisplayEvents=len(ticks),plannedEventsPresent=len(planned),encodedFramesCompared=len(record),geometricMotionExamplesChecked=len(moving),maxDiagramMAE=max(r['diagramMAE'] for r in record),maxNotesMAE=max(r['notesMAE'] for r in record),videoCodec='h264',audioCodec='aac',size=[1920,1080],chaptersEmbedded=10,fullDecodePassed=True)
    write(BUILD/'encoded-frame-checks.json',dict(samples=record))

def main():
    p=argparse.ArgumentParser();p.add_argument('--final',action='store_true');a=p.parse_args()
    t=load(ROOT/'public/timeline.json');report=structure(t)
    report.update(allPassed=True,duration=t['duration'],timelineSha256=digest(ROOT/'public/timeline.json'),courseSha256=digest(ROOT/'public/course.json'),drawingSourceSha256=digest(ROOT/'scripts/draw.py'),scope='math examples, all audio files, all planned motion ticks and persistent states; final mode additionally compares sampled actual encoded pixels and full-decodes A/V; no claim of manual listening to every minute')
    if a.final:encoded(t,report)
    write(BUILD/('final-validation.json' if a.final else 'preflight-validation.json'),report)
    print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
