"""Package editable Java sources and reusable audio; reject credential-shaped values."""
import json,pathlib,re,shutil,sys,zipfile
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
TEXT={'.py','.mjs','.tsx','.ts','.json','.md','.txt','.example','.gitignore','.java','.hash'}
def scan(p):
    if p.suffix.lower() not in TEXT and p.name!='.gitignore':return
    for pattern in (rb'sk-[A-Za-z0-9_.-]{24,}',rb'llm-[A-Za-z0-9]{10,}'):
        if re.search(pattern,p.read_bytes()):raise ValueError('Credential pattern in '+p.name)
def clock(seconds):
    n=int(seconds);h,n=divmod(n,3600);m,s=divmod(n,60);return f'{h:02}:{m:02}:{s:02}'
def main():
    report=json.loads((ROOT/'build/final-validation.json').read_text(encoding='utf-8'));assert report['allPassed']
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'));t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf-8'));duration=clock(round(report['durationSeconds']))
    rows=['# Java 课堂练习与答案','','面向完全零基础学生。每题朗读后保留四秒思考，完整上下文见 Java示例。','']
    for c in course['chapters']:
        q=next((s for s in c['scenes'] if s['kind']=='question'),None);a=next((s for s in c['scenes'] if s['kind']=='answer'),None)
        if not q:continue
        rows.extend(['## '+c['title']+' · '+c['english'],'','题目：'+q['sourceNarration'],'','```java',q['code'],'```','','原题的验证结果：','```text',q['output'].rstrip(),'```','','答案与原因：'+a['sourceNarration'],'','核对、修正或对比代码：','```java',a['code'],'```','','上方对比代码的验证结果：','```text',a['output'].rstrip(),'```',''])
    (DEL/'课堂练习与答案.md').write_text('\n'.join(rows),encoding='utf-8')
    source=(ROOT/'content/完整讲稿.md').read_text(encoding='utf-8');timings=['','## 实测章节起点','']+[f"- {clock(c['startFrame']/30)}　{c['title']} · {c['english']}" for c in t['chapters']]
    (DEL/'完整讲稿.md').write_text(source+'\n'+'\n'.join(timings)+'\n',encoding='utf-8')
    shutil.copy2(ROOT/'README.md',DEL/'制作与练习说明.md');shutil.copy2(ROOT/'docs/练习指南.md',DEL/'练习指南.md')
    notes=['# 成片验收说明','',f'成片时长：{duration}（{report["durationSeconds"]:.3f} 秒）。','',
        f'- {report["chapters"]} 章、{report["scenes"]} 个分镜、{report["questionHolds"]} 道原创练习与完整四秒思考。',
        f'- {report["exampleCases"]} 个完整代码案例通过；{report["normalPrograms"]} 个正常程序，{report["expectedCompileErrors"]} 个预期编译错误，{report["expectedRuntimeExceptions"]} 个预期运行时异常。',
        f'- {report["runCases"]} 组运行检查、{report["propertyAssertionGroups"]} 组状态变化与边界断言通过；另附已运行验证的增强 for 版本。',
        f'- 全部 {report["emptySubtitleAreaStatesChecked"]} 个编码显示状态确认底部无字幕，文件中没有字幕流。',
        f'- 全部 {report["removedFooterTextStatesChecked"]} 个显示状态确认已移除指定的底部短语，仅保留片段编号。',
        f'- {report["verifiedExtraSentencePauses"]} 处句号额外插入 0.1 秒静音；不额外改变逗号停顿。',
        f'- 每章首、中、尾共 {len(report["audioCorrelation"])} 段波形检验合成同步，全片严格解码通过。',
        '- 逐页检查代码、中文要点、运行结果、倒计时与答案，并检查实际成片章节首、中、尾及拼接位置。','',
        '自动音频和时间检查不等于对所有语音逐字人工听辨。本版按要求不提供字幕。','']
    (DEL/'验收说明.md').write_text('\n'.join(notes),encoding='utf-8')
    (DEL/'交付说明.md').write_text(f'# 一小时学习 Java：零基础入门\n\n- 主视频：一小时学习Java_零基础.mp4（{duration}，无字幕）。\n- 章节目录.md：实测章节起点，视频也内嵌章节标记。\n- 完整讲稿.md、课堂练习与答案.md、Java示例/：配套学习材料。\n- Java视频工程.zip：可编辑源码、原始与处理后的配音、对齐缓存和制作说明。\n- 验收说明.md、验收报告.json：检查结果。\n\n沿用 Rust 第二讲画面；面向完全没有接触编程的学生。工程不含原作者 API Key、Workspace ID、JDK、依赖目录或渲染图片缓存。\n',encoding='utf-8')
    (DEL/'Java示例/README.md').write_text('# Java 21 完整示例\n\n每个目录有 Main.java 和预期行为.json。先安装 JDK 21，在某个示例目录执行 javac -encoding UTF-8 Main.java，再执行 java Main。每个示例独立编译，不要把所有 Main 类放在一起。输入内容见预期行为.json。01-q 和 08-4 预期编译失败；07-q 预期发生数组越界异常。它们是刻意保留的错误案例，修正方案见对应答案。07-extra-enhanced-for 是数组累加的增强 for 完整版本。\n',encoding='utf-8')
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
    extra=[p for p in DEL.rglob('*') if p.is_file() and p.suffix in {'.md','.json','.java'}]
    for p in extra:scan(p)
    archive=DEL/'Java视频工程.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        for p in paths:z.write(p,'Java一小时制作工程/'+p.relative_to(ROOT).as_posix())
        for p in extra:z.write(p,'配套学习资料/'+p.relative_to(DEL).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert not any('/toolchain/' in n or '/node_modules/' in n or '/stills/' in n or n.endswith('.env') for n in z.namelist())
        assert sum(n.endswith('.mp3') for n in z.namelist())==len(keys)
        assert sum(n.endswith('.scaled.wav') for n in z.namelist())==len(keys)
    print('PACKAGED',len(paths),round(archive.stat().st_size/1024**2,1),'MiB; credential scan and CRC passed',flush=True)
if __name__=='__main__':main()
