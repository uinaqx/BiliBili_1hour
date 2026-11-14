# 一小时学完 SQL

这是课程的可编辑工程，包含讲稿、逐页脚本、章节目录和可运行示例。课程资料在 [docs](docs)，示例在 [examples](examples)。

## 运行课程示例

工程以 SQLite 3.42.0 实测。示例按章放在 `examples/01` 到 `examples/10`，对应逐页目录和讲稿。可以使用自己的 SQLite 客户端，先在一个空库运行 `examples/init.sql`，再粘贴当页查询。涉及写入的页可以在另一个空库中重新初始化，保持各题起点一致。

如果已安装 Python 3.11，可以在工程目录直接运行：

```powershell
python scripts/verify_examples.py examples/04/sq-04-04.sql
python scripts/verify_examples.py examples/10/sq-10-06.sql
```

每次命令都从新的内存数据库开始。第 7 章的主键、邮箱和外键冲突示例会给出 SQLite 错误信息，供练习读取约束反馈。金额以整数元保存。日期采用固定的 `YYYY-MM-DD` 文本格式。

## 无账号画面预览

在课程目录下使用 Python 3.11。预览字体使用微软雅黑和 Consolas。

```powershell
py -3.11 -m pip install -r requirements.txt
py -3.11 scripts/build_course.py
py -3.11 scripts/check_layout.py
```

预览图片写入 `build/layout` 和 `build/layout-contact.png`。SQL 的示例在课程清单生成时执行。

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
py -3.11 scripts/measure_subtitle_words.py
$workflow = '../00_skills/code-course-video/scripts/subtitle_workflow.py'
py -3.11 $workflow build --project '.' --video 'out/一小时学完SQL_零基础_无字幕.mp4' --out 'out/tracks' --font-size 56 --line-width 24
py -3.11 $workflow burn --plan 'out/tracks/subtitle-plan.json' --output 'out/一小时学完SQL_带字幕.mp4'
```

烧录自动检查显示边界、时长、章节与音轨。交付前按契约抽查实际语音与字幕内容。
