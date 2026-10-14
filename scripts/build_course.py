"""Turn the approved manuscript into scenes, retaining every spoken paragraph."""
import copy, hashlib, json, pathlib, re, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1]; DEL=ROOT/'out'
DEL.mkdir(parents=True,exist_ok=True); (ROOT/'public').mkdir(exist_ok=True)
config=json.loads((ROOT/'project.json').read_text(encoding='utf-8'))
document=ROOT/'content'/'审核通过文案.md'; text=document.read_text(encoding='utf-8')
English=['导学','variables','primitive_types','functions','if','move_semantics','structs','enums','options','vecs','strings','hashmaps','generics','traits','lifetimes','综合回顾']
Titles=['从一个小需求开始','给数据起名字','数据也分种类','把步骤写成函数','根据情况作决定','交出去、复制或借一下','把学生信息放在一起','几种情况分别处理','有结果或没有结果','保存一组成绩','保存与读取文字','根据姓名查成绩','同样做法、不同类型','说明能做什么','借来的数据必须还在','连成一个小程序']
English=config['chapterEnglish'];Titles=config['chapterTitles']
Targets=[1,3,4,3,2,9,4,3,4,4,4,4,4,4,5,2]
chapters=[]; units=[]; chapter=None; section='00'; heading='开场'; mode=False; current=None; pending_meta=None; pending_picture=''
def new_unit():
    return {'section':section,'title':heading,'code':'','narrationParts':[],'picture':pending_picture,'meta':None,'kind':'lesson','hold':2}
def flush():
    global current,mode
    if current and current['narrationParts']:
        current['narration']='\n\n'.join(current.pop('narrationParts'))
        chapter['scenes'].append(current)
    current=None; mode=False
rows=text.splitlines(); index=0
while index<len(rows):
    line=rows[index]; index+=1
    cm=re.match(r'## (\d{2}) (.*?)｜',line)
    if cm:
        if chapter:flush()
        ci=int(cm.group(1));section=cm.group(1);heading=cm.group(2);pending_picture='';pending_meta=None
        chapter={'key':f'{ci:02}','title':Titles[ci],'english':English[ci],'targetMinutes':Targets[ci],'scenes':[]}
        chapters.append(chapter);current=new_unit();continue
    if line.startswith('---') or (line.startswith('## ') and not cm):
        if chapter:flush()
        if line.startswith('---'):break
    if not chapter:continue
    sm=re.match(r'### (\d{2}-\d+) (.*)',line)
    if sm:
        flush();section=sm.group(1);heading=sm.group(2);pending_meta=None;pending_picture='';current=new_unit();continue
    mm=re.match(r'<!-- rust-check: (\{.*\}) -->',line)
    if mm:pending_meta=json.loads(mm.group(1));mode=False;continue
    if line.startswith('【画面'):
        flush();pending_picture=line;current=new_unit();continue
    if line.startswith('```'):
        language=line[3:];code=[]
        while index<len(rows) and not rows[index].startswith('```'):
            code.append(rows[index]);index+=1
        index+=1
        if current is None:current=new_unit()
        current['code']='\n'.join(code);current['meta']=pending_meta;current['codeLanguage']=language;mode=False;continue
    if line.startswith('【停顿】'):
        if current:
            prior=copy.deepcopy(current);current['kind']='question';current['hold']=4;flush()
            current=new_unit();current.update({k:prior[k] for k in ['code','meta','picture']});current['kind']='answer'
        continue
    if line.startswith('【口播】'):
        if current is None:current=new_unit()
        mode=True;continue
    if mode and line.strip():current['narrationParts'].append(line.strip())
if chapter:flush()

all_blocks={}
for c in chapters:
    for u in c['scenes']:
        if u['meta']:all_blocks[u['meta']['id']]=u['code']

