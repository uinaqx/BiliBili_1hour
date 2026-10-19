"""Package verified editable sources and reusable audio, excluding credentials and render caches."""
import json,pathlib,re,shutil,sys,zipfile
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def scan(p):
    if p.suffix.lower() not in {'.py','.mjs','.tsx','.ts','.json','.md','.txt','.example','.gitignore'}:return
    data=p.read_bytes()
    for pattern in (rb'sk-[A-Za-z0-9_.-]{24,}',rb'llm-[A-Za-z0-9]{10,}'):
        if re.search(pattern,data):raise ValueError('Credential pattern in '+p.name)
def clock(seconds):
    n=round(seconds);h,n=divmod(n,3600);m,s=divmod(n,60);return f'{h:02}:{m:02}:{s:02}'
def main():
    report=json.loads((ROOT/'build/final-validation.json').read_text(encoding='utf-8'));assert report['allPassed']
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'));t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf-8'));duration=clock(report['durationSeconds'])
    rows=['# 课堂练习与答案','','每题在成片中保留四秒思考。完整上下文与输入样本见 C示例。','']
    for c in course['chapters']:
        q=next((s for s in c['scenes'] if s['kind']=='question'),None);a=next((s for s in c['scenes'] if s['kind']=='answer'),None)
        if q is None:continue
        rows.extend(['## '+c['title']+' · '+c['english'],'','题目：'+q['sourceNarration'],'','```c',q['code'],'```','','答案与原因：'+a['sourceNarration'],'','修正或核对代码：','```c',a['code'],'```','','```text',a['output'].rstrip(),'```',''])
    (DEL/'课堂练习与答案.md').write_text('\n'.join(rows),encoding='utf-8')
    source=(ROOT/'content/完整讲稿.md').read_text(encoding='utf-8');timings=['','## 实测章节起点','']+[f"- {clock(c['startFrame']/30)}　{c['title']} · {c['english']}" for c in t['chapters']]
    (DEL/'完整讲稿.md').write_text(source+'\n'+'\n'.join(timings)+'\n',encoding='utf-8')
    shutil.copy2(ROOT/'README.md',DEL/'制作与练习说明.md')
    notes=['# 成片验收说明','',f'成片时长：{duration}（{report["durationSeconds"]:.3f} 秒）。','',f'- {report["chapters"]} 章、{report["scenes"]} 个分镜、{report["questionHolds"]} 道原创题与答案。',f'- {report["compiledExamples"]} 个完整 C11 程序、{report["runCases"]} 组运行输入核对通过，含失败输入与文件读写结果。',f'- {report["propertyAssertionGroups"]} 组边界对照断言通过。',f'- 全部 {report["actualSubtitleStatesChecked"]} 个编码显示状态核对字幕存在与消失，独立 SRT 与时间轴一致，共 {report["captions"]} 条字幕。',f'- 各章开头、中间、末尾共 {len(report["audioCorrelation"])} 段波形相关性核对合成同步；全片严格解码通过。','- 逐页检查代码、中文提示、运行结果、题目倒计时和答案；抽查实际成片各章首、中、尾及拼接位置。','','字幕采用已知讲稿声音强制对齐和波形起音修正；自动对齐及相关性检验不等于对每个字进行人工听辨。全部片段使用相同服务语速，是否做全课统一调整见音频设置记录。','']
    (DEL/'验收说明.md').write_text('\n'.join(notes),encoding='utf-8')
    (DEL/'交付说明.md').write_text(f'# 一小时学习C语言：零基础入门\n\n- 主视频：一小时学习C语言_零基础.mp4（{duration}）。\n- 中文字幕.srt、章节目录.md：独立字幕与实际章节时间。\n- 完整讲稿.md、课堂练习与答案.md、C示例/：学习材料。\n- C语言视频工程.zip：可编辑工程、原始配音、对齐后的配音及制作说明。\n- 验收说明.md、验收报告.json：实际检查记录。\n\n字幕已烧录进主视频。画面沿用 Rust 第二讲，面向完全没有编程基础的学生。\n',encoding='utf-8')
    (DEL/'C示例/README.md').write_text('# C11 完整示例\n\n每个编号目录包含 main.c；需要输入文件的例子同时提供文件样本。测试输入与预期.json 给出标准输入、预期输出和退出码。先进入对应目录，再编译运行。\n\n普通示例使用 gcc -std=c11 -Wall -Wextra main.c -o example.exe，然后执行 example.exe。03-3 和 10-4 等失败路径按预期返回非零，并不是尚未修复的错误。文件写入使用独立目录，w 会清空同名旧文件，a 在末尾追加。不要把示例运行目录当成个人资料目录。\n',encoding='utf-8')
    paths=[]
    for folder in ('content','scripts','src','docs'):paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='migrate_visual_cache.mjs')
    shutil.copy2(ROOT/'docs/零基础练习指南.md',DEL/'零基础练习指南.md')
    paths.extend(ROOT/p for p in ('README.md','requirements.txt','package.json','package-lock.json','tsconfig.json','.gitignore','.env.example','public/course.json','public/timeline.json'))
    keys={s['key'] for s in t['scenes']}
    for folder,ext in [('public/audio',{'.json','.wav'}),('public/audio_original',{'.json','.mp3'})]:paths.extend(p for p in (ROOT/folder).iterdir() if p.is_file() and p.stem in keys and p.suffix in ext)
    paths.extend((ROOT/'build/alignment').glob('*.json'))
    paths.extend(ROOT/'build'/p for p in ('audio-settings.json','audio-alignment.json','example-validation.json','property-validation.json','final-validation.json'))
    for p in paths:scan(p)
    archive=DEL/'C语言视频工程.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        for p in sorted(set(paths)):z.write(p,'C语言一小时制作工程/'+p.relative_to(ROOT).as_posix())
        for p in DEL.rglob('*'):
            if p.is_file() and p.suffix in {'.md','.json','.srt','.c'}:scan(p);z.write(p,'配套学习资料/'+p.relative_to(DEL).as_posix())
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    print('PACKAGED',len(set(paths)),round(archive.stat().st_size/1024**2,1),'MiB; credential scan and CRC passed',flush=True)
if __name__=='__main__':main()
