# Rust 进阶基础：九个主题

面向已学过变量、函数、集合、所有权、特征和生命周期的初学者及大学生。用学生姓名、成绩等小例子循序渐进讲解，每个主题都有原创课堂练习、4 秒思考时间和答案。原始成片时长 **57 分 57 秒**，由 11 章、69 个分镜组成。

这是可编辑的制作工程，沿用 [仓库 MIT 许可证](../LICENSE)。可以替换内容、改造画面，或扩展到其他语言。仓库只提供源码和教学资料，**不包含原作者的 API Key、Workspace ID、配音、语音服务返回数据、请求记录、个人音色或成片视频**。语音适配代码使用通用参数，调用时需要自己的账号。

## 课程内容

| 中文 | 英文 |
|---|---|
| 类型转换 | conversions |
| 模块 | modules |
| 错误处理 | error_handling |
| 单元测试 | tests |
| 迭代器 | iterators |
| 智能指针 | smart_pointers |
| 多线程 | threads |
| 宏 | macros |
| 代码检查 | clippy |

导学与综合回顾另设章节。先介绍智能指针，再学习线程中的 `Arc` 与 `Mutex`。完整讲解见 [讲稿与分镜](content/完整讲稿.md)，配套资料有 [课堂题与答案](docs/习题与答案.md)、[原片章节时间](docs/章节目录.md)、[原片验收记录](docs/成片验证报告.md)。这些时间和记录对应原始成片，更换旁白或配音后需要重新测量。

## 画面与停顿

- 1920×1080、30fps，Remotion 代码动画、中文字幕和可选的百炼中文男声，默认无背景音乐。
- 页左上方主标题采用“模块”“错误处理”等正规章节名；副标题标明当前知识点。
- 运行结果在左侧代码区下方，字号 **32px**；代码 **34px**，每屏主要代码最多 12 个可见行，较长程序分屏或显示节选。
- 两句话之间的中文句号位置额外插入 **0.100 秒**，逗号停顿不变，不整体改变语速。原课有 491 处片段内部边界和 68 处换页边界，共 559 处；题目仍保留完整 4 秒思考时间。

## 先预览画面：不需要语音账号

主要制作环境为 Windows。准备 Node.js 24、Python 3.11+、FFmpeg（含 ffprobe）、Rust（含 Cargo 和 Clippy），以及 Microsoft YaHei、Cascadia Code 字体。原始课程使用 Rust 2024 Edition，在 Rust/Cargo 1.98.1、Clippy 0.1.98、FFmpeg 8.0.1、Remotion 4.0.535 上验证。其他系统需适配字体与示例执行方式。

从仓库根目录进入本工程：

```powershell
cd Rust第二讲
npm ci
python -m pip install -r requirements.txt
npm run preview
npm run typecheck
npm run studio
```

`npm run preview` 根据讲稿生成**无声、估计时长的画面编辑时间轴**，不会读取语音账号或发出语音请求。Studio 可以查看代码、结果区、图示、题目和估计字幕；这份时间轴不能用于正式有声成片，导出脚本会拒绝它。课程编辑后重新运行该命令即可更新预览。

```powershell
npm run verify
python scripts/audio.py --dry-run
```

验证脚本实际编译、运行 55 个完整示例，包括正常输出、预期编译错误、运行时 panic、通过及故意失败的单元测试，以及 Clippy 提示和修正版本。模块例题提供全部文件。结果与可独立使用的例题写入 `build/verification.json` 和 `out/示例与习题/`。`--dry-run` 只显示配音任务大小，不调用在线服务。

## 生成自己的有声视频

