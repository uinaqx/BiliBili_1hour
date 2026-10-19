import importlib,json,pathlib,sys
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];(ROOT/'public').mkdir(exist_ok=True);(ROOT/'build').mkdir(exist_ok=True);(ROOT/'out').mkdir(exist_ok=True);CONTENT=ROOT/'content';DEL=ROOT/'out';DEL.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(CONTENT));from author import CHAPTERS,CHECKS
for name in ('chapters_a','chapters_b','chapters_c','chapters_d'):
    if (CONTENT/(name+'.py')).exists():importlib.import_module(name)
course=dict(title='一小时学习C语言：零基础入门',language='C11',audience='完全没有编程经验的学生',chapters=CHAPTERS)
(ROOT/'public/course.json').write_text(json.dumps(course,ensure_ascii=False,indent=2),encoding='utf-8')
(CONTENT/'example_manifest.json').write_text(json.dumps(CHECKS,ensure_ascii=False,indent=2),encoding='utf-8')
rows=['# 一小时学习C语言：完整讲稿','','面向没有编程经验的学生；C11。章节时间按实际配音生成。','']
for c in CHAPTERS:
    rows.extend([f"## {c['title']} · {c['english']}",''])
    for s in c['scenes']:
        rows.extend([f"### {s['key']} {s['title']}",'',s['sourceNarration'],''])
        if s['kind']=='question':rows.extend(['（四秒思考；随后核对答案）',''])
        if s['code']:rows.extend(['```c' if s['filename']!='终端命令' else '```powershell',s['code'],'```',''])
        if s['output'] is not None:rows.extend(['运行结果或操作说明：','```text',s['output'].rstrip(),'```',''])
        rows.extend(['画面要点：'+'；'.join(s['notes']),''])
manuscript='\n'.join(rows);(CONTENT/'完整讲稿.md').write_text(manuscript,encoding='utf-8');(DEL/'完整讲稿.md').write_text(manuscript,encoding='utf-8')
spoken=''.join(s['narration'] for c in CHAPTERS for s in c['scenes']);print(json.dumps(dict(chapters=len(CHAPTERS),scenes=sum(len(c['scenes']) for c in CHAPTERS),checks=len(CHECKS),narrationCharacters=len(spoken),cjk=sum('\u4e00'<=x<='\u9fff' for x in spoken)),ensure_ascii=False))
