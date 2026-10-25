"""Measured audio anchors drive persistent diagram states and 30fps motion intervals."""
import argparse,hashlib,json,math,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'content'))
from actions import PLANS
FPS=30
def read(p):return json.loads(p.read_text(encoding='utf8'))
def stamp(t):
    h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def anchor_seconds(scene,index,anchor,meta):
    aligned=read(ROOT/'build/alignment'/(scene['key']+f'-p{index:02}.json'))
    chars=[];times=[]
    for word in aligned['words']:
        for ch in word['text']:
            if ch.isspace():continue
            chars.append(ch);times.append(word['begin_time']/1000)
    text=''.join(chars);phrase=''.join(anchor.split());at=text.find(phrase)
    assert at>=0 and text.find(phrase,at+1)<0,('Missing or ambiguous authored anchor',scene['key'],index,anchor)
    raw=times[at];added=sum(.1 for x in meta['pauseRefinements'] if x['part']==index and x['acousticSeconds']<=raw)
    return meta['parts'][index]['start']+raw+added
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--layout',action='store_true');args=parser.parse_args()
    course=read(ROOT/'public/course.json');cursor=0;chapters=[];scenes=[];total=0
    for ci,c in enumerate(course['chapters']):
        begin=cursor;local=[]
        for si,source in enumerate(c['scenes']):
            if args.layout:
                meta=dict(samples=len(source['parts'])*8*24000,parts=[dict(onset=i*8,start=i*8,end=(i+1)*8) for i in range(len(source['parts']))],sha256='')
            else:meta=read(ROOT/'public/audio'/(source['key']+'.json'))
            speech=math.ceil(meta['samples']/800);lead=12;tail=3;hold=round(source['hold']*30);duration=lead+speech+tail+hold
            units=[];points={0,duration-1};keyframes=set(points)
            for index,(p,audio) in enumerate(zip(source['parts'],meta['parts'])):
                if not args.layout:assert p['text']==audio['cue']
                start=lead+math.ceil(audio['onset']*FPS-1e-6);stop=lead+math.floor(audio['end']*FPS);motions=[]
                visual=p['visual'];static=(visual['kind']=='matrix' and visual.get('operation') not in ['add','power','adjugate']) or (visual['kind']=='rank' and visual.get('phase') in ['columns','pivots','question','canonical']) or (visual['kind']=='basis' and visual.get('phase')=='orthogonal') or (visual['kind']=='vectors' and visual.get('phase') in ['static','independent','target'])
                if p['motion']>0 and not static:
                    plans=PLANS.get((source['key'],index))
                    if plans and not args.layout:
                        previous=0
                        starts=[max(start,lead+math.ceil(anchor_seconds(source,index,x[0],meta)*FPS-1e-6)) for x in plans]
                        for mi,(anchor,target,seconds) in enumerate(plans):
                            a=starts[mi];b=min(stop,a+round(seconds*FPS))
                            if mi+1<len(starts):b=min(b,starts[mi+1])
                            assert b>a and (not motions or a>=motions[-1]['end']),('Overlapping diagram operations',source['key'],index,anchor)
                            motions.append(dict(begin=a,end=b,fromProgress=previous,toProgress=target,anchor=anchor,method='authored-phrase/known-text-acoustic-alignment'));previous=target
                    else:motions=[dict(begin=start,end=min(stop,start+round(p['motion']*FPS)),fromProgress=0,toProgress=1,anchor=p['text'][:30],method='measured-unit-onset' if not args.layout else 'layout-only')]
                unit=dict(index=index,begin=start,end=stop,motions=motions)
                units.append(unit);points.add(start);keyframes.add(start)
                for m in motions:
                    points.update(range(m['begin'],m['end']+1));keyframes.update([m['begin'],(m['begin']+m['end'])//2,m['end']])
            if source['kind']=='question':
                pts=[lead+speech+tail+n*FPS for n in range(4)];points.update(pts);keyframes.update(pts)
            frames=sorted(x for x in points if 0<=x<duration)
            s=dict(**source,chapter=c['title'],chapterIndex=ci+1,sceneIndex=si+1,startFrame=cursor,durationFrames=duration,speechFrames=speech,leadFrames=lead,sentenceTailFrames=tail,audio=f"audio/{source['key']}.wav",audioSha256=meta['sha256'],units=units,renderFrames=frames,qaFrames=sorted(keyframes))
            total+=len(frames);cursor+=duration;local.append(s);scenes.append(s)
        chapters.append(dict(key=c['key'],title=c['title'],startFrame=begin,durationFrames=cursor-begin,scenes=local))
    d=dict(title=course['title'],scope='layout-only' if args.layout else 'complete-course',totalFrames=cursor,duration=cursor/FPS,fps=FPS,width=1920,height=1080,subtitles=False,chapters=chapters,scenes=scenes,renderedFrames=total)
    if not args.layout:assert 3300<=d['duration']<=4020,('Revise useful content for target duration',d['duration'])
    (ROOT/'public/timeline.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
    if not args.layout:
        out=ROOT/'out';(out/'章节目录.txt').write_text('\n'.join(stamp(c['startFrame']/FPS)+' '+c['title'] for c in chapters)+'\n',encoding='utf8')
        rows=[';FFMETADATA1','title=一小时学习线性代数：动态可视化']
        for c in chapters:rows+=['[CHAPTER]','TIMEBASE=1/30',f"START={c['startFrame']}",f"END={c['startFrame']+c['durationFrames']}",'title='+c['title']]
        (ROOT/'build/chapters.ffmetadata').write_text('\n'.join(rows)+'\n',encoding='utf8')
    print('TIMELINE_READY',d['scope'],stamp(d['duration']),total,'rendered states',flush=True)
if __name__=='__main__':main()
