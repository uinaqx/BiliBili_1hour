# 1小时Go：零基础可编辑视频工程

面向零基础学生，沿用系列课程的深色代码区、代码下方运行结果、右侧中文要点和持续高亮。首页为知识点总览，无底部字幕。十章，每章一道预测或纠错练习，保留四秒思考，答案下一页揭晓。原版章节时间见 [章节目录](docs/原版章节目录.txt)。

本目录包含完整讲稿、分镜、可独立运行的示例、答案、Remotion 源码和制作脚本。**公开仓库不包含配音、音视频、语音服务返回记录、模型权重、依赖缓存、API Key 或 Workspace ID。** 本地交付 ZIP 与公开仓库的内容不同；[原版制作说明](docs/原版制作说明.md)及验收记录只描述原成片，修改后须重新验证。

## 课程内容

1. 课程导学与程序结构
2. 变量常量与数据类型
3. 运算符与输入输出
4. 分支与循环
5. 数组与切片
6. 映射与字符串
7. 函数与延迟执行
8. 指针与结构体
9. 方法与接口
10. 错误处理与综合实践

讲稿与答案位于 `content/`，独立代码位于 `examples/normal/` 和 `examples/expected-failures/`。不要把故意失败的例子作为正常程序批量构建。

## 不需要账号的画面预览

视频环境为 Node.js 22 或 24、Python 3.11、FFmpeg / FFprobe。学习代码的验证参考 Go 1.27.3。把 Go 编译器的 bin 目录加入 PATH。每个 examples 子目录包含独立 main.go。 中文字体使用 Microsoft YaHei，代码字体使用 Cascadia Code / Consolas；其他系统请在 `src/` 和检查脚本中配置可用字体。

```powershell
cd "1小时Go"
npm ci --ignore-scripts
python -m pip install -r requirements.txt
npm run preview
npm run typecheck
node scripts/test_sync.mjs
npm run studio
```

`preview` 构建课程并生成无声编辑时间轴，不读取账号、不请求语音。其时间仅为编辑估算，不能当作最终语音对齐；正式导出脚本会拒绝估算时间轴。它不会把估算后的时间写入原版章节目录。所有生成数据都在当前课程目录的 `public/`、`build/` 和 `out/`，无需作者电脑上的其他课程目录。

```powershell
npm run verify
npm run voice:dry-run
```

## 使用自己的账号重新制作

先看[仓库首页的百炼申请及免费额度教程](../README.md#阿里云百炼开通与免费额度)，确认模型可用、业务空间权限及额度。用自己的进程环境设置 `DASHSCOPE_API_KEY` 和 `SFM_WORKSPACE_ID`；`.env.example` 留空，不会自动加载，不要提交真实值。默认北京地域、qwen-audio-3.0-tts-plus 和系统男声 longanlufeng。

```powershell
python scripts/voice.py --test
python scripts/voice.py --workers 3
python scripts/prepare_audio.py
python scripts/timeline.py
node scripts/test_sync.mjs
npm run stills
python scripts/preview_clip.py
npm run render
python scripts/check.py --final
python scripts/check_audio_placement.py
```

已知文本的声学对齐使用本地 Whisper base 模型，运行 `prepare_audio.py` 前需自行准备 `~/.cache/whisper/base.pt`。句号间增加 0.1 秒，逗号策略不变；先完成音频处理，再建立正式时间轴。视频采用 30fps 时间网格上的事件驱动 VFR，编码为 H.264/AAC。

## 修改、复用与验证边界

`content/chapters_*.py` 和 `author.py` 管理教学内容，`P` 中的行号是人工选择的讲解对象。修改内容后运行 `npm run course` 和 `npm run verify`。旁白未变时可在自己的本地制作缓存中复用声音，旁白变更必须重新配音及对齐；时间轴脚本会核对文本一致性。

`src/sync.ts` 的高亮持续到下一处讲解开始，句末、静音和思考期不清除。不要按字数均分正式时间，或用短语结束时间清除高亮。`test_sync.mjs` 验证渲染使用的同一状态函数；实际成片还须检查编码画面、音轨、章节和教学对应关系。原版通过记录不代表修改后的作品已经通过。

源码沿用[仓库许可证](../LICENSE)，可据此改造或扩展其他语言。使用之前完成的本地交付 ZIP 时可能带有最终配音，而本公开目录不分发这些声音。
