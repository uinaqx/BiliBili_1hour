"""Bind artifact properties and the actual QA scope to the delivered files."""
import json,pathlib,shutil
from check import digest
from document import stamp
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    r=load(BUILD/'final-validation.json');a=load(BUILD/'audio-placement.json');p=load(BUILD/'preview-validation.json');speech=load(BUILD/'speech-spotcheck.json');speed=load(BUILD/'original-speed-check.json');models=load(BUILD/'examples-verification.json');layout=load(BUILD/'layout-review.json');settings=load(BUILD/'audio-settings.json');t=load(ROOT/'public/timeline.json');video=DEL/'一小时学完计算机网络_百炼3.1Plus许南川_1.05倍速.mp4'
    assert all(x['allPassed'] for x in [r,a,p,speed,models,layout])
    assert r['videoSha256']==a['videoSha256']==speech['videoSha256']==digest(video)
    assert r['timelineSha256']==a['timelineSha256']==p['timelineSha256']==speed['timelineSha256']==digest(ROOT/'public/timeline.json')
    pause_count=sum(len(load((ROOT/'public'/s['audio']).with_suffix('.json'))['pauseRefinements']) for s in t['scenes'])
    units=sum(len(s['parts']) for s in t['scenes']);pages=len(t['scenes']);motions=r['motionIntervals']
    text=f'''# 计算机网络一小时视频验收记录

正式成片 **{stamp(t['duration'])}（{t['duration']:.3f}秒）**，10章、{pages}页、{units}段讲解、10道原创随堂练习。面向零基础大学生，强调分层模型、协议过程、计算例题和易错点。范围见references/参考资料.md，没有声称逐字覆盖某年度官方大纲。

## 声音与停顿

旁白使用阿里云百炼 **qwen-audio-3.1-tts-plus＋许南川（xunanchuan_v3.1）**，用户明确指定原生合成速率1.05，后期tempo=1.0，不再二次变速。原版内容和绘图逻辑保留；逐页时间、动作触发和章节起点依据新音频重新生成。

{units}份原始配音合计{settings['rawSeconds']:.3f}秒。原始MP3直接解码后，在{pause_count}处内部句号和{units}个段尾句号各增加0.1秒静音，合计{(pause_count+units)*.1:.1f}秒；逗号没有改动。原始语音样本全部保留，没有剪字或时长压缩。其他时长来自页面前后短暂保持、逐帧取整及10次4秒思考。

## 画面与同步

1920×1080，H.264/AAC，无底部字幕、无背景音乐。30fps时间格；动态图逐格渲染，静态画面VFR保持，不将其描述为全片恒定30fps。开头直接列出实际十章知识地图。

相关讲解行由内容源focus/show人工指定，持续到下段实际旁白起点，不在句末闪灭。{motions}段由唯一讲解短语触发的连续动作，共{r['continuousMotionSeconds']:.2f}秒，覆盖分层封装、时延构成、编码、以太网帧、交换机自学习、子网划分、IP分片、NAT、最长前缀匹配、握手挥手、滑动窗口、拥塞窗口和DNS访问链。动作锚点全部由人工在旁白中选定，结束状态持续显示。

## 检查范围与结果

- **数值例题**：{models['checks']}项独立固定期望及状态约束检查通过，包含子网地址与广播、CIDR聚合、分片长度与片偏移、发送/传播时延、TCP序号与确认号、滑动窗口位置、拥塞窗口轮次、RIP跳数与知名端口。只证明这些具体题例与约束，不是一般协议实现证明。
- **源画面**：全部{pages}页、{units}个讲解状态排版通过，{motions}段动作均检查四分位图形变化。已查看源状态联系表与关键图示完整画面。
- **原始语音**：{units}份MP3独立解码；所有{pages}份最终逐页WAV均由原样语音与约定静音逐样本精确重建。每段内部句号数量与实际插入数相符。音色与合成语速由缓存元数据核对。
- **时间轴**：{units}段实际起点、{motions}个人工短语锚点、所有动画格、状态保持和10组题答分离检查通过。不使用含糊文字匹配来猜动作。
- **内部试片**：90秒、2700帧，比较{p['actualSamples']}个实际编码样本，覆盖知识地图、练习倒计时与答案、编码、以太网帧、子网划分、握手与拥塞窗口，整片解码通过。
- **最终编码画面**：全部{r['plannedEventsPresent']}个计划显示事件存在于MP4；比较{r['encodedFramesCompared']}个编码帧，覆盖每页边界、每段状态、动作前后、全部动作四分位、所有练习倒计时与答案。{motions}段动作在编码后均存在图形变化。图示区最大RGB平均绝对差{r['maxDiagramMAE']:.3f}，侧栏{r['maxNotesMAE']:.3f}，为编码与源图差异。
- **最终音轨位置**：{units}段前后各取1.2秒，共{a['waveformSamples']}个波形样本与最终AAC核对通过；最大位置偏差{a['maxSecondsDeviation']:.6f}秒，最低相关系数{a['minimumCorrelation']:.4f}。这是合成位置检查，不是每个词的对齐准确度证明。
- **语音抽查**：前、中、后共54秒最终AAC做本地ASR核对，参考与转录见build/speech-spotcheck.json。字母和术语可能被ASR误识别；未声称逐分钟人工听看。
- **完整性**：整片音视频解码通过，10个内嵌章节与实测时间轴一致，无字幕轨；编码帧底部区域检查未发现烧录字幕。最终状态联系表按章查看。

## 交付与安全

MP4、10章目录、逐页目录、完整讲稿、考点速查、十题答案、解题步骤、知识地图封面及可编辑工程。工程保留逐页WAV、{units}份原始配音及对齐缓存，可以离线复用现有声音；不包含真实API Key、Workspace ID、私有账号加载器、请求标识及原始服务响应。另进行白名单打包、ZIP路径与CRC检查、模式扫描、离线缓存及语音重建验证。

## 版本绑定

- 视频SHA-256：`{r['videoSha256']}`
- 时间轴SHA-256：`{r['timelineSha256']}`
- 课程SHA-256：`{r['courseSha256']}`
- 绘图SHA-256：`{r['drawingSourceSha256']}`
- 图示SHA-256：`{r['diagramSourceSha256']}`
- 例题模型SHA-256：`{r['exampleSourceSha256']}`

输入变化后旧报告失效，应重新生成。
'''
    (ROOT/'docs/验收记录.md').write_text(text,encoding='utf8');shutil.copy2(ROOT/'docs/验收记录.md',DEL/'验收记录.md');out=DEL/'检查记录';out.mkdir(exist_ok=True)
    for name in ['final-validation.json','examples-verification.json','layout-review.json','audio-placement.json','speech-spotcheck.json','preview-validation.json','original-speed-check.json']:shutil.copy2(BUILD/name,out/name)
    print('DELIVERY_REPORT_READY',flush=True)
if __name__=='__main__':main()
