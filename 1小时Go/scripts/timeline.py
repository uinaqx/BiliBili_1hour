import argparse,json,math,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];FPS=30
def stamp(t):
    h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--internal-chapters',type=int);parser.add_argument('--layout-only',action='store_true',help='Synthetic positions for visual layout review only; never export');args=parser.parse_args()
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));chapters=[];flat=[];jobs=[];cursor=0
    if args.internal_chapters:
        assert 1<=args.internal_chapters<10
        course['chapters']=course['chapters'][:args.internal_chapters]
    for ci,c in enumerate(course['chapters']):
        start=cursor;scenes=[];visuals=[]
        for si,source in enumerate(c['scenes']):
            if args.layout_only:
                meta=dict(samples=len(source['parts'])*24000,sha256='',parts=[dict(cue=p['text'],onset=i,end=i+1,lines=p['lines'],result=p['result']) for i,p in enumerate(source['parts'])])
            else:meta=json.loads((ROOT/'public/audio'/(source['key']+'.json')).read_text(encoding='utf8'))
            speech=math.ceil(meta['samples']/800);lead=12;tail=3;hold=round(source['hold']*30);frames=lead+speech+tail+hold
            assert len(meta['parts'])==len(source['parts']),('Narration units changed',source['key'])
            for p,authored in zip(meta['parts'],source['parts']):
                assert p['cue']==authored['text'],('Narration changed; revoice and realign',source['key'])
                p.update(lines=authored['lines'],result=authored['result'])
            cues=[dict(beginFrame=lead+math.ceil(p['onset']*30-1e-6),endFrame=lead+math.ceil(p['end']*30-1e-6),lines=p['lines'],cue=p['cue'],method='authored-semantic-unit/measured-final-audio') for p in meta['parts'] if p['lines']]
            onsets=[lead+math.ceil(p['onset']*30-1e-6) for p in meta['parts']]
            second=onsets[min(1,len(onsets)-1)];steps=[0,second,second,second]
            result=next((lead+math.ceil(p['onset']*30-1e-6) for p in meta['parts'] if p['result']),frames)
            s=dict(**source,chapter=c['title'],english='',chapterIndex=ci+1,sceneIndex=si,sceneCount=len(c['scenes']),startFrame=cursor,durationFrames=frames,speechFrames=speech,leadFrames=lead,sentenceTailFrames=tail,steps=steps,resultFrame=result,audio=f"audio/{source['key']}.wav",audioSha256=meta['sha256'],captions=[],initialCodeLines=source['parts'][0]['lines'],codeCues=cues,diagramCues=[],cueFocus=False)
            points={0,frames-1,*onsets,*steps}
            if result<frames:points.add(result)
            if s['kind']=='question':points.update(lead+speech+tail+n*30 for n in range(4))
            for f in sorted(x for x in points if 0<=x<frames):
                rel=f"stills/{s['key']}-{f:05}.png";job=dict(frame=cursor+f,path=rel,sceneKey=s['key']);jobs.append(job);visuals.append(dict(frame=cursor+f-start,path=rel))
            cursor+=frames;scenes.append(s);flat.append(s)
        duration=cursor-start;images=[dict(**v,frames=(visuals[i+1]['frame'] if i+1<len(visuals) else duration)-v['frame']) for i,v in enumerate(visuals)]
        chapters.append(dict(key=c['key'],title=c['title'],english='',startFrame=start,durationFrames=duration,scenes=scenes,images=images,captions=[]))
    timeline=dict(title=course['title'],language=course['language'],totalFrames=cursor,duration=cursor/30,fps=30,width=1920,height=1080,subtitles=False,scenes=flat,chapters=chapters,renderJobs=jobs,captions=[],audioSettings=json.loads((ROOT/'build/audio-settings.json').read_text(encoding='utf8')))
    timeline['scope']='layout-only' if args.layout_only else 'incomplete-internal-review' if args.internal_chapters else 'complete-course'
    if not args.internal_chapters and not args.layout_only:assert len(chapters)==10 and 3300<=timeline['duration']<=3900,timeline['duration']
    (ROOT/'public/timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding='utf8')
    if args.internal_chapters or args.layout_only:
        print('INTERNAL_TIMELINE_ONLY',len(chapters),stamp(cursor/30),len(jobs),flush=True);return
    lines=[stamp(c['startFrame']/30)+' '+c['title'] for c in chapters];delivery=ROOT/'out'
    (delivery/'章节目录.txt').write_text('\n'.join(lines)+'\n',encoding='utf8')
    metadata=[';FFMETADATA1','title=一小时学习 Go：零基础入门']
    for c in chapters:metadata.extend(['[CHAPTER]','TIMEBASE=1/30',f"START={c['startFrame']}",f"END={c['startFrame']+c['durationFrames']}",'title='+c['title']])
    (ROOT/'build/chapters.ffmetadata').write_text('\n'.join(metadata)+'\n',encoding='utf8');print('TIMELINE_DONE',stamp(cursor/30),len(jobs),'visual states',flush=True)
if __name__=='__main__':main()
