# 一小时学完计算机网络：公开可编辑工程

零基础大学生；分层、协议过程、计算例题和易错点。10章、80页、139段旁白、26段连续图示动作。原片时长 **01:05:05**，章节起点见[原片时间目录](docs/原片时间目录.txt)。

包含完整讲稿、分镜、数学或算法例题、绘图代码、配音适配器、实际声音对齐和制作工具。深色画面、中文旁白、无底部字幕、无背景音乐，高亮持续到下一段实际讲解开始。计算机网络目录采用百炼3.1 Plus＋许南川换声后的最新源码。

公开目录不含原作者的API Key、Workspace ID、私有账号加载器、配音文件、语音服务响应、音频对齐缓存、模型权重或成片。原片验收记录仅供了解原制作检查范围，不能作为修改后版本的通过记录。文档中“本地交付包含配音”等表述仅适用于本地交付包。

## 无账号编辑预览

需要Python 3.11、FFmpeg/ffprobe。依赖见requirements.txt，原环境版本见requirements.lock.txt。中文使用Windows Microsoft YaHei，数学用Matplotlib STIX；系统字体不随源码提供，其他平台需先修改字体路径。

```powershell
python -m pip install -r requirements.txt
python scripts/build_course.py
python scripts/verify_examples.py
python scripts/timeline.py --layout
python scripts/edit_preview.py
python scripts/voice.py --dry-run
```

预览把全部讲解状态和联系表写入out/edit-preview/，不读取账号、不请求在线语音服务。时间轴明确标记为layout-only，正式渲染会拒绝此估算时间。public/、build/、out/为本课程内部生成目录，不依赖原作者电脑上的交付目录。

## 使用自己的账号配音并生成视频

先阅读[百炼开通与免费额度教程](docs/百炼语音配置说明.md)及[仓库共用教程](../README.md#阿里云百炼开通与免费额度)。在进程环境变量DASHSCOPE_API_KEY、SFM_WORKSPACE_ID中配置自己的账号，.env.example只列空变量名，脚本不自动加载.env。调用前自行确认模型权限、额度、有效期及价格。

本课程保留已确认的声音设置：**qwen-audio-3.1-tts-plus＋xunanchuan_v3.1，原生合成rate=1.05**。后期tempo=1.0；句号额外增加0.1秒，逗号不加停顿。修改这些设置前需向使用者说明并取得同意，不能为了凑时长自动变速。

```powershell
python scripts/voice.py --test
python scripts/voice.py
python scripts/prepare_audio.py
python scripts/timeline.py
python scripts/layout_review.py
python scripts/check_original_speed.py
python scripts/check.py
python scripts/preview.py
python scripts/check_preview.py
python scripts/render.py --workers 4
python scripts/check.py --final
python scripts/check_audio_placement.py
```

prepare_audio.py需要预先下载Whisper base模型，默认放在用户目录.cache/whisper/base.pt。模型不随工程提供。先完成全部配音及停顿，再以最终音频重建高亮、动画和章节时间。源音频、对齐、逐页时间和编码画面任何输入变化后，都需要重新生成对应检查记录。

检查脚本还可能依赖公式、图示、语音测试、例题等先前报告；按实际需要运行scripts/中的对应检查，未生成报告不能当作检查通过。高数下使用SymPy复算数学题；操作系统和计算机网络使用独立固定期望核对算法/协议例题。声音抽查、文档和打包脚本供进一步制作时使用，原片哈希及换声来源记录仅作参考。

## 修改入口与交付

- content/：课程讲稿、分镜、教师指定高亮及动作触发文字。
- scripts/draw.py与scripts/diagrams.py：画面和动态图示。
- scripts/timeline.py：按实际音频映射人工指定的动作。
- docs/、references/：学习材料、原片目录与参考来源。

生成文件位于本课程的out/、build/、public/。修改讲稿或图示后应先检查静态预览与内部试片，再完成最终视频验证。项目的document.py会生成本地交付说明；公开发布前需保留本README关于配音与私密文件排除的说明。

沿用[仓库许可证](../LICENSE)，可据此调整讲解、动画或拓展新的课程。
