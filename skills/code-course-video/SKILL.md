---
name: code-course-video
description: 制作或修复编程与计算机课程视频，使用代码或图示动画、中文旁白及可选字幕。适用于约一小时课程、逐页语音同步、持续高亮、无字幕导出和可编辑工程交付；不用于普通短视频剪辑。
---

# 编程与计算机课程视频

把课程内容、最终配音和画面状态组织为可修改、可续跑、可验收的工程。新课可采用 Remotion + FFmpeg；已有工程优先沿用其已认可的渲染链路。

## 确定本轮范围

先检查当前目录、用户最近要求、最新认可成片、运行进程和工程配置。继承已确认的受众、声音、字幕形式和风格；不要把一门课的选择推广到全部课程。制作视频本身不等于授权推送 GitHub。

| 模式 | 做什么 | 读取材料 |
| --- | --- | --- |
| 新课制作 | 内容、讲稿分镜、代码验证、配音、同步、渲染与交付 | [教学与画面](references/course-design.md)，按阶段读取其余材料 |
| 同步修复 | 修正讲解对象和实际语音起点，保留认可的高亮机制 | [同步规范](references/synchronization.md)、[渲染与验收](references/render-delivery.md) |
| 只导出无字幕 | 关闭字幕层，以相同时间轴导出，复制原音轨及章节 | [无字幕导出](references/render-delivery.md#只去掉字幕) |
| 只审查、不修改 | 只读复现，列课程、原时间戳、问题、预期和证据 | [验收分层](references/render-delivery.md#验收分层) |
| 打包或上传 | 整理可复现工程，扫描内容与版本记录，按已有授权上传 | [工程交付](references/render-delivery.md#工程与安全交付) |

用户只要完整文案审核时，交付文案后停在该阶段。已批准制作或修复时，检查试片后继续，不增加试片确认门槛。只澄清无法推断的关键选择，等待期间继续独立工作。

## 核心约定

- **语义与计时分开。** 人工确定每句讲哪行代码/哪个对象，再用最终音频定位。关键词匹配和按段均分只能辅助排查。
- **代码高亮持续选中。** 页面出现即有相符高亮；下一处讲解开始才移动。句末、静音和思考期不清除；允许回跳和相关多行选中。不能用短暂动画或短语结束时间控制可见性。
- **分幕隔离。** 换代码后重新确定初始行与行号，旧幕事件不作用于新幕。禁止以“总是第一行”掩盖缺失的对应表。
- **图示分别处理对象与状态。** ALU 结果、寄存器写回、主存更新和箭头方向按旁白触发；对象缺失时最小补齐对应小幕并记录，不能只换索引。
- **小修改保持范围。** 修同步保持配音、讲稿、示例、结果、布局和章节时间；确有必要的素材例外要列明。只去字幕不重新配音、不重写时间轴、不改变布局。
- **验收分层。** “有选中行”“语义对应”“实际 MP4 正确”是三种结论。旧位置回归不等于逐页覆盖，解码通过也不等于人工看完。
- **保护隐私。** 密钥、业务空间标识和真实 `.env` 不进入代码、日志、示例或公开工程。复用配音的修复任务不调用语音服务。

## 新课制作顺序

1. 写课程契约：受众与基础、时长及容差、知识点、字幕开关、参考版本、声音、交付位置。未指定的新课可先按零基础准备，现有课继承原受众。
2. 按依赖排列内容，以贯穿的小需求编写完整讲稿与分镜。先例子、再规则、再术语。每主题有示例与预测/纠错/判断题，分别验证正常运行、预期编译失败和运行时失败。
3. 用短段测试声音、术语与语速，再批量配音。接口与模型按执行时官方资料及工作适配器核对；指定服务持续不可用则保留进度报告，不用无声视频或别的声音冒充完成。
4. 先完成变速、补停顿等处理，再确定时间轴。用户指定句号间增加 0.1 秒时只改该类停顿，不顺带改逗号。音频哈希改变后原对齐和渲染缓存失效。
5. 逐页编写旁白短语到代码行/图示对象和状态的对应表，映射到最终音频起点。字幕按实际说完的时间结束，不按字数均分。
6. 制作约 60–90 秒内部试片，覆盖长代码、输出、图示、语音、字幕与高亮切换。检查后继续。时长按实测配音、阅读与思考停顿控制，不用大段空白凑时长。
7. 分章渲染并缓存。静态页可用事件驱动 VFR；持续动画应逐帧或充分采样。检查最终成片后再交付工程。

## 可复用资源

这些是工具和组件，不是已完成的一小时课程。正式课须扩充内容；已有工程不必为使用资源而重构。

- [assets/persistent-sync.ts](assets/persistent-sync.ts)：持续高亮、分幕隔离与图示状态函数；测试运行渲染所用的同一实现。
- [assets/CourseFrame.tsx](assets/CourseFrame.tsx)：深色画面骨架，左代码/图示、左下输出、右注解、独立字幕；无字幕开关不导致重排。
- [assets/course.example.json](assets/course.example.json)、[assets/anchors.example.json](assets/anchors.example.json)、[assets/words.example.json](assets/words.example.json)：最小格式示例。
- `python scripts/timeline_tools.py validate COURSE.json`：检查时间、行号、初始高亮、分幕、字幕与练习停顿；覆盖不足只报告，不编造语义。
- `python scripts/timeline_tools.py resolve COURSE.json ANCHORS.json --root PROJECT --output RESOLVED.json`：解析已人工选择的短语；重复短语明确出现次数，失败不写部分结果。
- `python scripts/media_qa.py extract VIDEO.mp4 --times 12.5,18.2 --output FRAMES`：提取 VFR 中该时刻正在显示的帧，防止误取未来画面。
- `python scripts/media_qa.py verify VIDEO.mp4 --reference ORIGINAL.mp4 --preserve-audio --decode --output REPORT.json`：检查媒体、时长、章节、音轨和解码，不代替语义或烧录字幕检查。
- `python scripts/safe_delivery.py scan PATH --output REPORT.json`：扫描目录、单文件或 ZIP；只报告位置和原因，不回显敏感值。可加 `--secret-env VAR1 VAR2` 检查实际环境值。
- `python scripts/safe_delivery.py pack --root PROJECT --include src content scripts public/audio --output PROJECT.zip`：白名单打包、扫描、ZIP 校验；自行加入其他必要文件，不收集整个工作目录。
- `node --experimental-strip-types scripts/test_sync_state.mjs`、`python scripts/test_tools.py`：在临时目录验证关键行为，不访问语音服务或账户。

工具修改后实际运行相关测试。不要为了低影响文案变动重渲染全套课；也不要修改测试期望来掩盖错行。

## 交付要求

链接实际产物，说明改动、保留项、通过检查、抽查范围和未测项。验收记录须对应本次视频与时间轴的哈希，不能沿用旧版本的通过标记。

用户要求十章目录时，合并关联的相邻章节，保留组内第一个原始起点，首章 `00:00:00`，简洁中文名；纯文本代码块中每行 `HH:MM:SS 名称`。这不要求重排视频内实际章节。

了解规则来源时，读[制作总结与反思](references/lessons-learned.md)。
