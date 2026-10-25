"""Final-PCM anchors drive explicit, continuous operations and persistent holds."""
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
    text=''.join(chars);phrase=''.join(phrase.split());at=text.find(phrase);assert at>=0 and text.find(phrase,at+1)<0,('Missing/ambiguous authored anchor',s['key'],index,phrase)
    raw=times[at];added=sum(.1 for p in meta['pauseRefinements'] if p['part']==index and p['acousticSeconds']<=raw)
    return meta['parts'][index]['start']+raw+added
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--layout',action='store_true');a=parser.parse_args();course=load(ROOT/'public/course.json');cursor=0;chapters=[];flat=[];total=0;motion_ticks=0
    for ci,c in enumerate(course['chapters']):
        begin=cursor;scenes=[]
        for si,source in enumerate(c['scenes']):
            if a.layout:
                pos=0;parts=[];thinks=[]
                for i,p in enumerate(source['parts']):
                    parts.append(dict(start=pos,onset=pos,end=pos+12,cue=p['text']));pos+=12
                    if p['think']:thinks.append(dict(part=i,start=pos,seconds=4));pos+=4
                m=dict(samples=pos*24000,sha256='',parts=parts,thinkPauses=thinks)
            else:m=load(ROOT/'public/audio'/(source['key']+'.json'))
            speech=math.ceil(m['samples']/800);lead=12;tail=3;duration=lead+speech+tail+round(source['hold']*30);units=[];points={0,duration-1};keyframes=set(points)
            for i,(p,voiced) in enumerate(zip(source['parts'],m['parts'])):
                assert p['text']==voiced['cue'];start=lead+math.ceil(voiced['onset']*30-1e-6);stop=lead+math.floor(voiced['end']*30);motions=[]
                starts=[start+round(j*5*30) if a.layout else max(start,lead+math.ceil(anchor_seconds(source,i,move['anchor'],m)*30-1e-6)) for j,move in enumerate(p['moves'])]
                previous=0
                for j,move in enumerate(p['moves']):
                    b=min(stop,starts[j]+round(move['seconds']*30),starts[j+1] if j+1<len(starts) else stop)
                    assert b>starts[j],('Motion does not fit actual phrase',source['key'],i,move)
                    motions.append(dict(begin=starts[j],end=b,fromProgress=previous,toProgress=move['target'],anchor=move['anchor'],method='layout-only' if a.layout else 'authored-phrase/Whisper-known-text/final-PCM-pause-map'));previous=move['target']
                    points.update(range(starts[j],b+1));keyframes.update([starts[j],(starts[j]+b)//2,b]);motion_ticks+=b-starts[j]
                units.append(dict(index=i,begin=start,end=stop,motions=motions));points.add(start);keyframes.add(start)
            intervals=[]
            for pause in m.get('thinkPauses',[]):
                b=lead+math.ceil(pause['start']*30);e=b+120;intervals.append(dict(part=pause['part'],begin=b,end=e));points.update([b,b+30,b+60,b+90,e]);keyframes.update([b,b+30,b+60,b+90,e])
            s=dict(**source,chapter=c['title'],chapterIndex=ci+1,sceneIndex=si+1,startFrame=cursor,durationFrames=duration,speechFrames=speech,leadFrames=lead,sentenceTailFrames=tail,audio=f"audio/{source['key']}.wav",audioSha256=m['sha256'],units=units,thinkIntervals=intervals,renderFrames=sorted(f for f in points if 0<=f<duration),qaFrames=sorted(f for f in keyframes if 0<=f<duration))
            cursor+=duration;total+=len(s['renderFrames']);scenes.append(s);flat.append(s)
        chapters.append(dict(key=c['key'],title=c['title'],startFrame=begin,durationFrames=cursor-begin,scenes=scenes))
    t=dict(title=course['title'],scope='layout-only' if a.layout else 'complete-course',totalFrames=cursor,duration=cursor/30,fps=30,width=1920,height=1080,subtitles=False,chapters=chapters,scenes=flat,renderedFrames=total,continuousMotionSeconds=motion_ticks/30)
    if not a.layout:
        assert 780<=t['duration']<=1080,('Duration sanity check only; never adjust speech to hit a target',t['duration'])
        settings=load(ROOT/'build/audio-settings.json');assert settings['wholeCourseTempo']==1.0 and settings['automaticTempoAdjustment'] is False
        t['speechTempo']=1.0;t['automaticTempoAdjustment']=False
    (ROOT/'public/timeline.json').write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf8')
    if not a.layout:
        DEL.mkdir(exist_ok=True);(DEL/'章节目录.txt').write_text('\n'.join(stamp(c['startFrame']/30)+' '+c['title'] for c in chapters)+'\n',encoding='utf8');(DEL/'逐页目录.txt').write_text('\n'.join(stamp(s['startFrame']/30)+' '+s['title'] for s in flat)+'\n',encoding='utf8')
        rows=[';FFMETADATA1','title=15分钟讲清Agent Harness底层原理']
        for c in chapters:rows+=['[CHAPTER]','TIMEBASE=1/30',f"START={c['startFrame']}",f"END={c['startFrame']+c['durationFrames']}",'title='+c['title']]
        (ROOT/'build/chapters.ffmetadata').write_text('\n'.join(rows)+'\n',encoding='utf8')
    print('TIMELINE_READY',t['scope'],stamp(t['duration']),total,'states',round(motion_ticks/30,2),'motion seconds',flush=True)
if __name__=='__main__':main()
