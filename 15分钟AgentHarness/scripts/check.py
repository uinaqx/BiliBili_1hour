"""Separate structural, semantic-invariant and actual encoded video checks."""
import argparse,bisect,hashlib,json,math,pathlib,subprocess,wave
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import draw
from timeline import anchor_seconds
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out';FINAL=DEL/'15分钟讲清AgentHarness_底层原理_正常语速版.mp4'
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
    assert len(t['chapters'])==10 and len(t['scenes'])==20 and t['chapters'][0]['startFrame']==0
    assert 780<=t['duration']<=1080 and t['speechTempo']==1.0 and t['automaticTempoAdjustment'] is False
    course=load(ROOT/'public/course.json');draw.init(t)
    speed=load(BUILD/'original-speed-check.json');assert speed['allPassed'] and speed['wholeCourseTempo']==1.0 and speed['automaticTempoAdjustment'] is False
    assert speed['timelineSha256']==digest(ROOT/'public/timeline.json') and speed['courseSha256']==digest(ROOT/'public/course.json')
    visual=load(BUILD/'visual-verification.json');demo=load(BUILD/'demo-verification.json')
    assert visual['allPassed'] and visual['courseSha256']==digest(ROOT/'public/course.json') and visual['drawingSourceSha256']==digest(ROOT/'scripts/draw.py')
    assert demo['allPassed'] and demo['courseSha256']==digest(ROOT/'public/course.json')
    assert demo['demoSourceSha256']==digest(ROOT/'demo/harness.py') and demo['testSourceSha256']==digest(ROOT/'demo/test_harness.py')
    manual=0;motions=0;animated=0;cursor=0;questions=0;units=0;events=0
    for c in t['chapters']:
        assert c['startFrame']==cursor
        for s in c['scenes']:
            assert s['startFrame']==cursor;cursor+=s['durationFrames'];path=ROOT/'public'/s['audio'];meta=load(path.with_suffix('.json'))
            assert digest(path)==s['audioSha256']==meta['sha256'],('Stale audio',s['key'])
            with wave.open(str(path)) as f:
                assert f.getframerate()==24000 and f.getnchannels()==1 and f.getsampwidth()==2
                assert f.getnframes()==meta['samples']<=s['speechFrames']*800
            assert len(s['parts'])==len(s['units'])==len(meta['parts'])
            assert all(p['text']==a['cue'] for p,a in zip(s['parts'],meta['parts']))
            assert s['renderFrames']==sorted(set(s['renderFrames']));ticks=set(s['renderFrames']);events+=len(ticks)
            for u in s['units']:
                units+=1;audio=meta['parts'][u['index']]
                assert u['begin']==s['leadFrames']+math.ceil(audio['onset']*30-1e-6)
                assert draw.state(s,u['begin'])[0]==u['index'];previous=u['begin'];progress=0
                for m,authored in zip(u['motions'],s['parts'][u['index']]['moves']):
                    assert previous<=m['begin']<m['end']<=u['end'],('Motion outside unit',s['key'],u['index'])
                    assert m['anchor']==authored['anchor'] and m['fromProgress']==progress and m['toProgress']==authored['target']
                    expected=max(u['begin'],s['leadFrames']+math.ceil(anchor_seconds(s,u['index'],m['anchor'],meta)*30-1e-6))
                    assert m['begin']==expected,('Motion onset is not actual authored phrase',s['key'],m['anchor'])
                    assert set(range(m['begin'],m['end']+1))<=ticks,('Motion is undersampled',s['key'])
                    assert draw.state(s,m['end'])[0]==u['index'] and abs(draw.state(s,m['end'])[1]-m['toProgress'])<1e-8
                    assert m['method'].startswith('authored-phrase');manual+=1;animated+=m['end']-m['begin'];motions+=1;previous=m['end'];progress=m['toProgress']
                if u['motions']:
                    hold_end=s['units'][u['index']+1]['begin']-1 if u['index']+1<len(s['units']) else s['durationFrames']-1
                    assert draw.state(s,hold_end)[0]==u['index'] and abs(draw.state(s,hold_end)[1]-progress)<1e-8,('State did not persist',s['key'])
            assert len(meta['thinkPauses'])==len(s['thinkIntervals'])
            for pause,interval in zip(meta['thinkPauses'],s['thinkIntervals']):
                questions+=1;assert pause['seconds']==4 and interval['end']-interval['begin']==120
                assert interval['begin']==s['leadFrames']+math.ceil(pause['start']*30)
                assert s['parts'][interval['part']]['think'] and s['parts'][interval['part']]['visual']['question']
                assert all(interval['begin']+n*30 in ticks for n in range(4))
                assert all(draw.state(s,f)[0]==interval['part'] for f in range(interval['begin'],interval['end']))
                assert s['units'][interval['part']+1]['begin']>=interval['end'],'Answer before thought pause ends'
        assert c['durationFrames']==sum(s['durationFrames'] for s in c['scenes'])
    assert cursor==t['totalFrames'] and events==t['renderedFrames'] and questions==10 and units==39 and motions==76
    return dict(chapters=10,pages=20,semanticUnits=units,questions=questions,runtimeTests=demo['tests'],speechTempo=1.0,originalSpeechClipsCompared=speed['speechClipsCompared'],motionIntervals=motions,phraseAnchoredIntervals=manual,continuousMotionSeconds=animated/30,plannedDisplayEvents=events)
