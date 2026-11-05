# 四小时计算机组成原理：课件知识点与考题精讲

对应原成片 **04:19:55**，共 10 章、253 个讲解场景、519 段旁白、88 个例题/考题解析场景。依据 920 页原始材料整理，保留 392 张实际使用的匿名技术图片；完整课程为无底部字幕版本。

## 学习资料

- [原片章节时间](docs/章节目录.txt)
- [知识点与考题时间目录](docs/知识点与考题目录.txt)
- [完整讲稿](docs/完整讲稿.md)
- [课件例题与考题详解](docs/课件例题与考题详解.md)
- [逐页复习总结](docs/逐页复习总结.md)
- [章节大纲](docs/章节大纲.md)
- [课件技术更正](docs/课件技术更正.md)
- [缺失题干清单](docs/缺失题干清单.md)
- [原材料覆盖对照](docs/课件覆盖对照.md)

课程依次讲解：计算机系统与性能、数据表示与校验、浮点数、计算机运算、总线、存储系统、输入输出、指令系统、CPU与流水线、控制单元与时序。

## 无账号查看与编辑画面

Python 3.11；完整依赖见 requirements.txt。Windows 使用已安装的微软雅黑；其他系统应先修改 scripts/draw.py 中的字体路径。预览仅需 Pillow，不调用配音服务。

```powershell
cd "4小时计算机组成原理"
python -m pip install Pillow
python scripts/build_course.py --public-only
python scripts/edit_preview.py
```

默认预览输出为 `out/preview/` 中每章的第一张画面。指定场景和讲解步骤：

```powershell
python scripts/edit_preview.py --scene m01-001 --beat 0
```

讲解数据在 `content/module_*.json`；图片关联、强调框与步骤卡在每个场景的 `beats` 中；右侧总结在 `points` 中。`public/slides/` 包含实际使用的匿名技术图片。`public/course.json` 是可重新构建的课程清单；`public/timeline.json` 保留原片实测时间，供学习定位和重制参考。

## 使用自己的账号重新制作

公开源码包含讲稿、图片、配音接口、声音处理、时间轴和渲染脚本。**本仓库不附成片、旁白音频、语音服务返回记录、原始 PPT/PDF、学校与个人身份资料、API Key 或 Workspace ID。** 本目录中的历史验收资料描述原本地成片；修改或重制后应重新验收。

安装 requirements.txt、准备 FFmpeg/ffprobe 及本地 Whisper base 模型。按[仓库首页的百炼开通教程](../README.md#阿里云百炼开通与免费额度)配置自己的环境变量 `DASHSCOPE_API_KEY` 和 `SFM_WORKSPACE_ID`，确认具体模型权限与费用后执行：

```powershell
python scripts/voice.py --test
python scripts/voice.py
python scripts/prepare_audio.py
python scripts/timeline.py
python scripts/render.py
```

原配音设置为百炼 3.1 Plus、许南川、原生 1.05 倍速；后期 tempo 为 1.0，句号额外增加 0.1 秒。`content/pause_overrides.json` 中的局部修订绑定原始音频哈希；重新生成的音频应按实际词边界重新处理，旧修订不会直接适用于新音频。

重新生成音频后再运行时间轴脚本。直接运行 render.py 需要实际音频及相应元数据；原片时间轴和静态预览均不能代替新配音的计时。生成的声音与缓存进入 public/audio_original、public/audio、build；成片和目录输出在本目录 out/。

## 内容验证

```powershell
python scripts/verify_data_examples.py
python scripts/verify_arithmetic.py
python scripts/verify_hardware_content.py
```

原片的覆盖、图像隐私及数值验证记录在 `review/`，原成片验收说明在 [docs/验收记录.md](docs/验收记录.md)。它们用于追溯原版本，不构成对修改版的验收。

制作代码和重新编写的讲解按附带 LICENSE 使用；课件技术图的原有权利归属保持。未提供完整题干的条目已在缺失题干清单中注明。
