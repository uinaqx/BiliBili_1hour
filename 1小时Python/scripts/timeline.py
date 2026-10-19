"""Sample-based scene timeline. This edition deliberately has no captions."""
import json,math,pathlib,sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out';FPS=30
def stamp(seconds):
    h,s=divmod(int(seconds),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def main():
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'));flat=[];chapters=[];jobs=[];cursor=0
    last=course['chapters'][-1]['scenes'][-1]['key']
    for ci,ch in enumerate(course['chapters']):
        chapter_start=cursor;scenes=[];visuals=[]
        for si,source in enumerate(ch['scenes']):
            meta=json.loads((ROOT/'public/audio'/(source['key']+'.json')).read_text(encoding='utf-8'))
            speech=math.ceil(meta['samples']/800);lead=12;tail=3 if source['key']!=last else 0;hold=round(source['hold']*FPS);frames=lead+speech+tail+hold
            steps=[0,lead+round(speech*.25),lead+round(speech*.53),lead+round(speech*.78)]
            s=dict(**source,chapter=ch['title'],english=ch['english'],chapterIndex=ci,sceneIndex=si,sceneCount=len(ch['scenes']),startFrame=cursor,durationFrames=frames,speechFrames=speech,leadFrames=lead,sentenceTailFrames=tail,steps=steps,audio=f"audio/{source['key']}.wav",captions=[])
            flat.append(s);scenes.append(s);points={0,frames-1}
            for step in steps:points.update(step+n for n in (0,3,6,9,12) if step+n<frames)
            if source['kind']=='question':points.update(lead+speech+tail+n*FPS for n in range(round(source['hold'])))
            for f in sorted(points):
                path=f"stills/{source['key']}-{f:05}.png";jobs.append(dict(frame=cursor+f,path=path,sceneKey=source['key']));visuals.append(dict(frame=cursor+f-chapter_start,path=path))
            cursor+=frames
        duration=cursor-chapter_start
        images=[dict(path=v['path'],frames=(visuals[i+1]['frame'] if i+1<len(visuals) else duration)-v['frame'],frame=v['frame']) for i,v in enumerate(visuals)]
        chapters.append(dict(key=ch['key'],title=ch['title'],english=ch['english'],startFrame=chapter_start,durationFrames=duration,scenes=scenes,captions=[],images=images))
    settings=json.loads((BUILD/'audio-settings.json').read_text(encoding='utf-8'))
    timeline=dict(title=course['title'],language=course['language'],totalFrames=cursor,duration=cursor/FPS,fps=FPS,width=1920,height=1080,subtitles=False,scenes=flat,chapters=chapters,captions=[],renderJobs=jobs,audioSettings=settings)
    assert len(chapters)==13 and 3000<=timeline['duration']<=4200
    (ROOT/'public/timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding='utf-8')
    rows=['# 一小时学习 Python：零基础章节目录','',f"总时长：{stamp(cursor/FPS)}.{round(cursor%FPS/FPS*1000):03}。Python 3.11，中文旁白，无字幕。",'','| 起点 | 章节 |','|---|---|']
    metadata=[';FFMETADATA1','title=一小时学习Python：零基础入门','artist=中文编程教学','comment=Python 3.11 beginner course; no subtitles; original verified examples']
    for c in chapters:
        rows.append(f"| {stamp(c['startFrame']/FPS)} | {c['title']} · {c['english']} |")
        metadata.extend(['[CHAPTER]','TIMEBASE=1/30',f"START={c['startFrame']}",f"END={c['startFrame']+c['durationFrames']}",'title='+c['title']+' · '+c['english']])
    (DEL/'章节目录.md').write_text('\n'.join(rows)+'\n',encoding='utf-8');(BUILD/'chapters.ffmetadata').write_text('\n'.join(metadata)+'\n',encoding='utf-8')
    print('TIMELINE_READY',json.dumps(dict(seconds=cursor/FPS,scenes=len(flat),captions=0,remotionFrames=len(jobs)),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
