import json,pathlib,re,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def stamp(t):
 h,r=divmod(int(t),3600);m,s=divmod(r,60);return f'{h:02}:{m:02}:{s:02}'
def main():
 course=load(ROOT/'public/course.json');t=load(ROOT/'public/timeline.json');lookup={s['key']:s for s in t['scenes']};script=['# 一小时学完 TypeScript：完整讲稿\n','面向零基础大学生；从必要的 JavaScript 执行基础开始。\n'];answers=['# 示例与习题答案\n'];index=['# TypeScript 课程配套示例\n','每页对应一个文件夹。`main.ts` 是原始示例；预期报错题目同时提供 `fixed.ts` 和 `expected-error.txt`；`out` 保存本次真实编译结果。\n','## 快速开始\n','先在课程工程根目录执行 `npm ci`。例如：\n','```powershell\nnode node_modules/typescript/lib/tsc.js --strict --target ES2022 --module commonjs examples/ts-01-02/main.ts\nnode examples/ts-01-02/main.js\n```\n','网页示例 `ts-09-05` 请通过本地 HTTP 服务打开；完整项目见 [完整项目/README.md](完整项目/README.md)。\n','| 时间 | 主题 | 代码 |\n|---|---|---|']
 for c in course['chapters']:
  script+=['\n## '+c['title']+'\n'];answers+=['\n## '+c['title']+'\n']
  for s in c['scenes']:
   ts=stamp(lookup[s['key']]['startFrame']/30);heading=f'### {ts} {s["title"]}\n';script+=[heading]
   for i,p in enumerate(s['parts']):script+=['\n'+p['text']+'\n',*(['\n【思考 4 秒】\n'] if p.get('think') else [])]
   script+=['\n本页总结：\n',*['- '+n+'\n' for n in s['notes']]]
   answers+=[heading,'```typescript\n'+s['code']+'\n```\n']
   if s.get('diagnostic'):answers+=['预期检查失败：`'+s['diagnostic']+'`。\n','修正版：\n```typescript\n'+s['answerCode']+'\n```\n']
   answers+=['运行结果：\n```text\n'+s['output']+'\n```\n',s['parts'][1]['text']+'\n']
   index.append(f'| {ts} | {s["title"]} | [{s["key"]}/main.ts]({s["key"]}/main.ts) |')
 (ROOT/'docs/完整讲稿.md').write_text('\n'.join(script),encoding='utf8');(ROOT/'docs/示例与习题答案.md').write_text('\n'.join(answers),encoding='utf8');(ROOT/'examples/README.md').write_text('\n'.join(index)+'\n',encoding='utf8')
 refs='''# 内容与参考版本

本课实际验证环境：TypeScript 5.9.3、Node.js 24.13.0；严格检查开启，示例生成目标为 ES2022。普通控制台例子输出 CommonJS；网页项目输出 ES 模块。

主要依据 TypeScript 官方手册编写。类型标注、联合类型与类型收窄、结构类型、泛型约束、类型工具和模块分别对照以下官方资料：

- [日常类型](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html)
- [类型收窄](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [对象类型](https://www.typescriptlang.org/docs/handbook/2/objects.html)
- [泛型](https://www.typescriptlang.org/docs/handbook/2/generics.html)
- [类](https://www.typescriptlang.org/docs/handbook/2/classes.html)
- [工具类型](https://www.typescriptlang.org/docs/handbook/utility-types.html)
- [模块](https://www.typescriptlang.org/docs/handbook/2/modules.html)

本课采用围绕“开销记录”的原创示例。从值、表达式和运行顺序建立基础，再用类型解释函数与数据结构。网页读取和 JSON 数据采用真实运行时检查。课程讲稿按直接说明规则、示例与操作的方式编写。
'''
 (ROOT/'docs/参考资料.md').write_text(refs,encoding='utf8');DEL.mkdir(parents=True,exist_ok=True)
 for name in ['完整讲稿.md','示例与习题答案.md','参考资料.md']:shutil.copy2(ROOT/'docs'/name,DEL/name)
 shutil.copy2(DEL/'章节目录.txt',ROOT/'docs/章节目录.txt');shutil.copy2(DEL/'逐页目录.txt',ROOT/'docs/逐页目录.txt')
 print('DOCUMENTS_READY',len(lookup),flush=True)
if __name__=='__main__':main()
