# Rust 基础58题习题跟练：公开可编辑工程

完整覆盖58道原题及答案，按读题、暂停动手、分步修改、实际运行或测试核对组织。10章、183页、247段旁白。保留Rustlings来源与原许可证。

原片实测时长 **01:42:11**，原片章节见[时间目录](docs/原片时间目录.txt)。深色画面、中文旁白、无底部字幕、无背景音乐，当前图示或高亮持续保留。Agent Harness目录来自恢复到原始1.0倍速后的最新版。

本目录提供课程内容、完整讲稿、分镜、绘图或Remotion源码、例子与制作工具。**公开仓库不包含原作者的配音、音频对齐缓存、语音服务响应、API Key、Workspace ID、私有账户加载器、模型权重或成片。** 文档中提及“本地交付包含声音”只适用于原本地交付，不适用于本公开目录。

## 无账号编辑预览

需要Python 3.11、FFmpeg/ffprobe和可用中文字体。数学/运行时图示使用Pillow、NumPy及Matplotlib；Rust画面另需Node.js，验证题目另需Rust编译器。

```powershell
python -m pip install -r requirements.txt
python scripts/verify_exercises.py
python scripts/build_course.py
python scripts/timeline.py --layout-only
npm ci --ignore-scripts
npm run typecheck
npm run studio
python scripts/voice.py --dry-run
```

预览使用明确标记的`layout-only`时间，不读取账号、不请求配音，不能当成正式成片或原片时间轴。Pillow工程将各页关键状态与联系表写入`out/edit-preview/`；Rust工程在Studio中无声编辑。生成文件全部位于本课程的`public/`、`build/`、`out/`，不依赖原作者电脑上的交付目录。

## 使用自己的声音制作

先读[仓库首页百炼开通与免费额度教程](../README.md#阿里云百炼开通与免费额度)，在自己的进程环境中设置`DASHSCOPE_API_KEY`、`SFM_WORKSPACE_ID`。`.env.example`仅列空变量名，脚本不自动读取.env。先确认模型、权限、额度与费用。

```powershell
python scripts/voice.py --test
python scripts/voice.py
python scripts/prepare_audio.py
python scripts/timeline.py
node scripts/stills.mjs
python scripts/render.py
python scripts/check.py --final
python scripts/check_audio_placement.py
```

语速默认保持原始**1.0倍速**，不为达到目标时长自动变速；要改语速应先与使用者说明并取得同意。句号处额外0.1秒、逗号不加停顿。重新准备音频使用本机Whisper base模型进行已知文本声学对齐，需要先下载模型。动画与高亮按最终音频重建，不能直接沿用原片时间戳。若新配音的时长超出旧版检查范围，应调整课程内容或适用的时长检查范围，不能自行变速凑时长。

正式导出前先检查内部试片、全部题目/答案及持续高亮。检查脚本依赖此前生成的示例、图示或公式检查报告，详细命令参阅`scripts/`；没有生成这些报告时应先完成对应检查。公开版本未重新配音或重渲染原视频，原片验收记录也不能作为修改后版本的通过记录。

## 修改入口

- `content/`：完整讲稿、课程内容、语义目标和分镜。
- `scripts/`：构建、配音、对齐、绘制、编码和分层检查。
- `docs/`、`references/`：练习、覆盖表、参考来源与制作约定。
- 原创工程遵循[仓库许可证](../LICENSE)；Rust原题另外遵循其保留的原始许可。

原始系统字体不随源码提供。非Windows平台需调整绘图/渲染文件的字体路径并重新检查中文、公式、代码布局。Pillow工程不依赖Remotion；Rust工程的`src/`管理实际画面和持续状态逻辑。
