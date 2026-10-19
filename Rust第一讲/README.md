# Rust_1hour：一小时学习 Rust

面向已了解 C/C++ 基础语法的初学者和大学生，用学生姓名、成绩等例子循序渐进讲解 Rust。工程采用 **Remotion 代码动画 + 中文讲稿 + 独立字幕 + 可选阿里云百炼男声**，包含 14 个主题、14 道原创课堂练习，以及正常、编译错误、运行时 panic 和修正示例。

这是可编辑的制作工程，采用 [MIT 许可证](../LICENSE)，允许修改、再分发和用于其他语言的课程制作。仓库包含源码和教学内容。阿里云接口代码使用通用参数，所有调用都需要使用者自己的账号。

本目录为第一讲；第二讲见 [Rust第二讲](../Rust第二讲/README.md)。所有课程入口与百炼开通教程见[仓库首页](../README.md)。

## 课程内容

| 中文 | 英文 |
|---|---|
| 变量 | variables |
| 基本数据类型 | primitive_types |
| 函数 | functions |
| 条件判断 | if |
| 移动语义与所有权 | move_semantics |
| 结构体 | structs |
| 枚举 | enums |
| Option 可选值类型 | options |
| 动态数组 | vecs |
| 字符串 | strings |
| 哈希表 | hashmaps |
| 泛型 | generics |
| 特征 | traits |
| 生命周期 | lifetimes |

导学与综合回顾另设章节。默认画面为 1920×1080、30fps，代码字号 34px，每屏最多 16 个可见代码行。示例采用 Rust 2024 Edition，原始课程示例在 rustc 1.98.1 上验证；本仓库修改后应重新运行验证。

## 先看画面：不需要语音账号

本工程的制作和画面检查以 Windows 为主。安装 Node.js 24、Python 3.11+、FFmpeg（含 ffprobe），并准备 Microsoft YaHei 和 Cascadia Code 字体。验证 Rust 示例还需要安装 Rust。其他系统可以运行内容处理脚本，但字体路径、字体名称和例题执行方式需要适配。

```powershell
git clone https://github.com/uinaqx/BiliBili_1hour.git
cd BiliBili_1hour/Rust第一讲
npm ci
python -m pip install -r requirements.txt
npm run preview
npm run studio
```

`npm run preview` 会从讲稿生成课程和**无声的画面预览时间轴**，不读取账号、不调用语音服务、不产生语音费用。Studio 中可以查看代码高亮、提示、图示和估计字幕。这个时间轴只用于编辑画面，不能当作正式成片的配音同步时间轴。

```powershell
npm run typecheck
npm run verify
python scripts/audio.py --dry-run
```

最后一条仅显示计划生成的片段数和文字量，没有网络请求。

## 生成自己的有声视频

先完成下面的百炼开通、额度检查与费用保护教程。不要直接运行全课程语音生成来测试账号。

脚本只读取进程环境变量。`.env.example` 是变量清单，**不会自动加载**。在自己的终端设置自己的信息，不要写入源码或提交 Git。

```powershell
$env:DASHSCOPE_API_KEY = '<自己的百炼 API Key>'
$env:SFM_WORKSPACE_ID = '<同一业务空间的 Workspace ID>'
$env:TTS_MODEL = 'qwen-audio-3.0-tts-plus'
$env:TTS_VOICE = 'longanlufeng'

# 确认具体模型的额度、有效期及费用保护后，先用一小段测试
python scripts/audio.py --test --confirm-quota

# 测试成功且额度/费用足够，再生成全课程
python scripts/audio.py --workers 2 --confirm-quota
python scripts/fit_duration.py
python scripts/timeline.py
npx remotion browser ensure
node scripts/stills.mjs --qa
python scripts/qa_sheets.py
node scripts/stills.mjs
python scripts/render.py --preview
python scripts/render.py --workers 2
python scripts/check.py
```

`--confirm-quota` 是使用者已检查费用的声明，**脚本不会查询额度，也不保证免费**。`longanlufeng` 是系统音色名称，不是原作者的个人音色。默认模型为 plus；flash 是可配置候选，本项目未实测 flash 的音色和字级时间戳兼容性。更换模型时应先小段验证。

产物位于 `out/`：MP4、SRT、章节目录、讲稿、示例与验证报告。配音放在 `public/audio/`，原始输出保留在 `public/audio_original/`；这些目录和生成记录均被 Git 忽略。再次运行会按内容缓存并分章续作。新增或修改旁白可能产生新的调用费用。

`fit_duration.py` 只在整课不满足 58～63 分钟目标时做温和的语速调整，保留原文和音高；无法温和调整时会停止，需要修改文案或目标参数。字幕使用服务的字级时间戳，并按语速比例换算，加上相同的 400ms 场景前导。换用没有字级时间戳的服务，需要实现自己的对齐步骤。

## 工程结构与二次改造

| 文件 | 用途 |
|---|---|
| `project.json` | 课程标题、封面、语言标签、章节中文与英文名称 |
| `content/审核通过文案.md` | 完整旁白、分镜、代码、停顿、课堂练习 |
| `content/approved_examples.json` | 带完整上下文的独立 Rust 程序、预期输出或错误编号 |
| `scripts/build_course.py` | 解析讲稿，关联片段、画面、代码与旁白 |
| `scripts/preview.py` | 无需语音服务的估计画面时间轴 |
| `scripts/audio.py` | 可选的百炼语音合成适配器 |
| `scripts/timeline.py` | 根据实测配音生成字幕、章节和动画事件 |
| `src/video.tsx` | 布局、代码高亮、图示与字幕 |
| `scripts/stills.mjs` | Remotion 动画关键帧渲染 |
| `scripts/render.py` | FFmpeg 分章编码、连续音频及章节合成 |
| `scripts/verify_examples.py` | Rust 正常、编译错误、panic 示例验证 |
| `scripts/check.py` | 当前 Rust 一小时课的成片检查 |
| `docs/扩展到其他语言.md` | 修改课程、编译验证、图示和语音服务的方法 |

生成文件 `public/course.json` 和 `public/timeline.json` 不提交到仓库，首次预览时自动生成。`build/`、`out/` 和依赖也不提交。

本工程提供可复用的制作流程；当前讲稿解析、练习数量检查、语法着色和部分图示仍为这门 Rust 课设计。替换为 Python、Java 或 C++ 时，请按照扩展说明同步修改内容、验证器和显示规则，不要只改封面。正式渲染不接受无声预览时间轴。

## 阿里云语音申请免费额度教程

以下入口和规则以控制台及官方文档为准。**开通服务不等于所有语音调用免费。**

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
npm run audit
git diff --cached --stat
```

审计脚本检查待跟踪文件中的凭证格式、Workspace ID、个人路径、音视频及生成目录，不显示匹配到的秘密内容。不要提交包含自己的配音与服务返回数据的压缩包。请在改动代码或文案后重新验证示例与画面。

Rust 内容参考 [Rust 官方教材](https://doc.rust-lang.org/book/)，重点参照[引用与借用](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html)及[生命周期](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html)。Remotion 和语音服务遵循其各自许可与服务条款。
