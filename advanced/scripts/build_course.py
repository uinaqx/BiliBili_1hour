import importlib,json,pathlib,sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1];CONTENT=ROOT/'content'
(ROOT/'public').mkdir(exist_ok=True)
DEL=ROOT/'out';DEL.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(CONTENT))
for name in ('intro','chapters_a','chapters_b','chapters_c','closing'):
    if (CONTENT/(name+'.py')).exists():importlib.import_module(name)
from author import CHAPTERS,CHECKS
course=dict(title='Rust 进阶基础：九个主题',edition='2024',compiler='rustc 1.98.1',voice='longanlufeng',ttsModel='qwen-audio-3.0-tts-plus',fps=30,width=1920,height=1080,chapters=CHAPTERS)
(ROOT/'public/course.json').write_text(json.dumps(course,ensure_ascii=False,indent=2),encoding='utf-8')
(CONTENT/'example_manifest.json').write_text(json.dumps(CHECKS,ensure_ascii=False,indent=2),encoding='utf-8')
rows=['# Rust 进阶基础：完整讲稿与分镜','','面向已学过上一部基础内容的初学者和大学生。以下为本片制作讲稿。','']
for c in CHAPTERS:
    rows.append(f'\n## {c["key"]} {c["title"]} · {c["english"]}')
    for s in c['scenes']:
        rows.extend([f'\n### {s["section"]} {s["title"]}', '\n【画面】'+'；'.join(s['notes'])])
        if s['code']:rows.append('\n```rust\n'+s['code']+'\n```')
        if s['excerpt']:rows.append('\n以上为节选；配套示例包含完整可编译上下文。')
        rows.extend(['\n【口播】\n'+s['sourceNarration']])
        if s['kind']=='question':rows.append('\n【思考停顿】4 秒')
        if s['output'] is not None:rows.append('\n【运行或检查结果】\n```text\n'+s['output'].rstrip()+'\n```')
text='\n'.join(rows)+'\n'
(CONTENT/'完整讲稿.md').write_text(text,encoding='utf-8');(DEL/'完整讲稿.md').write_text(text,encoding='utf-8')
spoken=''.join(s['sourceNarration'] for c in CHAPTERS for s in c['scenes'])
print(json.dumps(dict(chapters=len(CHAPTERS),scenes=sum(len(c['scenes']) for c in CHAPTERS),checks=len(CHECKS),narrationCharacters=len(spoken),cjk=sum('\u4e00'<=x<='\u9fff' for x in spoken)),ensure_ascii=False))
