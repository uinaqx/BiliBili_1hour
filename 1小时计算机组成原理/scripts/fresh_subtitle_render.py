"""Add fresh, independently recognized captions directly to the clean MP4.

No old caption timeline, still-image manifest or transcript is read here.
Video is rendered at constant 30fps. The original AAC packets are copied.
"""
import argparse,bisect,concurrent.futures,hashlib,json,math,pathlib,shutil,subprocess,sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1]
BASE=ROOT/'build/fresh-subtitles-20261019';OUT=BASE/'render';OUT.mkdir(parents=True,exist_ok=True)
DEL=ROOT/'out'
SOURCE=DEL/'一小时学习计算机组成原理_无字幕版.mp4'
FINAL=DEL/'一小时学习计算机组成原理_从零识别字幕版.mp4'
FPS=30
HEADER='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Microsoft YaHei,40,&H00F3F5FA,&H00FFFFFF,&H00101824,&H00101824,0,0,0,0,100,100,0,0,1,2,0,2,90,90,54,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def probe(p,*args):return json.loads(subprocess.check_output(['ffprobe','-v','error',*args,'-of','json',str(p)]))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        while b:=f.read(1024*1024):h.update(b)
    return h.hexdigest()
def ass_time(frame):
    # The guard is shorter than one frame. It makes a frame-quantized event
    # visible at its intended frame, while the previous frame remains earlier.
    cs=max(0,(frame*1000//30-1)//10);h,cs=divmod(cs,360000);m,cs=divmod(cs,6000);s,cs=divmod(cs,100)
    return f'{h}:{m:02}:{s:02}.{cs:02}'
def srt_time(frame):
    ms=round(frame/30*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
def dialogue(c,a,b):
    text=c['text'].replace('{','').replace('}','').replace('\\','').replace('\n',' ')
    return f'Dialogue: 0,{ass_time(a)},{ass_time(b)},Default,,0,0,0,,{text}'

def prepare(path):
    data=load(path);caps=data['captions'] if isinstance(data,dict) else data
    info=probe(SOURCE,'-show_format','-show_streams','-show_chapters')
    total=round(float(info['format']['duration'])*30);quantized=[]
    for i,c in enumerate(caps):
        assert c['text'].strip() and c['end']>c['start']>=0,(i,c)
        a=math.ceil(c['start']*30-1e-7);b=math.ceil(c['end']*30-1e-7)
        assert 0<=a<b<=total,(i,c,a,b)
        if quantized:assert quantized[-1]['endFrame']<=a,('overlapping cues',i,c)
        quantized.append(dict(c,startFrame=a,endFrame=b,start=a/30,end=b/30))
    chapters=[]
    for i,ch in enumerate(info['chapters']):
        a=round(float(ch['start_time'])*30);b=round(float(ch['end_time'])*30)
        local=[c for c in quantized if c['endFrame']>a and c['startFrame']<b]
        ass=OUT/f'{i:02}.ass'
        ass.write_text(HEADER+'\n'.join(dialogue(c,max(0,c['startFrame']-a),min(b-a,c['endFrame']-a)) for c in local)+'\n',encoding='utf-8-sig')
        chapters.append(dict(key=f'{i:02}',startFrame=a,durationFrames=b-a,captions=len(local)))
    assert chapters[0]['startFrame']==0 and sum(c['durationFrames'] for c in chapters)==total
    manifest=dict(source=str(SOURCE),sourceSha256=sha(SOURCE),sourceMetadata=info,captionSource=str(path),captions=quantized,chapters=chapters,totalFrames=total,duration=total/30)
    save(OUT/'manifest.json',manifest)
    srt='\n\n'.join(f"{i}\n{srt_time(c['startFrame'])} --> {srt_time(c['endFrame'])}\n{c['text']}" for i,c in enumerate(quantized,1))+'\n'
    (OUT/'subtitles.srt').write_text(srt,encoding='utf-8-sig')
    print('FRESH_CAPTIONS_PREPARED',len(quantized),'chapters',len(chapters),flush=True)

def run(args,name):
    with (OUT/name).open('w',encoding='utf-8') as log:
        subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','warning',*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
def encode(ch,preview=False):
    key=ch['key'];m=load(OUT/'manifest.json');n=min(2700,ch['durationFrames']) if preview else ch['durationFrames']
    dest=OUT/(key+('.preview.mp4' if preview else '.mp4'));tag=dest.with_suffix('.hash')
    fp=hashlib.sha256(json.dumps([ch,m['sourceSha256'],n,'direct-CFR-v1']).encode()+(OUT/f'{key}.ass').read_bytes()).hexdigest()
    if dest.exists() and tag.exists() and tag.read_text()==fp:return
    run(['-ss',f"{ch['startFrame']/30:.9f}",'-i',str(SOURCE),'-map','0:v:0','-an','-vf',f'fps=30:start_time=0,ass=build/fresh-subtitles-20261019/render/{key}.ass','-frames:v',str(n),'-c:v','libx264','-preset','veryfast','-tune','stillimage','-crf','19','-g','60','-pix_fmt','yuv420p','-threads','3','-video_track_timescale','30000',str(dest)],key+('.preview.log' if preview else '.log'))
    actual=probe(dest,'-show_streams')['streams'][0];assert int(actual['nb_frames'])==n
    tag.write_text(fp);print('FRESH_CHAPTER_RENDERED',key,n,'frames',flush=True)

def audio_hash(p):
    proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c:a','copy','-f','adts','-'],stdout=subprocess.PIPE)
    h=hashlib.sha256()
    while b:=proc.stdout.read(1024*1024):h.update(b)
    assert proc.wait()==0;return h.hexdigest()
def audio_clock(p):
    return hashlib.sha256(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_entries','packet=pts,dts,duration,size','-of','csv=p=0',str(p)])).hexdigest()

def render(preview=False):
    m=load(OUT/'manifest.json')
    if preview:encode(m['chapters'][0],True);return
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(encode,m['chapters']))
    listing=OUT/'videos.ffconcat';listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{c['key']}.mp4'\nduration {c['durationFrames']/30:.9f}\n" for c in m['chapters']),encoding='utf-8')
    staged=OUT/'complete.mp4'
    run(['-f','concat','-safe','0','-i',str(listing),'-i',str(SOURCE),'-map','0:v:0','-map','1:a:0','-map_metadata','1','-map_chapters','1','-c:v','copy','-c:a','copy','-video_track_timescale','30000','-movflags','+faststart',str(staged)],'mux.log')
    original_hash=audio_hash(SOURCE);output_hash=audio_hash(staged);clock=audio_clock(SOURCE)
    assert original_hash==output_hash and clock==audio_clock(staged)
    actual=probe(staged,'-show_streams','-show_format','-show_chapters')
    video=next(s for s in actual['streams'] if s['codec_type']=='video')
    assert video['avg_frame_rate']=='30/1' and int(video['nb_frames'])==m['totalFrames']
    assert abs(float(actual['format']['duration'])-m['duration'])<.002
    assert actual['chapters']==m['sourceMetadata']['chapters']
    save(OUT/'audio-proof.json',dict(aacSha256=original_hash,packetClockSha256=clock,audioPayloadUnchanged=True,audioPacketTimesUnchanged=True,chaptersUnchanged=True,constantFrameRate=30,videoFrames=m['totalFrames']))
    staged.replace(FINAL);print('FRESH_VIDEO_RENDERED',str(FINAL),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','preview','render']);p.add_argument('--captions',type=pathlib.Path,default=BASE/'qa/reviewed-captions.json');args=p.parse_args()
    if args.action=='prepare':prepare(args.captions)
    else:render(args.action=='preview')
