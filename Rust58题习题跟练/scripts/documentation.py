"""Build the delivery index from the actual completed course and measured timeline."""
import json,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def stamp(t):
    h,s=divmod(int(t),3600);m,s=divmod(s,60);return f'{h:02}:{m:02}:{s:02}'
def main():
    t=load(ROOT/'public/timeline.json');assert t['scope']=='complete-course'
    checked=load(ROOT/'build/exercise-verification.json');inventory=load(ROOT/'references/inventory.json');by={s['number']:s for s in t['scenes'] if s['kind']=='question'}
    rows=['# 58 道习题索引','','按用户材料原编号排列。每题先读目标和限制，建议暂停独立动手，再看视频修改与验证。','','| 题号 | 视频起点 | 习题 | 运行方式 | 原题状态 | 原题 | 参考答案 |','| --- | --- | --- | --- | --- | --- | --- |']
    names={'passed':'可通过；第 1 题检查 Rustlings 完成标记','compile_error':'编译错误','test_failed':'测试断言失败'}
    for r,v in zip(inventory,checked['records']):
        n=r['number'];rows.append(f"| {n:02} | {stamp(by[n]['startFrame']/30)} | {r['name']} | {'测试' if r['mode']=='test' else '编译运行'} | {names[v['variants']['original']['outcome']]} | [原题](../exercises/original/{r['file']}) | [答案](../exercises/solutions/{r['file']}) |")
    (ROOT/'docs/习题索引.md').write_text('\n'.join(rows)+'\n',encoding='utf8')
    rows=['# 逐题解析与实际结果','','原题与原材料参考答案都保留为独立源码。完整讲稿还包含逐页代码和高亮行号。','']
    for r,v in zip(inventory,checked['records']):
        n=r['number'];q=by[n];rows+=['## '+f"第 {n:02} 题 · {r['name']}",'',f"视频起点：{stamp(q['startFrame']/30)}",'',q['parts'][0]['text'],'']
        for s in t['scenes']:
            if s['number']==n and s['kind']=='answer':
                rows+=[p['text'] for p in s['parts']]+['']
        result=v['variants']['solutions'];rows+=['实际执行记录：','```text',(result['stdout'].strip() or '没有标准输出；退出码 0'),'```','',f"[原题](../exercises/original/{r['file']}) · [带注释参考答案](../exercises/solutions/{r['file']})",'']
    (ROOT/'docs/逐题解析与答案.md').write_text('\n'.join(rows),encoding='utf8')
    # These are measured original chapter onsets, not rounded target durations.
    shutil.copy2(DEL/'章节目录.txt',ROOT/'docs/章节目录.txt');shutil.copy2(DEL/'逐题时间目录.txt',ROOT/'docs/逐题时间目录.txt')
    for name in ['习题索引.md','逐题解析与答案.md']:shutil.copy2(ROOT/'docs'/name,DEL/name)
    shutil.copy2(ROOT/'content/完整讲稿.md',DEL/'完整讲稿.md')
    readme=f'''# Rust 基础 58 题习题跟练

面向第一次系统练习 Rust 的大学生，完整讲解用户提供目录中的 58 道题。成片 **{stamp(t['duration'])}**，共 10 章、183 页、247 段语义讲解。每题采用读题、暂停动手、分步修改、实际运行或测试核对的顺序。

画面沿用深色课程样式：左侧代码、左下结果、右侧要点与图示。无底部字幕、无背景音乐。高亮从页面开始持续保留，下一段实际发声时才移动；句末和思考期不会闪灭。1920×1080，以 30fps 时间格制作，静态语义状态使用 VFR 编码。

## 先使用习题

- [58 题索引](docs/习题索引.md)：原题、答案、视频起点与运行方式。
- [逐题解析与答案](docs/逐题解析与答案.md)：思路和实际输出。
- [完整讲稿与分镜](content/完整讲稿.md)：每页代码、旁白与人工指定的高亮行。
- [十章目录](docs/章节目录.txt)及[逐题目录](docs/逐题时间目录.txt)。

`exercises/original` 是相邻原题目录的快照，`exercises/solutions` 保留用户所给 exercises2.0 的答案及详细注释；未改写两套原文件。材料对应 Rustlings 5.5.1，使用 **Rust 2021 Edition**，本次实际验证版本 **Rust 1.98.1**。58 份答案均已编译运行或测试通过：29 道普通运行题、29 道测试题，共 56 个测试。原题中的编译错误、测试失败及第 1 题特殊完成标记均分别说明。

长文件在视频中按相关代码拆页展示。页面行号是当前节选的行号，结果来自完整文件；完整源码和测试输出在配套文件中。第 34 题包含预期 panic 的测试，测试通过属于正常结果。第 55 题按原题要求修正第二组示例数据的成绩类型。

## 安装与离线重新渲染

需要 Node.js、Python、FFmpeg/FFprobe，以及验证习题时的 Rust 编译器。先在本工程目录运行：

```powershell
npm ci
python -m pip install -r requirements.txt
python scripts/verify_exercises.py
python scripts/build_course.py
python scripts/timeline.py
node scripts/stills.mjs
python scripts/check.py --rendered
python scripts/preview.py
python scripts/render.py
python scripts/check.py --final
python scripts/check_audio_placement.py
```

交付工程含最终逐页 WAV、相应时间信息及已移除请求标识的原配音缓存，所以以上离线复用配音的流程**不需要语音账号**。只改动部分旁白时，可复用其余已成功的片段。视频导出到工程同级的 `交付/Rust习题跟练`。内置界面也可用 `npm run studio` 打开。90 秒内部试片覆盖长代码、思考倒计时、借用切换和测试结果，不是完整视频。

字体使用 Windows 的 Microsoft YaHei 与 Consolas；不打包系统字体。非 Windows 系统需自行选择有权使用的中文和等宽字体，并同步调整 `src/video.tsx`、`scripts/stills.mjs` 的字体路径及检查脚本。字体变化后需重渲染和重新检查。`public/stills` 和依赖没有打包，会按实际依赖指纹重新生成。

## 修改内容与配音

1. 在 `content/exercises_a.py` 至 `exercises_d.py` 修改讲稿、代码和人工目标。`P(target, text, visual, result)` 的 target 指向唯一的代码片段或明确行号；不能靠关键词自动推断正在讲哪行。
2. 执行 `python scripts/build_course.py` 生成统一清单。题目顺序和全覆盖由构建脚本检查。新增或改题时也要更新源码快照、索引和验证逻辑。
3. 只有旁白变化时才重新生成对应语音。设置自己的 `DASHSCOPE_API_KEY` 与 `SFM_WORKSPACE_ID` 环境变量，执行 `python scripts/voice.py --test`，再执行 `python scripts/voice.py`。脚本不会自动读取 `.env`；`.env.example` 仅说明变量名称。不要提交真实密钥或业务空间 ID。
4. 执行 `python scripts/prepare_audio.py`。它在最终速度下使用本地 Whisper base 做已知文本对齐，在句号对应的安全静音处增加 0.1 秒，逗号停顿不变，再测量每段实际发声起点。首次需要本地 Whisper base 模型；更换原音后原对齐缓存会失效。
5. 重新生成 timeline、stills、试片、成片与检查记录。不要仅修改 `public/timeline.json` 来掩盖代码和旁白的语义错误。

配音适配器使用北京地域百炼 `qwen-audio-3.0-tts-plus`，系统男声 `longanlufeng`。账号开通、免费额度及价格应以你自己的百炼控制台为准；本工程不附赠账号或额度。详见[语音配置说明](docs/语音配置说明.md)。已成功的语音按指纹缓存；403 时保留成功片段，恢复服务后继续。提供的工程未包含真实账号配置、请求原始记录或私有加载器。

## 同步与检查机制

- `public/course.json`：逐题、逐页、逐段语义与代码目标。
- `public/audio/<page>.wav/.json`：最终 PCM、实际起点、句号补停顿和哈希。
- `public/timeline.json`：实际音频计算的完整时间轴。
- `src/sync.ts`：渲染实际使用的持续高亮逻辑；`scripts/test_sync.mjs` 直接运行这份实现。
- `scripts/stills.mjs`：检查 DOM 排版和实际选中行，并记录全部渲染依赖。
- `scripts/check.py --final`：逐个检查成片中全部计划状态的代码高亮像素、页边界、输出、无字幕区域、章节、时长及完整解码。
- `scripts/check_audio_placement.py`：对成片 AAC 中各语义段开头及末段进行波形位置核对。

检查报告绑定本次素材及成片哈希。自动检查、关键帧人工抽看与整片人工听看是不同范围，未声称人工从头到尾听完全部时长。打包脚本只选择可编辑工程所需的文件，再扫描密钥和业务空间 ID、验证 ZIP 路径与 CRC。

## 来源与许可

原材料来源说明见 [原目录说明](references/原目录说明.md)，Rustlings 原许可见 [Rustlings-LICENSE.txt](references/Rustlings-LICENSE.txt)。保留原题及原答案的许可和来源，新增工程代码见根目录 LICENSE。官方核对材料：[Rust 教材](https://doc.rust-lang.org/book/)、[借用](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html)、[生命周期](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html)、[运算符](https://doc.rust-lang.org/reference/expressions/operator-expr.html#arithmetic-and-logical-binary-operators)。
'''
    (ROOT/'README.md').write_text(readme,encoding='utf8');shutil.copy2(ROOT/'README.md',DEL/'制作与使用说明.md')
    print('DOCUMENTATION_READY 58 exercises, 10 measured chapters',flush=True)
if __name__=='__main__':main()
