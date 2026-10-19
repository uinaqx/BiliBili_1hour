"""Use independent lexical/acoustic CTC boundaries, preserving all AV content.

The next cue is displayed at its aligned first speech token, never with an
advance offset. Each cue remains until the following cue actually begins.
"""
import argparse,bisect,concurrent.futures,copy,hashlib,json,math,pathlib,shutil,subprocess,sys
import numpy as np
from subtitle_calibrate import audio_hash,ass_time,stamp
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';OUT=BUILD/'subtitle-sync-v2'
DEL=ROOT/'out'
FINAL=DEL/'一小时学习计算机组成原理_字幕修正版V2.mp4'
SOURCE=DEL/'一小时学习计算机组成原理_字幕校准版.mp4'
OUT.mkdir(exist_ok=True)
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')

def prepare():
    frozen=OUT/'previous-timeline.json'
    if not frozen.exists():shutil.copy2(ROOT/'public/timeline.json',frozen)
    t=load(frozen);allcaps=[];changes=[];reviews=[]
    for s in t['scenes']:
        key=s['key'];ctc=load(BUILD/'subtitle-ctc'/f'{key}.json')
        assert ctc['audioSha256']==hashlib.sha256((ROOT/'public/audio'/f'{key}.wav').read_bytes()).hexdigest()
        phonetic=BUILD/'subtitle-ctc-phonetic'/f'{key}.json'
        if phonetic.exists():
            other=load(phonetic);assert other['audioSha256']==ctc['audioSha256']
            for j,(lexical,alt) in enumerate(zip(ctc['captions'],other['captions'])):
                # Homophone emissions confirm e.g. a spoken binary one as
                # "yao". Prefer that stronger acoustic evidence only when the
                # two independent transcript paths agree on its location.
                if alt['firstConfidence']>lexical['firstConfidence']+.05 and abs(alt['onset']-lexical['onset'])<=.12:
                    ctc['captions'][j]=alt
        oldcaps=copy.deepcopy(s['captions']);new=[]
        for i,(old,c) in enumerate(zip(oldcaps,ctc['captions'])):
            assert old['text']==c['text']
            # 400-sample receptive window centres are 12.5ms after the 20ms
            # output tick. Do not advance a cue before its actual token.
            # A CTC label may start on a weak pre-phoneme frame. Move at most
            # 40ms toward its actual acoustic peak, never beyond that peak.
            onset=min(c['onset']+.04,c['firstPeak'])+.0125
            previous_end=ctc['captions'][i-1]['offset']+.0125 if i else 0
            start=max(onset,previous_end)
            new.append(dict(start=start,end=c['offset']+.0125,text=old['text']))
            record=dict(scene=key,index=i,text=c['text'],oldStart=old['start'],newStart=start,change=start-old['start'],ctcOnset=c['onset'],ctcOffset=c['offset'],firstConfidence=c['firstConfidence'],meanConfidence=c['meanConfidence'])
            changes.append(record)
            if abs(start-old['start'])>.22 or c['meanConfidence']<.15:reviews.append(record)
        assert len(new)==len(oldcaps)
        assert all(a['start']<b['start'] for a,b in zip(new,new[1:])),key
        for i,c in enumerate(new):
            c['end']=new[i+1]['start'] if i+1<len(new) else oldcaps[-1]['end']
            assert c['end']>c['start'],(key,i)
        s['captions']=new
        for c in new:
            a=s['startFrame']+s['leadFrames']+math.ceil(c['start']*30-1e-6)
            b=s['startFrame']+s['leadFrames']+math.ceil(c['end']*30-1e-6)
            assert b>a
            allcaps.append(dict(start=a/30,end=b/30,startFrame=a,endFrame=b,text=c['text'].replace('KIB','KiB').replace('risc','RISC').replace('cisc','CISC'),scene=key))
    assert len(allcaps)==len(t['captions'])
    t['captions']=allcaps;scene_lookup={s['key']:s for s in t['scenes']}
    header=(BUILD/'00.ass').read_text(encoding='utf-8-sig').split('Dialogue:')[0]
    for ch in t['chapters']:
        begin=ch['startFrame'];end=begin+ch['durationFrames']
        ch['scenes']=[copy.deepcopy(scene_lookup[s['key']]) for s in ch['scenes']]
        ch['captions']=[dict(c,startFrame=c['startFrame']-begin,endFrame=c['endFrame']-begin,start=c['start']-begin/30,end=c['end']-begin/30) for c in allcaps if begin<=c['startFrame']<end]
        visuals=[dict(frame=j['frame']-begin,path=j['path']) for j in t['renderJobs'] if begin<=j['frame']<end]
        frames=[v['frame'] for v in visuals]
        points=sorted(({v['frame'] for v in visuals}|{c['startFrame'] for c in ch['captions']}|{c['endFrame'] for c in ch['captions']})-{ch['durationFrames']})
        assert points[0]==0
        ch['images']=[dict(path=visuals[bisect.bisect_right(frames,f)-1]['path'],frame=f,frames=(points[i+1] if i+1<len(points) else ch['durationFrames'])-f) for i,f in enumerate(points)]
        lines=[f"Dialogue: 0,{ass_time(c['startFrame'])},{ass_time(c['endFrame'])},Default,,0,0,0,,{c['text'].replace('{','').replace('}','')}" for c in ch['captions']]
        (OUT/f"{ch['key']}.ass").write_text(header+'\n'.join(lines)+'\n',encoding='utf-8-sig')
    t['subtitleCalibration']='v2 independent lexical CTC on frozen PCM; zero cue advance; preserve preceding speech tail'
    save(OUT/'timeline.json',t)
    srt='\n\n'.join(f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for i,c in enumerate(allcaps,1))+'\n'
    (OUT/'subtitles.srt').write_text(srt,encoding='utf-8-sig')
    save(OUT/'boundary-review.json',dict(captions=len(allcaps),changes=changes,outliers=reviews,allVisualStatesUnchanged=t['renderJobs']==load(frozen)['renderJobs'],durationSeconds=t['duration'],needsReview=len(reviews)))
    print('V2_PREPARED','captions',len(allcaps),'outliers',len(reviews),'changePercentiles',np.percentile([c['change'] for c in changes],[0,50,90,99,100]).tolist(),flush=True)
    for r in reviews:print('REVIEW',json.dumps(r,ensure_ascii=False),flush=True)

