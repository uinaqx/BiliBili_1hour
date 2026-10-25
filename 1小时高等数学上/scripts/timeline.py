import argparse,json,math,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def stamp(t):
    h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--layout',action='store_true');a=parser.parse_args();course=read(ROOT/'public/course.json');cursor=0;chapters=[];flat=[];total=0
    for ci,c in enumerate(course['chapters']):
        begin=cursor;scenes=[]
        for si,source in enumerate(c['scenes']):
            m=dict(samples=len(source['parts'])*8*24000,sha256='',parts=[dict(onset=i*8,end=(i+1)*8,cue=p['text']) for i,p in enumerate(source['parts'])]) if a.layout else read(ROOT/'public/audio'/(source['key']+'.json'))
            speech=math.ceil(m['samples']/800);lead=12;tail=3;duration=lead+speech+tail+round(source['hold']*30);units=[];points={0,duration-1}
            for i,(p,voice) in enumerate(zip(source['parts'],m['parts'])):
                assert p['text']==voice['cue'];onset=lead+math.ceil(voice['onset']*30-1e-6);units.append(dict(index=i,begin=onset,end=lead+math.ceil(voice['end']*30)));points.add(onset)
            if source['kind']=='question':points.update(lead+speech+tail+i*30 for i in range(4))
            s=dict(**source,chapter=c['title'],chapterIndex=ci+1,sceneIndex=si+1,startFrame=cursor,durationFrames=duration,speechFrames=speech,leadFrames=lead,sentenceTailFrames=tail,audio=f"audio/{source['key']}.wav",audioSha256=m['sha256'],units=units,renderFrames=sorted(points))
            scenes.append(s);flat.append(s);cursor+=duration;total+=len(points)
        chapters.append(dict(key=c['key'],title=c['title'],startFrame=begin,durationFrames=cursor-begin,scenes=scenes))
    d=dict(title=course['title'],scope='layout-only' if a.layout else 'complete-course',totalFrames=cursor,duration=cursor/30,fps=30,width=1920,height=1080,subtitles=False,chapters=chapters,scenes=flat,renderedFrames=total)
    if not a.layout:assert 3480<=d['duration']<=3780,('Revise content or natural tempo for one hour',d['duration'])
    (ROOT/'public/timeline.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
    if not a.layout:
        DEL.mkdir(exist_ok=True);(DEL/'章节目录.txt').write_text('\n'.join(stamp(c['startFrame']/30)+' '+c['title'] for c in chapters)+'\n',encoding='utf8')
        (DEL/'逐页知识点目录.txt').write_text('\n'.join(stamp(s['startFrame']/30)+' '+s['title'] for s in flat)+'\n',encoding='utf8')
        rows=[';FFMETADATA1','title=一小时学完高等数学（上）：期末基础题型']
        for c in chapters:rows+=['[CHAPTER]','TIMEBASE=1/30',f"START={c['startFrame']}",f"END={c['startFrame']+c['durationFrames']}",'title='+c['title']]
        (ROOT/'build/chapters.ffmetadata').write_text('\n'.join(rows)+'\n',encoding='utf8')
    print('TIMELINE_READY',d['scope'],stamp(d['duration']),total,'states',flush=True)
if __name__=='__main__':main()
