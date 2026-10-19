"""Recalibrate captions against frozen narration; never write or synthesize audio.

The provider's character times are mapped through EXISTING sample insertions
as a diagnostic reference. Semantic ASR timestamps and independent acoustic
checks replace the old timing. Remotion states and AAC packets stay unchanged.
"""
import argparse, bisect, concurrent.futures, copy, hashlib, json, math
import pathlib, shutil, subprocess, sys
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')
ROOT = pathlib.Path(__file__).resolve().parents[1]
BUILD = ROOT/'build'; BACKUP = BUILD/'subtitle-backup'
DEL = ROOT/'out'
FINAL = DEL/'一小时学习计算机组成原理.mp4'
CORRECTED = DEL/'一小时学习计算机组成原理_字幕校准版.mp4'
OUT = BUILD/'subtitle-corrected'
OUT.mkdir(exist_ok=True)
def load(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p, v): p.write_text(json.dumps(v, ensure_ascii=False, indent=2), encoding='utf-8')
def clean(text): return ''.join(c for c in text.casefold() if c.isalnum())
def backup():
    BACKUP.mkdir(exist_ok=True)
    for p in [ROOT/'public/timeline.json',FINAL,DEL/'中文字幕.srt',BUILD/'final-validation.json']:
        dest=BACKUP/p.name
        if not dest.exists():shutil.copy2(p,dest)
    for folder in ['audio','audio_original']:
        dest=BACKUP/folder;dest.mkdir(exist_ok=True)
        for p in (ROOT/'public'/folder).glob('*.json'):
            if not (dest/p.name).exists():shutil.copy2(p,dest/p.name)
    print('FROZEN_BASELINE_READY',flush=True)
