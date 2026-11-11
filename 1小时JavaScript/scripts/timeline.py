import argparse,hashlib,json,math,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out';FPS=30
def load(p):return json.loads(p.read_text(encoding='utf8'))
def stamp(t):
    h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def main():
    p=argparse.ArgumentParser();p.add_argument('--partial',action='store_true');args=p.parse_args();course=load(ROOT/'public/course.json');chapters=[];flat=[];cursor=0
    for ch in course['chapters']:
        begin=cursor;scenes=[]
        for source in ch['scenes']:
            path=ROOT/'public/audio'/(source['key']+'.json')
            if not path.exists():
                if args.partial:break
                raise RuntimeError('Missing final scene audio '+source['key'])
            m=load(path);assert all(a['text']==b['cue'] for a,b in zip(source['parts'],m['parts']))
            lead=12;frames=lead+math.ceil(m['samples']/800)+18
            starts=[0]+[lead+math.ceil(v['onset']*30-1e-6) for v in m['parts'][1:]]
            think=[dict(start=lead+round(x['start']*30),end=lead+round(x['end']*30)) for x in m['thinkIntervals']]
            events={0,frames-1,*starts}
            for x in think:events.update(range(x['start'],x['end']+1,30))
            s=dict(source,chapter=ch['title'],chapterKey=ch['key'],startFrame=cursor,durationFrames=frames,leadFrames=lead,audio='audio/'+source['key']+'.wav',audioSha256=m['sha256'],partFrames=starts,thinkFrames=think,renderFrames=sorted(events))
            flat.append(s);scenes.append(s);cursor+=frames
        if scenes:chapters.append(dict(key=ch['key'],title=ch['title'],startFrame=begin,durationFrames=cursor-begin,scenes=scenes))
        if len(scenes)<len(ch['scenes']):break
    scope='partial-review' if args.partial else 'complete'
    t=dict(title=course['title'],fps=30,scope=scope,totalFrames=cursor,duration=cursor/30,subtitles=True,synthesisRate=1.05,speechTempo=1.0,scenes=flat,chapters=chapters)
    from highlight_sync import apply_highlights
    t=apply_highlights(ROOT,t)
    (ROOT/'public/timeline.json').write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf8')
    DEL.mkdir(parents=True,exist_ok=True)
    if not args.partial:
        (DEL/'章节目录.txt').write_text('\n'.join(stamp(c['startFrame']/30)+' '+c['title'] for c in chapters)+'\n',encoding='utf8')
        (DEL/'逐页目录.txt').write_text('\n'.join(stamp(s['startFrame']/30)+' '+s['title'] for s in flat)+'\n',encoding='utf8')
    rows=[';FFMETADATA1','title=一小时学完JavaScript']
    for c in chapters:rows+=['[CHAPTER]','TIMEBASE=1/30',f"START={c['startFrame']}",f"END={c['startFrame']+c['durationFrames']}",'title='+c['title']]
    (ROOT/'build/chapters.ffmetadata').write_text('\n'.join(rows)+'\n',encoding='utf8')
    print('TIMELINE',scope,stamp(t['duration']),len(flat),flush=True)
if __name__=='__main__':main()
