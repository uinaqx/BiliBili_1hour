import json,pathlib,shutil
from check import digest
from document import stamp
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
 t=load(ROOT/'public/timeline.json');f=load(BUILD/'final-validation.json');a=load(BUILD/'audio-placement.json');p=load(BUILD/'preview-validation.json');speed=load(BUILD/'original-speed-check.json');m=load(BUILD/'examples-verification.json');speech=load(BUILD/'speech-spotcheck.json');layout=load(BUILD/'layout-review.json')
 assert all(x['allPassed'] for x in [f,a,p,speed,m,layout]);video=DEL/'一小时学完离散数学_可视化基础.mp4'
 assert f['videoSha256']==a['videoSha256']==speech['videoSha256']==digest(video)
 assert f['timelineSha256']==a['timelineSha256']==p['timelineSha256']==speed['timelineSha256']==digest(ROOT/'public/timeline.json')
 assert f['courseSha256']==m['courseSha256']==digest(ROOT/'public/course.json')
 text=f'''# 离散数学视频验收记录

成片{stamp(t['duration'])}（{t['duration']:.3f}秒），10章71页121段讲解，10道练习各有4秒思考与独立答案页。零基础大学生，常见本科基础知识入门。

声音为百炼3.1 Plus、许南川、原生1.05；后期tempo=1.0，保留所有语音样本，只增加约定句号静音。121份原始MP3独立解码、71份最终WAV逐样本重建通过。无字幕、无音乐。

190项例题计算、真值表穷举、有限关系与函数检查、计数、递推、欧拉路线、最短路、生成树、编码及模4结合律验证通过。84条公式排版通过。来源核对及题目适用条件见参考资料，不把有限检查当成一般定理的完整证明。

全部71页121段状态做源图排版检查并查看按章联系表。38个人工选定短语通过已知文本声学对齐定位，共{t['continuousMotionSeconds']:.2f}秒动画；强调对象保持到下段实际声音起点，动画末态继续保持。逐页检查中修正了德摩根律两种形式的表格对应、幂集与笛卡尔积的分幕，以及斐波那契对前两项的依赖箭头。

90秒内部试片，2700帧，对照{p['actualSamples']}个实际编码样本，覆盖知识地图、题答、集合、传递关系、计数、欧拉路线和生成树。实际MP4包含全部{f['plannedEventsPresent']}个计划画面事件，对比{f['encodedFramesCompared']}个编码帧，覆盖页面边界、语义切换前后、各段保持、所有动画四分位和10组练习答案。主区最大平均像素差{f['maxDiagramMAE']:.3f}，侧区{f['maxNotesMAE']:.3f}。38段动画编码后均有可见变化。

121段旁白的开头与结尾各取1.2秒，在最终AAC中匹配，共{a['waveformSamples']}个检查，最大位置偏差{a['maxSecondsDeviation']:.6f}秒，最低相关系数{a['minimumCorrelation']:.4f}。这是声音放置位置的验证，不是每个词时间的独立准确率。另对前中后54秒AAC做本地ASR辅助抽查，允许同音字和数学名词误识；没有声称逐分钟人工听完。

1920×1080、H.264/AAC、10个内嵌章节；30fps动态网格，静态VFR保持。全片解码通过，章节与实测时间一致，无字幕轨，底部像素检查无烧录字幕。实际编码状态联系表与代表完整画面已抽查。

交付工程以白名单选择，原始配音元数据只保留复用字段；账号值、私有加载器和请求标识不收集。ZIP另做安全路径、CRC和敏感模式扫描，离线缓存及原始样本重建检查结果见工程安全检查。

视频SHA-256：{f['videoSha256']}

时间轴SHA-256：{f['timelineSha256']}

课程SHA-256：{f['courseSha256']}

绘图SHA-256：{f['drawingSourceSha256']}

图示SHA-256：{f['diagramSourceSha256']}
'''
 (ROOT/'docs/验收记录.md').write_text(text,encoding='utf8');shutil.copy2(ROOT/'docs/验收记录.md',DEL/'验收记录.md');out=DEL/'检查记录';out.mkdir(exist_ok=True)
 for n in ['final-validation.json','examples-verification.json','layout-review.json','preview-validation.json','audio-placement.json','speech-spotcheck.json','original-speed-check.json']:shutil.copy2(BUILD/n,out/n)
 print('DELIVERY_REPORT_READY',flush=True)
if __name__=='__main__':main()
