import json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1];CHAPTERS=[]
def C(title):
    c=dict(key=f'{len(CHAPTERS)+1:02}',title=title,scenes=[]);CHAPTERS.append(c);return c
def R(label,math):return dict(label=label,math=math)
def T(label,text):return dict(label=label,math=None,text=text)
def G(kind,**data):return dict(kind=kind,**data)
def P(text,focus,notes,show=None,phase='first',anchor=None):
    assert 1<=len(notes)<=3
    text=text.strip();assert not anchor or text.count(anchor)==1,('Anchor not unique',anchor,text)
    return dict(text=text,focus=focus,show=max(focus) if show is None else show,notes=notes,phase=phase,moves=[dict(anchor=anchor,target=1,seconds=5)] if anchor else [],lines=[],result=False)
def S(c,title,rows,parts,tags,kind='lesson',visual=None):
    assert 1<=len(rows)<=5 and 1<=len(parts)<=3
    if visual:assert len(rows)<=3,('Diagram page has too many rows',title)
    shown=0
    for p in parts:
        p['show']=max(shown,p['show']);shown=p['show']
        assert p['focus'] and max(p['focus'])<=p['show']<=len(rows),('Focus/show out of range',title)
        if visual:assert p.get('moves'),('Diagram part needs an authored anchor',title)
        if kind=='lesson':assert len(parts)==2,('Lesson page needs exactly two parts',title)
        if kind in ('question','answer','overview'):assert len(parts)==1,('Single-part page',title)
    assert parts[-1]['show']==len(rows),('Last part must reveal all rows',title)
    scene=dict(key=f'net-{c["key"]}-{len(c["scenes"])+1:02}',title=title,rows=rows,parts=parts,tags=tags,kind=kind,visual=visual,hold=4 if kind=='question' else .65,narration=''.join(p['text'] for p in parts));c['scenes'].append(scene);return scene
def stats():
    scenes=[s for c in CHAPTERS for s in c['scenes']]
    return dict(chapters=len(CHAPTERS),pages=len(scenes),parts=sum(len(s['parts']) for s in scenes),cjk=len(re.findall('[\u4e00-\u9fff]',''.join(s['narration'] for s in scenes))),chars=sum(len(s['narration']) for s in scenes),visuals=sum(1 for s in scenes if s.get('visual')),motionIntervals=sum(len(p['moves']) for s in scenes for p in s['parts']))
def write():
    for path in [ROOT/'public',ROOT/'build',ROOT/'docs',ROOT/'out']:path.mkdir(parents=True,exist_ok=True)
    assert len(CHAPTERS)==10,('Need ten chapters',len(CHAPTERS))
    for c in CHAPTERS:
        questions=[i for i,s in enumerate(c['scenes']) if s['kind']=='question'];assert len(questions)==1,('One question per chapter',c['title'])
        assert c['scenes'][questions[0]+1]['kind']=='answer',('Answer must follow question',c['title'])
        assert len(c['scenes'])==8,('Eight pages per chapter',c['title'],len(c['scenes']))
    overview=[s for s in CHAPTERS[0]['scenes'] if s['kind']=='overview'];assert len(overview)==1
    course=dict(title='一小时学完计算机网络',audience='零基础大学生；计算机网络核心概念与基础题型',subtitles=False,speechTempo=1.0,synthesisRate=1.05,chapters=CHAPTERS)
    (ROOT/'public/course.json').write_text(json.dumps(course,ensure_ascii=False,indent=2),encoding='utf8')
    rows=['# 一小时学完计算机网络：完整讲稿与分镜','','按计算机网络常见核心范围组织，侧重概念辨析、协议过程、计算例题和易错点。无底部字幕。','']
    for c in CHAPTERS:
        rows+=['## '+c['title'],'']
        for s in c['scenes']:
            rows+=['### '+s['key']+' '+s['title'],'']
            for i,r in enumerate(s['rows'],1):rows += [f'{i}. '+r['label'],'','$$'+r['math']+'$$' if r['math'] else r['text'],'']
            for p in s['parts']:
                rows += [p['text'],'',f"持续高亮：{p['focus']}；显示到第{p['show']}行；提示："+'；'.join(p['notes']),'']
                for m in p['moves']:rows += ['图示动作锚点：'+m['anchor']+f"；最长连续变化{m['seconds']}秒（遇下一动作起点则衔接），结束后保留。",'']
            if s['kind']=='question':rows += ['（题目讲完保留4秒思考，答案在下一页。）','']
    text='\n'.join(rows);(ROOT/'content/完整讲稿.md').write_text(text,encoding='utf8');(ROOT/'out/完整讲稿.md').write_text(text,encoding='utf8')
    print(json.dumps(stats(),ensure_ascii=False),flush=True)
