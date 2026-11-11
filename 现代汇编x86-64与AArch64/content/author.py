import json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from examples import CASES
CHAPTERS=[]
def C(title):
 c=dict(key=f'{len(CHAPTERS)+1:02}',title=title,scenes=[]);CHAPTERS.append(c);return c
def add(c,title,points,texts,kind='lesson',run=None,states=None,regs=None,diagram=None):
 assert len(points)==4
 s=dict(key=f'ma-{c["key"]}-{len(c["scenes"])+1:02}',title=title,points=points,kind=kind,run=run,diagram=diagram,parts=[])
 if run:s.update(arch=CASES[run]['arch'],code=CASES[run]['code'],regs=regs or (['rax','rdi','rsi','rsp'] if CASES[run]['arch']=='x64' else ['x0','x1','x30','sp']))
 else:s.update(arch='compare',code=None,regs=[])
 for i,t in enumerate(texts):
  assert t.endswith('。'),title
  lines,after,*extra=states[i] if states else ([],None)
  s['parts'].append(dict(text=t,codeLines=lines,afterLine=after,occurrence=extra[0] if extra else 1))
 c['scenes'].append(s);return s
def L(c,title,run,points,texts,states,regs=None):return add(c,title,points,texts,run=run,states=states,regs=regs)
def P(c,title,points,texts,diagram=None):return add(c,title,points,texts,diagram=diagram)
def Q(c,title,prompt,question,answer,notes):
 add(c,title+' · 练习',prompt,[question],kind='question')
 add(c,title+' · 答案',notes,[answer],kind='answer')
def write():
 course=dict(title='现代汇编入门：x86-64与AArch64',audience='零基础大学生',status='modern-content-ready',voice=dict(model='qwen-audio-3.1-tts-plus',voice='xunanchuan_v3.1',synthesisRate=1.05,postProcessingTempo=1.0),chapters=CHAPTERS)
 (ROOT/'public/course.json').write_text(json.dumps(course,ensure_ascii=False,indent=2),encoding='utf8')
 text=['# 现代汇编入门：x86-64与AArch64','','完整重写稿。配音采用百炼3.1 Plus、许南川、原生1.05倍速；按最终音频实测时间安排画面、高亮和底部字幕。','']
 for c in CHAPTERS:
  text+=['## '+c['title'],'']
  for s in c['scenes']:
   text+=['### '+s['title'],'']
   if s['code']:text+=['```asm',*s['code'],'```','']
   for p in s['parts']:text+=[p['text'],'']
   if s['kind']=='question':text+=['（四秒思考，随后展示答案。）','']
   text+=['本页总结：','']+['- '+p for p in s['points']]+['']
 (ROOT/'docs/完整讲稿.md').write_text('\n'.join(text)+'\n',encoding='utf8')
 print('COURSE_BUILT',len(CHAPTERS),sum(len(c['scenes']) for c in CHAPTERS),sum(len(s['parts']) for c in CHAPTERS for s in c['scenes']),flush=True)
