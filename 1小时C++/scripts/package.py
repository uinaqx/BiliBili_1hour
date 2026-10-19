"""Package editable sources and reusable audio; reject credential-shaped values."""
import json,pathlib,re,shutil,sys,zipfile
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def scan(p):
    if p.suffix.lower() not in {'.py','.mjs','.tsx','.ts','.json','.md','.txt','.example','.gitignore','.cpp'}:return
    for pattern in (rb'sk-[A-Za-z0-9_.-]{24,}',rb'llm-[A-Za-z0-9]{10,}'):
        if re.search(pattern,p.read_bytes()):raise ValueError('Credential pattern in '+p.name)
def clock(seconds):
    n=int(seconds);h,n=divmod(n,3600);m,s=divmod(n,60);return f'{h:02}:{m:02}:{s:02}'
def main():
    report=json.loads((ROOT/'build/final-validation.json').read_text(encoding='utf-8'));assert report['allPassed']
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'));t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf-8'));duration=clock(round(report['durationSeconds']))
    rows=['# C++ 课堂练习与答案','','每题朗读后保留四秒思考。完整上下文见 C++示例。','']
    for c in course['chapters']:
        q=next((s for s in c['scenes'] if s['kind']=='question'),None);a=next((s for s in c['scenes'] if s['kind']=='answer'),None)
        if not q:continue
        rows.extend(['## '+c['title']+' · '+c['english'],'','题目：'+q['sourceNarration'],'','```cpp',q['code'],'```','','答案与原因：'+a['sourceNarration'],'','核对或修正代码：','```cpp',a['code'],'```','','```text',a['output'].rstrip(),'```',''])
    (DEL/'课堂练习与答案.md').write_text('\n'.join(rows),encoding='utf-8')
    source=(ROOT/'content/完整讲稿.md').read_text(encoding='utf-8');timings=['','## 实测章节起点','']+[f"- {clock(c['startFrame']/30)}　{c['title']} · {c['english']}" for c in t['chapters']]
    (DEL/'完整讲稿.md').write_text(source+'\n'+'\n'.join(timings)+'\n',encoding='utf-8')
    shutil.copy2(ROOT/'README.md',DEL/'制作与练习说明.md');shutil.copy2(ROOT/'docs/练习指南.md',DEL/'练习指南.md')
    notes=['# 成片验收说明','',f'成片时长：{duration}（{report["durationSeconds"]:.3f} 秒）。','',f'- {report["chapters"]} 章、{report["scenes"]} 个分镜、10 道原创课堂练习与四秒思考。',f'- {report["exampleCases"]} 个完整代码案例检查通过；{report["normalPrograms"]} 个可运行程序，{report["expectedCompileErrors"]} 个预期编译错误。',f'- {report["runCases"]} 组运行结果、{report["propertyAssertionGroups"]} 组对象关系与边界断言通过。',f'- 全部 {report["emptySubtitleAreaStatesChecked"]} 个编码显示状态确认底部无字幕，文件中没有字幕流。',f'- 每章首、中、尾共 {len(report["audioCorrelation"])} 段波形检验合成同步，全片严格解码通过。','- 逐页检查代码、中文要点、运行结果、倒计时与答案，并抽查实际成片章节首、中、尾及拼接位置。','','自动音频和时间检查不能代替逐字人工听辨；本版按要求不提供字幕。','']
    (DEL/'验收说明.md').write_text('\n'.join(notes),encoding='utf-8')
    (DEL/'交付说明.md').write_text(f'# 一小时学习 C++：基础与面向对象\n\n- 主视频：一小时学习C++_基础与面向对象.mp4（{duration}，无字幕）。\n- 章节目录.md：实测章节起点，视频也内嵌章节标记。\n- 完整讲稿.md、课堂练习与答案.md、C++示例/：配套学习材料。\n- C++视频工程.zip：可编辑源码、原始与处理后的配音、缓存记录和制作说明。\n- 验收说明.md、验收报告.json：检查结果。\n\n沿用 Rust 第二讲画面；面向有 C 基础、初学 C++ 的学生。工程不含原作者 API Key 或 Workspace ID。\n',encoding='utf-8')
    (DEL/'C++示例/README.md').write_text('# C++14 完整示例\n\n每个目录有 main.cpp 与预期行为.json。进入目录后执行 g++ -std=c++14 -Wall -Wextra main.cpp -o example.exe，再执行 .\\example.exe。01-1 输入 80 正常成功，输入 x 预期返回 1。compile_error 是刻意保留的错误示例，不能正常运行；reorder_warning 会产生初始化顺序警告，实际顺序见结果。\n',encoding='utf-8')
    paths=[]
    for folder in ('content','scripts','src','docs'):paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths.extend(ROOT/p for p in ('README.md','requirements.txt','package.json','package-lock.json','tsconfig.json','.gitignore','.env.example','public/course.json','public/timeline.json'))
    keys={s['key'] for s in t['scenes']}
    for folder,ext in [('public/audio',{'.json','.wav'}),('public/audio_original',{'.json','.mp3'})]:paths.extend(p for p in (ROOT/folder).iterdir() if p.is_file() and p.stem in keys and p.suffix in ext)
    paths.extend((ROOT/'build/alignment').glob('*.json'))
    paths.extend(ROOT/'build'/p for p in ('audio-settings.json','audio-alignment.json','example-validation.json','property-validation.json','final-validation.json'))
    # Retain final-tempo PCM and fingerprints so packaged sources can render offline.
    paths.extend(p for p in (ROOT/'public/audio').iterdir() if p.suffix=='.hash' or p.name.endswith('.scaled.wav'))
    for p in paths:scan(p)
    archive=DEL/'C++视频工程.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        for p in sorted(set(paths)):z.write(p,'C++一小时制作工程/'+p.relative_to(ROOT).as_posix())
        for p in DEL.rglob('*'):
            if p.is_file() and p.suffix in {'.md','.json','.cpp'}:scan(p);z.write(p,'配套学习资料/'+p.relative_to(DEL).as_posix())
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    print('PACKAGED',len(set(paths)),round(archive.stat().st_size/1024**2,1),'MiB; credential scan and CRC passed',flush=True)
if __name__=='__main__':main()
