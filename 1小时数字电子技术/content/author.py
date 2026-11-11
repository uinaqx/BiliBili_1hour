import json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1];CHAPTERS=[]
def C(title):
 c=dict(key=f'{len(CHAPTERS)+1:02}',title=title,scenes=[]);CHAPTERS.append(c);return c
def row(item):
 label,value=item;return dict(label=label,math=value[1:] if value.startswith('$') else None,text='' if value.startswith('$') else value)
def P(text,i,notes,anchor=None):
 assert text.endswith('。') and (not anchor or text.count(anchor)==1),(text,anchor)
 return dict(text=text,focus=[i],show=i,notes=notes,lines=[],codeLines=[],result=False,phase='trace',moves=[dict(anchor=anchor,target=1,seconds=6)] if anchor else [])
def add(c,title,rows,parts,kind='lesson',visual=None):
 s=dict(key=f'de-{c["key"]}-{len(c["scenes"])+1:02}',title=title,rows=[row(r) for r in rows],parts=parts,kind=kind,visual=visual,code=None,codeFile='',output=[],hold=4 if kind=='question' else .65,narration=''.join(p['text'] for p in parts),tags=[c['title']]);c['scenes'].append(s);return s
def L(c,title,a,b,t,u,n,m,visual=None,anchors=None):
 return add(c,title,[a,b],[P(t,1,n,anchors[0] if anchors else None),P(u,2,m,anchors[1] if anchors else None)],visual=visual)
def Q(c,title,a,b,q,ans,answerA,answerB):
 p=P(q,2,['先独立判断','讲完后留4秒思考']);p['focus']=[1,2];add(c,title+'：练习',[a,b],[p],kind='question')
 p=P(ans,2,['答案与条件一起核对','先找规则，再代入数字']);p['focus']=[1,2];add(c,title+'：答案',[answerA,answerB],[p],kind='answer')
def V(kind,**data):return dict(kind=kind,**data)
def write():
 for c in CHAPTERS:assert sum(s['kind']=='question' for s in c['scenes'])==sum(s['kind']=='answer' for s in c['scenes'])==1
 course=dict(title='一小时讲完数字电子技术',audience='零基础大学生；数字电子技术基础概念与常见例题',subtitles=False,speechTempo=1.0,synthesisRate=1.05,chapters=CHAPTERS)
 (ROOT/'public/course.json').write_text(json.dumps(course,ensure_ascii=False,indent=2),encoding='utf8')
 lines=['# 一小时讲完数字电子技术：完整讲稿与分镜','','原创例题；无底部字幕；先观察，再写规则。','']
 for c in CHAPTERS:
  lines+=['## '+c['title'],'']
  for s in c['scenes']:
   lines+=['### '+s['key']+' '+s['title'],'']
   for i,p in enumerate(s['parts']):lines += [p['text'],'','持续强调：'+str(p['focus'])+'；要点：'+'；'.join(p['notes']),'']
   if s['kind']=='question':lines+=['（停顿4秒，再显示答案。）','']
 (ROOT/'content/完整讲稿.md').write_text('\n'.join(lines),encoding='utf8')
 parts=[p for c in CHAPTERS for s in c['scenes'] for p in s['parts']];n=''.join(p['text'] for p in parts)
 print(json.dumps(dict(chapters=len(CHAPTERS),pages=sum(len(c['scenes']) for c in CHAPTERS),parts=len(parts),cjk=len(re.findall('[\u4e00-\u9fff]',n)),motions=sum(len(p['moves']) for p in parts)),ensure_ascii=False),flush=True)
