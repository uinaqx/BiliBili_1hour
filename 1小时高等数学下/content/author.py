import json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1];CHAPTERS=[]
def C(title):
    c=dict(key=f'{len(CHAPTERS)+1:02}',title=title,scenes=[]);CHAPTERS.append(c);return c
def R(label,math):return dict(label=label,math=math)
def T(label,text):return dict(label=label,math=None,text=text)
def G(kind,**data):return dict(kind=kind,**data)
def P(text,focus,notes,show=None,phase='first',anchor=None):
    assert 1<=len(notes)<=3
    text=text.strip();assert not anchor or text.count(anchor)==1
    return dict(text=text,focus=focus,show=max(focus) if show is None else show,notes=notes,phase=phase,moves=[dict(anchor=anchor,target=1,seconds=5)] if anchor else [],lines=[],result=False)
def S(c,title,rows,parts,tags,kind='lesson',visual=None):
    assert 1<=len(rows)<=5 and 1<=len(parts)<=3
    if visual:assert len(rows)<=3,('Diagram page has too many formula rows',title)
    for p in parts:assert p['focus'] and max(p['focus'])<=p['show']<=len(rows)
    assert parts[-1]['show']==len(rows)
    scene=dict(key=f'cb-{c["key"]}-{len(c["scenes"])+1:02}',title=title,rows=rows,parts=parts,tags=tags,kind=kind,visual=visual,hold=4 if kind=='question' else .65,narration=''.join(p['text'] for p in parts));c['scenes'].append(scene);return scene
def write():
    for path in [ROOT/'public',ROOT/'build',ROOT/'docs',ROOT/'out']:path.mkdir(parents=True,exist_ok=True)
    assert len(CHAPTERS)==10
    for c in CHAPTERS:
        questions=[i for i,s in enumerate(c['scenes']) if s['kind']=='question'];assert len(questions)==1
        assert c['scenes'][questions[0]+1]['kind']=='answer'
    course=dict(title='一小时学完高等数学（下）',audience='零基础大学生；常见期末基础题型与及格目标',subtitles=False,speechTempo=1.0,chapters=CHAPTERS)
    (ROOT/'public/course.json').write_text(json.dumps(course,ensure_ascii=False,indent=2),encoding='utf8')
    rows=['# 一小时学完高等数学（下）：完整讲稿与分镜','','按常见理工类高数下范围组织，侧重公式条件、题型步骤、原创例题与常见失分点。原始1.0倍速，无底部字幕。','']
    for c in CHAPTERS:
        rows+=['## '+c['title'],'']
        for s in c['scenes']:
            rows+=['### '+s['key']+' '+s['title'],'']
            for i,r in enumerate(s['rows'],1):rows += [f'{i}. '+r['label'],'','$$'+r['math']+'$$' if r['math'] else r['text'],'']
            for p in s['parts']:
                rows += [p['text'],'',f"持续高亮：{p['focus']}；显示到第{p['show']}行；提示："+'；'.join(p['notes']),'']
                for m in p['moves']:rows += ['图示动作锚点：'+m['anchor']+'；连续变化5秒，结束后保留。','']
            if s['kind']=='question':rows += ['（题目讲完保留4秒思考，答案在下一页。）','']
    text='\n'.join(rows);(ROOT/'content/完整讲稿.md').write_text(text,encoding='utf8');(ROOT/'out/完整讲稿.md').write_text(text,encoding='utf8')
    print(json.dumps(dict(chapters=10,pages=sum(len(c['scenes']) for c in CHAPTERS),parts=sum(len(s['parts']) for c in CHAPTERS for s in c['scenes']),cjk=len(re.findall('[\u4e00-\u9fff]',''.join(s['narration'] for c in CHAPTERS for s in c['scenes']))),motionIntervals=sum(len(p['moves']) for c in CHAPTERS for s in c['scenes'] for p in s['parts'])),ensure_ascii=False),flush=True)
