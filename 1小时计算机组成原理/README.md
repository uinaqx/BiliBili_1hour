# 1小时计算机组成原理：可编辑视频工程

面向初学者与大学生，12 章、73 个分镜、11 道课堂题。以“把内存中的十三和七相加并保存二十”为主线，连接数据表示、逻辑电路、运算器、存储系统、指令、CPU、流水线、输入输出和虚拟存储。

讲稿、代码或图示、Remotion 动画、配音接口与制作脚本均可编辑。保留原工程的字幕流程；C 语言和计组工程另带去字幕脚本。 详细内容和原片记录见 [原版制作说明](docs/原版制作说明.md)。原版说明里的“工程包含配音缓存”只适用于本地交付压缩包；本公开目录不附配音、语音返回记录、缓存、模型权重、依赖目录或成片，也不含原作者 API Key 或 Workspace ID。

## 不调用语音服务的画面预览

先准备 Node.js 24、Python 3.11+、FFmpeg/ffprobe；代码示例需要对应的 GCC/G++，计组使用 Python 教学模型。中文字体沿用 Microsoft YaHei，其他系统需要替换字体。

从仓库根目录进入本课程，再执行：

```powershell
cd "1小时计算机组成原理"
npm ci --ignore-scripts
python -m pip install -r requirements.txt
npm run preview
npm run typecheck
npm run studio
```

`preview` 仅按讲稿长度估计时间，生成无声的编辑预览，不读取账号、不产生语音请求。它不能用作正式成片的音画同步依据。`build/`、`out/` 和 `public/` 中的生成结果都在本课程目录内。

## 先验证，再制作

```powershell
python scripts/verify_models.py
python scripts/voice.py --dry-run
```

修改讲稿后，需要自己的配音。先阅读[仓库首页的百炼开通、免费额度和费用保护教程](../README.md#阿里云百炼开通与免费额度)，确认权限与费用，再在自己的进程环境中设置 `DASHSCOPE_API_KEY` 和 `SFM_WORKSPACE_ID`。`.env.example` 只列变量名，不自动加载。

```powershell
python scripts/voice.py --from-env --test
python scripts/voice.py --from-env --workers 3
python scripts/prepare_audio.py
python scripts/timeline.py
node scripts/stills.mjs --qa
python scripts/qa_sheets.py
node scripts/stills.mjs
python scripts/render.py --preview
python scripts/render.py
python scripts/check.py
```

配音、音频处理、字幕以及改稿后的最终时长均应重新检查。计组的字幕 V2 与去字幕流程、C 语言的去字幕流程见原版制作说明和对应脚本；已存在成片才可执行复制原音轨的转换脚本。无声编辑预览被禁止当作正式成片导出。

## 改造成其他课程

从 `content/` 的章节源和 `author.py` 修改讲稿、示例与习题；调整 `src/` 的画面和图示；重新构建课程并运行代码或模型验证。不要只替换标题。配套学习资料在 `docs/`，完整示例由验证脚本生成到 `out/`。
