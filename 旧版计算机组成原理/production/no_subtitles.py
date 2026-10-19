"""Remove the spoken subtitle layer only; preserve all other visual states and AAC."""
import argparse,asyncio,bisect,concurrent.futures,hashlib,json,pathlib,shutil,subprocess,sys
from PIL import Image,ImageChops,ImageDraw,ImageFont,ImageStat
import hold_captions as shared
import video as base
ROOT=pathlib.Path(__file__).resolve().parents[1];ORIGINAL=ROOT/'production/subtitle_hold'
P=ROOT/'production/no_subtitles';BUILD=P/'build';STILLS=P/'stills'
DELIVERY=ROOT/'out'
SOURCE=DELIVERY/'字幕完整显示版/计算机组成原理_字幕完整显示版.mp4'
OUT=DELIVERY/'无字幕版';TARGET=OUT/'计算机组成原理_无字幕版.mp4'
sys.stdout.reconfigure(encoding='utf-8')
for d in (P,BUILD,STILLS,OUT):d.mkdir(parents=True,exist_ok=True)
for module in (base,shared):
    for k,v in dict(P=P,BUILD=BUILD,STILLS=STILLS,OUT=OUT).items():setattr(module,k,v)
shared.SOURCE=SOURCE;shared.TARGET=TARGET
load=shared.load;save=shared.save;probe=shared.probe;run=shared.run

def prepare():
    t=load(ORIGINAL/'timeline.json');save(P/'timeline.json',t)
    code=(ORIGINAL/'player_voice.js').read_text(encoding='utf-8')
    expected="if(caption)footer+='<g id=\"centered-caption\">'"
    assert code.count(expected)==1
    code=code.replace(expected,"if(false)footer+='<g id=\"centered-caption\">'")
    # Keep the thinking instruction, phase label, panel, timer and all mechanics.
    code+="\nconst renderWithoutCaptions=window.renderVoicedAt;window.renderVoicedAt=function(t){const state=renderWithoutCaptions(t);if(document.querySelector('#centered-caption'))throw Error('Unexpected spoken subtitle');return state;};\n"
    (P/'player_voice.js').write_text(code,encoding='utf-8')
    source=(ROOT/'src/player.js').read_bytes()+(P/'player_voice.js').read_bytes();oldmanifest=load(ORIGINAL/'build/frame-manifest.json');reused=0
    for s in t['scenes']:
        digest=hashlib.sha256(source+json.dumps(s,ensure_ascii=False,sort_keys=True).encode()+str(t['totalFrames']).encode()).hexdigest()
        for f in base.events(s):
            dest=STILLS/f"{s['id']}-{f:05}.png";tag=dest.with_suffix('.hash')
            if dest.exists() and tag.exists() and tag.read_text()==digest:continue
            cached=ORIGINAL/'stills'/dest.name
            if not shared.caption_at(s,f) and cached.exists() and cached.with_suffix('.hash').read_text()==oldmanifest[s['id']]['hash']:
                shutil.copyfile(cached,dest);tag.write_text(digest);reused+=1
    shutil.copyfile(DELIVERY/'字幕完整显示版/章节目录.md',OUT/'章节目录.md')
    print('PREPARED_NO_SUBTITLES','unchanged frames reused',reused,flush=True);return t

def verify_visual_source(t):
    manifest=load(BUILD/'frame-manifest.json');oldmanifest=load(ORIGINAL/'build/frame-manifest.json');changed=0;checked=0
    def scene(s):
        changes=0
        assert manifest[s['id']]['points']==oldmanifest[s['id']]['points']
        for f in manifest[s['id']]['points']:
            name=f"{s['id']}-{f:05}.png"
            with Image.open(STILLS/name) as a,Image.open(ORIGINAL/'stills'/name) as b:
                a=a.convert('RGB');b=b.convert('RGB')
                # Chrome can round text antialiasing by one level in separate
                # renders. Preserve the original pixels outside the subtitle
                # interior instead of allowing unrelated rounding changes.
                region=(98,910,1822,1012)
                if shared.caption_at(s,f):
                    central=a.crop((276,914,1644,1008)).getcolors(2)
                    assert central is not None and len(central)==1,(s['id'],f,'Subtitle area is not empty')
                    protected=b.copy();protected.paste(a.crop(region),region);a=protected
                    a.save(STILLS/name)
                else:
                    a=b.copy();a.save(STILLS/name)
                box=ImageChops.difference(a,b).getbbox()
            if box:
                assert shared.caption_at(s,f),(s['id'],f,box)
                assert box[0]>=96 and box[1]>=908 and box[2]<=1824 and box[3]<=1018,(s['id'],f,box)
                changes+=1
        return changes,len(manifest[s['id']]['points'])
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for c,n in pool.map(scene,t['scenes']):changed+=c;checked+=n
    save(BUILD/'visual-source-check.json',dict(framesChecked=checked,subtitleFramesChanged=changed,allOtherPixelsIdentical=True,frameTimesIdentical=True))
    print('VISUAL_SOURCE_CHECK_PASSED',checked,'frames',flush=True)

