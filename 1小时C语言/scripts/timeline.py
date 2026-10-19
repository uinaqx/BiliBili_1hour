"""One sample-based narration timeline; subtitle transitions quantized to frame boundaries."""
import bisect,copy,json,math,pathlib,sys,re
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];FPS=30;DEL=ROOT/'out';BUILD=ROOT/'build'
course=json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'))
def stamp(seconds,sep=','):
    ms=round(seconds*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02}{sep}{ms:03}'
def ass_time(frame):
    # Leave a 1ms guard before quantizing to ASS centiseconds. Filter timestamp
    # rounding must not keep an expired cue alive for a long held VFR frame.
    cs=max(0,(frame*1000//30-1)//10);h,cs=divmod(cs,360000);m,cs=divmod(cs,6000);s,cs=divmod(cs,100);return f'{h}:{m:02}:{s:02}.{cs:02}'
def main():
    flat=[];chapters=[];jobs=[];allcaps=[];cursor=0;last=course['chapters'][-1]['scenes'][-1]['key']
    for ci,ch in enumerate(course['chapters']):
        chapter_start=cursor;scenes=[];caps=[];visuals=[]
        for si,source in enumerate(ch['scenes']):
            meta=json.loads((ROOT/'public/audio'/(source['key']+'.json')).read_text(encoding='utf-8'))
            speech=math.ceil(meta['samples']/800);lead=12;tail=3 if source['key']!=last else 0;hold=round(source['hold']*FPS);frames=lead+speech+tail+hold
            steps=[0,lead+round(speech*.25),lead+round(speech*.53),lead+round(speech*.78)]
            localcaps=copy.deepcopy(meta['captions'])
            for cap in localcaps:cap['text']=re.sub(r'(?<![A-Za-z_])null(?![A-Za-z_])','NULL',cap['text'],flags=re.I)
            # Hold the last spoken line throughout the reading interval; on a
            # question, clear it when the four-second thinking interval begins.
            localcaps[-1]['end']=(speech+tail+(0 if source['kind']=='question' else hold))/FPS
            s=dict(**source,chapter=ch['title'],english=ch['english'],chapterIndex=ci,sceneIndex=si,sceneCount=len(ch['scenes']),startFrame=cursor,durationFrames=frames,speechFrames=speech,leadFrames=lead,sentenceTailFrames=tail,steps=steps,audio=f"audio/{source['key']}.wav",captions=localcaps)
            flat.append(s);scenes.append(s)
            for cap in localcaps:
                a=cursor+lead+math.ceil(cap['start']*FPS-1e-6);b=cursor+lead+math.ceil(cap['end']*FPS-1e-6)
                assert b>a
                c=dict(start=a/FPS,end=b/FPS,text=cap['text'],startFrame=a,endFrame=b,scene=s['key'])
                allcaps.append(c);caps.append({**c,'startFrame':a-chapter_start,'endFrame':b-chapter_start,'start':(a-chapter_start)/FPS,'end':(b-chapter_start)/FPS})
            points={0,frames-1}
            for step in steps:points.update(step+n for n in (0,3,6,9,12) if step+n<frames)
            if source['kind']=='question':points.update(lead+speech+tail+n*FPS for n in range(round(source['hold'])))
            for f in sorted(points):
                path=f"stills/{source['key']}-{f:05}.png";jobs.append(dict(frame=cursor+f,path=path,sceneKey=source['key']));visuals.append(dict(frame=cursor+f-chapter_start,path=path))
            cursor+=frames
        duration=cursor-chapter_start;points={v['frame'] for v in visuals};points.update(c['startFrame'] for c in caps);points.update(c['endFrame'] for c in caps)
        points=sorted(f for f in points if 0<=f<duration);visual_frames=[v['frame'] for v in visuals];images=[]
        for i,f in enumerate(points):
            end=points[i+1] if i+1<len(points) else duration
            images.append(dict(path=visuals[bisect.bisect_right(visual_frames,f)-1]['path'],frames=end-f,frame=f))
        chapters.append(dict(key=ch['key'],title=ch['title'],english=ch['english'],startFrame=chapter_start,durationFrames=duration,scenes=scenes,captions=caps,images=images))
    settings=json.loads((BUILD/'audio-settings.json').read_text(encoding='utf-8'))
    timeline=dict(title=course['title'],language=course['language'],totalFrames=cursor,duration=cursor/FPS,fps=30,width=1920,height=1080,scenes=flat,chapters=chapters,captions=allcaps,renderJobs=jobs,audioSettings=settings)
    assert len(chapters)==12 and 3000<=timeline['duration']<=4200
    assert all(a['endFrame']<=b['startFrame'] for a,b in zip(allcaps,allcaps[1:]))
    (ROOT/'public/timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding='utf-8')
    (DEL/'中文字幕.srt').write_text('\n\n'.join(f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for i,c in enumerate(allcaps,1))+'\n',encoding='utf-8-sig')
    rows=['# 一小时学习C语言：章节目录','',f"总时长：{stamp(cursor/FPS,'.')}，C11 示例。",'','| 起点 | 章节 |','|---|---|']
    meta=[';FFMETADATA1','title=一小时学习C语言','artist=中文编程教学','comment=C11 absolute beginner course; original examples; uniform narration tempo; acoustic subtitles']
    for c in chapters:
        rows.append(f"| {stamp(c['startFrame']/FPS).split(',')[0]} | {c['title']} · {c['english']} |")
        meta.extend(['[CHAPTER]','TIMEBASE=1/30',f"START={c['startFrame']}",f"END={c['startFrame']+c['durationFrames']}",'title='+c['title']+' · '+c['english']])
    (DEL/'章节目录.md').write_text('\n'.join(rows)+'\n',encoding='utf-8');(BUILD/'chapters.ffmetadata').write_text('\n'.join(meta)+'\n',encoding='utf-8')
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
        events=[f"Dialogue: 0,{ass_time(x['startFrame'])},{ass_time(x['endFrame'])},Default,,0,0,0,,{x['text'].replace('{','').replace('}','')}" for x in c['captions']]
        (BUILD/(c['key']+'.ass')).write_text(header+'\n'.join(events)+'\n',encoding='utf-8-sig')
    print('TIMELINE_READY',json.dumps(dict(seconds=cursor/FPS,scenes=len(flat),captions=len(allcaps),remotionFrames=len(jobs),encodedDisplayStates=sum(len(c['images']) for c in chapters)),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
