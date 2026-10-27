"""Bind artifact properties and the actual QA scope to the delivered files."""
import json,pathlib,shutil
from check import digest
from document import stamp
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out'

def load(p):return json.loads(p.read_text(encoding='utf8'))

def main():
    r=load(BUILD/'final-validation.json');a=load(BUILD/'audio-placement.json');p=load(BUILD/'preview-validation.json');speech=load(BUILD/'speech-spotcheck.json');speed=load(BUILD/'original-speed-check.json');models=load(BUILD/'examples-verification.json');layout=load(BUILD/'layout-review.json');settings=load(BUILD/'audio-settings.json');t=load(ROOT/'public/timeline.json');video=DEL/'一小时学完408操作系统_基础考点与解题步骤.mp4'
    assert all(x['allPassed'] for x in [r,a,p,speed,models,layout])
    assert r['videoSha256']==a['videoSha256']==speech['videoSha256']==digest(video)
    assert r['timelineSha256']==a['timelineSha256']==p['timelineSha256']==speed['timelineSha256']==digest(ROOT/'public/timeline.json')
    pause_count=sum(len(load((ROOT/'public'/s['audio']).with_suffix('.json'))['pauseRefinements']) for s in t['scenes'])
    text=f'''# 408操作系统视频验收记录

正式成片 **{stamp(t['duration'])}（{t['duration']:.3f}秒）**，10章、83页、145段讲解、10道原创随堂练习。面向第一次系统学习操作系统的大学生，强调概念辨析、算法步骤、条件和基础题型。范围见references/参考资料.md，没有声称逐字覆盖某年度官方大纲。

## 声音与停顿

用户明确选定百炼qwen-audio-3.1-tts-plus＋许南川xunanchuan_v3.1，原生合成rate=1.05；后期tempo=1.0，没有再次改变速度。

145份原始配音合计{settings['rawSeconds']:.3f}秒。原始MP3直接解码后，在{pause_count}处内部句号和145个段尾句号各增加0.1秒静音，合计{(pause_count+145)*.1:.1f}秒；逗号没有改动。原始语音与合在其中的呼吸声全部保留，没有剪字、去呼吸或时长压缩。其他时长来自页面前后短暂保持、逐帧取整及10次4秒思考。

最初1.05试音约26秒的连接处只有约0.16秒原生低能量间隔，未包含课程约定的句号额外停顿。已另给出仅增加句号0.1秒的试听副本，未覆盖原试音。正式课程停顿在制作时间轴之前完成。

## 画面与同步

1920×1080，H.264/AAC，无底部字幕、无背景音乐。30fps时间格；动态图逐格渲染，静态画面VFR保持，不将其描述为全片恒定30fps。开头直接列出实际十章知识地图。

相关讲解行由内容源focus/show人工指定，持续到下段实际旁白起点，不在句末闪灭。106段由唯一讲解短语触发的连续动作，共{r['continuousMotionSeconds']:.2f}秒，展示进程状态、甘特图、信号量、银行家算法、页表、置换、文件索引、寻道与I/O。算法中的逐步动作分别设置实际短语锚点，结束状态持续显示。

## 检查范围与结果

- **例题**：240项固定期望及状态约束检查通过，包含调度、RR、银行家安全性、LRU/FIFO/OPT、地址、索引、磁盘距离、缓冲周期、竞态与信号量。只证明这些具体题例与约束，不是一般算法证明或真实性能测试。
- **源画面**：两条数学表达式及83页、145个讲解状态排版通过，106段动作均检查四分位图形变化。已查看全部源状态联系表与分页地址、磁盘及缓冲等完整画面；磁道标签采用错行布局以避免相邻数字相接。
- **原始语音**：145份MP3独立解码；所有83份最终逐页WAV均由原样语音与约定静音逐样本精确重建。每段内部句号数量与实际插入数相符。模型、音色和rate由缓存元数据核对。
- **时间轴**：145段实际起点、106个人工短语锚点、所有动画格、状态保持和10组题答分离检查通过。服务返回的英文大小写只做字符等价处理；不使用含糊文字匹配来猜动作。
- **内部试片**：90秒、2700帧，比较{p['actualSamples']}个实际编码样本，覆盖知识地图、进程、轮转、银行家、置换、磁盘、4秒倒计时与答案，整片解码通过。
- **最终编码画面**：全部{r['plannedEventsPresent']}个计划显示事件存在于MP4；比较{r['encodedFramesCompared']}个编码帧，覆盖每页边界、每段状态、动作前后、全部动作四分位、所有练习倒计时与答案。106段动作在编码后均存在图形变化。图示区最大RGB平均绝对差{r['maxDiagramMAE']:.3f}，侧栏{r['maxNotesMAE']:.3f}，为编码与源图差异。
- **最终音轨位置**：145段前后各取1.2秒，共{a['waveformSamples']}个波形样本与最终AAC核对通过；最大位置偏差{a['maxSecondsDeviation']:.6f}秒，最低相关系数{a['minimumCorrelation']:.4f}。这是合成位置检查，不是每个词的对齐准确度证明。
- **语音抽查**：前、中、后共54秒最终AAC做本地ASR核对，参考与转录见speech-spotcheck.json。字母和术语可能被ASR误识别；未声称逐分钟人工听看。
- **完整性**：整片音视频解码通过，10个内嵌章节与实测时间轴一致，无字幕轨；编码帧底部区域检查未发现烧录字幕。最终状态联系表按章查看。

## 交付与安全

MP4、10章目录、逐页目录、完整讲稿、考点算法速查、十题答案、解题步骤、知识地图封面及可编辑工程。工程保留逐页WAV、145份原始1.05配音及对齐缓存，可以离线复用现有声音；不包含真实API Key、Workspace ID、私有账号加载器、请求标识及原始服务响应。另进行白名单打包、ZIP路径与CRC检查、模式扫描、离线缓存及语音重建验证。

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
