"""Verify authored exercises, measured speech timing, rendered DOM and encoded pixels."""
import argparse,bisect,hashlib,json,math,pathlib,subprocess,wave
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out';FINAL=DEL/'Rust基础58题_习题跟练.mp4'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def capture(a):return subprocess.check_output(a,text=True,encoding='utf8')
def expected(s,local,measured=True):
    if s['kind']=='overview':return []
    # Start from the content author's targets and final PCM metadata, independently
    # of the renderer's codeCues; do not invent semantic expectations by keyword.
    rows=s['parts'][0]['lines'];meta=load(ROOT/'public/audio'/(s['key']+'.json')) if measured else None
    for i,p in enumerate(s['parts']):
        onset=s['leadFrames']+math.ceil(meta['parts'][i]['onset']*30-1e-6) if measured else s['leadFrames']+i*30
        if local>=onset:rows=p['lines']
    return rows
def pixels(path,s,local,target):
    with Image.open(path) as im:
        assert im.size==(1920,1080)
        a=np.asarray(im.convert('RGB'))
    if s['kind']=='overview':return
    evidence=load((ROOT/'public/stills'/f"{s['key']}-{local:05}.json"))['dom']
    assert evidence['key']==s['key'] and evidence['local']==local and evidence['frame']==s['startFrame']+local
    assert sorted(evidence['activeLines'])==sorted(target),('Actual DOM targets differ',s['key'],local,evidence['activeLines'],target)
    assert len(evidence['rows'])==len(s['code'].splitlines())
    for r in evidence['rows']:
        selected=r['line'] in target
        assert r['selected']==selected and r['bottom']<=760
        x=round(r['left'])+1;y=round((r['top']+r['bottom'])/2)
        rgb=a[y,x].astype(int);orange=rgb[0]>200 and 125<rgb[1]<220 and 55<rgb[2]<170
        assert orange==selected,('Actual highlight border differs',path.name,r['line'],rgb.tolist(),target)
    visible=s['kind']!='question' and s['output'] is not None and local>=s['resultFrame']
    assert evidence['resultVisible']==visible
    result='暂停视频先完成，再继续核对答案。' if s['kind']=='question' else s['output'] if visible else '跟随当前步骤，随后核对实际结果。'
    assert evidence['resultText']==result,('Wrong or premature result',s['key'],local)
    assert int(np.max(a[995:1070,20:1900]))<80,('Unexpected bottom subtitles',s['key'])
def contacts(t,folder,files=None,ticks=None):
    folder.mkdir(exist_ok=True);chosen=[]
    for s in t['scenes']:
        for i,p in enumerate(s['parts']):
            f=(s['steps'][i+1]-1) if i+1<len(s['steps']) else s['durationFrames']-1
            if files is None:
                jobs=[j for j in t['renderJobs'] if j['sceneKey']==s['key'] and j['frame']<=s['startFrame']+f]
                path=ROOT/'public'/jobs[-1]['path']
            else:path=files[bisect.bisect_right(ticks,s['startFrame']+f)-1]
            chosen.append((s['key'],i+1,path,(s['startFrame']+f)/30))
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    for start in range(0,len(chosen),12):
        sheet=Image.new('RGB',(1440,1184),'#111827');d=ImageDraw.Draw(sheet)
        for i,(key,part,path,seconds) in enumerate(chosen[start:start+12]):
            x=i%3*480;y=i//3*296
            with Image.open(path) as im:sheet.paste(im.resize((480,270)),(x,y))
            d.text((x+8,y+272),f'{key} · {part} · {seconds:.2f}s',font=font,fill='white')
        sheet.save(folder/f'pages-{start//12+1:02}.jpg',quality=92)
    return len(chosen)
