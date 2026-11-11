"""Hash-bound report of the actual encoded delivery, without claiming a full manual viewing."""
import json,pathlib,shutil
from check import digest
from document import stamp
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    t=load(ROOT/'public/timeline.json');f=load(BUILD/'final-validation.json');a=load(BUILD/'audio-placement.json');p=load(BUILD/'preview-validation.json');speed=load(BUILD/'original-speed-check.json');m=load(BUILD/'examples-verification.json');rtl=load(BUILD/'rtl-verification.json');speech=load(BUILD/'speech-spotcheck.json');layout=load(BUILD/'layout-review.json')
    assert all(x['allPassed'] for x in [f,a,p,speed,m,rtl,layout]);video=DEL/'一小时讲完数字电子技术_基础与电路.mp4'
    assert f['videoSha256']==a['videoSha256']==speech['videoSha256']==digest(video)
    assert f['timelineSha256']==a['timelineSha256']==p['timelineSha256']==speed['timelineSha256']==digest(ROOT/'public/timeline.json')
    assert f['courseSha256']==m['courseSha256']==rtl['courseSha256']==digest(ROOT/'public/course.json')
    text=f'''# 数字电子技术视频验收记录

成片{stamp(t['duration'])}（{t['duration']:.3f}秒），10章、{f['pages']}页、{f['semanticUnits']}段讲解，10道练习各有4秒思考与独立答案页。面向零基础大学生。

## 声音与语速

百炼3.1 Plus、许南川、原生1.05；后期tempo=1.0，仅在约定句号增加0.1秒静音，逗号未改。{speed['speechClipsCompared']}份原始MP3独立解码，{speed['finalPagesCompared']}份最终逐页WAV按全部语音样本重建一致。未为凑时长变速。无底部字幕，无音乐。

## 例题与仿真

{m['checks']}项有限枚举与计算检查通过，涉及数制与补码、BCD与格雷码、德摩根律、卡诺图、加法器、选择译码、优先编码、SR/JK/T、状态更新、计数与移位、存储容量、时序预算、DAC与明确分箱的ADC。

另外实际运行{rtl['normalSimulations']}组正常RTL仿真、{rtl['expectedFailures']}组预期失败，共{rtl['checks']}项自检通过，使用{rtl['toolVersion']}。保留编译器的timescale等提示，未声称无警告。仿真不等于综合、时序收敛或上板。

D锁存器与D触发器画面使用实际VCD。D触发器截取10～40ns，在5ns同步复位后观察15、25、35ns三个采样边沿。其他波形均按本课理想功能或路径延迟示意约定绘制，不伪装为器件实测。资料与适用条件见参考资料。

## 画面与同步

{f['formulas']}条公式排版通过。全部{f['pages']}页{f['semanticUnits']}段状态检查源图排版并查看联系表。{f['motionIntervals']}段人工短语触发动画，共{t['continuousMotionSeconds']:.2f}秒；当前公式与说明持续选中到下段实际旁白开始，动画结束后保留末态。卡诺图上下两组分别使用实际短语触发；译码10、优先输入D2与D0、模三旧01、DAC码101等具体例子显示对应状态。

90秒内部试片包含2700帧，对照{p['actualSamples']}个实际编码样本，覆盖知识地图、练习思考、答案、卡诺图、冒险、D触发器、移位与DAC。最终MP4保留全部{f['plannedEventsPresent']}个计划画面事件，对比{f['encodedFramesCompared']}个实际编码帧，覆盖页面边界、段落切换前后、持续选中保持、所有动画中间状态及10组题答。主区最大平均像素差{f['maxDiagramMAE']:.3f}，侧区{f['maxNotesMAE']:.3f}；所有动画编码后均有可见变化。

状态反馈沿当前Q回到组合逻辑的方向移动；移位数据从右侧最低位进入，旧位向左移动；环形回接明确指向最低位。ADC指示箭头始终落在当前编码区间内部，不停在定义域之外的8V边界。VCD显示范围终点若恰有事件，也保留实际边沿与端点值。

{f['semanticUnits']}段旁白的开头与结尾各取1.2秒，在最终AAC中匹配，共{a['waveformSamples']}次，最大位置偏差{a['maxSecondsDeviation']:.6f}秒，最低相关系数{a['minimumCorrelation']:.4f}。这证明声音放置位置，不是每个词的独立时间准确率。另取前、中、后三段共54秒AAC做本地ASR辅助抽查，允许同音字及电路术语识别误差；没有声称逐分钟人工听完整片。

## 编码与交付

1920×1080、H.264/AAC、10个内嵌章节。动态段30fps网格，静态段VFR保持。全片解码通过，章节与实测时间一致，无字幕轨，底部像素检查无烧录字幕。各章编码状态联系表和代表完整画面已抽查。

工程按白名单收集，原始声音元数据只留复用字段；真实账号值、私有加载器、请求标识不收集。ZIP另做安全路径、CRC、敏感模式扫描、离线配音缓存及原样本重建检查，结果见工程安全检查。

视频SHA-256：{f['videoSha256']}

时间轴SHA-256：{f['timelineSha256']}

课程SHA-256：{f['courseSha256']}

绘图SHA-256：{f['drawingSourceSha256']}

图示SHA-256：{f['diagramSourceSha256']}
'''
    (ROOT/'docs/验收记录.md').write_text(text,encoding='utf8');shutil.copy2(ROOT/'docs/验收记录.md',DEL/'验收记录.md');out=DEL/'检查记录';out.mkdir(exist_ok=True)
    for n in ['final-validation.json','examples-verification.json','rtl-verification.json','layout-review.json','preview-validation.json','audio-placement.json','speech-spotcheck.json','original-speed-check.json']:shutil.copy2(BUILD/n,out/n)
    print('DELIVERY_REPORT_READY',flush=True)
if __name__=='__main__':main()