def run(args,log):
    with (OUT/log).open('w',encoding='utf-8') as f:
        subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','warning',*args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,check=True)

def encode(ch):
    key=ch['key'];ass=OUT/f'{key}.ass';dest=OUT/f'{key}.mp4';tag=OUT/f'{key}.hash'
    fingerprint=hashlib.sha256(json.dumps(ch['images']).encode()+ass.read_bytes()).hexdigest()
    if dest.exists() and tag.exists() and tag.read_text()==fingerprint:return
    rows=['ffconcat version 1.0']
    for e in ch['images']:
        rows.extend([f"file '{(ROOT/'public'/e['path']).as_posix()}'",'option framerate 30',f"duration {e['frames']/30:.9f}"])
    rows.extend([f"file '{(ROOT/'public'/ch['images'][-1]['path']).as_posix()}'",'option framerate 30'])
    listing=OUT/f'{key}.ffconcat';listing.write_text('\n'.join(rows)+'\n',encoding='utf-8')
    run(['-f','concat','-safe','0','-i',str(listing),'-vf',f'ass=build/subtitle-sync-v2/{key}.ass','-an','-fps_mode','vfr','-enc_time_base','1:30','-t',f"{ch['durationFrames']/30:.9f}",'-c:v','libx264','-preset','fast','-crf','20','-bf','0','-g','30','-pix_fmt','yuv420p','-threads','4','-video_track_timescale','30000',str(dest)],key+'.log')
    tag.write_text(fingerprint);print('V2_CHAPTER',key,flush=True)