# A few concept-only screens explicitly refer to the preceding program.
for c in chapters:
    for u in c['scenes']:
        if not u['code'] and u['section']=='07-2':u['code']=all_blocks['07-1'];u['meta']={'kind':'run','stdout':'成绩：85\n'}
        if u['section']=='13-6':
            u['code']='struct Course;\n\nshow(&Course);' if u['kind']=='question' else 'impl Introduce for Course {\n    fn introduction(&self) -> String {\n        String::from("课程：Rust 基础")\n    }\n}\n\nshow(&Course);'
            u['meta']={'kind':'error','error':'E0277'} if u['kind']=='question' else {'kind':'run','stdout':'课程：Rust 基础\n'}
        if u['section']=='14-6':u['code']=all_blocks['14-1'] if u['kind']=='question' else all_blocks['14-2'];u['meta']={'kind':'error','error':'E0597'} if u['kind']=='question' else {'kind':'run','stdout':'小林\n'}
        if u['section']=='06-5':u['meta']={'kind':'error','error':'E0596'} if u['kind']=='question' else {'kind':'run','stdout':'小林 85\n'}
        if u['kind']=='answer':
            if u['section']=='03-4':u['code']=u['code'].replace('n * 2;','n * 2');u['meta']={'kind':'run','stdout':'12\n'}
            if u['section']=='04-3':u['code']=u['code'].replace('        1','        "有成绩"');u['meta']={'kind':'run','stdout':'有成绩\n'}
            if u['section']=='06-5':u['code']=u['code'].replace('let student =','let mut student =')
            if u['section']=='07-3':u['code']=u['code'].replace('Answer::Yes => println!("同意"),','Answer::Yes => println!("同意"),\n        Answer::No => println!("不同意"),');u['meta']={'kind':'run','stdout':'同意\n'}
            if u['section']=='12-5':u['code']='make_pair(80, 90)       // 两个参数同类型\n\n// make_pair(80, "小林")  // 类型不同，不能这样调用'

Notes={
'00':['从姓名与成绩开始','每次只增加一个新点','用例子理解概念'],
'01-1':['let：创建一个变量','score 保存 80','println! 显示结果'],
'01-2':['默认不能重新赋值','需要修改时加 mut','类型仍然保持一致'],
'01-3':['再次写 let 是新声明','同名变量称为“遮蔽”','const 表示固定设置'],
'02-1':['整数、小数、真假、字符','冒号后面写类型','先想清楚要存什么'],
'02-2':['整数除法不保留小数','不同类型先明确转换','检查目标类型是否装得下'],
'02-3':['元组：几项数据在一起','数组：长度固定、元素同类型','切片：借用原数据的一段'],
'03-1':['参数是函数的输入','箭头后面写结果类型','return 把结果交回来'],
'03-2':['最后一行可以提供结果','这种写法末尾不加分号','明确写 return 也可以'],
'03-3':['只显示信息','没有需要接住的成绩','返回类型写作 ()'],
'04-1':['条件得到 true 或 false','成立时执行 if 分支','否则执行 else 分支'],
'04-2':['if 也能选出一个值','分支末尾保留结果','两条分支类型一致'],
'05-1':['普通整数赋值会复制','String 赋值会交出数据','这次交接称为“移动”'],
'05-2':['谁拥有，谁负责清理','移动后由新拥有者负责','范围结束时自动清理'],
'05-3':['clone 明确创建副本','String 内容会被复制','两个名字各自拥有数据'],
'05-4':['参数 String 接收数据','调用也会发生移动','原来的名字不能再用'],
'05-5':['& 表示借用','只看一下，拥有者不变','显示以后还能继续用'],
'05-6':['只读取时可以一起看','&mut 允许通过借用修改','修改借用需要单独使用'],
'05-7':['先完成读取，再修改','检查引用的最后使用','读取和修改不要冲突'],
'06-1':['Student 保存一名学生','字段有名字和类型','用点访问具体字段'],
'06-2':['impl 添加相关功能','&self 借用当前学生','passed 判断是否及格'],
'06-3':['&mut self 允许修改','Student::new 创建对象','Self 表示当前类型'],
'06-4':['重新填写不同字段','..first 沿用其他字段','仍要区分复制与移动'],
'07-1':['enum 列出几种情况','一种情况可以附带数据','match 分别处理'],
'07-2':['先看当前是哪种情况','取出附带的数据','所有可能情况要处理'],
'08-1':['Some：有值','None：没有值','没有成绩不等于零分'],
'08-2':['if let 只关心一种情况','取出 Some 中的数据','没有值时不执行这段'],
'08-3':['有值时使用原值','没有值时使用默认值','默认值要符合实际含义'],
'08-4':['unwrap 要求必须有值','None.unwrap() 会失败','这是运行时问题'],
'09-1':['Vec 的长度可以变化','push 增加，pop 取末尾','空集合的 pop 返回 None'],
'09-2':['位置从零开始','get 查询可能不存在的位置','查询结果使用 Option'],
'09-3':['&scores 借来读取','&mut scores 借来修改','*score 修改指向的元素'],
'10-1':['String 拥有文字','&str 借来读取文字','只读函数通常接收 &str'],
'10-2':['push_str 追加文字','加号会接走左侧 String','右侧可以借用'],
'10-3':['UTF-8 保存文字','len 统计字节数量','chars 依次读取字符'],
'10-4':['切片位置按字节计算','边界必须保留完整编码','不确定时先用 chars'],
'11-1':['姓名是键，成绩是值','insert 放入一条记录','get 按姓名查询'],
'11-2':['同一个键只有一个当前值','再次 insert 会更新','历史成绩需要另外设计'],
'11-3':['entry 找到对应记录','不存在时先放入零','每遇到一次就增加一'],
'11-4':['String 插入后可能被接走','整数等简单值会复制','集合也遵守所有权规则'],
'12-1':['同一种做法写一次','使用时再确定类型','泛型帮助复用代码'],
'12-2':['T 代表一个类型位置','一次调用的 T 保持一致','从传入数据确定类型'],
'12-3':['结构体也能使用 T','方法可以返回 &T','Vec 与 Option 也是泛型'],
'12-4':['使用大于号需要比较能力','给 T 写明对应要求','满足要求才允许调用'],
'13-1':['不同类型都能给出介绍','数据和过程可以不同','trait 约定共同能力'],
'13-2':['先写方法约定','再让 Student 实现它','实现中补上具体过程'],
'13-3':['show 只要求能介绍自己','约束说明类型所需能力','通过 &T 借用数据'],
'13-4':['trait 可以提供默认做法','不另外编写就使用默认','需要时再提供自己的版本'],
'13-5':['where 换个位置写要求','derive 帮助生成常见能力','Debug 方便查看数据'],
'14-1':['引用依赖原来的数据','数据结束后不能再访问','调整数据的实际保存范围'],
'14-2':['返回的引用来自输入','标记说明输入输出关系','不复制，也不延长寿命'],
'14-3':['second 在内层结束','外面还使用结果就有风险','标记不能让数据继续存在'],
'14-4':['关系明确时可以省略写法','只有一个输入时关联明确','检查仍然会进行'],
'14-5':['NameTag 借用已有文字','使用时原文字必须有效','需要独立保存就用 String'],
'15-1':['用 Student 组织信息','用 Option 表示暂缺成绩','借用 Vec 逐个查看'],
}

