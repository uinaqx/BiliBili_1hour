# 旧版计算机组成原理：两小时工程

保留原来的 60 分镜、11 章、120 分钟版本，与新的“1小时计算机组成原理”独立。此目录包含原始互动课程、教学实验、讲稿和后续中文配音制作脚本。详见 [原版说明](docs/原版README.md) 和 [配音版制作说明](production/README.md)。

```powershell
python -X utf8 build_content.py
python -X utf8 -m src.build
python -X utf8 -m unittest discover -s tests -v
```

运行后打开 `output/index.html`，可以离线阅读和交互演示。浏览器渲染另需 Playwright/Chromium、Pillow 和 FFmpeg。`production/` 的配音和成片流程需自己的百炼账号；原作者凭据、音频、服务返回记录和生成的成片均不上传。配音输出改在此目录的 `out/`。
