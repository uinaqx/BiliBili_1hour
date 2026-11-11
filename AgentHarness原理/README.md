# AgentHarness原理

独立的 Remotion 原理讲解工程。这是系列课程的可编辑公开源码，包括讲稿、画面和制作脚本。有独立示例的课程同时提供示例源码。

公开版本使用自己的配音配置。配音缓存、语音返回数据和成片保存在本地交付工程。

## 画面预览

```powershell
npm ci
npm run studio
```

`content/script.json` 保存旁白，`src/scenes` 保存场景代码。`src/timeline.json` 提供无声预览。修改旁白后可运行 `npm run timeline` 更新预览。使用自己的百炼账号生成旁白后运行 `npm run render`，成片输出到 `out/`。渲染需要 FFmpeg，合成配音需要 Python 和 `requests`。

使用 `DASHSCOPE_API_KEY` 和 `SFM_WORKSPACE_ID` 环境变量配置自己的配音账号。申请步骤见[仓库首页](../README.md#阿里云百炼开通与免费额度)。
