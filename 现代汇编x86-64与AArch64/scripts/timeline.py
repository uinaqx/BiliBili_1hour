"""Editorial reading timeline. Explicitly has no audio-derived or TTS timing."""
import json,math,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def stamp(t):
 h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def main():
 course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));traces=json.loads((ROOT/'build/execution-data.json').read_text(encoding='utf8'));chapters=[];flat=[];cursor=0
 for c in course['chapters']:
  begin=cursor;pages=[]
  for source in c['scenes']:
   parts=[];frames={0};local=0;prior=0
   for i,p in enumerate(source['parts']):
    weight=len(re.findall('[\u4e00-\u9fff]',p['text']))+len(re.findall('[A-Za-z0-9]',p['text']))*.65
    duration=round(max(22 if source['kind']=='lesson' else 15,weight/4.1+1.2)*30)
    index=None
    if source['run']:
     matches=[x for x in traces[source['run']]['snapshots'] if x['line']==p['afterLine']];assert len(matches)>=p['occurrence'],(source['key'],p);index=matches[p['occurrence']-1]['step']
    motion=dict(begin=local+30,end=local+min(duration-30,210)) if source['run'] else None
    part=dict(**p,begin=local,end=local+duration,stateIndex=index,motion=motion)
    parts.append(part);frames.add(local)
    if motion:frames.update(range(motion['begin'],motion['end']+1))
    local+=duration
   think=120 if source['kind']=='question' else 0
   if think:frames.update(local+j*30 for j in range(4))
   hold=think if think else 75;total=local+hold;frames.add(total-1)
   s=dict(source,parts=parts,startFrame=cursor,durationFrames=total,chapter=c['title'],chapterKey=c['key'],renderFrames=sorted(frames),thinkStart=local if think else None)
   pages.append(s);flat.append(s);cursor+=total
  chapters.append(dict(key=c['key'],title=c['title'],startFrame=begin,durationFrames=cursor-begin,scenes=pages))
 timeline=dict(title=course['title'],status='visual-master-awaiting-new-narration',audio=False,subtitles=False,timingMethod='editorial reading plan; no voice synthesis or forced alignment; replace with measured final narration before spoken release',totalFrames=cursor,duration=cursor/30,fps=30,chapters=chapters,scenes=flat)
 (ROOT/'public/timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding='utf8');DEL.mkdir(exist_ok=True,parents=True)
 (DEL/'章节目录_画面版时间.txt').write_text('\n'.join(stamp(c['startFrame']/30)+' '+c['title'] for c in chapters)+'\n',encoding='utf8')
 rows=[';FFMETADATA1','title=现代汇编入门：x86-64与AArch64（画面版，待新配音）']
 for c in chapters:rows+=['[CHAPTER]','TIMEBASE=1/30',f"START={c['startFrame']}",f"END={c['startFrame']+c['durationFrames']}",'title='+c['title']]
 (ROOT/'build/chapters.ffmetadata').write_text('\n'.join(rows)+'\n',encoding='utf8');print('VISUAL_TIMELINE',stamp(timeline['duration']),len(flat),sum(len(s['parts']) for s in flat),sum(len(s['renderFrames']) for s in flat),flush=True)
if __name__=='__main__':main()