def structure(t):
    assert t['scope']=='complete-course' and not t['subtitles'] and not t['captions']
    assert len(t['chapters'])==10 and 5400<=t['duration']<=7200
    course=load(ROOT/'public/course.json');source={s['key']:s for c in course['chapters'] for s in c['scenes']}
    assert len(source)==len(t['scenes'])==183
    checked=load(BUILD/'exercise-verification.json');assert checked['allPassed'] and checked['exercises']==58 and checked['testsPassed']==56
    inventory=load(ROOT/'references/inventory.json')
    for r,record in zip(inventory,checked['records']):
        assert r['number']==record['number'] and record['variants']['solutions']['outcome']=='passed'
        for variant,field in [('original','originalSha256'),('solutions','sha256')]:
            assert digest(ROOT/'exercises'/variant/r['file'])==r[field]==record['variants'][variant]['sha256']
    assert [s['number'] for s in t['scenes'] if s['kind']=='question']==list(range(1,59))
    cursor=0;units=0;switches=0;silences=0
    for c in t['chapters']:
        assert c['startFrame']==cursor and c['scenes'][0]['startFrame']==cursor
        for si,s in enumerate(c['scenes']):
            assert s['startFrame']==cursor and s['parts']==source[s['key']]['parts']
            assert not s['captions'] and not s['cueFocus'] and s['initialCodeLines']==s['parts'][0]['lines']
            if s['number']:assert s['sourceFile']==f"exercises/{'original' if s['kind']=='question' else 'solutions'}/{s['filename']}"
            meta=load(ROOT/'public/audio'/(s['key']+'.json'));path=ROOT/'public'/s['audio']
            assert meta['timeBase']=='final-audio' and digest(path)==meta['sha256']==s['audioSha256']
            with wave.open(str(path)) as f:
                assert f.getframerate()==24000 and f.getnchannels()==1 and f.getsampwidth()==2 and f.getnframes()==meta['samples']
                assert math.ceil(f.getnframes()/800)==s['speechFrames']
            assert len(meta['parts'])==len(s['parts'])
            assert len(s['code'].splitlines())<=13
            for i,(p,m) in enumerate(zip(s['parts'],meta['parts'])):
                units+=1;assert p['text']==m['cue'] and p['lines']==m['lines']
                assert 0<=m['start']<=m['onset']<m['end']<=meta['duration']+.001
                assert s['kind']=='overview' or p['lines']
                assert all(1<=x<=len(s['code'].splitlines()) and s['code'].splitlines()[x-1].strip() for x in p['lines'])
                f=s['leadFrames']+math.ceil(m['onset']*30-1e-6)
                if i:assert s['steps'][i]==f
                if s['kind']!='overview':
                    cue=s['codeCues'][i];assert cue['beginFrame']==f and cue['lines']==p['lines'] and cue['cue']==p['text']
                    if i and p['lines']!=s['parts'][i-1]['lines']:switches+=1
                if i+1<len(meta['parts']) and meta['parts'][i+1]['onset']>m['end']+.05:silences+=1
            if s['kind']=='question':
                assert s['hold']==4 and c['scenes'][si+1]['kind']=='answer'
                assert s['resultFrame']==s['durationFrames']
            cursor+=s['durationFrames']
        assert cursor==c['startFrame']+c['durationFrames']
    assert cursor==t['totalFrames'] and units==247
    subprocess.run(['node','scripts/test_sync.mjs'],cwd=ROOT,check=True)
    return dict(chapters=10,exercises=58,pages=183,semanticParts=247,individualTestsPassed=56,changedLineSwitches=switches,interPartSilences=silences)
def rendered(t):
    manifest=load(BUILD/'render-inputs.json');cache=load(BUILD/'still-cache.json')
    for r in manifest['files']:
        p=pathlib.Path(r['path']);p=p if p.is_absolute() else ROOT/p
        assert digest(p)==r['sha256'],('Stale rendering dependency',r['path'])
    assert hashlib.sha256(''.join(r['sha256'] for r in manifest['files']).encode()).hexdigest()==manifest['sourceHash']
    by={s['key']:s for s in t['scenes']}
    for j in t['renderJobs']:
        path=ROOT/'public'/j['path'];assert cache[j['path']]==manifest['sourceHash']
        d=load(path.with_suffix('.json'));assert d['sourceHash']==manifest['sourceHash']
        s=by[j['sceneKey']];local=j['frame']-s['startFrame']
        pixels(path,s,local,expected(s,local))
    return dict(renderedStatesChecked=len(t['renderJobs']),renderInputFingerprint=manifest['sourceHash'])
