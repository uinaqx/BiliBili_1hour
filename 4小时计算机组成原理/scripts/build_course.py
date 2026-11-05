"""Assemble the reviewed modules, neutral source assets and coverage ledger."""
import argparse,collections,hashlib,json,pathlib,shutil,re
from PIL import Image,ImageDraw,ImageStat
ROOT=pathlib.Path(__file__).resolve().parents[1]
PRIVATE=ROOT.parent/'.cache/ppt_course_private'
TITLES={'01':'计算机系统、性能与发展','02':'数据表示与校验','03':'浮点数表示','04':'计算机运算方法','05':'系统总线','06':'存储系统','07':'输入输出系统','08':'指令系统','09':'CPU与流水线','10':'控制单元与时序'}
def load(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--public-only',action='store_true',help='Rebuild using the included anonymous assets and neutral inventory');args=parser.parse_args();public_mode=True  # Public sources always use the included anonymous assets
 images=ROOT/'public/slides' if public_mode else PRIVATE/'safe_images';inventory=ROOT/'content/source_inventory.json' if public_mode else PRIVATE/'safe_text/inventory.json'
 modules=[load(p) for p in sorted((ROOT/'content').glob('module_*.json'))];chapters=[];ledger=collections.defaultdict(list);corrections=[];missing=[];scenes=[];ids=set();imported={};identities=[] if public_mode else [s for s in load(PRIVATE/'private_identity_candidates.json')['metadata'] if len(s)>2]
 masks=load(ROOT/'content/image_redactions.json') if (ROOT/'content/image_redactions.json').exists() else []
 forbidden=re.compile(r'大学|学院|主讲|授课教师|联系电话|电子邮箱|1[3-9]\d{9}|[\w.+-]+@[\w.-]+')
 for m in modules:
  key=m['key'][:2]
  if not chapters or chapters[-1]['key']!=key:chapters.append(dict(key=key,title=TITLES[key],scenes=[]))
  for s in m['scenes']:
   assert s['id'] not in ids;ids.add(s['id']);assert len(s['points'])==4 and s['beats']
   public_text=json.dumps({k:v for k,v in s.items() if k!='sourcePages'},ensure_ascii=False)
   found=forbidden.search(public_text)
   if found:raise ValueError('Personal-information pattern in authored scene '+s['id'])
   if any(n in public_text for n in identities if len(n)>2):raise ValueError('Private metadata identity in authored scene '+s['id'])
   for i,b in enumerate(s['beats']):
    assert b['text'].endswith('。'),s['id'];b['key']=s['id']+f'-p{i:02}'
    if b.get('board'):b['board']=[dict(label='步骤'+str(j+1),text=row) if isinstance(row,str) else row for j,row in enumerate(b['board'])]
    if s.get('boardFallback') and not b.get('board'):b['board']=[dict(label='要点'+str(j+1),text=p) for j,p in enumerate(s['points'])]
    if not b.get('board'):
     page=b['page'];source=images/(page+'.jpg');assert source.exists(),page
     target=ROOT/'public/slides'/source.name
     if not public_mode:shutil.copy2(source,target)
     applied=[m for m in masks if m['page']==page]
     if applied and not public_mode:
      with Image.open(target) as original:
       image=original.convert('RGB');w,h=image.size;d=ImageDraw.Draw(image)
       for mask in applied:
        x,y,xx,yy=[round(v*n) for v,n in zip(mask['rect'],[w,h,w,h])];sample=image.crop((x,max(0,y-8),xx,max(1,y-2)));color=tuple(round(v) for v in ImageStat.Stat(sample).median);d.rectangle((x,y,xx,yy),fill=color)
       image.save(target,quality=95)
     imported[page]=dict(file='slides/'+source.name,sha256=hashlib.sha256(target.read_bytes()).hexdigest(),redactions=applied)
   chapters[-1]['scenes'].append(s);scenes.append(s)
  for item in m.get('coverage',[]):ledger[item['source']].append(item)
  corrections.extend(m.get('corrections',[]));missing.extend(m.get('missingQuestionStems',[]))
 expected={f"{d['id']}-{n:03}" for d in load(inventory) for n in range(1,d['pages']+1)}
 uncovered=sorted(expected-set(ledger));unknown=sorted(set(ledger)-expected)
 assert not unknown,unknown
 for stale in (ROOT/'public/slides').glob('*.jpg'):
  if stale.stem not in imported:stale.unlink()
 course=dict(title='计算机组成原理课件精讲',subtitles=False,sourceSlides=len(expected),scope='complete' if not uncovered else 'partial',chapters=chapters,sourceAssets=imported,synthesisRate=1.05,speechTempo=1.0)
 save(ROOT/'public/course.json',course);save(ROOT/'build/coverage.json',dict(sourceSlides=len(expected),accountedFor=len(ledger),uncovered=uncovered,items=dict(ledger),corrections=corrections,missingQuestionStems=missing))
 out=['# 计算机组成原理课件精讲：完整讲稿','']
 for c in chapters:
  out+=['## '+c['title'],'']
  for s in c['scenes']:
   out+=['### '+s['title'],'']
   for b in s['beats']:out+=[b['text'],'']
   out+=['本页总结：','']+['- '+x for x in s['points']]+['']
 (ROOT/'docs/完整讲稿.md').write_text('\n'.join(out),encoding='utf8')
 print('COURSE_READY',len(chapters),len(scenes),sum(len(s['beats']) for s in scenes),len(ledger),'/',len(expected),'source pages; missing',len(uncovered),flush=True)
if __name__=='__main__':main()
