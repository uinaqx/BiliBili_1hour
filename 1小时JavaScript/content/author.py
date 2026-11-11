import json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
CHAPTERS=[]
def chapter(title):
    c=dict(key=f'{len(CHAPTERS)+1:02}',title=title,scenes=[]);CHAPTERS.append(c);return c
def page(c,title,code,output,notes,first,second,*,lines=None,kind='lesson',answer=None,fixtures=None):
    key=f"js-{c['key']}-{len(c['scenes'])+1:02}"
    code=code.strip();n=len(code.splitlines());assert n<=16,(key,n)
    if lines is None:lines=[[],[]]  # Rendering uses the reviewed phrase plan, never half-page defaults.
    assert all(text.endswith('。') for text in [first,second])
    c['scenes'].append(dict(key=key,title=title,code=code,output=output,notes=notes,kind=kind,answerCode=answer,fixtures=fixtures or {},
        parts=[dict(text=first,lines=lines[0],showOutput=False,think=kind=='exercise' or title.startswith('练习')),dict(text=second,lines=lines[1],showOutput=True)],filename='index.html' if kind=='html' else ('budget.mjs' if kind=='module' else 'main.mjs')))
def write():
    p=ROOT/'public/course.json';course=dict(title='一小时学完JavaScript',audience='完全零基础学生',subtitles=True,chapters=CHAPTERS)
    p.write_text(json.dumps(course,ensure_ascii=False,indent=2),encoding='utf8')
    text=''.join(p['text'] for c in CHAPTERS for s in c['scenes'] for p in s['parts'])
    assert not re.search('不能说|这不等于|这不意味着|不代表|并不意味着|必须强调|需要注意的是',text)
    print('COURSE',len(CHAPTERS),sum(len(c['scenes']) for c in CHAPTERS),'CJK',len(re.findall('[\u4e00-\u9fff]',text)), 'characters',len(text),flush=True)
