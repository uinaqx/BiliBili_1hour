import json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1];CHAPTERS=[]
def chapter(title):
 c=dict(key=f'{len(CHAPTERS)+1:02}',title=title,scenes=[]);CHAPTERS.append(c);return c
def speech(marked):
 pieces=re.split(r'\[([0-9, ]+)\]',marked);assert pieces[0]=='',marked
 text='';cues=[]
 for i in range(1,len(pieces),2):
  lines=[int(x) for x in pieces[i].split(',')];segment=pieces[i+1];clean=''.join(c.casefold() for c in segment if c.isalnum());anchor=clean[:18]
  assert len(anchor)>5
  cues.append(dict(anchor=anchor,lines=lines));text+=segment
 assert text.endswith('。')
 return dict(text=text,cues=cues)
def page(c,title,code,output,notes,a,b,*,kind='lesson',fixed=None,diagnostic=None,fixtures=None):
 key=f"ts-{c['key']}-{len(c['scenes'])+1:02}";parts=[speech(a),speech(b)];parts[0]['think']=kind=='exercise';parts[0]['showOutput']=False;parts[1]['showOutput']=True
 code=code.strip();assert len(code.splitlines())<=16,(key,'code too long')
 for i,part in enumerate(parts):
  n=len((fixed if i and fixed else code).splitlines())
  for cue in part['cues']:assert all(1<=v<=n for v in cue['lines']),(key,cue)
 c['scenes'].append(dict(key=key,title=title,code=code,answerCode=fixed,output=output,notes=notes,kind=kind,parts=parts,filename='main.ts',diagnostic=diagnostic,fixtures=fixtures or {}))
def write():
 text=''.join(p['text'] for c in CHAPTERS for s in c['scenes'] for p in s['parts'])
 assert not re.search('不能说|这不等于|这不意味着|不代表|并不意味着|必须强调|需要注意的是',text)
 course=dict(title='一小时学完TypeScript',audience='零基础大学生，先建立必要的JavaScript执行基础',subtitles=False,chapters=CHAPTERS)
 (ROOT/'public/course.json').write_text(json.dumps(course,ensure_ascii=False,indent=2),encoding='utf8');print('COURSE',len(CHAPTERS),sum(len(c['scenes']) for c in CHAPTERS),'CJK',len(re.findall('[\u4e00-\u9fff]',text)),flush=True)
