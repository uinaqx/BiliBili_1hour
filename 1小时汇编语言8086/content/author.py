import json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1];CHAPTERS=[]
def C(title):
 c=dict(key=f'{len(CHAPTERS)+1:02}',title=title,scenes=[]);CHAPTERS.append(c);return c
def row(item):return dict(label=item[0],math=None,text=item[1])
def P(text,i,notes,anchor=None):
 assert text.endswith('。') and (not anchor or text.count(anchor)==1)
 return dict(text=text,focus=[i],show=i,notes=notes,lines=[],codeLines=[],result=False,phase='trace',highlights=[],moves=[dict(anchor=anchor,target=1,seconds=6)] if anchor else [])
def add(c,title,rows,parts,kind='lesson',visual=None,code=None,run=None,output=None):
 s=dict(key=f'as-{c["key"]}-{len(c["scenes"])+1:02}',title=title,rows=[row(r) for r in rows],parts=parts,kind=kind,visual=visual,code=code.splitlines() if code else None,codeFile=(run+'.asm') if run else '',run=run,output=output or [],hold=4 if kind=='question' else .65,narration=''.join(p['text'] for p in parts),tags=[c['title']]);c['scenes'].append(s);return s
def L(c,title,a,b,t,u,n,m,visual=None,anchors=None,code=None,run=None,output=None,lines=None,hints=None):
 ps=[P(t,1,n,anchors[0] if anchors else None),P(u,2,m,anchors[1] if anchors else None)]
 if code:
  assert len(code.splitlines())<=14
  for i,p in enumerate(ps):p['codeLines']=lines[i] if lines else [1];p['result']=i==1
 if hints:
  for i,h in enumerate(hints):
   for phrase,selected in h:
    assert ps[i]['text'].count(phrase)==1,(title,phrase);ps[i]['highlights'].append(dict(anchor=phrase,codeLines=selected))
 return add(c,title,[a,b],ps,visual=visual,code=code,run=run,output=output)
def Q(c,title,a,b,q,ans,answerA,answerB):
 p=P(q,2,['先独立判断','讲完后留4秒思考']);p['focus']=[1,2];add(c,title+'：练习',[a,b],[p],kind='question')
 p=P(ans,2,['答案连同条件核对','先追踪变化，再检查终态']);p['focus']=[1,2];add(c,title+'：答案',[answerA,answerB],[p],kind='answer')
def V(kind,**data):return dict(kind=kind,**data)
def write():
 for c in CHAPTERS:assert sum(s['kind']=='question' for s in c['scenes'])==sum(s['kind']=='answer' for s in c['scenes'])==1
 course=dict(title='一小时讲完汇编语言',audience='零基础大学生；8086实模式与NASM的Intel语法',subtitles=False,speechTempo=1.0,synthesisRate=1.05,chapters=CHAPTERS)
 (ROOT/'public/course.json').write_text(json.dumps(course,ensure_ascii=False,indent=2),encoding='utf8')
 out=['# 一小时讲完汇编语言：完整讲稿与分镜','','8086实模式；NASM Intel语法；无底部字幕；先看执行变化，再写规则。','']
 for c in CHAPTERS:
  out+=['## '+c['title'],'']
  for s in c['scenes']:
   out+=['### '+s['key']+' '+s['title'],'']
   if s['code']:out+=['```asm',*s['code'],'```','']
   for p in s['parts']:out+=[p['text'],'','持续选中：'+str(p['codeLines'] if s['code'] else p['focus'])+'；'+'；'.join(p['notes']),'']
   if s['kind']=='question':out+=['（停顿4秒，再显示答案。）','']
 (ROOT/'content/完整讲稿.md').write_text('\n'.join(out)+'\n',encoding='utf8')
 parts=[p for c in CHAPTERS for s in c['scenes'] for p in s['parts']];print(json.dumps(dict(chapters=len(CHAPTERS),pages=sum(len(c['scenes']) for c in CHAPTERS),parts=len(parts),cjk=len(re.findall('[\u4e00-\u9fff]',''.join(p['text'] for p in parts))),motions=sum(len(p['moves']) for p in parts),highlightCues=sum(len(p['highlights']) for p in parts)),ensure_ascii=False),flush=True)
