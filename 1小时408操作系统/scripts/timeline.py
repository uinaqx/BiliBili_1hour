"""Final original-speed PCM drives authored formula states and continuous geometry."""
import argparse,json,math,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def stamp(t):
    h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def anchor_seconds(s,index,phrase,meta):
    aligned=load(ROOT/'build/alignment'/(s['key']+f'-p{index:02}.json'));chars=[];times=[]
    for word in aligned['words']:
        for ch in word['text']:
            if not ch.isspace():chars.append(ch);times.append(word['begin_time']/1000)
    text=''.join(chars).lower();phrase=''.join(phrase.split()).lower();at=text.find(phrase);assert at>=0 and text.find(phrase,at+1)<0,('Missing or ambiguous authored anchor',s['key'],index,phrase)
    raw=times[at];added=sum(.1 for p in meta['pauseRefinements'] if p['part']==index and p['acousticSeconds']<=raw)
    return meta['parts'][index]['start']+raw+added
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--layout',action='store_true');a=parser.parse_args();course=load(ROOT/'public/course.json');cursor=0;chapters=[];flat=[];total=0;motion_ticks=0
    for ci,c in enumerate(course['chapters']):
        begin=cursor;scenes=[]
        for si,source in enumerate(c['scenes']):
            m=dict(samples=len(source['parts'])*10*24000,sha256='',parts=[dict(start=i*10,onset=i*10,end=(i+1)*10,cue=p['text']) for i,p in enumerate(source['parts'])]) if a.layout else load(ROOT/'public/audio'/(source['key']+'.json'))
            speech=math.ceil(m['samples']/800);lead=12;tail=3;duration=lead+speech+tail+round(source['hold']*30);units=[];points={0,duration-1};keyframes=set(points)
            for i,(p,voiced) in enumerate(zip(source['parts'],m['parts'])):
                assert p['text']==voiced['cue'];start=lead+math.ceil(voiced['onset']*30-1e-6);stop=lead+math.floor(voiced['end']*30);motions=[];progress=0
                starts=[start+j*max(1,(stop-start)//len(p['moves'])) if a.layout else max(start,lead+math.ceil(anchor_seconds(source,i,move['anchor'],m)*30-1e-6)) for j,move in enumerate(p['moves'])]
                for j,move in enumerate(p['moves']):
                    at=starts[j];end=min(stop,at+round(move['seconds']*30),starts[j+1] if j+1<len(starts) else stop);assert end>at
                    motions.append(dict(begin=at,end=end,fromProgress=progress,toProgress=move['target'],anchor=move['anchor'],method='layout-only' if a.layout else 'authored-phrase/known-transcript/final-original-speed-PCM'));progress=move['target'];points.update(range(at,end+1));keyframes.update([at,(at+end)//2,end]);motion_ticks+=end-at
                units.append(dict(index=i,begin=start,end=stop,motions=motions));points.add(start);keyframes.add(start)
            if source['kind']=='question':
                pause=lead+speech+tail;points.update(pause+j*30 for j in range(4));keyframes.update(pause+j*30 for j in range(4))
            s=dict(**source,chapter=c['title'],chapterIndex=ci+1,sceneIndex=si+1,startFrame=cursor,durationFrames=duration,speechFrames=speech,leadFrames=lead,sentenceTailFrames=tail,audio=f"audio/{source['key']}.wav",audioSha256=m['sha256'],units=units,thinkIntervals=[],renderFrames=sorted(f for f in points if 0<=f<duration),qaFrames=sorted(f for f in keyframes if 0<=f<duration))
            cursor+=duration;total+=len(s['renderFrames']);scenes.append(s);flat.append(s)
        chapters.append(dict(key=c['key'],title=c['title'],startFrame=begin,durationFrames=cursor-begin,scenes=scenes))
    t=dict(title=course['title'],scope='layout-only' if a.layout else 'complete-course',totalFrames=cursor,duration=cursor/30,fps=30,width=1920,height=1080,subtitles=False,speechTempo=1.0,synthesisRate=1.05,automaticTempoAdjustment=False,chapters=chapters,scenes=flat,renderedFrames=total,continuousMotionSeconds=motion_ticks/30)
    if not a.layout:
        settings=load(ROOT/'build/audio-settings.json');assert settings['wholeCourseTempo']==1.0 and settings['automaticTempoAdjustment'] is False
        assert 3000<=t['duration']<=4200,('Revise useful content, never speech speed, for about one hour',t['duration'])
    (ROOT/'public/timeline.json').write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf8')
    if not a.layout:
        DEL.mkdir(exist_ok=True);(DEL/'章节目录.txt').write_text('\n'.join(stamp(c['startFrame']/30)+' '+c['title'] for c in chapters)+'\n',encoding='utf8');(DEL/'逐页知识点目录.txt').write_text('\n'.join(stamp(s['startFrame']/30)+' '+s['title'] for s in flat)+'\n',encoding='utf8')
        rows=[';FFMETADATA1','title=一小时学完408操作系统：基础考点与解题步骤']
        for c in chapters:rows+=['[CHAPTER]','TIMEBASE=1/30',f"START={c['startFrame']}",f"END={c['startFrame']+c['durationFrames']}",'title='+c['title']]
        (ROOT/'build/chapters.ffmetadata').write_text('\n'.join(rows)+'\n',encoding='utf8')
    print('TIMELINE_READY',t['scope'],stamp(t['duration']),total,'events;',round(motion_ticks/30,2),'motion seconds',flush=True)
if __name__=='__main__':main()
