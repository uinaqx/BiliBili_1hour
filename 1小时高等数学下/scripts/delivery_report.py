"""Bind the delivered course, timing and QA scope to the actual final artifact."""
import json,pathlib,shutil
from check import digest
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    r=load(BUILD/'final-validation.json');a=load(BUILD/'audio-placement.json');p=load(BUILD/'preview-validation.json');speech=load(BUILD/'speech-spotcheck.json');speed=load(BUILD/'original-speed-check.json');m=load(BUILD/'math-verification.json');layout=load(BUILD/'layout-review.json');video=DEL/'一小时学完高等数学下_期末基础题型.mp4'
    assert all(x['allPassed'] for x in [r,a,p,speed,m,layout])
    assert r['videoSha256']==a['videoSha256']==speech['videoSha256']==digest(video)
    assert r['timelineSha256']==a['timelineSha256']==p['timelineSha256']==speed['timelineSha256']==digest(ROOT/'public/timeline.json')
    text=f'''# 高等数学（下）视频验收记录

正式成片 **01:03:30.933**，10章、82页、143段讲解。面向零基础大学生，延续高数上期末基础题型定位：先识别题型，再列公式、条件与解题步骤，不展开证明。10道练习各保留4秒思考，答案单独一页。学校的具体范围与评分要求以本校考纲和教材为准。

## 声音与画面

1920×1080，H.264/AAC，中文系统男声，无底部字幕、无背景音乐。原始配音总长60分26.256秒，加入句间静音、短暂页面保持、练习停顿后成为63分30.933秒。143段原始语音均为1.0倍速；没有通过改变语速去凑时长。句号之间额外增加0.1秒静音，逗号未改。

采用深色公式板、逐步显示与持续高亮，当前相关行保持到下段实际讲解开始，不在句末闪灭。64个由教师选定短语触发的连续动画区间，共{r['continuousMotionSeconds']:.2f}秒，展示向量、积分区域、球坐标、方向、法向与级数变化。动态图每30fps时间格渲染，静态段VFR保持，非全片恒定30fps。开头直接列10章知识点。

## 检查结果与实际范围

- **计算核对**：117项独立符号/数值核验通过，包含导数、积分、Jacobian、级数边界与前六个傅里叶系数。使用条件另按一手教材核对，来源见references/参考资料.md；例题核验不等于一般定理证明。
- **源画面**：215条数学表达式排版通过；82页、143个讲解状态及64段动画的四分位图形变化检查通过。已查看各章节源图联系表及代表性完整画面。
- **原始语速**：143份MP3独立解码后与预停顿PCM逐样本一致；82份最终逐页WAV均可由原样语音和约定静音精确重建。报告original-speed-check.json保存各片段与逐页哈希。
- **时间轴**：143段实际声学起点、64个人工短语锚点、动画逐格事件、句末保持及10组题答分离检查通过。语义对象由内容源的focus/show/phase指定，未按语速平均分配高亮。
- **内部试片**：90秒、2700帧，比较{p['actualSamples']}个实际编码样本，覆盖知识地图、公式、球坐标、高斯、倒计时与答案、傅里叶部分和；联系表已查看。
- **实际成片画面**：全部{r['plannedEventsPresent']}个计划显示事件存在于MP4时间戳；比较{r['encodedFramesCompared']}个编码画面，覆盖每段状态、每页边界、切换前后、所有动画四分位、练习倒计时及答案。64段动画在编码后均存在实际变化。最大图示/公式区RGB平均绝对差{r['maxDiagramMAE']:.3f}，侧栏{r['maxNotesMAE']:.3f}，为有损编码与源图差异。
- **实际成片音轨**：每段前后各取1.2秒波形，共{a['waveformSamples']}个样本，与最终AAC位置核对通过。最大位置偏差{a['maxSecondsDeviation']:.6f}秒，最低相关系数{a['minimumCorrelation']:.4f}。这是音轨合成位置检查，不是每个词对齐准确度的证明。
- **语音抽查**：对前、中、后共54秒最终AAC做本地ASR核对，样本及参考保存在speech-spotcheck.json。数学字母和术语可能有识别误差；未声称整片已逐分钟人工听看。
- **格式与完整性**：全片音视频解码通过，10个内嵌章节与原始时间轴一致，无字幕轨；实际底部抽样像素无烧录字幕。最终关键帧联系表按章查看。

## 配套与安全

交付MP4、10章目录、逐页目录、完整讲稿、公式速查、十章练习答案、考前步骤清单、知识地图封面及可编辑工程。工程保留最终逐页WAV、配音缓存和对齐资料，可离线复用配音。真实API Key、Workspace ID、私有账号加载器与原始服务响应不进入包。打包后另核对ZIP路径、CRC、模式扫描、离线缓存和原始语音重建。

## 版本绑定

- 视频SHA-256：`{r['videoSha256']}`
- 时间轴SHA-256：`{r['timelineSha256']}`
- 课程SHA-256：`{r['courseSha256']}`
- 绘图SHA-256：`{r['drawingSourceSha256']}`
- 数学图示SHA-256：`{r['diagramSourceSha256']}`

修改内容、音频或渲染输入后，相关旧报告视为过期，须重新生成。
'''
    (ROOT/'docs/验收记录.md').write_text(text,encoding='utf8');shutil.copy2(ROOT/'docs/验收记录.md',DEL/'验收记录.md');out=DEL/'检查记录';out.mkdir(exist_ok=True)
    for name in ['final-validation.json','math-verification.json','layout-review.json','audio-placement.json','speech-spotcheck.json','preview-validation.json','original-speed-check.json']:shutil.copy2(BUILD/name,out/name)
    print('DELIVERY_REPORT_READY',flush=True)
if __name__=='__main__':main()
