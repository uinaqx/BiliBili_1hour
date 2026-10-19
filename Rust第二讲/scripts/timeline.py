import argparse, json, math, pathlib, re, sys
from caption_text import display_caption
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1]; FPS=30
course=json.loads((ROOT/'public'/'course.json').read_text(encoding='utf-8'))
DEL=ROOT/'out'; BUILD=ROOT/'build'; BUILD.mkdir(exist_ok=True); DEL.mkdir(exist_ok=True)
parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);args=parser.parse_args()
def stamp(seconds,sep=','):
    ms=round(seconds*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02}{sep}{ms:03}'
def clock(seconds):
    secs=int(seconds); h,secs=divmod(secs,3600); m,s=divmod(secs,60)
    return f'{h:02}:{m:02}:{s:02}'
def captions(words):
    group=[]; result=[]; last=-1
    def flush():
        if group:
            text=''.join(w['text'] for w in group)
            # Bailian expands the source & symbol to the spoken word "and".
            # Keep the original Rust notation on screen, e.g. &str and &mut self.
            text=re.sub(r'(?<![A-Za-z])and(?![A-Za-z])\s*','&',text)
            result.append({'start':group[0]['begin_time']/1000,'end':group[-1]['end_time']/1000,'text':text})
            group.clear()
    for word in words:
        begin=word['begin_time']/1000; end=word['end_time']/1000
        if begin<last-.02: raise ValueError('Nonmonotonic provider timestamps')
        last=begin
        # The provider attaches punctuation to the NEXT spoken character, e.g. "。我".
        # Move it to the preceding text before choosing clause boundaries.
        text=word['text']; leading=re.match(r'^[，。！？；：、]+',text)
        if leading:
            punctuation=leading.group();text=text[len(punctuation):]
            if group:
                group[-1]['text']+=punctuation
                length=sum(len(w['text']) for w in group)
                if any(p in punctuation for p in '。！？；') or (any(p in punctuation for p in '，：') and length>=8):flush()
            elif result:result[-1]['text']+=punctuation
        if not text:continue
        length=sum(len(w['text']) for w in group)
        if group and (length+len(text)>36 or begin-group[0]['begin_time']/1000>7.2):flush()
        group.append({**word,'text':text})
        if text[-1:] in '。！？；' or (text[-1:] in '，：' and sum(len(w['text']) for w in group)>=8):flush()
    flush()
    return result
flat=[]; chapters=[]; all_captions=[]; jobs=[]; frame=0
last_scene_key=course['chapters'][-1]['scenes'][-1]['key']
for ci,ch in enumerate(course['chapters']):
    if args.limit and len(flat)>=args.limit:break
    start=frame; local_caps=[]; image_events=[]; chapter_scenes=[]
    for si,source in enumerate(ch['scenes']):
        if args.limit and len(flat)>=args.limit:break
        meta=json.loads((ROOT/'public'/'audio'/(source['key']+'.json')).read_text(encoding='utf-8'))
        if not meta['words']: raise ValueError(f"Missing timestamps: {source['key']}")
        speech=math.ceil(meta['duration']*FPS); lead=12
        tail=3 if source['key']!=last_scene_key else 0
        frames=lead+speech+tail+round(source['hold']*FPS)
        # Use speech-time landmarks for the three progressive explanations.
        steps=[0,lead+round(speech*.25),lead+round(speech*.53),lead+round(speech*.78)]
        cues=source.get('stageCues')
        if cues:
            clean=lambda text:re.sub(r'[\s，。！？；：、,.!?;:]', '',text)
            joined=''.join(clean(w['text']) for w in meta['words'])
            for k,cue in enumerate(cues,1):
                position=joined.find(clean(cue))
                if position>=0:
                    cursor=0
                    for w in meta['words']:
                        cursor+=len(clean(w['text']))
                        if cursor>position:
                            steps[k]=lead+round(w['begin_time']/1000*FPS);break
            for k in range(1,4):steps[k]=max(steps[k],steps[k-1]+15)
        panels=[]
        for panel in source.get('panels',[]):
            joined=''.join(re.sub(r'[\s，。！？；：、,.!?;:]','',w['text']) for w in meta['words'])
            position=joined.find(re.sub(r'[\s，。！？；：、,.!?;:]','',panel['cue']))
            if position<0:raise ValueError('Cannot synchronize code panel: '+source['key']+' '+panel['cue'])
            cursor=0
            for w in meta['words']:
                cursor+=len(re.sub(r'[\s，。！？；：、,.!?;:]','',w['text']))
                if cursor>position:panels.append({**panel,'beginFrame':lead+round(w['begin_time']/1000*FPS)});break
        scene={**source,'panels':panels,'chapter':ch['title'],'english':ch['english'],'chapterIndex':ci,'sceneIndex':si,'sceneCount':len(ch['scenes']),'startFrame':frame,'durationFrames':frames,'speechFrames':speech,'leadFrames':lead,'sentenceTailFrames':tail,'steps':steps,'audio':f"audio/{source['key']}.mp3",'captions':captions(meta['words'])}
        flat.append(scene); chapter_scenes.append(scene)
        for cap in scene['captions']:
            cap_global={**cap,'start':cap['start']+(frame+lead)/FPS,'end':cap['end']+(frame+lead)/FPS}
            all_captions.append(cap_global)
            local_caps.append({**cap_global,'start':cap_global['start']-start/FPS,'end':cap_global['end']-start/FPS})
        # Render only changing visual states, reusing stable frames during narration.
        points=set()
        for step in steps:
            points.update(step+n for n in [0,3,6,9,12] if step+n<frames)
        for panel in panels:
            points.update(panel['beginFrame']+n for n in [0,3,6,9,12] if panel['beginFrame']+n<frames)
        if source['kind']=='question':
            pause=lead+speech+tail
            for n in range(round(source['hold'])): points.add(pause+n*FPS)
        ordered=sorted(points)
        for index,p in enumerate(ordered):
            path=f"stills/{source['key']}-{p:05}.png"
            jobs.append({'frame':frame+p,'path':path,'sceneKey':source['key']})
            stop=ordered[index+1] if index+1<len(ordered) else frames
            image_events.append({'path':path,'frames':stop-p})
        frame+=frames
    chapters.append({'key':ch['key'],'title':ch['title'],'english':ch['english'],'startFrame':start,'durationFrames':frame-start,'scenes':chapter_scenes,'captions':local_caps,'images':image_events})
