"""Build a silent editing timeline without credentials, audio or network calls."""
import json,pathlib,sys
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1]
course=json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'));flat=[];chapters=[];jobs=[];cursor=0
for ci,c in enumerate(course['chapters']):
    start=cursor;local=[];images=[]
    for si,s in enumerate(c['scenes']):
        speech=max(180,round(len(s['narration'])/4.1*30));lead=12;tail=3;hold=round(s['hold']*30);duration=lead+speech+tail+hold
        if s.get('beats'):
            total=sum(len(x) for x in s['beats']);count=0;steps=[0]
            for beat in s['beats'][:-1]:count+=len(beat);steps.append(lead+round(speech*count/total))
        else:steps=[0,lead+round(speech*.25),lead+round(speech*.53),lead+round(speech*.78)]
        panels=[{**p,'beginFrame':steps[min(i+2,3)]} for i,p in enumerate(s.get('panels',[]))]
        row={**s,'panels':panels,'chapter':c['title'],'english':c['english'],'chapterIndex':ci,'sceneIndex':si,'sceneCount':len(c['scenes']),'startFrame':cursor,'durationFrames':duration,'speechFrames':speech,'leadFrames':lead,'sentenceTailFrames':tail,'steps':steps,'audio':'','captions':[]}
        flat.append(row);local.append(row);points={0,duration-1}
        for step in steps:points.update(step+n for n in (0,3,6,9,12) if step+n<duration)
        points.update(p['beginFrame'] for p in panels)
        if s['kind']=='question':points.update(lead+speech+tail+n*30 for n in range(round(s['hold'])))
        points=sorted(points)
        for i,f in enumerate(points):
            path=f'stills/{s["key"]}-{f:05}.png';jobs.append(dict(frame=cursor+f,path=path,sceneKey=s['key']));images.append(dict(path=path,frame=cursor+f-start,frames=(points[i+1] if i+1<len(points) else duration)-f))
        cursor+=duration
    chapters.append(dict(key=c['key'],title=c['title'],english=c['english'],startFrame=start,durationFrames=cursor-start,scenes=local,captions=[],images=images))
timeline=dict(title=course['title'],language=course.get('language',''),audioAvailable=False,previewOnly=True,timing='estimated-no-audio',fps=30,width=1920,height=1080,totalFrames=cursor,duration=cursor/30,scenes=flat,chapters=chapters,captions=[],renderJobs=jobs)
(ROOT/'build').mkdir(exist_ok=True);(ROOT/'public/timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding='utf-8')
print('SILENT_EDITING_PREVIEW_READY',len(flat),'scenes; no TTS request; not a final audio timeline')
