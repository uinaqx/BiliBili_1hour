"""Resolve authored cues to final measured speech; never estimate starts by length."""
import bisect,hashlib,json,math,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out';sys.path.insert(0,str(ROOT/'content'))
from highlights import CUES
def load(p):return json.loads(p.read_text(encoding='utf8'))
def stamp(t):
 h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def normal(s):return ''.join(c.lower() for c in s if c.isalnum())
def anchor_seconds(anchor,part):
 chars=[];times=[]
 for w in part['words']:
  for c in w['text']:
   if c.isalnum():chars.append(c.lower());times.append(w['begin_time']/1000)
 text=''.join(chars);needle=normal(anchor);at=text.find(needle)
 assert at>=0 and text.find(needle,at+1)<0,('Missing or ambiguous voice anchor',part['rawKey'],anchor)
 return part['start']+times[at]
def srt_time(sec):
 value=round(sec*1000);h,value=divmod(value,3600000);m,value=divmod(value,60000);s,ms=divmod(value,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'
def main():
 course=load(ROOT/'public/course.json');traces=load(ROOT/'build/execution-data.json');cursor=0;chapters=[];flat=[];srt=[];cuecount=0
 for c in course['chapters']:
  begin=cursor;pages=[]
  for src in c['scenes']:
   audio=load(ROOT/'public/audio'/(src['key']+'.json'));lead=12;speech=math.ceil(audio['samples']/800);think=120 if src['kind']=='question' else 75;total=lead+speech+3+think;parts=[];events={0,total-1}
   for i,(p,v) in enumerate(zip(src['parts'],audio['parts'])):
    assert p['text']==v['cue'];start=lead+math.ceil(v['onset']*30-1e-6);stop=lead+math.ceil(v['end']*30-1e-6);cues=[]
    if src['run']:
     for cue in CUES[src['run']]:
      pi,anchor,lines,after,*extra=cue
      if pi!=i:continue
      assert p['text'].count(anchor)==1
      at=max(start,lead+math.ceil(anchor_seconds(anchor,v)*30-1e-6));assert at<stop,(src['key'],anchor,at,stop)
      matches=[x for x in traces[src['run']]['snapshots'] if x['line']==after];occ=extra[0] if extra else 1;assert len(matches)>=occ
      cues.append(dict(begin=at,anchor=anchor,codeLines=lines,stateIndex=matches[occ-1]['step'],afterLine=after,occurrence=occ,method='authored phrase / acoustic known-transcript / measured final PCM'))
     assert cues and all(a['begin']<=b['begin'] for a,b in zip(cues,cues[1:])),(src['key'],i,'Cue order')
     if cues[0]['begin']>start:cues.insert(0,dict(cues[0],begin=start,anchor='page/part initial persistent selection'))
     for j,cue in enumerate(cues):
      next_at=cues[j+1]['begin'] if j+1<len(cues) else stop;end=min(cue['begin']+60,next_at)
      cue['motion']=dict(begin=cue['begin'],end=max(cue['begin']+1,end))
      events.update(range(cue['motion']['begin'],cue['motion']['end']+1));cuecount+=1
    parts.append(dict(p,begin=start,end=stop,cues=cues,stateIndex=cues[0]['stateIndex'] if cues else None,motion=cues[0]['motion'] if cues else None));events.add(start)
   captions=[]
   for cap in audio['captions']:
    a=lead+math.ceil(cap['start']*30-1e-6);b=lead+math.ceil(cap['end']*30-1e-6)
    if b<=a:continue
    captions.append(dict(begin=a,end=b,text=cap['text']));events.update([a,b]);srt.append((cursor/30+lead/30+cap['start'],cursor/30+lead/30+cap['end'],cap['text']))
   thinking=lead+speech+3 if src['kind']=='question' else None
   if thinking is not None:events.update(thinking+j*30 for j in range(4))
   s=dict(src,parts=parts,startFrame=cursor,durationFrames=total,chapter=c['title'],chapterKey=c['key'],audio='audio/'+src['key']+'.wav',audioSha256=audio['sha256'],leadFrames=lead,speechFrames=speech,subtitles=True,captions=captions,thinkStart=thinking,renderFrames=sorted(f for f in events if 0<=f<total))
   pages.append(s);flat.append(s);cursor+=total
  chapters.append(dict(key=c['key'],title=c['title'],startFrame=begin,durationFrames=cursor-begin,scenes=pages))
 timeline=dict(title=course['title'],status='complete-spoken-course',audio=True,subtitles=True,timingMethod='authored semantic cues resolved to known-transcript acoustic alignment on final measured PCM',totalFrames=cursor,duration=cursor/30,fps=30,synthesisRate=1.05,postProcessingTempo=1.0,automaticTempoAdjustment=False,chapters=chapters,scenes=flat)
 (ROOT/'public/timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding='utf8')
 (DEL/'章节目录.txt').write_text('\n'.join(stamp(c['startFrame']/30)+' '+c['title'] for c in chapters)+'\n',encoding='utf8')
 (DEL/'逐页目录.txt').write_text('\n'.join(stamp(s['startFrame']/30)+' '+s['title'] for s in flat)+'\n',encoding='utf8')
 subtitle='\n\n'.join(f'{i+1}\n{srt_time(a)} --> {srt_time(b)}\n{t}' for i,(a,b,t) in enumerate(srt))+'\n'
 (DEL/'现代汇编_x86-64与AArch64.srt').write_text(subtitle,encoding='utf8')
 rows=[';FFMETADATA1','title=现代汇编入门：x86-64与AArch64']
 for c in chapters:rows+=['[CHAPTER]','TIMEBASE=1/30',f"START={c['startFrame']}",f"END={c['startFrame']+c['durationFrames']}",'title='+c['title']]
 (ROOT/'build/chapters-spoken.ffmetadata').write_text('\n'.join(rows)+'\n',encoding='utf8')
 print('SPOKEN_TIMELINE',stamp(timeline['duration']),len(flat),cuecount,len(srt),sum(len(s['renderFrames']) for s in flat),flush=True)
if __name__=='__main__':main()
