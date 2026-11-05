import argparse,json,math,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def stamp(t):
 h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--through');args=parser.parse_args();c=load(ROOT/'public/course.json');cursor=0;chapters=[];scenes=[]
 for chapter in c['chapters']:
  if args.through and chapter['key']>args.through:continue
  begin=cursor;local=[]
  for scene in chapter['scenes']:
   a=load(ROOT/'public/audio'/(scene['id']+'.json'));lead=12;duration=lead+math.ceil(a['samples']/800)+20;events=[0]
   for p in a['parts'][1:]:events.append(lead+math.floor(p['start']*30))
   s=dict(**scene,startFrame=cursor,durationFrames=duration,leadFrames=lead,chapter=chapter['title'],chapterKey=chapter['key'],audio='audio/'+scene['id']+'.wav',audioSha256=a['sha256'],beatFrames=events,renderFrames=sorted(set(events+[duration-1])))
   cursor+=duration;scenes.append(s);local.append(s)
  chapters.append(dict(key=chapter['key'],title=chapter['title'],startFrame=begin,durationFrames=cursor-begin,scenes=local))
 t=dict(title=c['title'],scope='partial' if args.through else c['scope'],chapters=chapters,scenes=scenes,totalFrames=cursor,duration=cursor/30,subtitles=False,fps=30,synthesisRate=1.05,speechTempo=1.0)
 (ROOT/'public/timeline.json').write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf8');DEL.mkdir(parents=True,exist_ok=True)
 for name,text in [('章节目录.txt','\n'.join(stamp(c['startFrame']/30)+' '+c['title'] for c in chapters)),('知识点与考题目录.txt','\n'.join(stamp(s['startFrame']/30)+' '+s['title'] for s in scenes))]: (DEL/(('内部试制_部分' if args.through else '')+name)).write_text(text+'\n',encoding='utf8')
 rows=[';FFMETADATA1','title=计算机组成原理课件精讲']
 for ch in chapters:rows+=['[CHAPTER]','TIMEBASE=1/30',f"START={ch['startFrame']}",f"END={ch['startFrame']+ch['durationFrames']}",'title='+ch['title']]
 (ROOT/'build/chapters.ffmetadata').write_text('\n'.join(rows)+'\n',encoding='utf8');print('TIMELINE_READY',stamp(t['duration']),len(scenes),sum(len(s['beats']) for s in scenes),flush=True)
if __name__=='__main__':main()
