import json,pathlib,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    r=load(BUILD/'final-validation.json');a=load(BUILD/'audio-placement.json');p=load(BUILD/'preview-validation.json');speech=load(BUILD/'speech-spotcheck.json');assert r['allPassed'] and a['allPassed'] and p['allPassed'] and r['videoSha256']==a['videoSha256']==speech['videoSha256']
    text=f'''# 高等数学（上）视频验收记录

成片时长 **00:59:34.233**，10章、39组考点、78页、136段讲解。按用户清单完整覆盖，教学重点为必要条件、公式、固定解题步骤与易错点，不展开证明或概念内涵。

## 画面与语音

1920×1080，H.264/AAC，无底部字幕、无背景音乐。深色公式板逐步显示计算，当前相关行持续高亮，下一段实际发声时移动，句尾与思考阶段不闪灭。使用30fps时间格上的事件驱动VFR。中文系统男声，句号停顿额外增加0.1秒，逗号未作额外处理。

## 已完成检查

- 39组用户考点在覆盖索引中均有对应页，另有实测起点索引；不靠关键词自动判断讲解对象。
- {r['mathChecks']}项独立数学计算核验：极限、求导、原函数验算、定积分、面积体积、方程解代回、初值及常见边界例子。定理条件与讲稿另外人工核对，参考见references/参考资料.md。
- {r['formulaExpressions']}条公式实际解析和尺寸检查通过；78页全部136个讲解状态完成排版检查，没有小字缩到阈值以下或侧栏溢出。后续步骤在未讲到前保持隐藏。
- 实际渲染使用的state函数通过保持、静音和新页面检查，累计{r['persistentBoundaryChecks']}个持续状态边界检查。
- 90秒内部试片，实际2700帧，检查{p['actualSamples']}个实际编码帧，覆盖密集公式、逐步显示、倒计时、答案、隐式求导与方程模板。
- 最终MP4全部{r['encodedStatesChecked']}个计划显示状态检查通过，包括实际高亮边框像素、未显示公式区、公式区与侧栏图像比较、无字幕区域。另检查{r['heldStateSamples']}个切换前后、段尾、换页和停留位置。
- 136段讲解的开头和末段共{a['waveformSamples']}个实际AAC波形位置检查通过。相对计划位置测得的最大偏差{a['maxSecondsDeviation']:.6f}秒，最低相关系数{a['minimumCorrelation']:.4f}。此项验证合并后的音轨位置，不判断数学语义或每个字的发音。
- 完整音视频解码、格式、时长及10个章节起点检查通过。公式区最大平均像素差{r['maxFormulaMAE']:.3f}，侧栏{r['maxNotesMAE']:.3f}，为有损编码后的RGB平均绝对差。
- 人工抽看内部试片与各章关键页；另对实际AAC开头、中段、末段共54秒进行本地语音识别抽查。识别中的数学术语和字母有误识别可能，未宣称人工逐分钟听看完整成片。

## 配套与使用

公式速查、每章解题检查表、十章练习与答案、39考点定位、逐页目录、完整讲稿及可编辑工程一并交付。凹凸方向与二阶导符号并列，单独凹/凸名称按本校教材。课程围绕常见期末基础题型组织，实际复习仍以本校范围和往年题校准。

工程保留最终配音与时间信息，现有内容可离线重渲染。语音缓存只保留复用需要的字段，真实账号配置、私有加载器、请求标识及原始服务响应不入包。包另做密钥/业务空间ID模式扫描、路径检查与ZIP完整性校验。

## 版本绑定

- 视频SHA-256：`{r['videoSha256']}`
- 时间轴SHA-256：`{r['timelineSha256']}`
- 课程清单SHA-256：`{r['courseSha256']}`
- 绘制程序SHA-256：`{r['drawingSourceSha256']}`

修改后必须重新制作对应报告，不能沿用本次通过标记。
'''
    (ROOT/'docs/验收记录.md').write_text(text,encoding='utf8');shutil.copy2(ROOT/'docs/验收记录.md',DEL/'验收记录.md');(DEL/'检查记录').mkdir(exist_ok=True)
    for name in ['final-validation.json','math-verification.json','audio-placement.json','speech-spotcheck.json','preview-validation.json']:shutil.copy2(BUILD/name,DEL/'检查记录'/name)
    print('DELIVERY_REPORT_READY',flush=True)
if __name__=='__main__':main()
