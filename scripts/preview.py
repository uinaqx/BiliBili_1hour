"""Generate an estimated, silent Studio timeline without any TTS calls."""
import json, pathlib, re
ROOT=pathlib.Path(__file__).resolve().parents[1]
course=json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'))
scenes=[];chapters=[];jobs=[];frame=0
for ci,c in enumerate(course['chapters']):
    start=frame;local=[];caps=[];images=[]
    weight=sum(len(s['narration']) for s in c['scenes'])
    for si,s in enumerate(c['scenes']):
        duration=max(180,round(c['targetMinutes']*1800*len(s['narration'])/weight))
        lead=12;hold=round(s['hold']*30);speech=duration-lead-hold
        steps=[0]+[lead+round(speech*x) for x in (.25,.53,.78)]
        parts=[p.strip() for p in re.split(r'(?<=[。！？；])',s['narration']) if p.strip()]
        parts=[p[i:i+36] for p in parts for i in range(0,len(p),36)]
        caption=[];cursor=0;total=sum(map(len,parts))
        for p in parts:
            caption.append({'start':speech/30*cursor/total,'end':speech/30*(cursor+len(p))/total,'text':p})
            cursor+=len(p)
        panels=[{**p,'beginFrame':steps[min(i+2,3)]} for i,p in enumerate(s.get('panels',[]))]
        row={**s,'panels':panels,'chapter':c['title'],'english':c['english'],'chapterIndex':ci,'sceneIndex':si,'sceneCount':len(c['scenes']),'startFrame':frame,'durationFrames':duration,'speechFrames':speech,'leadFrames':lead,'steps':steps,'audio':'','captions':caption}
        local.append(row);scenes.append(row)
        for cap in caption:caps.append({**cap,'start':cap['start']+(frame-start+lead)/30,'end':cap['end']+(frame-start+lead)/30})
        points=sorted({p for step in steps for p in (step,step+3,step+6,step+9,step+12)}|{p['beginFrame'] for p in panels})
        for i,p in enumerate(points):
            path=f'stills/{s["key"]}-{p:05}.png'
            jobs.append({'frame':frame+p,'path':path,'sceneKey':s['key']})
            images.append({'path':path,'frames':(points[i+1] if i+1<len(points) else duration)-p})
        frame+=duration
    chapters.append({**c,'scenes':local,'startFrame':start,'durationFrames':frame-start,'captions':caps,'images':images})
timeline={**course,'audioAvailable':False,'previewOnly':True,'timing':'estimated-no-audio','totalFrames':frame,'duration':frame/30,'scenes':scenes,'chapters':chapters,'renderJobs':jobs}
(ROOT/'public/timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'build').mkdir(exist_ok=True)
print('Silent Studio preview ready. Timing is estimated, not the final audio timeline.')
