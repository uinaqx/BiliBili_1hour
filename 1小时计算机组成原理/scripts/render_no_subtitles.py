"""Render clean cached teaching visuals and stream-copy the existing narration.

No TTS, no audio encoding, no subtitle filter, no modifications to the captioned
edition. All teaching labels, diagrams, animation steps and chapters are kept.
"""
import concurrent.futures,hashlib,json,pathlib,subprocess,sys
import numpy as np
from subtitle_calibrate import audio_hash
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build'
OUT=BUILD/'no-subtitles';OUT.mkdir(exist_ok=True)
DEL=ROOT/'out'
SOURCE=DEL/'一小时学习计算机组成原理_字幕修正版V2.mp4'
FINAL=DEL/'一小时学习计算机组成原理_无字幕版.mp4'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def run(args,name):
    with (OUT/name).open('w',encoding='utf-8') as f:
        subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','warning',*args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)

def clean_chapters(t):
    chapters=[]
    for c in t['chapters']:
        begin=c['startFrame'];end=begin+c['durationFrames']
        jobs=[j for j in t['renderJobs'] if begin<=j['frame']<end]
        assert jobs[0]['frame']==begin
        images=[dict(path=j['path'],frame=j['frame']-begin,frames=(jobs[i+1]['frame'] if i+1<len(jobs) else end)-j['frame']) for i,j in enumerate(jobs)]
        assert sum(e['frames'] for e in images)==c['durationFrames']
        chapters.append(dict(key=c['key'],startFrame=begin,durationFrames=c['durationFrames'],images=images))
    return chapters

def encode(c):
    key=c['key'];dest=OUT/f'{key}.mp4';tag=OUT/f'{key}.hash'
    # Hash the real clean stills, so visual edits invalidate the chapter cache.
    hashes={e['path']:hashlib.sha256((ROOT/'public'/e['path']).read_bytes()).hexdigest() for e in c['images']}
    fingerprint=hashlib.sha256(json.dumps([c,hashes,'clean-no-ass-v1']).encode()).hexdigest()
    if dest.exists() and tag.exists() and tag.read_text()==fingerprint:return
    rows=['ffconcat version 1.0']
    for e in c['images']:
        rows.extend([f"file '{(ROOT/'public'/e['path']).as_posix()}'",'option framerate 30',f"duration {e['frames']/30:.9f}"])
    rows.extend([f"file '{(ROOT/'public'/c['images'][-1]['path']).as_posix()}'",'option framerate 30'])
    listing=OUT/f'{key}.ffconcat';listing.write_text('\n'.join(rows)+'\n',encoding='utf-8')
    run(['-f','concat','-safe','0','-i',str(listing),'-an','-fps_mode','vfr','-enc_time_base','1:30','-t',f"{c['durationFrames']/30:.9f}",'-c:v','libx264','-preset','fast','-crf','20','-bf','0','-g','30','-pix_fmt','yuv420p','-threads','4','-video_track_timescale','30000',str(dest)],key+'.log')
    tag.write_text(fingerprint);print('CLEAN_CHAPTER_READY',key,flush=True)

def probe(path,*args):
    return json.loads(subprocess.check_output(['ffprobe','-v','error',*args,'-of','json',str(path)]))
def packet_clock(path):
    return hashlib.sha256(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_entries','packet=pts,dts,duration,size','-of','csv=p=0',str(path)])).hexdigest()

def verify(t,chapters):
    info=probe(FINAL,'-show_streams','-show_format','-show_chapters')
    original=probe(SOURCE,'-show_chapters')
    v=next(s for s in info['streams'] if s['codec_type']=='video')
    a=next(s for s in info['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'],v['codec_name'],a['codec_name'],a['sample_rate'])==(1920,1080,'h264','aac','48000')
    assert not any(s['codec_type']=='subtitle' for s in info['streams'])
    assert abs(float(info['format']['duration'])-t['duration'])<.002
    assert info['chapters']==original['chapters'] and len(info['chapters'])==12
    expected=[(c['startFrame']+e['frame'],e['frames']) for c in chapters for e in c['images']]
    packets=probe(FINAL,'-select_streams','v:0','-show_packets','-show_entries','packet=pts_time,duration_time')['packets']
    assert len(packets)==len(expected)
    for p,(frame,duration) in zip(packets,expected):
        assert abs(float(p['pts_time'])*30-frame)<.002
        assert abs(float(p['duration_time'])*30-duration)<.002
    # Check every encoded state, including all question countdowns and joins.
    p=subprocess.Popen(['ffmpeg','-v','error','-i',str(FINAL),'-an','-vf','crop=1740:110:90:955,scale=580:37,format=gray','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','gray','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    size=580*37;count=0;bad=[]
    while True:
        raw=bytearray()
        while len(raw)<size:
            block=p.stdout.read(size-len(raw))
            if not block:break
            raw.extend(block)
        if not raw:break
        assert len(raw)==size
        pixels=int(np.count_nonzero(np.frombuffer(raw,dtype=np.uint8)>170))
        if pixels>5:bad.append(dict(frame=expected[count][0],captionPixels=pixels))
        count+=1
    err=p.stderr.read().decode(errors='replace');assert p.wait()==0,err
    assert count==len(expected) and not bad,(count,bad)
    before=audio_hash(SOURCE);after=audio_hash(FINAL)
    before_clock=packet_clock(SOURCE);after_clock=packet_clock(FINAL)
    assert before==after and before_clock==after_clock
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(FINAL),'-map','0:v:0','-map','0:a:0','-f','null','-'],check=True)
    report=dict(allPassed=True,durationSeconds=t['duration'],width=1920,height=1080,chapters=12,subtitleStreams=0,cleanStatesChecked=count,burnedCaptionStates=0,audioPayloadUnchanged=True,audioPacketTimingUnchanged=True,audioSha256=after,audioPacketClockSha256=after_clock,strictDecodePassed=True,method='clean original Remotion PNGs at original visual event times; exact AAC stream copy')
    save(OUT/'validation.json',report);save(DEL/'无字幕版_检查报告.json',report)
    print('NO_SUBTITLES_VERIFIED',count,'states; audio payload and clocks identical',flush=True)

def main():
    t=load(ROOT/'public/timeline.json');chapters=clean_chapters(t)
    save(OUT/'visual-timeline.json',dict(duration=t['duration'],chapters=chapters))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(encode,chapters))
    listing=OUT/'videos.ffconcat';listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{c['key']}.mp4'\nduration {c['durationFrames']/30:.9f}\n" for c in chapters),encoding='utf-8')
    staged=OUT/'complete.mp4'
    run(['-f','concat','-safe','0','-i',str(listing),'-i',str(SOURCE),'-f','ffmetadata','-i',str(BUILD/'chapters.ffmetadata'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','copy','-video_track_timescale','30000','-movflags','+faststart',str(staged)],'mux.log')
    staged.replace(FINAL)
    verify(t,chapters)
    print('NO_SUBTITLES_DONE',str(FINAL),flush=True)
if __name__=='__main__':main()
