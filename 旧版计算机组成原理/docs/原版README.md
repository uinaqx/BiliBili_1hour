# 两小时计算机组成原理制作包

> 已新增中文配音版：60 分镜、11 章、完整两小时，含真实配音字幕与每题六秒思考。制作与重建见 [production/README.md](production/README.md)，成片位于当前工作目录的 `交付/计算机组成原理/`。下文是所提供静音版工程的原始说明，保留作为来源记录；配音版以新增制作说明和验收报告为准。

面向大学课程学习，有基本编程经验即可。采用代码生成机制图、状态演示和小实验，配音按用户要求暂不处理。完整主干导学不替代整学期教材、实验和习题。

## 直接查看

- `output/index.html`：双击打开的离线互动课程，60镜、120分钟；可播放、定位、逐镜跳转、查看全稿和分镜。
- `output/course_120min_silent.mp4`：全长静音学习版（生成后存在），关键状态与文稿阅读提示按时间推进。
- `output/silent_preview.mp4`：30秒逐帧渲染的LRU/脏块写回样片（生成后存在）。
- `docs/02_完整逐字稿与分镜.md`：约2.7万字符全稿；每镜包含画面、屏显、自测与答案。
- `output/完整讲义.html`：可打印、可展开答案的完整阅读讲义。
- `output/manuscript_estimated.srt`：文稿估时阅读提示，未做语音对齐。
- `docs/00_时间轴.md`：11章完整时间码。
- `docs/01_课程与导演总案.md`：教学目标、内容取舍、统一模型与视觉规范。
- `docs/07_交付状态.md`：实际交付范围、媒体规格和验证结果。
- `docs/05_课后实验与答案.md`：18道补充练习、过程答案与开放实验。
- `output/review/`：60张关键帧，`output/browser_audit.json`为浏览器检查证据。

静音全长版使用**关键状态保持**方式，让演算、题目和字幕有阅读时间；播放器按连续时间更新，短样片逐帧捕获。短样片为恒定30fps；全长状态保持版采用可变帧率（VFR），按时间戳保持画面，不写入大量重复帧，观看总时长仍为120分钟。文稿提示为估时阅读安排，未进行语音对齐。

## 环境与重建

内容与教学实验只需Python3.12标准库。HTML不依赖网络、账号或构建框架。视频渲染和浏览器审阅另外需要Playwright、Chromium、ffmpeg/ffprobe；图片总览用Pillow。实际验证版本见`output/environment.json`。

从项目根运行：

```bash
python build_content.py
python -m src.build
python -m unittest discover -s tests -v
python -m src.audit_browser
```

源与生成关系：`build_content.py` → `data/course.json`与讲稿；`src/experiments.py` → 实验轨迹；`src/player.html`+`src/player.js`+数据 → `output/index.html`。不要仅修改生成的HTML或讲稿。

## 运行实验

```bash
python -m src.lab add 120 20 --bits 8
python -m src.lab float 5.75
python -m src.lab cache --capacity 16 --block 4 --ways 1 --addresses 0,16,0,16
python -m src.lab cache --capacity 16 --block 4 --ways 2 --addresses 0,16,0,16
python -m src.lab sum --array=-2,4,-6,8
python -m src.lab pipeline
```

还可编译高层语言示例：`cc -std=c11 -Wall -Wextra -Werror examples/sum.c -o output/sum_demo && output/sum_demo`，预期输出24。

结果为JSON，便于检查每次状态变化。CPU是RV32I风格的语义子集，不执行完整二进制解码；流水线是单独的明确假设模型；所有时间数值都是给定教学参数，不是运行Python测得的真实CPU性能。Cache支持小端字节数据、LRU、回写、写分配，不宣称模拟全部策略。

## 视频重渲染

```bash
# LRU：覆盖命中A、装入C、淘汰脏B与写回的30秒样片
python -m src.render --start 2565 --duration 30 --mode smooth --output output/silent_preview.mp4

# 完整两小时，教学状态与字幕变化时更新画面
python -m src.render --duration 7200 --mode keyframes --output output/course_120min_silent.mp4

# 任意片段；start为全片秒数
python -m src.render --start 5040 --duration 60 --mode keyframes --output output/load_use_clip.mp4
```

导出1920×1080、H.264/yuv420p的MP4；smooth模式为恒定30fps，keyframes模式为时间基准1/30秒的可变帧率。媒体元数据写入同名`.metadata.json`。全长版含11章导航元数据。渲染会临时存储PNG，结束后清理；可用`--keep-frames`保留。当前云浏览器限制file导航，自动渲染通过Playwright的`set_content`载入本地HTML；普通本地浏览器仍可双击打开。

## 学习与制作状态

完整结构：导学4分钟、表示14分钟、运算14分钟、存储16分钟、指令14分钟、CPU16分钟、流水12分钟、性能8分钟、I/O10分钟、整机实验8分钟、总结4分钟。共120分钟。

最终可运行`python -m src.validate_delivery`重新核验，再运行`python -m src.package`打包源工程。

`output/production_state.json`记录完成范围；`output/coverage.json`逐镜说明专用/共享构图，`output/validation.json`记录最终检查。共享构图用于比较相同部件在不同条件下的行为，不代表每镜独立设计了一套全新视觉系统。

配音、真实音频测时、语音对齐和声音母版暂不实施；当前交付为可学习、可修改、可重渲染的静音制作工程。`docs/03_工程与代码规格.md`保留未来接入设计，但本轮不以音频为验收条件。

## 许可与来源

文字、教学例子与SVG画面由本项目编写生成，不复制教材整页图。中文字体使用系统Noto Sans CJK SC，遵循SIL Open Font License；等宽字体使用Noto Sans Mono CJK SC/DejaVu Sans Mono。播放器没有内嵌字体文件。参考阅读与技术边界见`docs/06_技术审核与参考资料.md`。
