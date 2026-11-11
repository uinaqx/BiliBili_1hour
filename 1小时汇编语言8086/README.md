# 1小时汇编语言8086

8086、寄存器、标志位、内存与指令练习。这是系列课程的可编辑公开源码，包括讲稿、画面和制作脚本。有独立示例的课程同时提供示例源码。

公开版本使用自己的配音配置。配音缓存、语音返回数据和成片保存在本地交付工程。

## 画面预览

```powershell
python -m pip install -r requirements.txt
python scripts/build_course.py
python scripts/verify_math.py
python scripts/timeline.py --layout
python scripts/edit_preview.py
```

预览图写入 `out/edit-preview`。画面使用微软雅黑和 Consolas，字体配置位于 `scripts/draw.py`。渲染有声视频需要 FFmpeg 和 FFprobe，声学校准需要本地 Whisper base 权重。

生成指令执行记录需要把 NASM 加入 PATH。

## 重新生成有声视频

使用自己的环境变量配置配音后，依次运行 `scripts/voice.py`、`scripts/prepare_audio.py`、`scripts/timeline.py` 和 `scripts/render.py`。

使用 `DASHSCOPE_API_KEY` 和 `SFM_WORKSPACE_ID` 环境变量配置自己的配音账号。申请步骤见[仓库首页](../README.md#阿里云百炼开通与免费额度)。

原版时间见 [章节目录](docs/章节目录.txt)。
