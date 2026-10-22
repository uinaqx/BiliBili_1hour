import json,pathlib,textwrap
ROOT=pathlib.Path(__file__).resolve().parents[1]
CHAPTERS=[]
def C(title):
    c=dict(key=f'{len(CHAPTERS)+1:02}',title=title,english='',scenes=[]);CHAPTERS.append(c);return c
def M(body):return 'fun main() {\n'+textwrap.indent(textwrap.dedent(body).strip(),'    ')+'\n}'
def P(lines,text,result=False):return dict(lines=sorted(set(lines)),text=text.strip(),result=result)
def S(c,title,code,parts,notes,output=None,kind='lesson',stdin='',mode='run',diagnostic=None,full=None):
    key=f'kt-{c["key"]}-{len(c["scenes"])+1:02}'
    code=textwrap.dedent(code).strip('\n')
    assert len(code.splitlines())<=13,(key,len(code.splitlines()))
    if code:
        for p in parts:
            assert p['lines'] and all(1<=x<=len(code.splitlines()) and code.splitlines()[x-1].strip() for x in p['lines']),(key,p['lines'])
    row=dict(key=key,section=key,title=title,code=code,parts=parts,notes=notes,output=None if kind=='question' else output,kind=kind,hold=4 if kind=='question' else .7,filename='Main.kt',excerpt=bool(full),source=full or code,stdin=stdin,verify=bool(code and kind!='question'),mode=mode,diagnostic=diagnostic,error=diagnostic if mode=='compile_error' else None,panic=mode=='runtime_error',testFailed=False,diagram=None,panels=[],focus=[],narration=''.join(p['text'] for p in parts))
    c['scenes'].append(row);return row
def write():
    (ROOT/"public").mkdir(parents=True,exist_ok=True)
    (ROOT/"out").mkdir(parents=True,exist_ok=True)
    d=dict(title='一小时学习 Kotlin：零基础入门',language='Kotlin 2.0.21 / JVM',audience='零基础',subtitles=False,chapters=CHAPTERS)
    (ROOT/'public/course.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
    rows=['# 一小时学习 Kotlin：完整讲稿与分镜','','面向零基础学生。中文旁白，无底部字幕。代码高亮随人工选定的讲解对象持续显示。','']
    for c in CHAPTERS:
        rows.extend(['## '+c['title'],''])
        for s in c['scenes']:
            rows.extend(['### '+s['key']+' '+s['title'],''])
            for p in s['parts']:rows.extend([p['text'],''])
            if s['kind']=='question':rows.extend(['（四秒独立思考，答案在下一页揭晓）',''])
            if s['code']:rows.extend(['```kotlin',s['code'],'```',''])
            if s['output'] is not None:rows.extend(['预期结果：','```text',s['output'],'```',''])
            rows.extend(['画面要点：'+'；'.join(s['notes']),''])
    text='\n'.join(rows)
    (ROOT/'content/完整讲稿.md').write_text(text,encoding='utf8')
    (ROOT/'out/完整讲稿.md').write_text(text,encoding='utf8')
    speech=''.join(s['narration'] for c in CHAPTERS for s in c['scenes'])
    print(json.dumps(dict(chapters=len(CHAPTERS),scenes=sum(len(c['scenes']) for c in CHAPTERS),parts=sum(len(s['parts']) for c in CHAPTERS for s in c['scenes']),cjk=sum('\u4e00'<=x<='\u9fff' for x in speech)),ensure_ascii=False))
