"""Persistent semantic code states driven by the final measured narration."""
import argparse,json,math,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1];FPS=30;DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def stamp(t):
    h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--layout-only',action='store_true');parser.add_argument('--available',action='store_true');a=parser.parse_args()
    course=load(ROOT/'public/course.json');chapters=[];flat=[];jobs=[];cursor=0
    for ci,c in enumerate(course['chapters']):
        start=cursor;scenes=[];visuals=[]
        for si,source in enumerate(c['scenes']):
            path=ROOT/'public/audio'/(source['key']+'.json')
            if a.available and not path.exists():continue
            if a.layout_only:meta=dict(samples=len(source['parts'])*24000,sha256='',parts=[dict(cue=p['text'],onset=i,end=i+1) for i,p in enumerate(source['parts'])])
            else:meta=load(path)
            assert len(source['parts'])==len(meta['parts'])
            speech=math.ceil(meta['samples']/800);lead=12;tail=3;hold=round(source['hold']*30);duration=lead+speech+tail+hold
            onsets=[];cues=[];diagrams=[]
            for p,spoken in zip(source['parts'],meta['parts']):
                assert p['text']==spoken['cue'],('Stale voice metadata',source['key'])
                begin=lead+math.ceil(spoken['onset']*30-1e-6);end=lead+math.ceil(spoken['end']*30-1e-6);onsets.append(begin)
                if p['lines']:cues.append(dict(beginFrame=begin,endFrame=end,lines=p['lines'],cue=p['text'],method='authored-semantic-target/measured-final-PCM-onset'))
                if p.get('visual') is not None:diagrams.append(dict(beginFrame=begin,spec=p['visual'],cue=p['text']))
            result=next((onsets[i] for i,p in enumerate(source['parts']) if p['result']),duration)
            s=dict(**source,chapter=c['title'],chapterIndex=ci+1,sceneIndex=si,sceneCount=len(c['scenes']),startFrame=cursor,durationFrames=duration,speechFrames=speech,leadFrames=lead,sentenceTailFrames=tail,steps=[0,*onsets[1:]],resultFrame=result,audio=f"audio/{source['key']}.wav",audioSha256=meta['sha256'],captions=[],initialCodeLines=source['parts'][0]['lines'],codeCues=cues,diagramCues=diagrams,cueFocus=False)
            points={0,duration-1,*onsets}
            if source['kind']=='question':points.update(lead+speech+tail+n*30 for n in range(4))
            for f in sorted(x for x in points if 0<=x<duration):
                rel=f"stills/{source['key']}-{f:05}.png";jobs.append(dict(frame=cursor+f,path=rel,sceneKey=s['key']));visuals.append(dict(frame=cursor+f-start,path=rel))
            scenes.append(s);flat.append(s);cursor+=duration
        if not scenes:continue
        duration=cursor-start;images=[dict(**v,frames=(visuals[i+1]['frame'] if i+1<len(visuals) else duration)-v['frame']) for i,v in enumerate(visuals)]
        chapters.append(dict(key=c['key'],title=c['title'],startFrame=start,durationFrames=duration,scenes=scenes,images=images,captions=[]))
    scope='layout-only' if a.layout_only else 'incomplete-internal-review' if a.available else 'complete-course'
    t=dict(title=course['title'],language=course['language'],scope=scope,width=1920,height=1080,fps=30,subtitles=False,totalFrames=cursor,duration=cursor/30,chapters=chapters,scenes=flat,renderJobs=jobs,captions=[],audioSettings=load(ROOT/'build/audio-settings.json') if (ROOT/'build/audio-settings.json').exists() else {})
    if scope=='complete-course':
        assert len(chapters)==10 and len(flat)==sum(len(c['scenes']) for c in course['chapters'])
        assert 5400<=t['duration']<=7200,('Revise useful teaching content for the requested duration',t['duration'])
    (ROOT/'public/timeline.json').write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf8')
    if scope=='complete-course':
        DEL.mkdir(parents=True,exist_ok=True);(DEL/'章节目录.txt').write_text('\n'.join(stamp(c['startFrame']/30)+' '+c['title'] for c in chapters)+'\n',encoding='utf8')
        (DEL/'逐题时间目录.txt').write_text('\n'.join(stamp(s['startFrame']/30)+f" 第{s['number']:02}题 {s['exercise']}" for s in flat if s['kind']=='question')+'\n',encoding='utf8')
        rows=[';FFMETADATA1','title=Rust基础58题：习题跟练']
        for c in chapters:rows+=['[CHAPTER]','TIMEBASE=1/30',f"START={c['startFrame']}",f"END={c['startFrame']+c['durationFrames']}",'title='+c['title']]
        (ROOT/'build/chapters.ffmetadata').write_text('\n'.join(rows)+'\n',encoding='utf8')
    print('TIMELINE_READY',scope,stamp(cursor/30),len(flat),'pages',len(jobs),'states',flush=True)
if __name__=='__main__':main()
