# 1小时Python：零基础可编辑视频工程

面向完全没有接触编程的学生，沿用 Rust 第二讲画面：深色代码、左侧代码下方运行结果、右侧中文要点与图示。13 章、67 个分镜、11 道原创练习，无字幕；题目朗读后保留四秒思考。原成片时长约 59 分 58 秒，章节起点见 [章节目录](docs/章节目录.md)。

本目录提供讲稿、完整示例清单、Remotion 源码、图示、配音接口和制作脚本。**公开仓库不附配音、服务返回记录、音视频缓存、依赖目录或成片，也不含原作者 API Key 和 Workspace ID。** [原版制作说明](docs/原版制作说明.md) 中关于“压缩包含配音”的描述仅针对原本地交付，不适用于此公开目录。

## 无需语音账号的画面预览

制作环境采用 Node.js 22、Python 3.11、FFmpeg/ffprobe。学习例子另需：Python 3.11 及以后版本即可运行学习示例。其他系统若没有 Microsoft YaHei 字体，请在 `src/` 及检查脚本中换成可用中文字体。

```powershell
cd "1小时Python"
npm ci --ignore-scripts
python -m pip install -r requirements.txt
npm run preview
npm run typecheck
npm run studio
```

`preview` 按讲稿长度估算时间，仅供无声编辑预览，不读取账号、不请求语音服务。正式导出必须重新生成配音并按实际音频建立时间轴；脚本禁止将估算时间轴直接导出为最终视频。全部生成结果留在本目录内的 `public/`、`build/`、`out/`，不会依赖作者的私人交付目录。

## 验证示例与检查配音清单

```powershell
python scripts/verify_examples.py
python scripts/property_checks.py
python scripts/voice.py --dry-run
```

完整例子生成到 `out/Python示例/`，包括需要的上下文、输入、正确结果和刻意保留的错误。学习步骤见 [练习指南](docs/练习指南.md)，题目见 [课堂练习与答案](docs/课堂练习与答案.md)。原片的验收记录仅说明原片，改稿后需要重新验证。

## 使用自己的配音重制

先读[仓库首页的百炼开通与免费额度教程](../README.md#阿里云百炼开通与免费额度)，确认账号权限、具体模型额度与费用。在自己的进程环境里设置 `DASHSCOPE_API_KEY`、`SFM_WORKSPACE_ID`，不要将真实值写进源码或提交仓库。`.env.example` 仅列变量名，不会自动加载。

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
python scripts/final_frames.py
```

保持全课一致语速，在实际句号位置额外增加 0.1 秒，不额外改变逗号停顿。先检查每页及 90 秒试片，再完成全片；正式输出在 `out/`。调整内容后若总时长变化，应同步检查旁白、代码、图示和章节。

## 修改与扩展

`content/chapters_*.py` 与 `author.py` 管理讲稿、代码、题目和预期行为；`src/video.tsx` 管理代码区及动画，`src/diagrams.tsx` 管理关系图。修改后重新构建课程、验证代码，并检查所有题目与答案画面。源码使用[仓库许可证](../LICENSE)，可据此继续扩展。