def diagram(u):
    sec=u['section']; code=u['code']
    if sec=='03-1':return 'function'
    if sec in ['06-1','06-2']:return 'student'
    if sec=='06-3':return 'student-changing'
    if sec in ['07-1','07-2']:return 'states'
    if sec in ['08-1','08-2','08-3']:return 'option'
    if sec=='09-1':return 'vec-changing'
    if sec=='09-2':return 'vec'
    if sec=='11-1':return 'hashmap'
    if sec=='11-2':return 'hashmap-update'
    if sec=='11-3':return 'counts'
    if sec in ['12-1','12-2','12-3']:return 'generic'
    if sec in ['13-1','13-2','13-3']:return 'trait'
    if sec=='05-1':return 'copy' if 'another = score' in code else 'move'
    if sec=='05-2':return 'scope'
    if sec=='05-3':return 'clone'
    if sec=='05-4':return 'call'
    if sec=='05-5':return 'borrow'
    if sec=='05-6':return 'mut-borrow' if 'add_suffix' in code else 'shared'
    if sec=='05-7':return 'conflict' if 'println!("{view}");' in code and code.index('push_str')<code.index('println!("{view}");') else 'nll'
    if sec in ['10-3','10-4']:return 'utf8'
    if sec=='10-5':return 'utf8-hello'
    if sec=='14-1':return 'dangling' if '\n    {' in code else 'lifetime'
    if sec=='14-2':return 'lifetime'
    if sec=='14-3':return 'lifetime-invalid'
    return None

