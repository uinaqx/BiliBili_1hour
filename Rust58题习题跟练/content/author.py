import hashlib,json,pathlib,re,textwrap
ROOT=pathlib.Path(__file__).resolve().parents[1]
INVENTORY=json.loads((ROOT/'references/inventory.json').read_text(encoding='utf8'))
BY={r['number']:r for r in INVENTORY};EXERCISES=[]
GROUPS=[('程序入门与变量',1,8),('函数与条件判断',9,17),('基本类型与动态数组',18,25),('所有权与借用',26,31),('结构体与枚举',32,37),('字符串与哈希表',38,44),('可选值',45,47),('泛型',48,49),('特征与综合练习',50,55),('生命周期',56,58)]
def clean(s):
    return '\n'.join(re.sub(r'\s+//.*$','',x).rstrip() for x in s.splitlines() if x.strip() and not x.lstrip().startswith('//'))
def code(n,variant='solutions',start=None,end=None):
    text=clean((ROOT/'exercises'/variant/BY[n]['file']).read_text(encoding='utf8'))
    rows=text.splitlines();return '\n'.join(rows[slice(start,end)])
def F(n,name,variant='solutions'):
    rows=code(n,variant).splitlines();hits=[i for i,s in enumerate(rows) if re.search(r'\bfn\s+'+re.escape(name)+r'(?:<|\()',s)]
    assert len(hits)==1,(n,name,hits)
    begin=hits[0];depth=0;seen=False
    for end in range(begin,len(rows)):
        depth+=rows[end].count('{')-rows[end].count('}');seen=seen or '{' in rows[end]
        if seen and depth==0:return textwrap.dedent('\n'.join(rows[begin:end+1]))
    raise ValueError((n,name,'Unclosed function'))
def V(title,rows,foot=''):return dict(title=title,rows=[[x] if isinstance(x,str) else x for x in rows],foot=foot)
def P(target,text,visual=None,result=False):return dict(target=target,text=text.strip(),visual=visual,result=result)
def A(code,parts,notes):return dict(code=textwrap.dedent(code).strip(),parts=parts,notes=notes)
def E(n,title,question_code,question_text,question_notes,stages,verify_text,verify_target=None):
    assert n not in [x['number'] for x in EXERCISES]
    EXERCISES.append(dict(number=n,title=title,question_code=textwrap.dedent(question_code).strip(),question_text=question_text.strip(),question_notes=question_notes,stages=stages,verify_text=verify_text.strip(),verify_target=verify_target))
def lines_for(code,target):
    if isinstance(target,list):
        assert all(isinstance(i,int) and 1<=i<=len(code.splitlines()) and code.splitlines()[i-1].strip() for i in target)
        return target
    needles=[target] if isinstance(target,str) else list(target);found=[]
    for needle in needles:
        hits=[i+1 for i,row in enumerate(code.splitlines()) if needle in row]
        assert len(hits)==1,('Authored target must match exactly one visible line',needle,hits,code)
        found+=hits
    return sorted(set(found))
def scene(n,stage,title,display,parts,notes,kind='lesson',output=None,initial=None):
    assert len(display.splitlines())<=13,(n,stage,'Too many visible code lines',len(display.splitlines()))
    for p in parts:p['lines']=lines_for(display,p.pop('target')) if display else []
    r=BY[n];return dict(key=f'rp-{n:02}-{stage}',number=n,exercise=r['name'],section=f'{n:02}',title=f'第 {n:02} 题 · {r["name"]} · {title}',code=display,parts=parts,notes=notes,output=output,kind=kind,hold=4 if kind=='question' else .7,filename=r['file'],excerpt=True,sourceFile=f'exercises/solutions/{r["file"]}',initialVisual=initial,narration=''.join(p['text'] for p in parts),error=None,panic=False,testFailed=False,answer=None,panels=[],focus=[],diagram='practice' if initial or any(p.get('visual') for p in parts) else None)
