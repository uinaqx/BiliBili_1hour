"""Keep aligned caption starts; hold text until the next cue or the voice ends.

Reuses unchanged rendered frames and copies the approved AAC track verbatim.
"""
import argparse,asyncio,bisect,concurrent.futures,copy,hashlib,json,math,pathlib,shutil,subprocess,sys
from PIL import Image,ImageChops,ImageStat,ImageDraw,ImageFont
import video as base
ROOT=pathlib.Path(__file__).resolve().parents[1];ORIGINAL=ROOT/'production/repair_sync'
P=ROOT/'production/subtitle_hold';BUILD=P/'build';STILLS=P/'stills'
DELIVERY=ROOT/'out'
SOURCE=DELIVERY/'统一语速_字幕校准版/计算机组成原理_统一语速字幕校准版.mp4'
OUT=DELIVERY/'字幕完整显示版';TARGET=OUT/'计算机组成原理_字幕完整显示版.mp4'
sys.stdout.reconfigure(encoding='utf-8')
for d in (P,BUILD,STILLS,OUT):d.mkdir(parents=True,exist_ok=True)
base.P=P;base.BUILD=BUILD;base.STILLS=STILLS;base.OUT=OUT
def load(p):return json.loads(p.read_text(encoding='utf-8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def stamp(sec):
    ms=round(sec*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-show_chapters','-of','json',str(path)]))
def run(args,name):base.run(['ffmpeg','-y','-hide_banner','-loglevel','warning',*args],BUILD/name)

def prepare():
    before=load(ORIGINAL/'timeline.json');t=copy.deepcopy(before);changes=[];allcaps=[]
    for old,s in zip(before['scenes'],t['scenes']):
        for part in s['clips']:
            group=[c for c in s['captions'] if c['part']==part['key']]
            limit=s['questionStart']/30 if part['key'].endswith('-lesson') else s['thinkStart']/30 if part['key'].endswith('-question') else s['durationFrames']/30
            voice_end=part['startFrame']/30+part['duration']
            for i,c in enumerate(group):
                original_end=c['end'];c['end']=group[i+1]['start'] if i+1<len(group) else min(limit,voice_end+.2)
                assert c['end']>=original_end-1e-6 and c['end']>c['start']
                changes.append(dict(scene=s['id'],part=c['part'],start=c['start'],oldEnd=original_end,newEnd=c['end'],text=c['text'],voiceEnd=voice_end,last=i==len(group)-1))
        assert [c['start'] for c in old['captions']]==[c['start'] for c in s['captions']]
        assert [c['text'] for c in old['captions']]==[c['text'] for c in s['captions']]
        allcaps.extend({**c,'start':c['start']+s['startFrame']/30,'end':c['end']+s['startFrame']/30} for c in s['captions'])
    t['captions']=allcaps;save(P/'timeline.json',t);save(BUILD/'end-time-changes.json',changes)
    shutil.copyfile(ORIGINAL/'player_voice.js',P/'player_voice.js')
    for name in ('章节目录.md','完整讲稿.md'):shutil.copyfile(DELIVERY/'统一语速_字幕校准版'/name,OUT/name)
    (OUT/'中文字幕.srt').write_text('\n\n'.join(f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for i,c in enumerate(allcaps,1))+'\n',encoding='utf-8-sig')
    shutil.copyfile(ORIGINAL/'build/chapters.ffmetadata',BUILD/'chapters.ffmetadata')
    (OUT/'调整说明.md').write_text('# 字幕完整显示版\n\n字幕起点、文字、语速、配音、章节及画面布局均沿用上一版。每条字幕保留至下一条字幕出现，每段最后一条覆盖实际配音结束并稍作保留，读题字幕在独立思考开始时让位。字幕保持靠下居中，之前删除的文字保持删除。\n\n音轨直接复制上一版，未重新配音或变速。总时长1小时38分19.4秒。\n\n工程：production/hold_captions.py；时间轴及渲染缓存：production/subtitle_hold/。运行 python production/hold_captions.py 可断点继续。\n',encoding='utf-8')
    return before,t,changes

def caption_at(s,f):return next((c['text'] for c in s['captions'] if c['start']<=f/30<c['end']),'')
def reuse(before,t):
    source=(ROOT/'src/player.js').read_bytes()+(P/'player_voice.js').read_bytes();oldmanifest=load(ORIGINAL/'build/frame-manifest.json');count=0;total=0
    for old,s in zip(before['scenes'],t['scenes']):
        digest=hashlib.sha256(source+json.dumps(s,ensure_ascii=False,sort_keys=True).encode()+str(t['totalFrames']).encode()).hexdigest()
        for f in base.events(s):
            total+=1;dest=STILLS/f"{s['id']}-{f:05}.png";tag=dest.with_suffix('.hash')
            if dest.exists() and tag.exists() and tag.read_text()==digest:count+=1;continue
            cached=ORIGINAL/'stills'/dest.name
            if cached.exists() and cached.with_suffix('.hash').read_text()==oldmanifest[s['id']]['hash'] and caption_at(old,f)==caption_at(s,f):
                shutil.copyfile(cached,dest);tag.write_text(digest);count+=1
    print('REUSED_FRAMES',count,'/',total,flush=True)

async def audit(t,changes):
    from playwright.async_api import async_playwright
    samples=[]
    for s in t['scenes']:
        for c in s['captions']:
            a=math.ceil(c['start']*30-1e-6);b=math.ceil(c['end']*30-1e-6)-1
            assert b>=a
            samples.extend([dict(time=(s['startFrame']+a)/30,text=c['text'],kind='start'),dict(time=(s['startFrame']+b)/30,text=c['text'],kind='lastVisibleFrame')])
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True)
        page=await browser.new_page(viewport=dict(width=1920,height=1080),device_scale_factor=1)
        await page.set_content(base.make_html(t),wait_until='load');await page.evaluate("document.body.classList.add('export')");await page.evaluate('document.fonts.ready')
        for n in range(0,len(samples),100):
            failed=await page.evaluate("jobs=>{let bad=[];for(let j of jobs){let s=window.renderVoicedAt(j.time);let text=[...document.querySelectorAll('#centered-caption text')].map(n=>n.textContent).join('');let issues=window.auditVoicedLayout();if(text!==j.text||issues.length)bad.push({job:j,state:s,text,issues});}return bad}",samples[n:n+100]);assert not failed,failed[:2]
        await browser.close()
    for s in t['scenes']:
        for part in s['clips']:
            group=[c for c in s['captions'] if c['part']==part['key']]
            assert all(abs(a['end']-b['start'])<1e-9 for a,b in zip(group,group[1:]))
            assert group[-1]['end']>=part['startFrame']/30+part['duration']-1e-8
    result=dict(cues=len(t['captions']),startAndEndFramesChecked=len(samples),startsUnchanged=True,textUnchanged=True,noInternalBlankGaps=True,allPartFinalCuesCoverActualAudio=True,layoutPassed=True)
    save(BUILD/'caption-coverage-audit.json',result);print('CAPTION_COVERAGE_PASSED',json.dumps(result),flush=True)

def chapter(ch,t):
    manifest=load(BUILD/'frame-manifest.json');scenes=[s for s in t['scenes'] if s['id'] in ch['sceneIds']]
    digest=hashlib.sha256(json.dumps([manifest[s['id']] for s in scenes],sort_keys=True).encode()+b'caption-hold-v1').hexdigest();tag=BUILD/(ch['id']+'.hash');dest=BUILD/(ch['id']+'.mp4')
    if dest.exists() and tag.exists() and tag.read_text()==digest:return
    rows=[]
    for s in scenes:
        points=manifest[s['id']]['points']
        for i,f in enumerate(points):
            image=STILLS/f"{s['id']}-{f:05}.png";assert image.exists() and image.with_suffix('.hash').read_text()==manifest[s['id']]['hash']
            end=points[i+1] if i+1<len(points) else s['durationFrames']
            rows.extend([f"file '{image.as_posix()}'",'option framerate 30',f'duration {(end-f)/30:.9f}'])
    rows.extend([f"file '{image.as_posix()}'",'option framerate 30']);listing=BUILD/(ch['id']+'.ffconcat');listing.write_text('ffconcat version 1.0\n'+'\n'.join(rows)+'\n',encoding='utf-8')
    run(['-f','concat','-safe','0','-i',str(listing),'-an','-fps_mode','vfr','-enc_time_base','1:30','-t',f"{ch['durationFrames']/30:.9f}",'-c:v','libx264','-preset','fast','-crf','20','-bf','0','-g','30','-pix_fmt','yuv420p','-threads','4','-video_track_timescale','30000','-movflags','+faststart',str(dest)],ch['id']+'.encode.log');tag.write_text(digest);print('CHAPTER_DONE',ch['id'],flush=True)

def encode(t):
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda ch:chapter(ch,t),t['chapters']))
    listing=BUILD/'videos.ffconcat';listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{c['id']}.mp4'\nduration {c['durationFrames']/30:.9f}\n" for c in t['chapters']),encoding='utf-8')
    staged=TARGET.with_name(TARGET.stem+'.rendering.mp4')
    run(['-f','concat','-safe','0','-i',str(listing),'-i',str(SOURCE),'-f','ffmetadata','-i',str(BUILD/'chapters.ffmetadata'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c','copy','-t',f"{t['duration']:.9f}",'-video_track_timescale','30000','-movflags','+faststart',str(staged)],'final-mux.log');staged.replace(TARGET)
    print('FINAL_ENCODED',str(TARGET),flush=True)

def audio_packets(path):
    return subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_packets','-show_data_hash','sha256','-show_entries','packet=pts,dts,duration,size,data_hash','-of','compact',str(path)])

def verify(t,changes):
    info=probe(TARGET);v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
    assert all(abs(float(x)-t['duration'])<.01 for x in (v['duration'],a['duration'],info['format']['duration']))
    assert v['codec_name']=='h264' and (v['width'],v['height'])==(1920,1080) and a['codec_name']=='aac'
    assert len(info['chapters'])==11 and all(abs(float(c['start_time'])-ch['startFrame']/30)<.0011 for c,ch in zip(info['chapters'],t['chapters']))
    assert audio_packets(SOURCE)==audio_packets(TARGET),'Audio or its timestamps changed'
    manifest=load(BUILD/'frame-manifest.json');assert int(v['nb_frames'])==sum(len(s['points']) for s in manifest.values())
    packets=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts_time,duration_time','-of','json',str(TARGET)]))['packets']
    expected=[(s['startFrame']+f)/30 for s in t['scenes'] for f in manifest[s['id']]['points']]
    assert len(packets)==len(expected) and all(abs(float(p['pts_time'])-sec)<.000002 for p,sec in zip(packets,expected))
    assert all(abs(float(p['pts_time'])+float(p['duration_time'])-(expected[i+1] if i+1<len(expected) else t['duration']))<.000002 for i,p in enumerate(packets))
    jobs=[]
    for s in t['scenes']:
        for part in s['clips']:
            part_changes=[c for c in changes if c['part']==part['key'] and c['newEnd']-c['oldEnd']>.08]
            c=max(part_changes,key=lambda c:c['newEnd']-c['oldEnd'])
            frame=min(math.ceil(c['newEnd']*30-1e-6)-1,math.ceil((c['oldEnd']+.07)*30));assert caption_at(s,frame)==c['text']
            jobs.append((part['key'],s,frame,c['text']))
    (BUILD/'final-frames').mkdir(exist_ok=True)
    def sample(job):
        label,s,f,text=job;dest=BUILD/'final-frames'/(label+'.png');sec=(s['startFrame']+f)/30
        points=manifest[s['id']]['points'];source=STILLS/f"{s['id']}-{points[bisect.bisect_right(points,f)-1]:05}.png"
        held=bisect.bisect_right(expected,sec+1e-7)-1;packet=packets[held]
        assert float(packet['pts_time'])<=sec+1e-6 and float(packet['pts_time'])+float(packet['duration_time'])>sec-1e-6
        # Seek to the display state's actual PTS, not into the middle of a VFR
        # hold; some decoders otherwise return the following display state.
        subprocess.run(['ffmpeg','-y','-v','error','-ss',f'{max(0,expected[held]-.00001):.7f}','-i',str(TARGET),'-frames:v','1','-fps_mode','passthrough','-update','1',str(dest)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        with Image.open(dest) as a,Image.open(source) as b:
            delta=sum(ImageStat.Stat(ImageChops.difference(a.convert('RGB'),b.convert('RGB'))).mean)/3
            roi=(96,914,1824,1015);subtitle_delta=sum(ImageStat.Stat(ImageChops.difference(a.crop(roi).convert('RGB'),b.crop(roi).convert('RGB'))).mean)/3
        assert delta<3 and subtitle_delta<3,(label,delta,subtitle_delta)
        return dict(label=label,file=str(dest),text=text,seconds=sec,difference=delta,subtitleDifference=subtitle_delta)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:frames=list(pool.map(sample,jobs))
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
    for off in range(0,len(frames),12):
        sheet=Image.new('RGB',(1920,930),(10,18,30));draw=ImageDraw.Draw(sheet)
        for i,item in enumerate(frames[off:off+12]):
            with Image.open(item['file']) as im:sheet.paste(im.resize((480,270)),((i%4)*480,(i//4)*310))
            draw.text(((i%4)*480+8,(i//4)*310+279),item['label'],font=font,fill='#eef2fa')
        sheet.save(BUILD/f'actual-tails-{off//12:02}.jpg',quality=94)
    print('TAIL_FRAMES_VERIFIED',len(frames),flush=True)
    run(['-xerror','-i',str(TARGET),'-f','null','-'],'decode.log')
    report=dict(duration=t['duration'],subtitles=len(t['captions']),coverage=load(BUILD/'caption-coverage-audit.json'),audioPacketsAndTimesIdentical=True,videoHoldPacketIntervalsChecked=len(packets),actualExtendedTailFramesChecked=len(frames),maxPixelDifference=max(f['difference'] for f in frames),maxSubtitleRegionPixelDifference=max(f['subtitleDifference'] for f in frames),fullDecodePassed=True)
    save(BUILD/'acceptance.json',report)
    (OUT/'检查结果.md').write_text(f"# 检查结果\n\n- 1983条字幕起点和文字完全保留。\n- 3966个字幕起点/最后显示帧检查通过；每段配音内部字幕连续，180段末条字幕均覆盖真实音轨结尾。\n- 实际成片抽查{len(frames)}处原本会提前清屏的位置，字幕均保留。\n- 音轨全部压缩包及时间戳与上一版逐一一致；语速、音质和音画位置不变。\n- 11章节、音视频时长、1080p编码及全片解码检查通过。\n",encoding='utf-8')
    print('HOLD_DONE',json.dumps(report,ensure_ascii=False),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--verify-only',action='store_true');p.add_argument('--encode-only',action='store_true');args=p.parse_args()
    if args.verify_only:verify(load(P/'timeline.json'),load(BUILD/'end-time-changes.json'));return
    before,t,changes=prepare()
    if not args.encode_only:
        reuse(before,t);asyncio.run(audit(t,changes));asyncio.run(base.capture(t))
    encode(t);verify(t,changes)
if __name__=='__main__':main()
