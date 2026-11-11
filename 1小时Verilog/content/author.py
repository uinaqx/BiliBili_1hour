import hashlib,json,pathlib,re,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'examples'))
from catalog import DESIGNS
CHAPTERS=[]
def C(title):
 c=dict(key=f'{len(CHAPTERS)+1:02}',title=title,scenes=[]);CHAPTERS.append(c);return c
def P(text,focus,notes,codeLines=None,anchor=None):
 assert text.endswith('。') and (not anchor or text.count(anchor)==1),(text,anchor)
 return dict(text=text,focus=focus,show=max(focus),notes=notes,codeLines=codeLines or [],lines=codeLines or [],result=False,phase='trace',moves=[dict(anchor=anchor,target=1,seconds=5)] if anchor else [])
def add(c,title,rows,parts,kind='lesson',code=None,codeFile='',visual=None,output=None):
 s=dict(key=f'vl-{c["key"]}-{len(c["scenes"])+1:02}',title=title,rows=[dict(label=a,text=b,math=None) for a,b in rows],parts=parts,kind=kind,code=code,codeFile=codeFile,visual=visual,output=output or [],hold=4 if kind=='question' else .65,narration=''.join(p['text'] for p in parts),tags=[c['title']])
 assert not code or len(code)<=15,(title,len(code or []))
 assert parts[-1]['show']==len(rows),(title,'all rows must be discussed')
 c['scenes'].append(s);return s
def L(c,title,key,focus,texts,notes,visual=None,anchors=None,excerpt=None,output=None):
 code=DESIGNS[key].splitlines() if key else None
 if excerpt:code=code[excerpt[0]-1:excerpt[1]]
 parts=[P(t,[i+1],notes[i],focus[i] if code else None,anchors[i] if anchors else None) for i,t in enumerate(texts)]
 rows=[('先观察',notes[0][0]),('再判断',notes[1][0])]
 return add(c,title,rows,parts,code=code,codeFile=(key+'.v'+(' · 节选' if excerpt else '')) if key else '',visual=visual,output=output)
def Q(c,title,question,answer,questionRows,answerRows):
 add(c,title+'：练习',questionRows,[P(question,list(range(1,len(questionRows)+1)),['先独立判断','讲完后有4秒思考'])],kind='question')
 add(c,title+'：答案',answerRows,[P(answer,list(range(1,len(answerRows)+1)),['按实际规则判断','把原因一起写出来'])],kind='answer')
def W(key,signals=None):return dict(kind='wave',trace=key,signals=signals)
def G(kind,**data):return dict(kind=kind,**data)
def B(c,title,key,excerpt,focus,texts,notes):
 from catalog import TESTS,bench
 code=bench(next(t for t in TESTS if t['key']==key)).splitlines()[excerpt[0]-1:excerpt[1]]
 return add(c,title,[('测试目的',notes[0][0]),('检查依据',notes[1][0])],[P(t,[i+1],notes[i],focus[i]) for i,t in enumerate(texts)],code=code,codeFile='tb_'+key+'.v · 节选')
def write():
 assert len(CHAPTERS)==10
 for c in CHAPTERS:assert sum(s['kind']=='question' for s in c['scenes'])==sum(s['kind']=='answer' for s in c['scenes'])==1
 course=dict(title='一小时学完Verilog',audience='零基础大学生；电路描述、RTL设计与仿真入门',subtitles=False,speechTempo=1.0,synthesisRate=1.05,chapters=CHAPTERS)
 (ROOT/'public/course.json').write_text(json.dumps(course,ensure_ascii=False,indent=2),encoding='utf8')
 lines=['# 一小时学完Verilog：完整讲稿与分镜','','Verilog-2005设计语法；波形来自实际RTL仿真，无底部字幕。','']
 for c in CHAPTERS:
  lines+=['## '+c['title'],'']
  for s in c['scenes']:
   lines+=['### '+s['key']+' '+s['title'],'']
   if s['code']:lines+=['代码：'+s['codeFile'],'','```verilog','\n'.join(s['code']),'```','']
   for p in s['parts']:lines += [p['text'],'','持续代码高亮：'+str(p['codeLines'])+'；要点：'+'；'.join(p['notes']),'']
   if s['kind']=='question':lines+=['（停顿4秒，再显示答案。）','']
 (ROOT/'content/完整讲稿.md').write_text('\n'.join(lines),encoding='utf8')
 parts=[p for c in CHAPTERS for s in c['scenes'] for p in s['parts']];text=''.join(p['text'] for p in parts)
 print(json.dumps(dict(chapters=10,pages=sum(len(c['scenes']) for c in CHAPTERS),parts=len(parts),cjk=len(re.findall('[\u4e00-\u9fff]',text)),chars=len(text),motions=sum(len(p['moves']) for p in parts)),ensure_ascii=False),flush=True)