def write():
    assert sorted(x['number'] for x in EXERCISES)==list(range(1,59))
    checked=json.loads((ROOT/'build/exercise-verification.json').read_text(encoding='utf8'));assert checked['allPassed'];checks={r['number']:r for r in checked['records']}
    chapters=[];allscenes=[]
    for ci,(title,first,last) in enumerate(GROUPS,1):
        c=dict(key=f'{ci:02}',title=title,english='',scenes=[])
        for e in sorted((x for x in EXERCISES if first<=x['number']<=last),key=lambda x:x['number']):
            n=e['number'];q=scene(n,'q',e['title']+'：读题',e['question_code'],[P([1] if n==1 else [i+1 for i,line in enumerate(e['question_code'].splitlines()) if line.strip() and not line.lstrip().startswith('//')],e['question_text'])],e['question_notes'],kind='question');q['answer']=e['title'];q['sourceFile']=f'exercises/original/{BY[n]["file"]}';c['scenes'].append(q)
            for j,a in enumerate(e['stages']):
                c['scenes'].append(scene(n,f'a{j+1}',e['title']+'：分步修改',a['code'],a['parts'],a['notes'],kind='answer',initial=a['parts'][0].get('visual')))
            final=e['stages'][-1];result=checks[n]['variants']['solutions']
            if BY[n]['mode']=='test':output=f"test result: ok. {result['testsPassed']} passed; 0 failed"
            else:
                output=result['stdout'].strip()
                if n==1:output='Hello and\n...\nThis exercise compiles successfully.'
                elif len(output.splitlines())>3:output='\n'.join(output.splitlines()[:2])+'\n...（其余输出见配套记录）'
                elif not output:output='运行结束：未打印内容；退出码 0'
            target=e['verify_target'] or final['parts'][-1]['lines']
            # parts were resolved above; final target is explicitly the last authored target.
            p=dict(target=target,text=e['verify_text'],visual=final['parts'][-1].get('visual'),result=True)
            c['scenes'].append(scene(n,'v',e['title']+'：运行验证',final['code'],[p],['以实际编译或测试结果为准','合上答案，回到原题独立完成'],kind='answer',output=output,initial=p['visual']))
        chapters.append(c);allscenes+=c['scenes']
    overview=scene(1,'overview','课程导学','',[
        P([],'这部跟练课完整讲解文件夹里的五十八道习题，从变量、函数和条件，逐步走到所有权、特征与生命周期。即使刚接触 Rust，也可以跟着例子补足需要的知识。每道题先读目标与限制，再暂停自己动手，恢复播放后一起分析修改，最后用实际运行或测试核对。'),
        P([],'配套文件保留原题与带详细注释的参考答案。视频中长文件会拆开讲，窗口只显示当前需要的部分。正常程序看运行输出，测试题看断言是否通过，编译错误与测试失败要分别判断。四秒思考只是提示，需要更长时间就暂停，不必赶着记住答案。')
    ],['按原编号完整覆盖 58 题','先独立动手，再核对答案','看清编译、运行与测试的区别'],kind='overview')
    overview.update(key='rp-overview',number=0,section='导学',exercise='',sourceFile=None)
    chapters[0]['scenes'].insert(0,overview);allscenes.insert(0,overview)
    d=dict(title='Rust 基础 58 题习题跟练',language='Rust 1.98.1 · Edition 2021',audience='零基础大学生，逐题补足必要知识',subtitles=False,chapters=chapters)
    (ROOT/'public/course.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
    rows=['# Rust 基础 58 题习题跟练：完整讲稿与分镜','','逐题读题、暂停动手、修改与运行验证。无底部字幕。','']
    for c in chapters:
        rows+=['## '+c['title'],'']
        for s in c['scenes']:
            rows+=['### '+s['title'],'','```rust',s['code'],'```','']
            for p in s['parts']:rows += [p['text'],'',f"高亮行：{p['lines']}",'']
            if s['kind']=='question':rows+=['（四秒思考；需要更久请暂停视频，答案在下一页。）','']
            if s['output']:rows+=['实际结果：','```text',s['output'],'```','']
    text='\n'.join(rows);(ROOT/'content/完整讲稿.md').write_text(text,encoding='utf8');(ROOT/'out/完整讲稿.md').write_text(text,encoding='utf8')
    speech=''.join(s['narration'] for s in allscenes);print(json.dumps(dict(chapters=len(chapters),exercises=58,pages=len(allscenes),parts=sum(len(s['parts']) for s in allscenes),cjk=sum('\u4e00'<=c<='\u9fff' for c in speech)),ensure_ascii=False))
