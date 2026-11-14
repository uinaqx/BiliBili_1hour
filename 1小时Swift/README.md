# 一小时学完 Swift

这是课程的可编辑工程，包含讲稿、逐页脚本、章节目录和可运行示例。课程资料在 [docs](docs)，示例在 [examples](examples)。

## 学习和运行示例

- 安装 Swift 6 工具链。打开终端，用 `swift --version` 查看版本。安装方式见 [Swift 官方安装指南](https://www.swift.org/install/)。
- `examples/01` 到 `examples/10` 按章节收录示例。进入任意示例目录，执行 `swift main.swift`，对照 `expected.txt` 查看结果。第五章读取输入的示例可按 `input.txt` 输入 125。
- 第一章的练习目录还包含 `compile-error.swift`，可用它观察修改 let 绑定时的编译诊断。修正后的文件为 `main.swift`。
- 进入 `examples/完整项目`，执行 `swift main.swift`。菜单支持添加、查看、删除和退出。金额以整数分输入，例如输入 1800 表示 18 元。开销保存在当前目录的 `expenses.json`。
- 时间戳、旁白和练习答案见 `docs` 目录。

## 无账号画面预览

在课程目录下使用 Python 3.11。预览字体使用微软雅黑和 Consolas。

```powershell
py -3.11 -m pip install -r requirements.txt
py -3.11 scripts/build_course.py
py -3.11 scripts/check_layout.py
```

预览图片写入 `build/layout` 和 `build/layout-contact.png`。Swift 示例可另运行 `py -3.11 scripts/verify_examples.py` 进行编译与输出检查。

## 重制视频

1. 安装 FFmpeg、PyTorch 和 openai-whisper，将 Whisper Base 权重放在用户目录的 `.cache/whisper/base.pt`。
2. 在进程环境中设置自己的 `DASHSCOPE_API_KEY`、`SFM_WORKSPACE_ID`。账户配置见[仓库首页](../README.md#阿里云百炼开通与免费额度)。公开工程仅分发源文件。
3. 依次生成配音、PCM、时间轴和无字幕母版。

```powershell
py -3.11 scripts/voice.py
py -3.11 scripts/prepare_audio.py
py -3.11 scripts/timeline.py
py -3.11 scripts/render.py
```

## 生成字幕

按[课程字幕契约](../00_skills/code-course-video/references/subtitle-contract.md)处理本次重新生成的音轨。词对齐和切点保存在本次构建的 `build` 和 `public/audio`，按重新配音后的时间生成字幕和目录。

```powershell
$workflow = '../00_skills/code-course-video/scripts/subtitle_workflow.py'
py -3.11 $workflow build --project '.' --video 'out/一小时学完Swift_零基础_无字幕.mp4' --out 'out/tracks' --font-size 56 --line-width 24
py -3.11 $workflow burn --plan 'out/tracks/subtitle-plan.json' --output 'out/一小时学完Swift_带字幕.mp4'
```

烧录自动检查显示边界、时长、章节与音轨。交付前按契约抽查实际语音与字幕内容。
