"""Deliver editable Python sources, exercises and reusable audio without account credentials."""
import json,pathlib,re,shutil,sys,zipfile
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
TEXT={'.py','.mjs','.tsx','.ts','.json','.md','.txt','.example','.gitignore','.hash'}
def scan(p):
    if p.suffix.lower() not in TEXT and p.name!='.gitignore':return
    for pattern in (rb'sk-[A-Za-z0-9_.-]{24,}',rb'llm-[A-Za-z0-9]{10,}'):
        if re.search(pattern,p.read_bytes()):raise ValueError('Credential pattern in '+p.name)
def clock(seconds):
    n=int(seconds);h,n=divmod(n,3600);m,s=divmod(n,60);return f'{h:02}:{m:02}:{s:02}'
def main():
    report=json.loads((ROOT/'build/final-validation.json').read_text(encoding='utf-8'));assert report['allPassed']
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'));t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf-8'));duration=clock(round(report['durationSeconds']))
    rows=['# Python 课堂练习与答案','','面向完全零基础学生。每题朗读后保留四秒思考，完整脚本和初始文件见 Python示例。','']
    for c in course['chapters']:
        q=next((s for s in c['scenes'] if s['kind']=='question'),None);a=next((s for s in c['scenes'] if s['kind']=='answer'),None)
        if not q:continue
        rows.extend(['## '+c['title']+' · '+c['english'],'','题目：'+q['sourceNarration'],'','```python',q['code'],'```','','原题验证结果：','```text',q['output'].rstrip(),'```','','答案与原因：'+a['sourceNarration'],'','核对、修正或对比代码：','```python',a['code'],'```','','上方对比代码的验证结果：','```text',a['output'].rstrip(),'```',''])
    (DEL/'课堂练习与答案.md').write_text('\n'.join(rows),encoding='utf-8')
    source=(ROOT/'content/完整讲稿.md').read_text(encoding='utf-8');timings=['','## 实测章节起点','']+[f"- {clock(c['startFrame']/30)}　{c['title']} · {c['english']}" for c in t['chapters']]
    (DEL/'完整讲稿.md').write_text(source+'\n'+'\n'.join(timings)+'\n',encoding='utf-8')
    shutil.copy2(ROOT/'README.md',DEL/'制作与练习说明.md');shutil.copy2(ROOT/'docs/练习指南.md',DEL/'练习指南.md')
    notes=['# 成片验收说明','',f'成片时长：{duration}（{report["durationSeconds"]:.3f} 秒）。','',
        f'- {report["chapters"]} 章、{report["scenes"]} 个分镜、{report["questionHolds"]} 道原创练习与完整四秒思考。',
        f'- {report["exampleCases"]} 个完整脚本通过；{report["normalPrograms"]} 个正常程序，{report["expectedSyntaxErrors"]} 个预期语法错误，{report["expectedRuntimeExceptions"]} 个预期运行时异常。',
        f'- {report["runCases"]} 组运行检查、{report["propertyAssertionGroups"]} 组状态变化和边界检查通过。文件操作例子另核对实际文件内容。',
        f'- 全部 {report["emptySubtitleAreaStatesChecked"]} 个编码显示状态确认底部无字幕，文件中没有字幕流。',
        f'- 全部 {report["removedFooterTextStatesChecked"]} 个显示状态确认底部短语已移除，仅保留片段编号。',
        f'- {report["verifiedExtraSentencePauses"]} 处句号额外插入 0.1 秒静音；不额外改变逗号停顿。',
        f'- 每章首、中、尾共 {len(report["audioCorrelation"])} 段波形检查确认合成同步，全片严格解码通过。',
        '- 逐页检查代码、中文要点、运行结果、倒计时和答案，并检查实际成片章节首、中、尾及拼接位置。','',
        '自动媒体检查不等于对所有语音逐字人工听辨。本版按要求不提供字幕。','']
    (DEL/'验收说明.md').write_text('\n'.join(notes),encoding='utf-8')
    (DEL/'交付说明.md').write_text(f'# 一小时学习 Python：零基础入门\n\n- 主视频：一小时学习Python_零基础.mp4（{duration}，无字幕）。\n- 章节目录.md：实测章节起点，视频也内嵌章节标记。\n- 完整讲稿.md、课堂练习与答案.md、Python示例/：学习材料。\n- Python视频工程.zip：可编辑源码、原始与处理后的配音、对齐缓存和制作说明。\n- 验收说明.md、验收报告.json：检查结果。\n\n沿用 Rust 第二讲视觉效果，面向完全没有接触编程的学生。工程不含原作者 API Key、Workspace ID、解释器、依赖目录或渲染图片缓存。\n',encoding='utf-8')
    (DEL/'Python示例/README.md').write_text('# Python 3 完整示例\n\n每个目录有 main.py 和预期行为.json。在对应目录执行 python main.py；有些系统使用 py 或 python3。先检查解释器版本。示例兼容 3.11 及以后常见版本，本机以 3.11.6 实测。01-q 预期语法错误；06-q 预期列表越界。输入内容见预期行为.json。10-2 的 budget_tools.py 要与 main.py 保持同目录。文件操作例子在各自目录运行；10-q、10-a 的初始 expenses.txt 都是一行 12 并带换行，再次比较前应恢复初始文件。\n',encoding='utf-8')
    paths=[]
    for folder in ('content','scripts','src','docs'):paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths.extend(ROOT/p for p in ('README.md','requirements.txt','package.json','package-lock.json','tsconfig.json','.gitignore','.env.example','public/course.json','public/timeline.json'))
    keys={s['key'] for s in t['scenes']}
    for folder,ext in [('public/audio',{'.json','.wav','.hash'}),('public/audio_original',{'.json','.mp3'})]:
        paths.extend(p for p in (ROOT/folder).iterdir() if p.is_file() and (p.stem in keys or p.name.endswith('.scaled.wav') and p.name[:-11] in keys or p.suffix=='.hash' and p.name.split('.')[0] in keys) and p.suffix in ext)
    paths.extend((ROOT/'build/alignment').glob('*.json'))
    paths.extend(ROOT/'build'/p for p in ('audio-settings.json','audio-alignment.json','example-validation.json','property-validation.json','final-validation.json'))
    paths=sorted(set(paths))
    for p in paths:scan(p)
    extra=[p for p in DEL.rglob('*') if p.is_file() and p.suffix in {'.md','.json','.py','.txt'} and '__pycache__' not in p.parts]
    for p in extra:scan(p)
    archive=DEL/'Python视频工程.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        for p in paths:z.write(p,'Python一小时制作工程/'+p.relative_to(ROOT).as_posix())
        for p in extra:z.write(p,'配套学习资料/'+p.relative_to(DEL).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert not any('/node_modules/' in n or '/stills/' in n or n.endswith('.env') for n in z.namelist())
        assert sum(n.endswith('.mp3') for n in z.namelist())==len(keys)
        assert sum(n.endswith('.scaled.wav') for n in z.namelist())==len(keys)
    print('PACKAGED',len(paths),round(archive.stat().st_size/1024**2,1),'MiB; credential scan and CRC passed',flush=True)
if __name__=='__main__':main()
