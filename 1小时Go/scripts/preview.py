"""Silent editing preview only: estimated timing, no credentials or online calls."""
import json,math,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    for name in ['public','build','out']:(ROOT/name).mkdir(parents=True,exist_ok=True)
    subprocess.run([sys.executable,str(ROOT/'scripts/build_course.py')],check=True)
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))
    chapters=[];scenes=[];jobs=[];cursor=0
    for ci,c in enumerate(course['chapters']):
        begin=cursor;local=[];images=[]
        for si,source in enumerate(c['scenes']):
            elapsed=0;units=[]
            for p in source['parts']:
                frames=max(60,math.ceil(len(p['text'])/4.1*30))
                units.append(dict(beginFrame=12+elapsed,endFrame=12+elapsed+frames,lines=sorted(set(p['lines'])),cue=p['text'],method='estimated-editing-preview-only'))
                elapsed+=frames
            lead=12;tail=3;hold=round(source['hold']*30);duration=lead+elapsed+tail+hold
            onsets=[u['beginFrame'] for u in units];second=onsets[min(1,len(onsets)-1)]
            result=next((u['beginFrame'] for u,p in zip(units,source['parts']) if p['result']),duration)
            s=dict(**source,chapter=c['title'],english='',chapterIndex=ci+1,sceneIndex=si,sceneCount=len(c['scenes']),startFrame=cursor,durationFrames=duration,speechFrames=elapsed,leadFrames=lead,sentenceTailFrames=tail,steps=[0,second,second,second],resultFrame=result,audio='',audioSha256='',captions=[],initialCodeLines=sorted(set(source['parts'][0]['lines'])),codeCues=[u for u in units if u['lines']],diagramCues=[],cueFocus=False)
            points={0,duration-1,*onsets}
            if result<duration:points.add(result)
            if s['kind']=='question':points.update(lead+elapsed+tail+n*30 for n in range(4))
            for f in sorted(points):
                rel=f"stills/{s['key']}-{f:05}.png";jobs.append(dict(frame=cursor+f,path=rel,sceneKey=s['key']));images.append(dict(frame=cursor+f-begin,path=rel))
            cursor+=duration;local.append(s);scenes.append(s)
        frames=cursor-begin
        images=[dict(**v,frames=(images[i+1]['frame'] if i+1<len(images) else frames)-v['frame']) for i,v in enumerate(images)]
        chapters.append(dict(key=c['key'],title=c['title'],english='',startFrame=begin,durationFrames=frames,scenes=local,images=images,captions=[]))
    t=dict(title=course['title'],language=course['language'],audioAvailable=False,previewOnly=True,scope='layout-only',timing='estimated-no-audio',totalFrames=cursor,duration=cursor/30,fps=30,width=1920,height=1080,subtitles=False,scenes=scenes,chapters=chapters,renderJobs=jobs,captions=[],audioSettings={})
    (ROOT/'public/timeline.json').write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf8')
    print('SILENT_EDITING_PREVIEW_READY',len(scenes),'pages; no TTS request; estimated positions are not final speech timings')
if __name__=='__main__':main()
