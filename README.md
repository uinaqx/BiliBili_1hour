# BiliBili_1hour：编程与计算机基础视频工程

七套可独立编辑、验证和重制的课程工程。首页按课程分为七个文件夹，Rust 两讲和旧版计组分别保留。

| 文件夹 | 内容 |
|---|---|
| [1小时数据结构](1小时数据结构/README.md) | 完整讲稿、示例或教学模型、Remotion 画面与制作脚本 |
| [1小时计算机组成原理](1小时计算机组成原理/README.md) | 完整讲稿、示例或教学模型、Remotion 画面与制作脚本 |
| [1小时C语言](1小时C语言/README.md) | 完整讲稿、示例或教学模型、Remotion 画面与制作脚本 |
| [1小时C++](1小时C++/README.md) | 完整讲稿、示例或教学模型、Remotion 画面与制作脚本 |
| [Rust第一讲](Rust第一讲/README.md) | Rust 基础十四个主题 |
| [Rust第二讲](Rust第二讲/README.md) | Rust 进阶基础九个主题 |
| [旧版计算机组成原理](旧版计算机组成原理/README.md) | 原两小时互动课程与配音工程 |

各目录独立安装依赖；新四部工程先运行 `npm run preview` 再打开 Studio。预览不调用语音服务，正式配音和导出流程见各目录 README。源码沿用[仓库许可证](LICENSE)，可据此修改或扩展其他语言。

仓库不包含原作者 API Key、Workspace ID、私密配置、配音缓存、语音服务返回记录、模型权重、node_modules 或成片视频。`out/`、`build/`、音频和画面缓存均被忽略。修改语音时使用自己的账号；免费额度和模型权限需要自行确认。

## 阿里云百炼开通与免费额度

以下教程供所有课程共用。账号开通不保证后续调用免费。

### 一、开通账号与百炼服务

1. 打开 [阿里云百炼控制台](https://bailian.console.aliyun.com/)。
2. 注册或登录自己的阿里云账号，按要求完成实名认证。
3. 阅读并同意百炼服务协议，开通服务。
4. 地域统一选择 **华北2（北京）**。

本项目使用普通百炼模型 API，**不需要购买 Token Plan，不需要购买服务器，也不需要创建智能体应用**。账号开通不代表后续所有语音调用都免费。[官方开通说明](https://help.aliyun.com/zh/model-studio/first-api-call-to-qwen)

### 二、创建 API Key

在首页“常用功能 → API Key”中创建：

| 项目 | 选择 |
|---|---|
| 地域 | 华北2（北京） |
| 归属账号 | 你自己的主账号 |
| 归属业务空间 | 默认业务空间，或你专门为本项目创建的空间 |
| 模型权限 | 如果设置了自定义权限，需包含后续使用的语音模型 |

将密钥保存在自己的密码管理器中，不要发到聊天、截图或公开仓库。这里需要的是 **百炼 API Key**，不是阿里云 AccessKey，也不是旧版智能语音服务的 Access Token。[官方密钥说明](https://help.aliyun.com/zh/model-studio/get-api-key/)

### 三、获取 Workspace ID

进入“业务空间”，复制 **API Key 所属空间**的 Workspace ID。

注意：必须是同一个空间，不能使用另一个空间的 ID，也不能用账号 UID 或 APP ID 代替。[官方获取说明](https://help.aliyun.com/zh/model-studio/obtain-the-app-id-and-workspace-id)

### 四、确认语音模型是否可用

在百炼顶部进入“模型”，查找以下完整名称：

- `qwen-audio-3.0-tts-plus`
- `qwen-audio-3.0-tts-flash`

本项目默认使用 plus，flash 列为可配置候选，先以 plus 作为验证对象。它们是**语音合成模型**，不是名称相近的语音识别模型，也不是实时语音对话模型。

进入详情后：

1. 确认地域仍为北京。
2. 查看调用说明、价格和账号可用状态。
3. 如果页面要求额外开通或申请，按该模型页面的要求办理；没有提示则不必另找申请入口。
4. 如果使用子业务空间，确认它已获得该模型的调用权限。

这两个模型列在官方支持声音复刻的模型名单中，但你的账号能否正常调用，最终仍须实际请求验证。本项目不需要声音复刻，也不提供个人音色。[官方支持列表](https://help.aliyun.com/zh/model-studio/voice-cloning-user-guide)

### 五、检查免费额度与费用保护【首次调用前必须做】

回到首页，进入 **“免费额度”**：

1. 搜索上述具体模型。
2. 查看剩余额度和有效期，不要只看整个账号的汇总。
3. 如果该模型提供 **“免费额度用完即停”** 开关，建议开启。
4. 如果没有额度、额度已过期，或没有对应开关，**先不要调用**，先确认价格及是否接受付费。

免费额度并不保证每个账号、每个模型都有；符合条件的模型开启“用完即停”后，额度耗尽会停止服务。[官方额度规则](https://help.aliyun.com/zh/model-studio/new-free-quota)

## 提交改动

```powershell
git add .
python audit_public.py
git diff --cached --stat
```

审计脚本检查待跟踪文件中的凭证格式、Workspace ID、个人路径、音视频及生成目录，不显示匹配到的秘密内容。不要提交包含自己的配音与服务返回数据的压缩包。请在改动代码或文案后重新验证示例与画面。

Rust 部分内容参考 [Rust 官方教材](https://doc.rust-lang.org/book/)，重点参照[引用与借用](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html)及[生命周期](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html)。Remotion 和语音服务遵循其各自许可与服务条款。