def selection(t):
    targets=set();contacts=[]
    for s in t['scenes']:
        local={0,s['durationFrames']-1}
        for u in s['units']:
            local.update([u['begin'],max(0,u['begin']-1)])
            for m in u['motions']:
                local.update([max(0,m['begin']-1),m['begin'],m['end'],min(s['durationFrames']-1,m['end']+15)])
                local.update(m['begin']+round((m['end']-m['begin'])*q) for q in [.25,.5,.75])
            end=s['units'][u['index']+1]['begin']-1 if u['index']+1<len(s['units']) else s['durationFrames']-1
            local.add(end);contacts.append(dict(frame=s['startFrame']+end,key=s['key'],part=u['index']+1))
        for p in s['thinkIntervals']:local.update(p['begin']+n*30 for n in range(4))
        targets.update(s['startFrame']+f for f in local if 0<=f<s['durationFrames'])
    return sorted(targets),contacts
def pixel_check(im,s,local):
    assert im.size==(1920,1080);a=np.asarray(im.convert('RGB')).astype(np.int16);b=np.asarray(draw.render(s,local)).astype(np.int16);maes=[]
    for x,y,xx,yy in [(70,225,1235,915),(1290,235,1855,915)]:
        mae=float(np.mean(abs(a[y:yy,x:xx]-b[y:yy,x:xx])));maes.append(mae);assert mae<4,('Encoded visible state differs',s['key'],local,mae)
    assert np.max(a[980:1060,20:1900])<80,('Unexpected subtitles',s['key'],local)
    return maes
def encoded(t,report):
    meta=json.loads(capture(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(FINAL)]));video=next(s for s in meta['streams'] if s['codec_type']=='video');audio=next(s for s in meta['streams'] if s['codec_type']=='audio')
    assert video['codec_name']=='h264' and video['width']==1920 and video['height']==1080
    assert audio['codec_name']=='aac' and int(audio['sample_rate'])==48000 and not any(s['codec_type']=='subtitle' for s in meta['streams'])
    assert abs(float(meta['format']['duration'])-t['duration'])<.08 and len(meta['chapters'])==10
    for c,m in zip(t['chapters'],meta['chapters']):assert abs(float(m['start_time'])-c['startFrame']/30)<.002 and m['tags']['title']==c['title']
    data=json.loads(capture(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(FINAL)]))['frames'];pts=[float(f['best_effort_timestamp_time']) for f in data];ticks=[round(p*30) for p in pts]
    assert all(abs(p-k/30)<.0001 for p,k in zip(pts,ticks)) and all(a<b for a,b in zip(ticks,ticks[1:]))
    actual=set(ticks);planned={s['startFrame']+f for s in t['scenes'] for f in s['renderFrames']};assert planned<=actual,('Encoded events missing',len(planned-actual),sorted(planned-actual)[:12])
    targets,contacts=selection(t);chosen=sorted({bisect.bisect_right(ticks,f)-1 for f in targets});out=BUILD/'final-frames';out.mkdir(exist_ok=True);filt=BUILD/'qa-filter.txt';filt.write_text("select='"+'+'.join(f'eq(n,{i})' for i in chosen)+"'",encoding='ascii')
    subprocess.run(['ffmpeg','-y','-v','error','-threads','2','-i',str(FINAL),'-filter_script:v',str(filt),'-fps_mode','passthrough','-threads','2',str(out/'sample-%04d.png')],check=True)
    starts=[s['startFrame'] for s in t['scenes']];record=[];files={}
    for ordinal,index in enumerate(chosen,1):
        tick=ticks[index];s=t['scenes'][bisect.bisect_right(starts,tick)-1];local=tick-s['startFrame'];path=out/f'sample-{ordinal:04}.png';files[index]=path
        with Image.open(path) as im:maes=pixel_check(im,s,local)
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
    evidence=[]
    for s in t['scenes']:
        for u in s['units']:
            for m in u['motions']:
                images=[]
                for q in [.25,.5,.75]:
                    tick=s['startFrame']+m['begin']+round((m['end']-m['begin'])*q);i=bisect.bisect_right(ticks,tick)-1
                    with Image.open(files[i]) as im:images.append(np.asarray(im.crop((70,225,1235,915))).astype(np.int16))
                diffs=[float(np.mean(abs(x-y))) for x,y in zip(images,images[1:])];assert min(diffs)>.003,('Encoded animation is static',s['key'],u['index'],m['anchor'],diffs)
                evidence.append(dict(key=s['key'],part=u['index'],anchor=m['anchor'],changes=diffs))
    write(BUILD/'encoded-motion-checks.json',dict(allPassed=True,examples=evidence))
    subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(FINAL),'-fps_mode','passthrough','-f','null','-'],check=True)
    report.update(videoSha256=digest(FINAL),videoBytes=FINAL.stat().st_size,encodedDisplayEvents=len(ticks),plannedEventsPresent=len(planned),encodedFramesCompared=len(record),motionIntervalsCheckedInVideo=len(evidence),maxDiagramMAE=max(r['diagramMAE'] for r in record),maxNotesMAE=max(r['notesMAE'] for r in record),videoCodec='h264',audioCodec='aac',size=[1920,1080],chaptersEmbedded=10,fullDecodePassed=True)
    write(BUILD/'encoded-frame-checks.json',dict(samples=record))
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--final',action='store_true');a=parser.parse_args();t=load(ROOT/'public/timeline.json');report=structure(t)
    report.update(allPassed=True,duration=t['duration'],timelineSha256=digest(ROOT/'public/timeline.json'),courseSha256=digest(ROOT/'public/course.json'),drawingSourceSha256=digest(ROOT/'scripts/draw.py'),topologySourceSha256=digest(ROOT/'content/visuals.py'),scope='all final PCM files, phrase onset mapping, 76 continuous intervals and persistent holds; final mode additionally checks sampled encoded pixels, all motion intervals and full A/V decode; does not claim manual listening to every minute')
    if a.final:encoded(t,report)
    write(BUILD/('final-validation.json' if a.final else 'preflight-validation.json'),report);print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
