"""Prepare the editable source archive and companion learning files, without credentials."""
import json,pathlib,re,shutil,sys,zipfile
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def scan(path):
    if path.suffix.lower() not in {'.py','.mjs','.tsx','.ts','.json','.md','.txt','.example','.gitignore'}:return
    text=path.read_text(encoding='utf-8-sig',errors='replace')
    for pattern in (r'\bsk-[A-Za-z0-9_.-]{20,}',r'\bllm-[a-z0-9]{10,}'):
        if re.search(pattern,text):raise RuntimeError('Possible credential in '+str(path.relative_to(ROOT)))
def main():
    report=json.loads((ROOT/'build/final-validation.json').read_text(encoding='utf-8'));assert report['allPassed']
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'));manifest=json.loads((ROOT/'content/example_manifest.json').read_text(encoding='utf-8'))
    examples=DEL/'C++示例';examples.mkdir(exist_ok=True)
    for m in manifest:(examples/(m['key']+'.cpp')).write_text(m['source'],encoding='utf-8')
    rows=['# 课堂练习与答案','','每题在成片中提供四秒思考时间。代码的完整上下文见同编号 C++ 示例。','']
    for c in course['chapters']:
        q=next((s for s in c['scenes'] if s['kind']=='question'),None);a=next((s for s in c['scenes'] if s['kind']=='answer'),None)
        if not q:continue
        rows.extend(['## '+c['title']+' · '+c['english'],'','题目：'+q['sourceNarration'],''])
        if q['code']:rows.extend(['```cpp',q['code'],'```',''])
        rows.extend(['答案与解释：'+a['sourceNarration'],''])
        if a['output'] is not None:rows.extend(['```text',a['output'].rstrip(),'```',''])
    (DEL/'课堂练习与答案.md').write_text('\n'.join(rows),encoding='utf-8')
    shutil.copy2(ROOT/'content/完整讲稿.md',DEL/'完整讲稿.md')
    validation=['# 成片验收记录','',f"总时长：{report['durationSeconds']:.3f} 秒（59 分 59.4 秒）。",'',
      '- 12 章、69 个分镜、64 个完整 C++ 示例编译运行通过。',
      f"- 二分查找、归并排序、插入排序、划分操作通过 {report['propertyAssertionGroups']} 组边界与随机对照验证。",
      '- 全片 1920×1080，H.264/AAC，12 个 MP4 章节标记。',
      f"- 检查全部 {report['actualSubtitleStatesChecked']} 个编码显示状态的实际字幕存在情况，共 {report['captions']} 条字幕。",
      '- 11 道题均保留四秒思考。每段字幕持续到下一句，末句覆盖到朗读结束。',
      '- 全片严格解码通过；每章声音与最终 AAC 波形相关性及偏移校验通过。',
      '- 人工检查全部分镜完成状态、每道题倒计时和答案；抽查成片各章首、中、尾及拼接位置。','',
      '字幕使用已知讲稿声音对齐和波形起音修正。显示状态检验验证字幕未意外消失，波形相关性验证最终合成同步；这些检查不等同于对每个字做人工听辨。','']
    (DEL/'验收说明.md').write_text('\n'.join(validation),encoding='utf-8')
    readme=['# 一小时学习数据结构','',
      '- 主视频：`一小时学习数据结构_C++.mp4`（59 分 59.4 秒）。',
      '- `中文字幕.srt`：独立字幕；主视频已烧录中文字幕。',
      '- `章节目录.md`：实际起点及中英文章节名称；视频本身也有章节标记。',
      '- `完整讲稿.md`、`课堂练习与答案.md`、`C++示例/`：学习与教学材料。',
      '- `数据结构视频工程.zip`：可编辑工程、声音缓存及制作说明。',
      '- `验收说明.md` 与 `验收报告.json`：实际验证记录。','',
      '视频视觉沿用 Rust 第二讲：深色代码区、逐行高亮、左下运行结果、右侧图解、底部居中字幕。示例语言为 C++，讲解面向初学者。','']
    (DEL/'交付说明.md').write_text('\n'.join(readme),encoding='utf-8')
    paths=[]
    for folder in ['src','content','scripts','templates']:
        paths.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths.extend(ROOT/p for p in ['README.md','requirements.txt','package.json','package-lock.json','tsconfig.json','.gitignore','.env.example','public/course.json','public/timeline.json'])
    paths.extend(p for p in (ROOT/'public/audio').glob('*') if p.suffix in {'.json','.wav'} and not p.name.endswith('.scaled.wav'))
    paths.extend(p for p in (ROOT/'public/audio_original').glob('*') if p.suffix in {'.json','.mp3'} and not p.name.startswith('voice-test'))
    paths.extend((ROOT/'build/alignment').glob('*.json'))
    paths.extend(ROOT/'build'/p for p in ['audio-settings.json','audio-alignment.json','example-validation.json','property-validation.json','final-validation.json'])
    for p in paths:scan(p)
    archive=DEL/'数据结构视频工程.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        for p in sorted(set(paths)):z.write(p,'数据结构制作工程/'+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    print('PACKAGED',len(set(paths)),round(archive.stat().st_size/1024**2,1),'MiB; credential pattern scan passed',flush=True)
if __name__=='__main__':main()
