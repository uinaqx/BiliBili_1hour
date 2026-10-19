"""Render centered subtitles and clean headings; accelerate original master 1.21x."""
import argparse,asyncio,concurrent.futures,hashlib,json,math,pathlib,re,subprocess,sys
from fractions import Fraction
from PIL import Image,ImageChops,ImageDraw,ImageFont,ImageStat
import video as base
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1];ORIGINAL=ROOT/'production'
REV=ORIGINAL/'revision_121';BUILD=REV/'build';STILLS=REV/'stills'
SOURCE=ROOT/'out'
OUT=SOURCE/'字幕居中_1.21倍版';TARGET=OUT/'计算机组成原理_字幕居中加速版.mp4'
SPEED=Fraction(121,100);FPS=30
for p in (REV,BUILD,STILLS,OUT):p.mkdir(parents=True,exist_ok=True)
T=json.loads((ORIGINAL/'timeline.json').read_text(encoding='utf-8'))
base.P=REV;base.BUILD=BUILD;base.STILLS=STILLS;base.OUT=OUT

def overlay():
    text=(ORIGINAL/'player_voice.js').read_text(encoding='utf-8')
    old="svg.querySelectorAll('text').forEach(n=>{if(n.textContent==='静音学习版')n.textContent='中文配音版';});"
    new="svg.querySelectorAll('text').forEach(n=>{if(n.textContent==='静音学习版'||n.textContent==='中文配音版'){const r=n.previousElementSibling;if(r&&r.tagName==='rect'&&Number(r.getAttribute('x'))===1510&&Number(r.getAttribute('y'))===110)r.remove();n.remove();}});"
    assert old in text;text=text.replace(old,new)
    old="rect(1330,230,500,625,'#121f32',C.line)+text(1360,280,answered?'自测答案与要点':q?'独立思考':'本镜头要点',27,C.muted)"
    assert old in text;text=text.replace(old,"rect(1330,230,500,625,'#121f32',C.line)")
    text=text.replace('let y=338;items.forEach','let y=300;items.forEach')
    text=text.replace('text(122,916,phase,22','text(122,905,phase,18')
    old="if(caption)footer+=lines(122,966,caption,45,36,C.ink,1.24);"
    new="if(caption)footer+='<g id=\"centered-caption\">'+wrap(caption,43).map((line,i)=>text(960,950+i*44,line,36,C.ink,'middle')).join('')+'</g>';"
    assert old in text;text=text.replace(old,new)
    text=text.replace("text(122,969,'先把结果写下来，再看答案。',34,C.gold)","text(960,950,'先把结果写下来，再看答案。',34,C.gold,'middle')")
    text=text.replace("formatTime(frame/30)+' / '+formatTime(VOICED.displayFrames/30)","formatTime(frame/30/1.21)+' / '+formatTime(VOICED.displayFrames/30/1.21)")
    # Visible captions are centered by text-anchor, and the removed headings
    # must not survive in any lesson, question or answer screen.
    text=text.replace(' return bad;'," for(const n of svg.querySelectorAll('text')){if(['本镜头要点','中文配音版','静音学习版'].includes(n.textContent))bad.push({kind:'removed-label',text:n.textContent});}\n for(const n of svg.querySelectorAll('#centered-caption text')){const b=n.getBBox();if(n.getAttribute('text-anchor')!=='middle'||Number(n.getAttribute('x'))!==960||Math.abs(b.x+b.width/2-960)>2||b.y<900||b.y+b.height>1018)bad.push({kind:'caption-center',text:n.textContent,box:[b.x,b.y,b.width,b.height]});}\n return bad;")
    (REV/'player_voice.js').write_text(text,encoding='utf-8')

def run(args,name):
    with (BUILD/name).open('w',encoding='utf-8') as f:r=subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','warning',*args],stdout=f,stderr=subprocess.STDOUT)
    if r.returncode:raise RuntimeError((BUILD/name).read_text(encoding='utf-8',errors='replace')[-3000:])
def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-show_chapters','-of','json',str(path)]))
def clock(ms):
    h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
def srt_ms(s):
    h,m,s,ms=map(int,re.split('[:,]',s));return ((h*60+m)*60+s)*1000+ms