先阅读仓库首页的 [百炼开通、API Key、Workspace ID 和免费额度教程](../README.md#一开通账号与百炼服务)。免费额度不是每个账号、每个模型都有，先确认具体模型的额度、有效期、价格和费用保护。

本仓库没有可复用的原作者配音。脚本只读取自己的**进程环境变量**，不会自动加载 `.env.example`。该文件只有变量名称和空占位值，不要把真实信息提交到 Git。

```powershell
$env:DASHSCOPE_API_KEY = '<自己的百炼 API Key>'
$env:SFM_WORKSPACE_ID = '<API Key 所属空间的 Workspace ID>'
$env:TTS_MODEL = 'qwen-audio-3.0-tts-plus'
$env:TTS_VOICE = 'longanlufeng'

# 先检查额度和费用保护，再用短片段测试自己的账号
python scripts/audio.py --test --confirm-quota

# 短片段成功且确认剩余额度或费用后，再生成课程
python scripts/audio.py --workers 2 --confirm-quota
python scripts/pause_sentences.py
python scripts/timeline.py
npm run typecheck
npx remotion browser ensure
node scripts/stills.mjs --qa
python scripts/qa_sheets.py
node scripts/stills.mjs
python scripts/render.py --preview
python scripts/render.py --workers 2
python scripts/check.py
```

`--confirm-quota` 表示使用者已自行检查，脚本不会查询额度，也不保证免费。默认使用北京区域、`qwen-audio-3.0-tts-plus`、系统音色 `longanlufeng`。模型与音色可通过环境变量更改，但其他模型的音色和字级时间戳兼容性需要先用短片段验证。

素材和产物保存在当前工程内：

| 路径 | 内容 |
|---|---|
| `public/course.json` | 根据内容源生成的课程清单 |
| `public/audio/` | 视频使用的配音和字级时间戳 |
| `public/audio_original/` | 未插入额外停顿的原始配音及时间戳 |
| `public/timeline.json` | 按实测音频生成的正式时间轴 |
| `public/stills/`、`build/` | 渲染缓存、分章音视频与检查记录 |
| `out/` | MP4、SRT、章节目录、讲稿、完整例题与验收报告 |

以上生成文件均被 Git 忽略。`pause_sentences.py` 从原始配音插入静音，并同步平移后续字级时间戳，重复运行不会叠加停顿。`timeline.py` 为相邻分镜再增加 3 帧（0.1 秒）并保留阅读、答题时间；正式字幕使用实测时间轴，恢复 `map_err`、`into_iter`、`macro_rules!` 等代码的书面写法。只有完成实际配音后，才能运行正式渲染及成片检查。

## 修改课程或拓展到其他语言

| 文件 | 修改内容 |
|---|---|
| `content/author.py` | 章节、分镜、题目、答案和完整验证程序的统一数据结构 |
| `content/intro.py`、`chapters_a.py`、`chapters_b.py`、`chapters_c.py`、`closing.py` | 可编辑的旁白、代码、运行结果、提示与图示类型 |
| `scripts/build_course.py` | 课程元信息、内容导入与讲稿生成 |
| `content/example_manifest.json` | 内容源生成的完整例题、预期输出与错误编号 |
| `src/video.tsx` | 正规章节标题、代码与结果区、语法颜色、图示、动画和字幕布局 |
| `scripts/audio.py` | 语音服务适配、音色、朗读指令和字级时间戳获取 |
| `scripts/pause_sentences.py` | 中文句号停顿的插入和时间戳偏移 |
| `scripts/timeline.py` | 正式时间轴、字幕、章节、动画事件 |
| `scripts/stills.mjs`、`scripts/render.py` | 帧渲染、分章缓存、编码与合成 |
| `scripts/verify_examples.py`、`scripts/check.py` | 示例验证与当前课程的成片验收 |

先改内容源，再运行 `npm run course` 和 `npm run verify`。调整画面可用 `npm run preview`；新增或修改旁白需要重新合成受影响的配音，可能产生调用费用。保留 `public/audio_original/` 才能复现句间停顿处理。

本工程的例题验证、关键字高亮、课程标签、九主题检查与 491 处内部句号断言针对当前 Rust 课程；改为其他语言或改写讲稿时，需要同步调整这些规则。`pause_sentences.py` 的单片段句号校验和 `check.py` 的课程总数检查不同，后者尤其需要随内容变化更新。若更换为没有字级时间戳的语音服务，需要另行实现字幕对齐。推荐以“正常例题通过、错误例题按预期失败、画面抽查无溢出、最终音视频完整”为验收依据。

## 隐私检查与参考

上传前运行 `npm run audit`。检查只报告文件路径，不打印命中的敏感值；`.gitignore` 排除环境文件、配音、返回记录、缓存、日志和视频。不要使用 `git add -f` 绕过排除规则。通用模型名称、系统音色名称、环境变量名称和占位符可以公开，它们不是账号凭据。

课程组织和例题依据 [Rust 官方教材](https://doc.rust-lang.org/book/)、[语言参考](https://doc.rust-lang.org/reference/)与 [Clippy 使用说明](https://doc.rust-lang.org/stable/clippy/usage.html)。关于原片的字幕数值误差，验收记录测量的是时间轴舍入误差，不代表独立语音识别测量。