for ci,c in enumerate(chapters):
    counts={}
    for u in c['scenes']:
        sec=u['section'];counts[sec]=counts.get(sec,0)+1;u['key']='v2-'+sec+'-'+str(counts[sec])
        if ci==0:u['key']='v2-opening';u['hold']=1
        u['notes']=Notes.get(sec,['先看这段代码在做什么','把每一步的结果连起来','亲手改一处再运行'])
        if u['kind']=='question':u['notes']=['先自己想一想','用刚才的例子作判断','四秒后一起看答案']
        if u['kind']=='answer':u['notes']={
            '01-4':['第二次 let 创建新变量','3 × 2 得到 6','因此不需要 mut'],
            '02-4':['位置 2 是第三项','第三个成绩是 90','一共有 4 个元素'],
            '03-4':['最后的结果不要加分号','也可以明确写 return','修正后返回 12'],
            '04-3':['两个分支类型必须一致','改条件不能取消检查','修正后都返回文字'],
            '05-8':['&name 表示借用','拥有者仍然是 name','两次输出都可以'],
            '06-5':['方法会修改成绩','变量声明需要 mut','修正后得到 85'],
            '07-3':['遗漏了 No 这种情况','match 要处理完整','补上 No 对应的分支'],
            '08-5':['Some(0) 是真的有值','None 才使用默认值','依次输出 0 和 60'],
            '09-4':['get 返回 None','没有第五个成绩','这是正常处理结果'],
            '10-5':['两个汉字共 6 字节','chars 在这里得到 2 项','字节数与字符数分开看'],
            '11-5':['存在记录就保留原值','2 再增加 7','结果是 9'],
            '12-5':['同一次调用的 T 一致','两个整数可以组成一对','整数与文字不能混用'],
            '13-6':['Course 还缺少所需能力','实现 Introduce','补上 introduction 方法'],
            '14-6':['标记不会延长数据寿命','真正调整保存或使用范围','引用不能依赖失效数据'],
        }.get(sec,['回到关键一行','把原因说清楚','看修正后的版本'])
        meta=u['meta'] or {}
        u['error']=meta.get('error') if meta.get('kind')=='error' else None
        u['panic']=meta.get('kind')=='panic';u['output']=meta.get('stdout') if meta.get('kind')=='run' else None
        if meta.get('kind')=='part' and 'fn main' in u['code']:
            u['output']='学生：小林\n' if ci==13 else '小林：80\n'
        u['diagram']=diagram(u);u['compare']=None;u['focus']=[]
        u['panels']=[]
        if sec=='01-3':u['panels']=[{'cue':'另外，像课程的满分','code':'const MAX_SCORE: u32 = 100;\n\nfn main() {\n    println!("{MAX_SCORE}");\n}','notes':['const 表示固定设置','声明时需要写类型','名字通常用大写字母'],'output':'100\n'}]
        if sec=='02-3':
            u['code']='fn main() {\n    let student = (18, 85);\n    let (age, score) = student;\n    println!("{age} {score}");\n}'
            u['panels']=[{'cue':'如果我们要保存三门课的成绩','code':'fn main() {\n    let scores = [80, 85, 90];\n    println!("{} {}", scores[1], scores.len());\n    let first_two = &scores[..2];\n    println!("{}", first_two[0]);\n}','notes':['数组长度固定','位置从零开始','切片借用数组的一段'],'output':'85 3\n80\n'}]
            u['output']='18 85\n'
        if sec=='10-2':u['panels']=[{'cue':'如果想保留两个原字符串','code':'fn main() {\n    let first = String::from("小林");\n    let second = String::from("，欢迎");\n    let message = format!("{first}{second}");\n    println!("{message}");\n    println!("{first} {second}");\n}','notes':['format! 创建新 String','这里保留两个原字符串','按实际需求选择写法'],'output':'小林，欢迎\n小林 ，欢迎\n'}]
        parts=u['narration'].split('\n\n');u['stageCues']=[p[:12] for p in parts[1:4]]
        if sec=='09-1':u['stageCues']=['这里用 vec','push 把九十加到末尾','pop 从末尾取出一个元素']
        u['sourceNarration']=u['narration']
        # Only pronunciation spelling is normalized; preserve the approved words.
        u['narration']=u['narration'].replace('C/C++','C 和 C 加加').replace('C++','C 加加')
        units.append(u)

# Preserve the exact approved source as well as the machine-readable course.
course={'title':'一小时学习 Rust：初学者版','edition':'2024','compiler':'rustc 1.98.1','voice':'longanlufeng','ttsModel':'qwen-audio-3.0-tts-plus','fps':30,'width':1920,'height':1080,'approvedManuscriptSha256':hashlib.sha256(document.read_bytes()).hexdigest(),'chapters':chapters}
course.update(title=config['title'],edition=config['edition'],compiler=config['compiler'])
(ROOT/'public/course.json').write_text(json.dumps(course,ensure_ascii=False,indent=2),encoding='utf-8')
original_spoken=[];reading=False
for line in text.splitlines():
    if line.startswith('【口播】'):reading=True;continue
    if line.startswith(('【画面','【停顿','<!--','### ','## ','---')):reading=False
    if reading and line.strip():original_spoken.append(line.strip())
actual_spoken=[p for u in units for p in u['sourceNarration'].split('\n\n')]
assert actual_spoken==original_spoken, 'Spoken content differs from the approved manuscript'
assert len(chapters)==16 and sum(u['kind']=='question' for u in units)==14
(DEL/'完整讲稿.md').write_text(text,encoding='utf-8')
story=['# 初学者版：分镜清单','','配音逐段对应审核通过文案。']
story.extend(f"\n- {u['key']}｜{u['title']}｜{u['kind']}｜{u['picture']}" for u in units)
(DEL/'分镜清单.md').write_text('\n'.join(story),encoding='utf-8')
print(json.dumps({'chapters':len(chapters),'scenes':len(units),'questions':14,'narrationCharacters':sum(len(u['narration']) for u in units),'approvedNarrationPreserved':True},ensure_ascii=False))