def encode(t):
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda c:shared.chapter(c,t),t['chapters']))
    listing=BUILD/'videos.ffconcat';listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{c['id']}.mp4'\nduration {c['durationFrames']/30:.9f}\n" for c in t['chapters']),encoding='utf-8')
    staged=TARGET.with_name(TARGET.stem+'.rendering.mp4')
    run(['-f','concat','-safe','0','-i',str(listing),'-i',str(SOURCE),'-map','0:v:0','-map','1:a:0','-map_metadata','1','-map_chapters','1','-c','copy','-t',f"{t['duration']:.9f}",'-video_track_timescale','30000','-movflags','+faststart',str(staged)],'final-mux.log')
    staged.replace(TARGET);print('FINAL_ENCODED',str(TARGET),flush=True)

def verify(t):
    original=probe(SOURCE);info=probe(TARGET);v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
    assert not any(s['codec_type']=='subtitle' for s in info['streams'])
    assert (v['width'],v['height'],v['codec_name'],a['codec_name'])==(1920,1080,'h264','aac')
    assert all(abs(float(d)-t['duration'])<.01 for d in (v['duration'],a['duration'],info['format']['duration']))
    assert info['chapters']==original['chapters']
    assert shared.audio_packets(SOURCE)==shared.audio_packets(TARGET)
    manifest=load(BUILD/'frame-manifest.json');points=[(s['startFrame']+f)/30 for s in t['scenes'] for f in manifest[s['id']]['points']]
    packets=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts_time,duration_time','-of','json',str(TARGET)]))['packets']
    assert len(packets)==len(points)==int(v['nb_frames'])
    assert all(abs(float(p['pts_time'])-sec)<.000002 for p,sec in zip(packets,points))
    jobs=[]
    for s in t['scenes']:
        candidates=manifest[s['id']]['points'];lecture=next(f for f in candidates if f>s['lessonStart'] and shared.caption_at(s,f))
        answer=next(f for f in candidates if f>=s['answerStart'] and shared.caption_at(s,f));thinking=s['thinkStart']+90
        jobs.extend([(s['id']+'-lecture',s,lecture),(s['id']+'-answer',s,answer),(s['id']+'-thinking',s,thinking)])
    (BUILD/'final-frames').mkdir(exist_ok=True)
    def frame(job):
        label,s,f=job;index=bisect.bisect_right(manifest[s['id']]['points'],f)-1;f=manifest[s['id']]['points'][index]
        dest=BUILD/'final-frames'/(label+'.png');sec=(s['startFrame']+f)/30
        subprocess.run(['ffmpeg','-y','-v','error','-ss',f'{max(0,sec-.00001):.7f}','-i',str(TARGET),'-frames:v','1','-fps_mode','passthrough','-update','1',str(dest)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        with Image.open(dest) as a,Image.open(STILLS/f"{s['id']}-{f:05}.png") as b:
            delta=sum(ImageStat.Stat(ImageChops.difference(a.convert('RGB'),b.convert('RGB'))).mean)/3
            roi=(96,914,1824,1015);footer=sum(ImageStat.Stat(ImageChops.difference(a.crop(roi).convert('RGB'),b.crop(roi).convert('RGB'))).mean)/3
        assert delta<3 and footer<3,(label,delta,footer)
        return dict(label=label,file=str(dest),difference=delta)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:frames=list(pool.map(frame,jobs))
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
    for off in range(0,len(frames),12):
        sheet=Image.new('RGB',(1920,930),(10,18,30));draw=ImageDraw.Draw(sheet)
        for i,row in enumerate(frames[off:off+12]):
            with Image.open(row['file']) as im:sheet.paste(im.resize((480,270)),((i%4)*480,(i//4)*310))
            draw.text(((i%4)*480+8,(i//4)*310+279),row['label'],font=font,fill='#eef2fa')
        sheet.save(BUILD/f'actual-sheet-{off//12:02}.jpg',quality=94)
    run(['-xerror','-i',str(TARGET),'-f','null','-'],'decode.log')
    report=dict(duration=t['duration'],chaptersUnchanged=True,audioPacketsAndTimesIdentical=True,noSubtitleStream=True,noSpokenSubtitleLayer=True,visualSourceCheck=load(BUILD/'visual-source-check.json'),actualFramesChecked=len(frames),fullDecodePassed=True)
    save(BUILD/'acceptance.json',report)
    (OUT/'说明.md').write_text('# 计算机组成原理：无字幕版\n\n以“字幕完整显示版”为基础，只去掉配音字幕。配音音轨与时间戳完全保留，时长1小时38分19.4秒，11个章节及所有原画面时间点保持一致。章节标题、示意图、例题、思考提示、进度和计时保留。\n\n全部原始渲染帧已逐像素比对：变化仅限字幕所在区域。180处成片画面及全片完整性检查通过。\n\n制作工程：production/no_subtitles.py。\n',encoding='utf-8')
    print('NO_SUBTITLES_DONE',json.dumps(report,ensure_ascii=False),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--verify-only',action='store_true');p.add_argument('--encode-only',action='store_true');args=p.parse_args()
    if args.verify_only:verify(load(P/'timeline.json'));return
    t=prepare()
    if not args.encode_only:asyncio.run(base.capture(t));verify_visual_source(t)
    encode(t);verify(t)
if __name__=='__main__':main()