def packet_clock(p):
    return hashlib.sha256(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_entries','packet=pts,dts,duration,size','-of','csv=p=0',str(p)])).hexdigest()

def render():
    t=load(OUT/'timeline.json')
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(encode,t['chapters']))
    listing=OUT/'videos.ffconcat';listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{ch['key']}.mp4'\nduration {ch['durationFrames']/30:.9f}\n" for ch in t['chapters']),encoding='utf-8')
    run(['-f','concat','-safe','0','-i',str(listing),'-i',str(SOURCE),'-f','ffmetadata','-i',str(BUILD/'chapters.ffmetadata'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','copy','-video_track_timescale','30000','-movflags','+faststart',str(FINAL)],'mux.log')
    before=audio_hash(SOURCE);after=audio_hash(FINAL);clock=packet_clock(SOURCE)
    assert before==after and clock==packet_clock(FINAL),'Frozen narration changed'
    save(OUT/'audio-proof.json',dict(identical=True,packetTimesIdentical=True,originalAacSha256=before,correctedAacSha256=after,packetClockSha256=clock))
    print('V2_RENDERED_EXACT_ORIGINAL_AUDIO',flush=True)

def publish():
    report=load(OUT/'validation.json');assert report['allPassed']
    timeline=load(OUT/'timeline.json');save(ROOT/'public/timeline.json',timeline)
    for s in timeline['scenes']:
        path=ROOT/'public/audio'/f"{s['key']}.json";meta=load(path)
        caps=copy.deepcopy(s['captions']);caps[-1]['end']=meta['duration']
        meta['captions']=caps
        meta['captionCalibration']=dict(version=2,method='independent transcript-constrained CTC with phonetic review; zero advance; verify actual encoded caption identity',audioUnchanged=True)
        save(path,meta)
    for ch in timeline['chapters']:shutil.copy2(OUT/f"{ch['key']}.ass",BUILD/f"{ch['key']}.ass")
    for name in ['中文字幕.srt','中文字幕_修正版V2.srt']:
        shutil.copy2(OUT/'subtitles.srt',DEL/name)
    shutil.copy2(FINAL,DEL/'一小时学习计算机组成原理.mp4')
    save(DEL/'字幕修正版V2_检查报告.json',report)
    (DEL/'字幕修正版V2_说明.md').write_text('''# 字幕修正版 V2

请使用 `一小时学习计算机组成原理_字幕修正版V2.mp4`。主文件也已更新，旧的“字幕校准版”文件保留作历史版本。

本次只调整字幕时间：以现有配音做独立的逐字 CTC 对齐；连续数字、同音字及边界分歧另作语音复核。取消字幕起点的提前量，保留上一句到下一句起音后再切换。没有重新生成、调速或编码语音，没有修改教学画面和章节时间。

检查记录：

- 73 段配音在成片中的首、中、尾共 219 处波形对照，未检测到声音时间轴偏移。
- 1,396 条字幕起点逐项检查；对可疑位置查看波形并交叉比较词语对齐结果。
- 从输出视频解码全部 2,918 个显示状态，将实际字幕文字与对应文字参考图比较，无错行、提前显示另一条文字或应显示却空白的状态。
- AAC 音频载荷以及每个音频包的 PTS、DTS、时长和大小均与原版一致。
- 时长 68 分 12.1 秒、12 个章节、教学图示步骤时间保持不变，全片严格解码通过。

以上为自动对齐、波形复核和实际字幕图像检查记录，不声称已经进行全片逐字人工听辨。
''',encoding='utf-8')
    (DEL/'交付说明.md').write_text('''# 一小时学习计算机组成原理

当前版本：`一小时学习计算机组成原理_字幕修正版V2.mp4`；主文件 `一小时学习计算机组成原理.mp4` 为相同内容。时长 68 分 12.1 秒。

- `中文字幕_修正版V2.srt` 与 `中文字幕.srt`：最新独立字幕。
- `字幕修正版V2_说明.md`、`字幕修正版V2_检查报告.json`：本次字幕修正与输出检查记录。
- `章节目录.md`、`完整讲稿.md`、`课堂练习与答案.md`：课程配套材料。
- `计算机组成原理视频工程.zip`：已同步本次修正的可编辑工程与声音缓存，不包含个人凭据。

旧“字幕校准版”视频与同名字幕保留作历史版本。`验收报告.json`、`验收说明.md` 是该历史版本的检查记录；本次以 V2 检查报告为准。
''',encoding='utf-8')
    print('V2_PUBLISHED',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','render','publish']);a=p.parse_args()
    {'prepare':prepare,'render':render,'publish':publish}[a.action]()
