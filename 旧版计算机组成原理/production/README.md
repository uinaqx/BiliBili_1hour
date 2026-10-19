# 计算机组成原理：中文配音版制作

此目录是在用户提供的静音工程基础上新增的配音与成片流程。原始 `data/`、`src/`、`build_content.py` 保留；`output/index.html` 仍是原始互动预览。配音版为 **60 分镜、11 章、120 分钟**，每道自测题在读题结束后留出完整六秒，再揭示答案。

## 实现方式

- 画面沿用原工程的 SVG 机制图和实验轨迹，改为按真实配音推进。中文采用本机 Noto Sans SC / Microsoft YaHei，等宽代码采用 Cascadia Code / Consolas。
- 使用阿里云百炼北京区域、`qwen-audio-3.0-tts-plus`、系统男声 `longanlufeng`，无背景音乐。180 段分别对应 60 个分镜的讲解、读题、答案。
- 朗读请求速率为 0.88；根据每镜的实际音频长度用保留音高的 `atempo` 做温和调整，使 60 个分镜各为 120 秒，并保留约五秒阅读时间。实际逐镜调整系数与字级时间戳写入本地时间轴。
- 中文句号之间额外插入 0.100 秒静音，逗号不额外插入；按同样的时长变换平移字幕时间戳。题目思考时间在读题音频结束之后开始。
- 字幕字号 36px，保留独立底栏。已移除“静音学习版”和“估时字幕”画面标记。
- 沿用源工程的关键状态切换与保持设计，以 1/30 秒为时间网格、VFR 编码，保留实际字幕和机制变化；不是全片逐帧插值的连续动画。H.264/yuv420p、1920×1080，AAC/48kHz 单声道。关闭 B 帧以确保长时间状态保持时的章节和结尾时间戳准确。

## 重建

环境：Python 3.11+、requests、Pillow、Playwright、FFmpeg/ffprobe，以及本机 Chrome。`video.py` 默认 Chrome 路径位于 `C:/Program Files/Google/Chrome/Application/chrome.exe`，其他系统请修改该路径和字体。

从项目根目录运行：

```powershell
python -m pip install requests Pillow playwright
python -X utf8 -m src.build
python -X utf8 -m unittest discover -s tests -v
python production/plan.py
```

配音已生成且讲稿不变时，不要重新调用在线服务，可直接复用本地 `production/audio_original/`。需要新增配音时，先自行确认具体模型的免费额度、有效期和费用保护，再使用自己的进程环境变量：

```powershell
$env:DASHSCOPE_API_KEY = '<自己的百炼 API Key>'
$env:SFM_WORKSPACE_ID = '<自己的同一业务空间 ID>'
python production/voice.py --dry-run
python production/voice.py --from-env --workers 3
```

脚本不会自动加载 `.env`，也不会把账号参数保存到工程。服务返回的原始音频和字级时间戳仅在本地缓存。不要提交配音、服务返回记录、请求日志或真实环境变量到公开仓库。

```powershell
python production/prepare.py
python production/video.py --qa
python production/video.py
python production/verify.py
python production/deliver.py
```

`prepare.py` 将原稿中最后的自测问句与解释分开；少量结束页补充口头答案，原稿内容按原顺序保留。字幕来自实际配音字级时间戳，不再使用原工程的估时 SRT。该步骤对原始音频做派生处理，不覆盖原始文件，重复运行不会累积句间静音。

原稿有 12 处屏显自测题与口播讨论的问题不同。配音版将原有讨论完整保留在讲解中，再按原屏显题目读题、留六秒、朗读对应答案。对应分镜为 S09、S15、S30、S33、S36、S40、S42、S44、S53、S55、S57、S58。

`--qa` 检查全部 60 分镜的讲解、思考和答案三种状态。`video.py` 缓存显示状态和分章结果，失败后可重跑；只改画面后可用 `--scenes S13` 更新指定分镜，再用 `--encode-only` 编码，仍需先运行完整流程生成各章所需状态。

最终产物在当前工作目录下的 `交付/计算机组成原理/`。时间轴、素材、渲染缓存和验证证据在本项目的 `production/` 下。原来的 `output/production_state.json` 是所提供静音版工程的历史状态，不代表本配音版；以配音版验收报告为准。

## 检查范围

原工程 13 项模型测试重新执行通过。配音版另检查原稿保留、180 段配音与时间戳、60 个完整六秒静音段、中文布局、音视频和章节时长、实际显示状态、独立字幕、153 个成片抽样帧、全片严格解码及音频信号。字幕误差数值是时间轴和显示帧的舍入误差，不代表独立语音识别测量，也未声称实时人工观看完整两小时。
