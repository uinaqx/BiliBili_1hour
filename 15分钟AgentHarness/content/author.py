import json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parents[1];CHAPTERS=[]
KINDS={'cover','architecture','loop','sequence','contract','dispatch','window','compact','gate','injection','retry','checkpoint','dag','cancel','case','trace','eval','code','summary'}
def C(title):
    c=dict(key=f'{len(CHAPTERS)+1:02}',title=title,scenes=[]);CHAPTERS.append(c);return c
def V(kind,phase,**data):assert kind in KINDS;return dict(kind=kind,phase=phase,**data)
def M(anchor,target,seconds=3):return dict(anchor=anchor,target=target,seconds=seconds)
def P(text,visual,notes,moves,think=False):return dict(text=text.strip(),visual=visual,notes=notes,moves=moves,think=think,lines=[],result=False)
def S(c,title,parts,sources):
    assert 1<=len(parts)<=2
    for p in parts:
        assert 1<=len(p['notes'])<=3
        assert p['moves'] or p['visual']['kind']=='cover'
        last=0
        for m in p['moves']:
            assert p['text'].count(m['anchor'])==1 and last<m['target']<=1,(title,m);last=m['target']
    scene=dict(key=f'ah-{c["key"]}-{len(c["scenes"])+1:02}',title=title,parts=parts,sources=sources,kind='overview' if parts[0]['visual']['kind']=='cover' else 'lesson',hold=.65,narration=''.join(p['text'] for p in parts));c['scenes'].append(scene);return scene
def write():
    assert len(CHAPTERS)==10
    (ROOT/'public').mkdir(exist_ok=True);(ROOT/'build').mkdir(exist_ok=True)
    (ROOT/'out').mkdir(parents=True,exist_ok=True)
    d=dict(title='15分钟讲清Agent Harness底层原理',audience='了解大模型聊天，尚不熟悉智能体运行时的学生',subtitles=False,chapters=CHAPTERS)
    (ROOT/'public/course.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8');rows=['# 15分钟讲清Agent Harness底层原理：完整讲稿与分镜','','讲通用执行机制，厂商实现只作参考。动态图表示外部可观察事件，不表示隐藏推理。','']
    for c in CHAPTERS:
        rows+=['## '+c['title'],'']
        for s in c['scenes']:
            rows+=['### '+s['key']+' '+s['title'],'','来源：'+', '.join(s['sources']),'']
            for i,p in enumerate(s['parts']):
                rows += [p['text'],'','图示：'+p['visual']['kind']+' / '+p['visual']['phase'],'','要点：'+'；'.join(p['notes']),'']
                for m in p['moves']:rows += [f"动画锚点：{m['anchor']} → 进度 {m['target']}；连续变化 {m['seconds']} 秒。",'']
                if p['think']:rows+=['（4秒思考，状态保留，下一段揭晓。）','']
    text='\n'.join(rows);(ROOT/'content/完整讲稿.md').write_text(text,encoding='utf8');(ROOT/'out/完整讲稿.md').write_text(text,encoding='utf8')
    speech=''.join(s['narration'] for c in CHAPTERS for s in c['scenes']);print(json.dumps(dict(chapters=len(CHAPTERS),pages=sum(len(c['scenes']) for c in CHAPTERS),parts=sum(len(s['parts']) for c in CHAPTERS for s in c['scenes']),cjk=len(re.findall('[\u4e00-\u9fff]',speech)),thinkPauses=sum(p['think'] for c in CHAPTERS for s in c['scenes'] for p in s['parts'])),ensure_ascii=False))
