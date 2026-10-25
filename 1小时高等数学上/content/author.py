import json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1];CHAPTERS=[]
TOPICS=['等价无穷小替换','无穷小的比较','左右极限','第二类重要极限','连续的定义','间断点分类','闭区间连续函数的性质','导数的定义','幂指函数求导','参数方程求导','隐函数求导','复合函数链式法则','抽象函数求导','切线方程、法线方程','高阶导数','微分','微分中值定理','洛必达法则','单调区间','极值的第一、第二判别法','凹凸区间、拐点','最值','渐近线','原函数的定义','不定积分的定义','基本积分公式','积分变限函数求导','微积分基本定理','定积分的性质','定积分偶倍奇零','第一、第二换元积分法','分部积分','反常积分敛散性','定积分求面积','定积分求绕轴旋转的旋转体体积','微分方程的相关概念','可分离变量微分方程','一阶线性微分方程','二阶常系数齐次线性方程']
def C(title):
    c=dict(key=f'{len(CHAPTERS)+1:02}',title=title,scenes=[]);CHAPTERS.append(c);return c
def R(label,math):return dict(label=label,math=math)
def T(label,text):return dict(label=label,math=None,text=text)
def P(text,focus,notes,show=None):return dict(text=text.strip(),focus=focus,show=max(focus) if show is None else show,notes=notes,lines=[],result=False)
def S(c,title,rows,parts,tags,kind='lesson'):
    assert 1<=len(rows)<=5 and 1<=len(parts)<=3
    for p in parts:
        assert p['focus'] and all(1<=i<=len(rows) for i in p['focus']) and max(p['focus'])<=p['show']<=len(rows)
        assert len(p['notes'])<=3
    s=dict(key=f'ca-{c["key"]}-{len(c["scenes"])+1:02}',title=title,rows=rows,parts=parts,tags=tags,kind=kind,hold=4 if kind=='question' else .7,narration=''.join(p['text'] for p in parts));c['scenes'].append(s);return s
def write():
    coverage={tag:[] for tag in TOPICS};out=ROOT/'out';out.mkdir(parents=True,exist_ok=True)
    rows=['# 一小时学完高等数学（上）：完整讲稿与分镜','','面向零基础大学生，聚焦常见期末题型、公式条件、计算步骤与易错点。不展开证明。无底部字幕。','']
    for c in CHAPTERS:
        rows+=['## '+c['title'],'']
        for s in c['scenes']:
            rows+=['### '+s['key']+' '+s['title'],'']
            for i,r in enumerate(s['rows'],1):rows += [f"{i}. {r['label']}",'',f"$${r['math']}$$" if r['math'] else r['text'],'']
            for p in s['parts']:rows += [p['text'],'',f"持续高亮：{p['focus']}；显示到第 {p['show']} 行。",'','提示：'+'；'.join(p['notes']),'']
            if s['kind']=='question':rows+=['（四秒思考，答案下一页；需要更久请暂停。）','']
            for tag in s['tags']:assert tag in coverage,tag;coverage[tag].append(s['key'])
    assert len(CHAPTERS)==10 and all(coverage.values()),[k for k,v in coverage.items() if not v]
    d=dict(title='一小时学完高等数学（上）',audience='零基础大学生；常见期末基础题与及格目标',subtitles=False,topics=TOPICS,chapters=CHAPTERS)
    (ROOT/'public/course.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8');(ROOT/'docs/考点覆盖.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2),encoding='utf8')
    text='\n'.join(rows);(ROOT/'content/完整讲稿.md').write_text(text,encoding='utf8');(out/'完整讲稿.md').write_text(text,encoding='utf8')
    speech=''.join(s['narration'] for c in CHAPTERS for s in c['scenes']);print(json.dumps(dict(chapters=10,topics=len(TOPICS),pages=sum(len(c['scenes']) for c in CHAPTERS),parts=sum(len(s['parts']) for c in CHAPTERS for s in c['scenes']),cjk=len(re.findall('[\u4e00-\u9fff]',speech))),ensure_ascii=False))