def stamp(sec):
    ms=round(sec*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
def ass_time(frame):
    cs=max(0,(frame*1000//30-1)//10);h,cs=divmod(cs,360000);m,cs=divmod(cs,6000);s,cs=divmod(cs,100)
    return f'{h}:{m:02}:{s:02}.{cs:02}'
def mapped_words(key):
    raw=load(ROOT/'public/audio_original'/f'{key}.json')
    frozen=load(BACKUP/'audio'/f'{key}.json')
    cuts=frozen['insertedPauseSamples']; chars=[]
    def mapped(ms, end=False):
        pos=round(ms*24)
        n=bisect.bisect_left(cuts,pos) if end else bisect.bisect_right(cuts,pos)
        return ms/1000+n*.1
    for w in raw['words']:
        text=clean(w['text'])
        for i,c in enumerate(text):
            a=w['begin_time']+(w['end_time']-w['begin_time'])*i/len(text)
            b=w['begin_time']+(w['end_time']-w['begin_time'])*(i+1)/len(text)
            chars.append(dict(text=c,start=mapped(a),end=mapped(b,True)))
    return chars,frozen

def prepare():
    t=load(BACKUP/'timeline.json'); globalcaps=[]; changes=[]; acoustic=[]
    for scene in t['scenes']:
        key=scene['key']; chars,meta=mapped_words(key); old=meta['captions']
        assert clean(''.join(c['text'] for c in old))==''.join(c['text'] for c in chars),key
        fa_path=BUILD/'subtitle-asr'/f'{key}.json'
        fa=load(fa_path) if fa_path.exists() else None
        assert fa is not None, 'Run subtitle_asr.py first: '+key
        assert fa['audioSha256']==hashlib.sha256((ROOT/'public/audio'/f'{key}.wav').read_bytes()).hexdigest()
        pos=0; caps=[]
        for i,c in enumerate(old):
            n=len(clean(c['text'])); a,b=chars[pos],chars[pos+n-1]
            onset=fa['captions'][i]['onset']; offset=fa['captions'][i]['offset']
            delta=onset-a['start']
            start=max(0,onset-.035,caps[-1]['end']-.01 if caps else 0)
            caps.append(dict(start=start,end=offset,text=c['text']))
            changes.append(dict(scene=key,index=i,text=c['text'],oldStart=c['start'],newStart=start,change=start-c['start']))
            acoustic.append(dict(scene=key,index=i,providerStart=a['start'],acousticOnset=onset,start=start,spokenEnd=offset,providerEnd=b['end'],providerOnsetDelta=delta))
            pos+=n
        # Hold each line until the next actually spoken phrase. In particular,
        # a line must not vanish during its final syllable or a sentence pause.
        assert all(a['start']<b['start'] for a,b in zip(caps,caps[1:])),key
        for i,c in enumerate(caps):
            end=caps[i+1]['start'] if i+1<len(caps) else meta['duration']
            assert end>=c['end']-.10,(key,i,'early disappearance',end,c['end'])
            c['end']=end
        newmeta=copy.deepcopy(meta);newmeta['captions']=caps
        newmeta['captionCalibration']=dict(method='semantic ASR character timing with independent Chinese acoustic verification; provider times used as diagnostic reference',audioUnchanged=True)
        save(ROOT/'public/audio'/f'{key}.json',newmeta)
        local=copy.deepcopy(caps)
        local[-1]['end']=(scene['speechFrames']+scene['sentenceTailFrames']+(0 if scene['kind']=='question' else round(scene['hold']*30)))/30
        scene['captions']=local
        for c in local:
            a=scene['startFrame']+scene['leadFrames']+math.ceil(c['start']*30-1e-6)
            b=scene['startFrame']+scene['leadFrames']+math.ceil(c['end']*30-1e-6)
            assert b>a,(key,c)
            globalcaps.append(dict(start=a/30,end=b/30,text=c['text'].replace('KIB','KiB').replace('risc','RISC').replace('cisc','CISC'),startFrame=a,endFrame=b,scene=key))
    t['captions']=globalcaps
    original_ass=(BUILD/'00.ass').read_text(encoding='utf-8-sig')
    header=original_ass.split('Dialogue:')[0]
    scene_by_key={s['key']:s for s in t['scenes']}
    for chapter in t['chapters']:
        begin=chapter['startFrame'];length=chapter['durationFrames']
        chapter['scenes']=[copy.deepcopy(scene_by_key[s['key']]) for s in chapter['scenes']]
        chapter['captions']=[dict(c,startFrame=c['startFrame']-begin,endFrame=c['endFrame']-begin,start=c['start']-begin/30,end=c['end']-begin/30) for c in globalcaps if begin<=c['startFrame']<begin+length]
        visuals=[dict(frame=j['frame']-begin,path=j['path']) for j in t['renderJobs'] if begin<=j['frame']<begin+length]
        vf=[v['frame'] for v in visuals]
        points=sorted(({v['frame'] for v in visuals}|{c['startFrame'] for c in chapter['captions']}|{c['endFrame'] for c in chapter['captions']})-{length})
        assert points[0]==0 and all(0<=f<length for f in points)
        chapter['images']=[dict(path=visuals[bisect.bisect_right(vf,f)-1]['path'],frames=(points[i+1] if i+1<len(points) else length)-f,frame=f) for i,f in enumerate(points)]
        events=[f"Dialogue: 0,{ass_time(c['startFrame'])},{ass_time(c['endFrame'])},Default,,0,0,0,,{c['text'].replace('{','').replace('}','')}" for c in chapter['captions']]
        (BUILD/f"{chapter['key']}.ass").write_text(header+'\n'.join(events)+'\n',encoding='utf-8-sig')
    assert t['renderJobs']==load(BACKUP/'timeline.json')['renderJobs']
    t['subtitleCalibration']='2026-10-18 frozen audio, semantic ASR character anchors and independent Chinese acoustic check'
    save(ROOT/'public/timeline.json',t)
    srt='\n\n'.join(f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for i,c in enumerate(globalcaps,1))+'\n'
    for name in ['中文字幕.srt','中文字幕_校准版.srt']:(DEL/name).write_text(srt,encoding='utf-8-sig')
    report=dict(captions=len(globalcaps),changes=changes,acoustic=acoustic,maxChangedSeconds=max(abs(x['change']) for x in changes),changedOver100ms=sum(abs(x['change'])>.1 for x in changes),providerAcousticDeltaP95=float(np.percentile([abs(x['providerOnsetDelta']) for x in acoustic],95)),audioReencoded=False,visualTimingUnchanged=True)
    save(BUILD/'subtitle-calibration.json',report)
    print('CAPTIONS_CALIBRATED',json.dumps({k:v for k,v in report.items() if k not in ['changes','acoustic']},ensure_ascii=False),flush=True)

def run(args,log):
    with (OUT/log).open('w',encoding='utf-8') as f:
        subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','warning',*args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)
def encode_chapter(ch):
    key=ch['key']; dest=OUT/f'{key}.mp4';ass=BUILD/f'{key}.ass'
    fp=hashlib.sha256(json.dumps(ch['images']).encode()+ass.read_bytes()).hexdigest();tag=OUT/f'{key}.hash'
    if dest.exists() and tag.exists() and tag.read_text()==fp:return
    rows=['ffconcat version 1.0']
    for e in ch['images']:
        p=ROOT/'public'/e['path'];assert p.exists()
        rows.extend([f"file '{p.as_posix()}'",'option framerate 30',f"duration {e['frames']/30:.9f}"])
    rows.extend([f"file '{(ROOT/'public'/ch['images'][-1]['path']).as_posix()}'",'option framerate 30'])
    listing=OUT/f'{key}.ffconcat';listing.write_text('\n'.join(rows)+'\n',encoding='utf-8')
    run(['-f','concat','-safe','0','-i',str(listing),'-vf',f'ass=build/{key}.ass','-an','-fps_mode','vfr','-enc_time_base','1:30','-t',f"{ch['durationFrames']/30:.9f}",'-c:v','libx264','-preset','fast','-crf','20','-bf','0','-g','30','-pix_fmt','yuv420p','-threads','4','-video_track_timescale','30000',str(dest)],key+'.log')
    tag.write_text(fp);print('SUBTITLE_VIDEO_READY',key,flush=True)
def audio_hash(path):
    p=subprocess.Popen(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c:a','copy','-f','adts','-'],stdout=subprocess.PIPE)
    h=hashlib.sha256()
    while True:
        b=p.stdout.read(1024*1024)
        if not b:break
        h.update(b)
    assert p.wait()==0
    return h.hexdigest()
def render():
    t=load(ROOT/'public/timeline.json')
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(encode_chapter,t['chapters']))
    listing=OUT/'videos.ffconcat';listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{ch['key']}.mp4'\nduration {ch['durationFrames']/30:.9f}\n" for ch in t['chapters']),encoding='utf-8')
    run(['-f','concat','-safe','0','-i',str(listing),'-i',str(BACKUP/FINAL.name),'-f','ffmetadata','-i',str(BUILD/'chapters.ffmetadata'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','copy','-video_track_timescale','30000','-movflags','+faststart',str(CORRECTED)],'mux.log')
    before=audio_hash(BACKUP/FINAL.name);after=audio_hash(CORRECTED);assert before==after
    def packet_clock(path):
        return hashlib.sha256(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_entries','packet=pts,dts,duration,size','-of','csv=p=0',str(path)])).hexdigest()
    before_clock=packet_clock(BACKUP/FINAL.name);after_clock=packet_clock(CORRECTED)
    assert before_clock==after_clock,'Audio packet timing changed'
    proof=dict(originalAacSha256=before,correctedAacSha256=after,identical=True,packetClockSha256=before_clock,packetTimesIdentical=True,method='AAC stream copied; ADTS payload and packet pts/dts/duration/size SHA256 equal')
    save(BUILD/'subtitle-audio-proof.json',proof)
    shutil.copy2(CORRECTED,FINAL)
    print('AUDIO_BIT_IDENTICAL',before,flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['backup','prepare','render']);a=p.parse_args()
    {'backup':backup,'prepare':prepare,'render':render}[a.action]()
