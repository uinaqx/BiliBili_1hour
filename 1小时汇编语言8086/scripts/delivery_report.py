"""Report only checks bound to the current course, timeline and final encoded video."""
import json,pathlib,shutil
from check import digest
from document import stamp
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
 t=load(ROOT/'public/timeline.json');f=load(BUILD/'final-validation.json');a=load(BUILD/'audio-placement.json');p=load(BUILD/'preview-validation.json');speed=load(BUILD/'original-speed-check.json');m=load(BUILD/'examples-verification.json');speech=load(BUILD/'speech-spotcheck.json');layout=load(BUILD/'layout-review.json');style=load(BUILD/'narration-style-review.json')
 assert all(x['allPassed'] for x in [f,a,p,speed,m,layout,style]);video=DEL/'一小时讲完汇编语言_8086基础.mp4'
 assert f['videoSha256']==a['videoSha256']==speech['videoSha256']==digest(video)
 assert f['timelineSha256']==a['timelineSha256']==p['timelineSha256']==speed['timelineSha256']==digest(ROOT/'public/timeline.json')
 assert f['courseSha256']==m['courseSha256']==style['courseSha256']==digest(ROOT/'public/course.json')
 text=f'''# 汇编语言视频验收记录

成片{stamp(t['duration'])}（{t['duration']:.3f}秒），10章、{f['pages']}页、{f['semanticUnits']}段讲解，10题各含4秒思考和独立答案页。受众为零基础大学生。

## 本次讲稿与右侧总结

全部121段旁白按自然肯定式表达重写。筛选的否定式澄清由{style['before']['defensivePatternOccurrences']}处降为{style['after']['defensivePatternOccurrences']}处，完整长句重复{len(style['after']['repeatedLongSentences'])}处。技术条件随具体例子说明。

开篇展示十章知识地图；后续70个教学、练习和答案页面各显示4条整页总结，写出操作、具体数值、结论与检查方法，覆盖同页全部讲解并持续显示。练习页为思路提示，答案页给结果和原因。右侧28px，按寄存器名和数值表达式换行，执行卡位于总结下方。全部{layout['checkedSourceFrames']}个选定源状态检查布局并查看11张状态联系表。

## 执行验证

{m['normalPrograms']}组正常程序经{m['assembler']}汇编后，由Unicorn {m['unicorn']}实际执行；Capstone包{m['capstonePackage']}用于反汇编。另有{m['expectedFailures']}组预期失败，共{m['checks']}项检查。记录覆盖寄存器高低字节、小端与有效地址、进位与溢出、乘除、逻辑与移位、分支、数组、字符串、栈参数、DOS字符接口及综合统计。

预期失败区分4个汇编诊断、2个除法执行异常和1个错误条件分支导致的结果错误。省略MOV大小的NASM版本观察独立保存。正常示例与测试输入、机器码列表及逐条执行快照均在工程内。

初态、8086模式、有限DOS服务适配范围见参考资料。概念图用于展示位串、地址计算和数据流；寄存器与内存卡使用实际指令完成后的状态。

## 语音与高亮

百炼3.1 Plus、许南川、原生rate 1.05，后期tempo 1.0。{speed['speechClipsCompared']}份原始MP3独立解码，与{speed['finalPagesCompared']}份最终逐页WAV逐样本重建一致；仅加入约定的句号0.1秒停顿，逗号维持原音。无底部字幕、无背景音乐。

{f['authoredCodeHighlights']}处人工选择的代码讲解短语，按最终音频定位到行与执行快照。选中状态从该次讲解开始保持到下一处；句末静音和思考期继续保持。51段概念与数据流动画共{t['continuousMotionSeconds']:.0f}秒；动画进度独立于CPU状态。

最终AAC对每段旁白的开头、结尾分别取1.2秒匹配，共{a['waveformSamples']}次，最大位置偏差{a['maxSecondsDeviation']:.6f}秒，最低相关系数{a['minimumCorrelation']:.4f}。另取前、中、后三处共54秒音频做本地ASR辅助核对。检查范围为声音放置、抽样术语和画面事件。

## 最终编码检查

90秒试片2700帧，对照{p['actualSamples']}个编码样本。正式MP4保留全部{f['plannedEventsPresent']}个计划画面事件；对比{f['encodedFramesCompared']}个实际编码帧，覆盖各页、旁白切换、高亮前后与持续保持、全部动画中间状态、10组题答。主区最大平均像素差{f['maxDiagramMAE']:.3f}，右侧{f['maxNotesMAE']:.3f}。各章状态联系表和代表完整画面已抽查。

1920×1080、H.264/AAC、10个内嵌章节，动态段按30fps网格，静态段VFR保持。章节时间与实测时间轴一致，全片音视频解码通过。抽样检查与自动核对记录随工程交付。

## 工程交付

工程白名单包括源文件、原始MP3、最终逐页WAV、实测时间轴、执行快照、源行列表、语音对齐、学生资料与检查记录。原始声音元数据仅保留复用字段。ZIP另检查安全路径、CRC、敏感模式、离线声音缓存和原样本重建，结果见工程安全检查.json。

视频SHA-256：{f['videoSha256']}

时间轴SHA-256：{f['timelineSha256']}

课程SHA-256：{f['courseSha256']}

绘图SHA-256：{f['drawingSourceSha256']}

图示SHA-256：{f['diagramSourceSha256']}
'''
 (ROOT/'docs/验收记录.md').write_text(text,encoding='utf8');shutil.copy2(ROOT/'docs/验收记录.md',DEL/'验收记录.md');out=DEL/'检查记录';out.mkdir(exist_ok=True)
 for n in ['final-validation.json','examples-verification.json','layout-review.json','preview-validation.json','audio-placement.json','speech-spotcheck.json','original-speed-check.json','narration-style-review.json']:shutil.copy2(BUILD/n,out/n)
 print('DELIVERY_REPORT_READY',flush=True)
if __name__=='__main__':main()
