"""Privacy-scanned, explicit-file editable release."""
import hashlib,json,pathlib,re,shutil
from safe_delivery import pack,secrets_from_env
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def release(known=()):
 report=load(ROOT/'build/final-verification.json');video=DEL/'一小时学完CSharp_零基础_无字幕.mp4'
 assert report['allPassed'] and report['videoSha256']==hashlib.sha256(video.read_bytes()).hexdigest()
 for n in ['example-verification','project-verification','layout-verification']:assert load(ROOT/'build'/f'{n}.json')['allPassed']
 course=load(ROOT/'public/course.json');narration=''.join(p['text'] for c in course['chapters'] for s in c['scenes'] for p in s['parts'])
 hits=re.findall('不能说|这不等于|这不意味着|不代表|并不意味着|必须强调|需要注意的是',narration);assert not hits
 (ROOT/'build/language-style-verification.json').write_text(json.dumps(dict(allPassed=True,checkedPhrases=['不能说','这不等于','这不意味着','不代表','并不意味着','必须强调','需要注意的是'],matches=0,method='Phrase scan plus authored direct example-first narration'),ensure_ascii=False,indent=2),encoding='utf8')
 seconds=report['duration'];minutes,sec=divmod(seconds,60)
 text=f'''# C# 课程交付说明

成片时长 {int(minutes)} 分 {sec:.2f} 秒，1920×1080，H.264/AAC，无字幕，十章六十个页面。

内容面向零基础大学生，从第一行输出开始，覆盖变量、类型、输入输出、判断循环、集合、方法、泛型、类与属性、继承接口多态、委托、LINQ、异常、文件、JSON 和异步基础，最后完成控制台开销管理项目。

高亮沿用老版 Rust 第二讲和已确认的 TypeScript 成片效果：浅暖色底、3px 橙色左侧竖条、橙色活动行号。高亮持续保持，按人工标记的旁白短语移动；40px 代码行距，运行结果在左侧下方，右侧为具体的本页总结。

配音使用百炼 3.1 Plus、许南川、服务原生 1.05 倍速，后期 tempo=1.0；句号间多停 0.1 秒，逗号保持。讲稿按先例子再规则的方式编写，已检查用户列举的防御性措辞。

代码实际验证：C# 12、net8.0，SDK 9.0.304。六十个页面示例逐个独立编译运行，两个预期编译错误核对错误编号并运行修正版，另有一个未捕获格式异常示例。完整项目通过十项交互、持久保存和恢复检查。

成片逐编码状态检查高亮像素，对照生成画面，检查章节和音轨样本对应。已检查内部 90 秒试片及代表性代码、练习和答案帧；未做完整一小时的人工逐句听看。

可编辑工程包含讲稿、代码、最终时间轴、原始旁白和最终 WAV、声学对齐缓存、渲染与验证脚本。真实账户配置、密钥和业务空间标识留在工程包外。
'''
 (ROOT/'docs/交付说明.md').write_text(text,encoding='utf8')
 for n in ['完整讲稿.md','示例与习题答案.md','参考资料.md','交付说明.md']:shutil.copy2(ROOT/'docs'/n,DEL/n)
 shutil.copy2(ROOT/'build/final-verification.json',DEL/'成片验证报告.json')
 examples=[str(p.relative_to(ROOT)) for p in sorted((ROOT/'examples').rglob('*')) if p.is_file() and not {'bin','obj','__pycache__'}&set(p.relative_to(ROOT).parts) and p.suffix in {'.cs','.csproj','.txt','.md','.json'}]
 includes=['README.md','.gitignore','.env.example','requirements.txt','content','docs','public/course.json','public/timeline.json','public/audio_original','build/alignment',*examples]
 includes += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'scripts').glob('*.py')) if p.name!='bootstrap.py']
 for c in course['chapters']:
  for s in c['scenes']:includes+=['public/audio/'+s['key']+'.wav','public/audio/'+s['key']+'.json']
 includes += ['build/'+n+'.json' for n in ['audio-preparation','example-verification','project-verification','layout-verification','highlight-resolution','final-verification','language-style-verification']]
 result=pack(ROOT,includes,DEL/'CSharp可编辑工程.zip',known);assert result['allPassed'],result
 example_result=pack(ROOT,examples,DEL/'CSharp配套示例与完整项目.zip',known);assert example_result['allPassed'],example_result
 (DEL/'工程隐私扫描报告.json').write_text(json.dumps(dict(project=result,examples=example_result),ensure_ascii=False,indent=2),encoding='utf8');print('SAFE_CSHARP_RELEASE_READY',result['filesScanned'],example_result['filesScanned'],flush=True)
if __name__=='__main__':release(secrets_from_env(['DASHSCOPE_API_KEY','SFM_WORKSPACE_ID']))