def encoded(t,report):
    m=json.loads(capture(['ffprobe','-v','error','-show_streams','-show_format','-show_chapters','-of','json',str(FINAL)]))
    v=next(s for s in m['streams'] if s['codec_type']=='video');a=next(s for s in m['streams'] if s['codec_type']=='audio')
    assert v['codec_name']=='h264' and (v['width'],v['height'])==(1920,1080) and a['codec_name']=='aac' and int(a['sample_rate'])==48000
    assert not any(s['codec_type']=='subtitle' for s in m['streams']) and abs(float(m['format']['duration'])-t['duration'])<.08
    assert len(m['chapters'])==10
    for c,mc in zip(t['chapters'],m['chapters']):assert abs(float(mc['start_time'])-c['startFrame']/30)<.002 and mc['tags']['title']==c['title']
    frames=json.loads(capture(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(FINAL)]))['frames']
    pts=[float(f['best_effort_timestamp_time']) for f in frames];ticks=[round(x*30) for x in pts]
    assert all(abs(x-f/30)<.0001 for x,f in zip(pts,ticks)) and all(x<y for x,y in zip(ticks,ticks[1:]))
    jobs={j['frame']:j for j in t['renderJobs']};assert set(jobs)<=set(ticks)
    indices=[i for i,f in enumerate(ticks) if f in jobs]
    out=BUILD/'final-frames';out.mkdir(exist_ok=True)
    filt=BUILD/'qa-filter.txt';filt.write_text("select='"+'+'.join(f'eq(n,{i})' for i in indices)+"'",encoding='ascii')
    subprocess.run(['ffmpeg','-y','-v','error','-threads','2','-i',str(FINAL),'-filter_script:v',str(filt),'-fps_mode','passthrough','-threads','2',str(out/'sample-%04d.png')],check=True)
    by={s['key']:s for s in t['scenes']};records=[];files={}
    for ordinal,index in enumerate(indices,1):
        tick=ticks[index];j=jobs[tick];s=by[j['sceneKey']];local=tick-s['startFrame'];path=out/f'sample-{ordinal:04}.png';files[index]=path
        pixels(path,s,local,expected(s,local))
        with Image.open(path) as im,Image.open(ROOT/'public'/j['path']) as ref:
            a=np.asarray(im.convert('RGB')).astype(np.int16);b=np.asarray(ref.convert('RGB')).astype(np.int16)
            maes=[]
            for x,y,xx,yy in [(64,208,1400,943),(1432,215,1856,935)]:
                mae=float(np.mean(abs(a[y:yy,x:xx]-b[y:yy,x:xx])));maes.append(mae)
                assert mae<4,('Encoded frame differs',s['key'],tick,mae)
        records.append(dict(frame=tick,seconds=tick/30,key=s['key'],local=local,activeLines=expected(s,local),codeAndResultMAE=maes[0],notesMAE=maes[1]))
        if ordinal%150==0:print('ACTUAL_VIDEO_STATES_CHECKED',ordinal,len(indices),flush=True)
    # Check that each before/on/after boundary, speech ending, silent gap and
    # question hold displays the most recent authored state, never a future one.
    held=0
    for s in t['scenes']:
        meta=load(ROOT/'public/audio'/(s['key']+'.json'));targets={0,s['durationFrames']-1}
        for i,p in enumerate(meta['parts']):
            f=s['leadFrames']+math.ceil(p['onset']*30-1e-6)
            targets.update([max(0,f-1),f,min(s['durationFrames']-1,f+1),min(s['durationFrames']-1,s['leadFrames']+math.ceil(p['end']*30)+1)])
        for f in targets:
            if f>=s['durationFrames']:continue
            index=bisect.bisect_right(ticks,s['startFrame']+f)-1;j=jobs[ticks[index]]
            assert j['sceneKey']==s['key'],('Page boundary leak',s['key'],f)
            assert expected(s,f)==expected(s,ticks[index]-s['startFrame']),('Highlight flashed or moved early',s['key'],f)
            held+=1
    contactCount=contacts(t,BUILD/'qa',files,ticks)
    subprocess.run(['ffmpeg','-v','error','-threads','2','-i',str(FINAL),'-fps_mode','passthrough','-f','null','-'],check=True)
    write(BUILD/'encoded-frame-checks.json',dict(allPassed=True,records=records))
    report.update(videoSha256=digest(FINAL),videoBytes=FINAL.stat().st_size,encodedEvents=len(ticks),actualEncodedStatesCompared=len(records),heldStateBoundaryChecks=held,contactStates=contactCount,maxCodeAndResultMAE=max(r['codeAndResultMAE'] for r in records),maxNotesMAE=max(r['notesMAE'] for r in records),fullDecodePassed=True,chaptersEmbedded=10)
def main():
    p=argparse.ArgumentParser();p.add_argument('--final',action='store_true');p.add_argument('--rendered',action='store_true');a=p.parse_args()
    t=load(ROOT/'public/timeline.json');r=structure(t)
    if a.rendered or a.final:r.update(rendered(t))
    if a.final:encoded(t,r)
    r.update(allPassed=True,duration=t['duration'],timelineSha256=digest(ROOT/'public/timeline.json'),courseSha256=digest(ROOT/'public/course.json'),scope='all sources, authored semantic targets, final PCM and persistent-state implementation; final mode additionally checks every planned encoded state, actual highlight border pixels and full A/V decoding; no claim of listening to every minute')
    write(BUILD/('final-validation.json' if a.final else 'preflight-validation.json'),r);print(json.dumps(r,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