async def audit_captions():
    from playwright.async_api import async_playwright
    html=base.make_html(T);maximum=0;count=0
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True)
        page=await browser.new_page(viewport=dict(width=1920,height=1080),device_scale_factor=1)
        await page.set_content(html,wait_until='load');await page.evaluate("document.body.classList.add('export')");await page.evaluate('document.fonts.ready')
        for cap in T['captions']:
            frame=math.ceil(cap['start']*30-1e-6)
            if frame/30>=cap['end']:raise ValueError('Caption has no display frame')
            state=await page.evaluate('(t)=>window.renderVoicedAt(t)',frame/30)
            result=await page.evaluate("()=>({issues:window.auditVoicedLayout(),lines:[...document.querySelectorAll('#centered-caption text')].map(n=>{let b=n.getBBox();return {center:b.x+b.width/2,y:b.y,height:b.height}})})")
            assert not result['issues'],(state,result)
            assert result['lines'],cap
            maximum=max(maximum,max(abs(n['center']-960) for n in result['lines']));count+=1
        await browser.close()
    report=dict(captionsChecked=count,maxHorizontalCenterErrorPx=maximum,removedLabelsAbsent=True,captionBaselineY=950)
    (BUILD/'caption-centering.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('ALL_CAPTIONS_CENTERED',json.dumps(report),flush=True)

def chapter(ch):
    manifest=json.loads((BUILD/'frame-manifest.json').read_text());rows=[]
    scenes=[s for s in T['scenes'] if s['id'] in ch['sceneIds']]
    digest=hashlib.sha256(json.dumps([manifest[s['id']] for s in scenes],sort_keys=True).encode()+b'centered-v1-bf0').hexdigest()
    tag=BUILD/(ch['id']+'.encodehash');target=BUILD/(ch['id']+'.mp4')
    if target.exists() and tag.exists() and tag.read_text()==digest:print('CHAPTER_CACHED '+ch['id'],flush=True);return
    for s in scenes:
        points=manifest[s['id']]['points']
        for i,f in enumerate(points):
            image=STILLS/f"{s['id']}-{f:05}.png"
            assert image.exists() and image.with_suffix('.hash').read_text()==manifest[s['id']]['hash']
            end=points[i+1] if i+1<len(points) else s['durationFrames']
            rows.extend([f"file '{image.as_posix()}'",'option framerate 30',f'duration {(end-f)/30:.9f}'])
    rows.extend([f"file '{image.as_posix()}'",'option framerate 30'])
    listing=BUILD/(ch['id']+'.ffconcat');listing.write_text('ffconcat version 1.0\n'+'\n'.join(rows)+'\n',encoding='utf-8')
    run(['-f','concat','-safe','0','-i',str(listing),'-an','-fps_mode','vfr','-enc_time_base','1:30','-t',f"{ch['durationFrames']/30:.9f}",'-c:v','libx264','-preset','fast','-crf','20','-bf','0','-g','30','-pix_fmt','yuv420p','-threads','4','-video_track_timescale','30000','-movflags','+faststart',str(target)],ch['id']+'.encode.log')
    tag.write_text(digest);print('CHAPTER_DONE '+ch['id'],flush=True)

def encode():
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(chapter,T['chapters']))
    listing=BUILD/'videos.ffconcat';listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{c['id']}.mp4'\nduration {c['durationFrames']/30:.9f}\n" for c in T['chapters']),encoding='utf-8')
    retimed=BUILD/'video-121.mp4'
    run(['-f','concat','-safe','0','-i',str(listing),'-map','0:v:0','-map_metadata','-1','-map_chapters','-1','-c:v','copy','-bsf:v','setts=ts=TS:duration=DURATION:time_base=1/36300','-video_track_timescale','36300','-movflags','+faststart',str(retimed)],'video-retime.log')
    duration=Fraction(7200)/SPEED
    assert abs(float(probe(retimed)['format']['duration'])-float(duration))<.01
    meta=[';FFMETADATA1','title=计算机组成原理：字幕居中加速版','artist=中文计算机课程','comment=1.21x original speed; centered subtitles; clean headings; pitch-preserved narration']
    for ch in T['chapters']:
        meta.extend(['[CHAPTER]','TIMEBASE=1/36300',f"START={ch['startFrame']*1000}",f"END={(ch['startFrame']+ch['durationFrames'])*1000}",'title='+ch['title']])
    metadata=BUILD/'chapters.ffmetadata';metadata.write_text('\n'.join(meta)+'\n',encoding='utf-8')
    staged=TARGET.with_name(TARGET.stem+'.rendering.mp4')
    run(['-i',str(retimed),'-i',str(SOURCE/'两小时学习计算机组成原理.mp4'),'-f','ffmetadata','-i',str(metadata),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-af','atempo=1.21,asetpts=N/SR/TB,apad','-t',f'{float(duration):.9f}','-c:a','aac','-b:a','128k','-ar','48000','-ac','1','-video_track_timescale','36300','-movflags','+faststart',str(staged)],'audio-mux.log')
    staged.replace(TARGET);print('FINAL_ENCODED '+str(TARGET),flush=True)

def documents():
    pattern=r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})'
    srt=(SOURCE/'中文字幕.srt').read_text(encoding='utf-8-sig')
    srt=re.sub(pattern,lambda m:clock(round(Fraction(srt_ms(m[1]))/SPEED))+' --> '+clock(round(Fraction(srt_ms(m[2]))/SPEED)),srt)
    (OUT/'中文字幕.srt').write_text(srt,encoding='utf-8-sig')
    rows=['# 计算机组成原理：字幕居中加速版章节目录','',f'在上一版基础上再加速 1.10 倍，累计为原片 1.21 倍。总时长约 {clock(round(Fraction(7200000)/SPEED))}。','', '| 起点 | 章节 |','|---|---|']
    rows.extend(f"| {clock(round(Fraction(c['startFrame']*1000,30)/SPEED)).split(',')[0]} | {c['title']} |" for c in T['chapters'])
    (OUT/'章节目录.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    script=(SOURCE/'完整讲稿.md').read_text(encoding='utf-8')
    def heading(m):
        h,minutes,s=map(int,m[2].split(':'));return m[1]+clock(round(Fraction((h*3600+minutes*60+s)*1000)/SPEED)).split(',')[0]
    script=re.sub(r'(?m)^(#{2,3} )(\d{2}:\d{2}:\d{2})',heading,script).replace('读题结束后 6 秒无新旁白','读题结束后约 4.96 秒无新旁白')
    (OUT/'完整讲稿.md').write_text(script,encoding='utf-8')
    (OUT/'调整说明.md').write_text('# 字幕居中加速版\n\n- 在上一版基础上再加速 1.10 倍，累计为原两小时版的 1.21 倍，约 1 小时 39 分 10 秒。配音保持音调。\n- 去掉右侧“本镜头要点”等栏标题及“中文配音版”文字和外框。\n- 中文字幕在画面下方居中，所有字幕按同样比例加速，章节导航和讲稿时间同步更新。\n- 沿用原工程的关键状态切换与保持方式；1080p，H.264/AAC，VFR。原两小时版和上一个加速版保留。\n',encoding='utf-8')

def sample(job):
    label,scene,local=job;frame=scene['startFrame']+local;when=float(Fraction(frame,30)/SPEED)
    dest=BUILD/'final-frames'/(label+'.png')
    subprocess.run(['ffmpeg','-y','-v','error','-ss',f'{max(0,when-.00001):.7f}','-i',str(TARGET),'-frames:v','1','-fps_mode','passthrough','-update','1',str(dest)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,check=True)
    with Image.open(dest) as a,Image.open(STILLS/f"{scene['id']}-{local:05}.png") as b:delta=sum(ImageStat.Stat(ImageChops.difference(a.convert('RGB'),b.convert('RGB'))).mean)/3
    return dict(label=label,frame=frame,seconds=when,meanPixelDifference=delta,file=dest.name)

def verify():
    info=probe(TARGET);v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio');duration=float(Fraction(7200)/SPEED)
    assert max(abs(float(x)-duration) for x in (v['duration'],a['duration'],info['format']['duration']))<.01
    assert v['codec_name']=='h264' and (v['width'],v['height'])==(1920,1080) and a['codec_name']=='aac'
    assert int(v['nb_frames'])==sum(len(x['points']) for x in json.loads((BUILD/'frame-manifest.json').read_text()).values())
    assert len(info['chapters'])==11 and all(abs(float(c['start_time'])-float(Fraction(ch['startFrame'],30)/SPEED))<.0011 and c['tags']['title']==ch['title'] for c,ch in zip(info['chapters'],T['chapters']))
    assert (OUT/'中文字幕.srt').read_text(encoding='utf-8-sig').count(' --> ')==2014
    audit=json.loads((BUILD/'caption-centering.json').read_text(encoding='utf-8'));qa=json.loads((BUILD/'qa-layout.json').read_text(encoding='utf-8'))
    assert audit['captionsChecked']==2014 and audit['maxHorizontalCenterErrorPx']<=2 and len(qa)==180 and all(not x['issues'] for x in qa)
    jobs=[];manifest=json.loads((BUILD/'frame-manifest.json').read_text())
    for s in T['scenes']:
        jobs.extend([(s['id']+'-think',s,s['thinkStart']+90),(s['id']+'-answer',s,s['answerStart'])])
    for ch in T['chapters']:
        group=[s for s in T['scenes'] if s['id'] in ch['sceneIds']];middle=group[len(group)//2];points=manifest[middle['id']]['points']
        jobs.extend([(ch['id']+'-start',group[0],0),(ch['id']+'-middle',middle,points[len(points)//2]),(ch['id']+'-end',group[-1],group[-1]['durationFrames']-1)])
    (BUILD/'final-frames').mkdir(exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:frames=list(pool.map(sample,jobs))
    assert all(f['meanPixelDifference']<3 for f in frames),max(f['meanPixelDifference'] for f in frames)
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
    for off in range(0,len(frames),12):
        sheet=Image.new('RGB',(1920,930),(10,18,30));draw=ImageDraw.Draw(sheet)
        for i,item in enumerate(frames[off:off+12]):
            with Image.open(BUILD/'final-frames'/item['file']) as im:sheet.paste(im.resize((480,270)),((i%4)*480,(i//4)*310))
            draw.text(((i%4)*480+8,(i//4)*310+279),item['label'],font=font,fill='#eef2fa')
        sheet.save(BUILD/f'actual-sheet-{off//12:02}.jpg',quality=94)
    print('FULL_DECODE_START',flush=True)
    with (BUILD/'decode.log').open('w',encoding='utf-8') as f:result=subprocess.run(['ffmpeg','-hide_banner','-nostats','-xerror','-i',str(TARGET),'-af','volumedetect','-f','null','-'],stdout=f,stderr=subprocess.STDOUT)
    assert result.returncode==0
    log=(BUILD/'decode.log').read_text(encoding='utf-8',errors='replace');assert not re.search(r'corrupt decoded|Error while|Invalid data|non.monoton',log,re.I)
    report=dict(speedFromOriginal=1.21,speedFromPrevious=1.1,duration=info['format']['duration'],videoFrames=int(v['nb_frames']),chapters=11,subtitles=2014,captionCenterAudit=audit,actualFramesChecked=len(frames),maxPixelDifference=max(f['meanPixelDifference'] for f in frames),fullDecodePassed=True)
    (BUILD/'acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'检查结果.md').write_text(f"# 检查结果\n\n累计原片 1.21 倍速，时长 {clock(round(Fraction(7200000)/SPEED))}。\n\n- 2014 条字幕全部检查，靠下居中，横向中心偏差最大 {audit['maxHorizontalCenterErrorPx']:.3f}px。\n- 60 分镜的讲解、思考、答案画面共 180 帧检查，已删除指定文字和音色角标。\n- 实际成片抽查 {len(frames)} 帧，最大平均像素差 {report['maxPixelDifference']:.3f}/255。\n- 11 个章节及字幕时间同步；音视频时长一致，全片严格解码通过。\n",encoding='utf-8')
    print('REVISION_DONE',json.dumps(report,ensure_ascii=False),flush=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--qa',action='store_true');parser.add_argument('--encode-only',action='store_true');args=parser.parse_args();overlay()
    if args.qa:
        asyncio.run(base.capture(T,qa=True));asyncio.run(audit_captions());return
    if not args.encode_only:asyncio.run(base.capture(T))
    encode();documents();verify()
if __name__=='__main__':main()
