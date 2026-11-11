"""Bind the actual verification scope to this video's hashes."""
import json,pathlib,shutil
from check import digest
from document import stamp
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
 t=load(ROOT/'public/timeline.json');f=load(BUILD/'final-validation.json');a=load(BUILD/'audio-placement.json');p=load(BUILD/'preview-validation.json');speed=load(BUILD/'original-speed-check.json');sim=load(BUILD/'examples-verification.json');speech=load(BUILD/'speech-spotcheck.json');settings=load(BUILD/'audio-settings.json')
 assert all(r['allPassed'] for r in [f,a,p,speed,sim])
 assert f['videoSha256']==a['videoSha256']==speech['videoSha256']==digest(DEL/'一小时学完Verilog_电路与仿真.mp4')
 assert f['timelineSha256']==a['timelineSha256']==p['timelineSha256']==speed['timelineSha256']==digest(ROOT/'public/timeline.json')
 assert f['courseSha256']==sim['courseSha256']==digest(ROOT/'public/course.json')
 internal=sum(len(load((ROOT/'public'/s['audio']).with_suffix('.json'))['pauseRefinements']) for s in t['scenes'])
 text=f'''# Verilog课程验收记录

正式成片 **{stamp(t['duration'])}（{t['duration']:.3f}秒）**，10章、71页、121段旁白、10道练习。面向零基础大学生，以Verilog-2005电路描述和RTL仿真为范围。

## 声音

百炼qwen-audio-3.1-tts-plus、许南川xunanchuan_v3.1，原生rate=1.05，后期tempo=1.0。121份原始配音合计{settings['rawSeconds']:.3f}秒；{internal}处内部句号和121个段尾句号各增加0.1秒，合计{(internal+121)*.1:.1f}秒。逗号未改，原始语音样本完整保留。全部71份最终WAV独立重建比对通过，只允许约定静音插入。

## 电路与例题

使用 **{sim['toolVersion']}**，-g2005模式。{sim['normalSimulations']}组正常仿真及{sim['checks']}项检查通过，包含真值表、位宽截断、移位、四态值、锁存反例与修正、同步/异步复位、使能保持、计数回绕、阻塞/非阻塞流水差别、参数实例、生成结构、函数、状态机和闪灯设计。

另验证3种预期失败：缺少模块结束、引用不存在模块，以及把与门误写为或门。功能错误例子可编译，测试明确产生两次FAIL；修正版本正常通过。没有把非零退出码当作唯一证据。工具原始诊断与检查输出见build/examples-verification.json。

波形直接读取21组实际VCD仿真记录，以仿真时间为横轴，动画游标仅放慢展示；未知值区间明确标记。状态图依据实际仿真状态点亮节点，并显示播放游标。该检查证明本课具体RTL行为与刺激，不证明已完成综合、时序收敛或硬件上板。

## 画面与同步

1920×1080，H.264/AAC，无底部字幕、无背景音乐。30fps动画网格，静态画面VFR保持。代码34px，输出30px且在左侧代码下方，长文件明确标注节选。每个代码页都有教师逐页复核的明确行号表content/focus.py，覆盖回跳、多行与保持；高亮保持至下段实际声音开始，不在句末闪灭。32段按人工编写的唯一短语触发，合计{t['continuousMotionSeconds']:.2f}秒连续播放区间。

全部71页、121段状态完成源画面排版检查；动态区间检查中间状态。实际成片{f['plannedEventsPresent']}个计划显示事件均存在；比对{f['encodedFramesCompared']}个编码帧，覆盖页面起止、段落切换前后、静止保持、32段动画四分位、全部练习倒计时和答案。主区最大平均像素差{f['maxDiagramMAE']:.3f}，侧区{f['maxNotesMAE']:.3f}。实际编码中全部32段均有可见变化。

90秒内部试片为2700帧，对照{p['actualSamples']}个编码样本，覆盖开场地图、思考与答案、加法进位、锁存、计数、非阻塞流水与闪灯波形。121段声音首尾各取1.2秒，共{a['waveformSamples']}个样本在最终AAC中匹配通过，最大位置偏差{a['maxSecondsDeviation']:.6f}秒，最低相关系数{a['minimumCorrelation']:.4f}。这是音轨合成位置验证，不是每个词的独立准确度证明。

另对前、中、后54秒最终AAC做本地ASR抽查，转录仅作辅助，可能有字母和同音词误识。按章查看编码状态联系表，并抽查关键完整画面；未声称逐分钟人工听看全片。全片音视频解码通过，10个内嵌章节与实测时间轴一致，无字幕轨，抽检底部无烧录字幕。

## 工程与安全

白名单工程包保留完整讲稿、71份逐页WAV、121份原始配音与精简复用字段、对齐缓存、实际VCD与波形数据、完整RTL和测试平台、例题答案及制作工具。仿真器、系统字体、模型权重、API Key、Workspace ID、私有账户加载器、原始服务响应、请求标识和帧缓存不打包。ZIP路径/CRC、敏感模式、无账号音频缓存及逐样本重建另外核对。

视频SHA-256：{f['videoSha256']}

时间轴SHA-256：{f['timelineSha256']}

课程SHA-256：{f['courseSha256']}

绘图源码SHA-256：{f['drawingSourceSha256']}

图示源码SHA-256：{f['diagramSourceSha256']}

输入改变后这些记录失效，需重新验证。
'''
 (ROOT/'docs/验收记录.md').write_text(text,encoding='utf8');shutil.copy2(ROOT/'docs/验收记录.md',DEL/'验收记录.md');out=DEL/'检查记录';out.mkdir(exist_ok=True)
 for name in ['final-validation.json','examples-verification.json','layout-review.json','preview-validation.json','audio-placement.json','speech-spotcheck.json','original-speed-check.json']:shutil.copy2(BUILD/name,out/name)
 print('VERILOG_DELIVERY_REPORT_READY',flush=True)
if __name__=='__main__':main()
