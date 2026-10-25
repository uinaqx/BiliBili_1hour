import json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1];CHAPTERS=[]
def C(title):
    c=dict(key=f'{len(CHAPTERS)+1:02}',title=title,scenes=[]);CHAPTERS.append(c);return c
def V(kind,**data):return dict(kind=kind,**data)
def P(text,visual,formulas,notes,motion=6):return dict(text=text.strip(),visual=visual,formulas=formulas,notes=notes,motion=motion,lines=[],result=False)
def S(c,title,parts,tags,kind='lesson',answer=None):
    key=f'la-{c["key"]}-{len(c["scenes"])+1:02}'
    assert 1<=len(parts)<=3
    for p in parts:
        assert len(p['notes'])<=3 and len(p['formulas'])<=4
    s=dict(key=key,title=title,parts=parts,tags=tags,kind=kind,hold=4 if kind=='question' else .7,answer=answer,narration=''.join(p['text'] for p in parts));c['scenes'].append(s);return s
def write():
    for folder in [ROOT/'public',ROOT/'docs',ROOT/'out']:folder.mkdir(parents=True,exist_ok=True)
    d=dict(title='一小时学习线性代数',audience='零基础大学生；使用高中代数和二维坐标',subtitles=False,source=dict(name='线性代数知识点.pdf',sha256='384480778ed65eae1ffca84ad9fb915f4002a0b576dc85a902e232b890399fdc'),chapters=CHAPTERS)
    (ROOT/'public/course.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
    rows=['# 一小时学习线性代数：完整讲稿与分镜','','面向零基础大学生。先看几何与数值变化，再说明术语和公式。无底部字幕。','']
    coverage={}
    for c in CHAPTERS:
        rows+=['## '+c['title'],'']
        for s in c['scenes']:
            rows+=['### '+s['key']+' '+s['title'],'']
            for p in s['parts']:
                rows += [p['text'],'','画面：'+p['visual']['kind']+'；'+'；'.join(p['notes']),'','公式：'+'；'.join(p['formulas']),'']
            if s['kind']=='question':rows+=['（留四秒思考；答案下一页揭晓）','']
            for tag in s['tags']:coverage.setdefault(tag,[]).append(s['key'])
    text='\n'.join(rows)
    (ROOT/'content/完整讲稿.md').write_text(text,encoding='utf8');(ROOT/'out/完整讲稿.md').write_text(text,encoding='utf8')
    (ROOT/'docs/覆盖索引.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf8')
    alltext=''.join(s['narration'] for c in CHAPTERS for s in c['scenes'])
    print(json.dumps(dict(chapters=len(CHAPTERS),pages=sum(len(c['scenes']) for c in CHAPTERS),units=sum(len(s['parts']) for c in CHAPTERS for s in c['scenes']),cjk=len(re.findall('[\u4e00-\u9fff]',alltext))),ensure_ascii=False))
