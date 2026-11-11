import json,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def stamp(t):
 h,r=divmod(int(t),3600);m,s=divmod(r,60);return f'{h:02}:{m:02}:{s:02}'
def main():
 course=load(ROOT/'public/course.json');t=load(ROOT/'public/timeline.json');lookup={s['key']:s for s in t['scenes']}
 script=['# 一小时学完 C#：完整讲稿\n','面向零基础大学生，从运行第一行控制台程序开始。\n']
 answers=['# 示例与习题答案\n'];index=['# C# 配套示例索引\n','安装支持 net8.0 的 .NET SDK；各页代码都有独立项目。进入示例文件夹执行 `dotnet run`。\n','预期编译错误题目的原始程序会报错；正确版本请执行 `dotnet run --project corrected`。\n','`Program.cs` 是本页示例，`ConsoleEnvironment.cs` 统一 UTF-8 输入输出及数字显示格式，`Example.csproj` 保存 C# 12 与 net8.0 项目配置。\n','完整菜单项目见 [完整项目/README.md](完整项目/README.md)。\n','| 原始时间 | 知识点 | 程序文件 |\n|---|---|---|']
 for c in course['chapters']:
  script+=['\n## '+c['title']+'\n'];answers+=['\n## '+c['title']+'\n']
  for s in c['scenes']:
   time=stamp(lookup[s['key']]['startFrame']/30);heading=f'### {time} {s["title"]}\n';script+=[heading]
   for p in s['parts']:script+=[p['text']+'\n',*(['【思考 4 秒】\n'] if p.get('think') else [])]
   script+=['本页总结：\n',*['- '+n+'\n' for n in s['notes']]]
   answers+=[heading,'```csharp\n'+s['code']+'\n```\n']
   if s.get('diagnostic'):answers+=['预期编译错误：`'+s['diagnostic']+'`。\n','修正版：\n```csharp\n'+s['answerCode']+'\n```\n']
   stdin=s.get('fixtures',{}).get('stdin')
   if stdin:answers+=['本页输入：\n```text\n'+stdin+'```\n']
   answers+=['运行输出：\n```text\n'+s['output']+'\n```\n',s['parts'][1]['text']+'\n']
   index.append(f'| {time} | {s["title"]} | [{s["key"]}/Program.cs]({s["key"]}/Program.cs) |')
 (ROOT/'docs/完整讲稿.md').write_text('\n'.join(script),encoding='utf8');(ROOT/'docs/示例与习题答案.md').write_text('\n'.join(answers),encoding='utf8');(ROOT/'examples/README.md').write_text('\n'.join(index)+'\n',encoding='utf8')
 refs='''# 参考资料与版本

本课以 C# 12 语言版本、net8.0 目标框架编写，并使用本机 .NET SDK 9.0.304 实际编译运行。控制台项目启用隐式 using 和可空引用类型检查。所有例子都有对应 Program.cs 与项目文件，类型定义位于顶层语句之后。

内容依据 Microsoft Learn 官方文档，采用围绕开销记录的原创示例与课堂练习：

- [C# 语言概览](https://learn.microsoft.com/en-us/dotnet/csharp/tour-of-csharp/overview)
- [创建控制台应用](https://learn.microsoft.com/en-us/dotnet/core/tutorials/create-console-app)
- [顶层语句](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/program-structure/top-level-statements)
- [C# 类型系统](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/)
- [LINQ 查询简介](https://learn.microsoft.com/en-us/dotnet/csharp/linq/get-started/introduction-to-linq-queries)
- [异步编程场景](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/async-scenarios)

示例分为正常执行、预期编译失败及修正版、补充的未捕获运行时异常。控制台输入包含在示例目录的 input.txt，输出保存在 expected-output.txt。
'''
 (ROOT/'docs/参考资料.md').write_text(refs,encoding='utf8');DEL.mkdir(parents=True,exist_ok=True)
 for n in ['完整讲稿.md','示例与习题答案.md','参考资料.md']:shutil.copy2(ROOT/'docs'/n,DEL/n)
 for n in ['章节目录.txt','逐页目录.txt']:shutil.copy2(DEL/n,ROOT/'docs'/n)
 print('DOCUMENTS_READY',len(lookup),flush=True)
if __name__=='__main__':main()
