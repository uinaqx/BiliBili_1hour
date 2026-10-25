"""Describe the checks actually completed, with hashes and explicit coverage limits."""
import json,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    final=load(BUILD/'final-validation.json');audio=load(BUILD/'audio-placement.json');speech=load(BUILD/'speech-spotcheck.json');preview=load(BUILD/'preview-validation.json');v=load(BUILD/'exercise-verification.json')
    assert final['allPassed'] and audio['allPassed'] and preview['allPassed']
    assert final['videoSha256']==audio['videoSha256']==speech['videoSha256']
    rows=f'''# Rust 基础 58 题习题跟练：交付与验收记录

成片：`Rust基础58题_习题跟练.mp4`。

- 总时长：01:42:11.333，覆盖用户提供的全部 58 题，按原编号顺序，分为 10 章。
- 规格：1920×1080，H.264 / AAC，静态页面使用 30fps 时间格上的 VFR；无底部字幕、无背景音乐；内嵌 10 个章节标记。
- 教学结构：读题与限制、4 秒动手提示、分步修改与原因、完整文件的实际运行或测试结果。长文件按关键部分拆页。
- 布局：左代码、左下实际结果、右侧要点与图示。相关多行可以同时高亮，页面开始即显示，下一段真实语音开始才切换，句尾和思考期持续保持。
- 配音：北京地域百炼系统男声。保留自然速度，句号停顿增加 0.1 秒，逗号不改。已成功的配音通过缓存复用。

## 代码与内容

原题和所给答案均保留快照及 SHA-256。本次按 Rust 2021 Edition、Rust 1.98.1 验证：{v['compileExercises']} 道普通运行题、{v['testExercises']} 道测试题，58 份答案全部通过，实际 {v['testsPassed']} 个测试通过。原题状态分别记录，区分编译失败、测试失败与正常可通过。第 1 题的完成标记是练习工具流程；第 34 题预期 panic 的测试属于成功；第 55 题按原题要求更换第二组示例成绩类型。

讲解对象由教师式逐段人工确定，共 {final['semanticParts']} 段，未用关键词猜测目标行。涉及声明、修改与返回的多行内容按相关代码组选中。完整讲稿记录每段目标，源码保留完整注释。

## 完成的检查

1. 所有 183 页的真实浏览器排版检查，覆盖代码、结果、侧栏及图示边界。代码区 34px，结果区 32px。
2. 运行实际渲染所用的持续高亮函数，检查初始状态、切换、句尾保持、静音、多行和回跳等行为。
3. 90 秒内部试片实际 2700 帧，抽取 {preview['actualSamples']} 个实际编码帧，检查长代码、四秒倒计时、借用的切换与测试结果。
4. 最终 MP4 中逐个比较全部 {final['actualEncodedStatesCompared']} 个计划画面状态，检查真实选中边框像素、代码/结果区域、侧栏与无字幕区域；并检查 {final['heldStateBoundaryChecks']} 个切换前后、段尾、换页与停留位置，确认显示的是最近已经开始的状态。
5. 247 段语音各核对开头和末段，共 {audio['waveformSamples']} 个实际 AAC 波形样本。本次相对计划位置测得的最大偏差为 {audio['maxSecondsDeviation']:.6f} 秒，最低相关系数 {audio['minimumCorrelation']:.4f}。这证明音轨没有在合并中发生位移，不等同于每个词的语义或发音都由波形检验判断。
6. 完整音视频解码、格式、总时长和全部 10 个章节起点检查通过。最终代码与结果区域最大平均像素差 {final['maxCodeAndResultMAE']:.3f}，侧栏 {final['maxNotesMAE']:.3f}（H.264 有损编码后的 RGB 平均绝对误差）。
7. 抽看内部试片与关键帧，特别检查所有权、借用、多行代码、测试答案和生命周期。另用本地语音识别抽查实际 AAC 的开头、中段、末段共 54 秒，内容对应讲稿；英文标识的识别可能不准确。没有声称人工逐分钟听看整个 102 分钟。

## 可编辑工程

工程包包含内容源文件、语义映射、Remotion 组件、制作脚本、依赖锁、全部最终逐页配音及其时间信息、可复用原配音缓存和源码。原配音缓存元数据只保留重用所需字段，不包含请求标识或原始服务响应。依赖、浏览器缓存、渲染缓存、临时编译结果和私有账号加载器未打包。包会另做密钥/空间标识模式扫描、路径检查和 ZIP CRC 校验，结果见工程安全检查文件。

## 版本绑定

- 成片 SHA-256：`{final['videoSha256']}`
- 时间轴 SHA-256：`{final['timelineSha256']}`
- 课程清单 SHA-256：`{final['courseSha256']}`
- 渲染依赖指纹：`{final['renderInputFingerprint']}`

原始验证 JSON 存在工程 `build` 中，已选择本次有效报告打包；修改内容或渲染结果后须重新生成报告。
'''
    (ROOT/'docs/验收记录.md').write_text(rows,encoding='utf8');shutil.copy2(ROOT/'docs/验收记录.md',DEL/'验收记录.md')
    (DEL/'检查记录').mkdir(exist_ok=True)
    for name in ['final-validation.json','exercise-verification.json','audio-placement.json','speech-spotcheck.json','preview-validation.json']:shutil.copy2(BUILD/name,DEL/'检查记录'/name)
    print('DELIVERY_REPORT_READY',flush=True)
if __name__=='__main__':main()