timeline={**{k:v for k,v in course.items() if k!='chapters'},'totalFrames':frame,'duration':frame/FPS,'scenes':flat,'chapters':chapters,'renderJobs':jobs}
(ROOT/'public'/'timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding='utf-8')
srt=[]
for i,c in enumerate(all_captions,1):srt.extend([str(i),stamp(c['start'])+' --> '+stamp(c['end']),display_caption(c['text']),''])
(DEL/'中文字幕.srt').write_text('\n'.join(srt),encoding='utf-8-sig')
chapter_doc=['# Rust 进阶基础：九个主题章节目录',f"\n总时长：{stamp(frame/FPS,'.')}（约 {round(frame/FPS)//60} 分 {round(frame/FPS)%60} 秒）。时间以最终音频实测为准。",'\n| 起点 | 章节 |','|---|---|']
for c in chapters:chapter_doc.append(f"| {clock(c['startFrame']/FPS)} | {c['title']} · {c['english']} |")
(DEL/'章节目录.md').write_text('\n'.join(chapter_doc),encoding='utf-8')
metadata=[';FFMETADATA1','title=Rust 进阶基础：九个主题','artist=中文编程教学','comment=Rust 2024 Edition; nine topics; Chinese AI narration; original practice questions']
for c in chapters:
    metadata.extend(['[CHAPTER]','TIMEBASE=1/30',f"START={c['startFrame']}",f"END={c['startFrame']+c['durationFrames']}",f"title={c['title']} · {c['english']}"])
(BUILD/'chapters.ffmetadata').write_text('\n'.join(metadata)+'\n',encoding='utf-8')
def ass_time(t):
    cs=round(t*100); h,cs=divmod(cs,360000); m,cs=divmod(cs,6000); s,cs=divmod(cs,100)
    return f'{h}:{m:02}:{s:02}.{cs:02}'
header='''[Script Info]
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
for c in chapters:
    events=[f"Dialogue: 0,{ass_time(cap['start'])},{ass_time(cap['end'])},Default,,0,0,0,,{display_caption(cap['text']).replace('{','').replace('}','')}" for cap in c['captions']]
    (BUILD/f"{c['key']}.ass").write_text(header+'\n'.join(events)+'\n',encoding='utf-8-sig')
print(json.dumps({'duration':clock(frame/FPS),'seconds':frame/FPS,'frames':frame,'scenes':len(flat),'visualFrames':len(jobs),'subtitles':len(all_captions)},ensure_ascii=False))
