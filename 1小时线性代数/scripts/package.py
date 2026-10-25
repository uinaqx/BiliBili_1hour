"""Package only source, final narration, synchronization data and validation evidence."""
import hashlib,json,pathlib,shutil
import safe_delivery
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    t=load(ROOT/'public/timeline.json');v=load(ROOT/'build/final-validation.json');a=load(ROOT/'build/audio-placement.json')
    assert v['allPassed'] and a['allPassed']
    video=DEL/'一小时学习线性代数_动态可视化.mp4';video_hash=hashlib.sha256(video.read_bytes()).hexdigest()
    assert v['videoSha256']==a['videoSha256']==video_hash
    assert v['timelineSha256']==a['timelineSha256']==hashlib.sha256((ROOT/'public/timeline.json').read_bytes()).hexdigest()
    include=['README.md','LICENSE','requirements.txt','requirements-lock.txt','.gitignore','.env.example','content','scripts','docs','references','public/course.json','public/timeline.json','build/alignment','build/chapters.ffmetadata']
    reports=['math-verification.json','preflight-validation.json','final-validation.json','audio-settings.json','audio-preparation.json','audio-placement.json','speech-spotcheck.json','formula-review.json','encoded-frame-checks.json','encoded-motion-checks.json','render-manifest.json','preview-validation.json']
    for name in reports:
        assert (ROOT/'build'/name).exists(),name
        include.append('build/'+name)
    for s in t['scenes']:
        path=ROOT/'public'/s['audio'];assert path.is_file() and path.with_suffix('.json').is_file()
        include.extend([path.relative_to(ROOT).as_posix(),path.with_suffix('.json').relative_to(ROOT).as_posix()])
    target=DEL/'线性代数一小时_可编辑工程.zip'
    if target.exists():raise RuntimeError('Package already exists; retain the reviewed archive and choose a new version explicitly')
    report=safe_delivery.pack(ROOT,include,target)
    assert report['allPassed'],report
    report['archiveSha256']=hashlib.sha256(target.read_bytes()).hexdigest();report['archiveBytes']=target.stat().st_size
    (ROOT/'build/package-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    (DEL/'工程包检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    summary=dict(video=v,audioPlacement={k:value for k,value in a.items() if k!='samples'},package=report)
    (DEL/'验收报告.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
    rows=['# 线性代数课程验收记录','',f"成片时长：{t['duration']:.3f} 秒（59 分 54 秒）。",'',f"- 数学例题：{v['mathematicalChecks']} 项精确计算通过。",f"- PDF：{v['pdfSubsections']} 个小节；{v['chapters']} 章、{v['pages']} 页、{v['questions']} 道题。",f"- 持续动画：{v['motionIntervals']} 个区间，每秒 30 个时间点；{v['plannedEventsPresent']} 个计划显示事件全部存在。",f"- 实际视频画面对比：{v['encodedFramesCompared']} 帧，分别比较图示区与提示区。",f"- 语音位置：{a['semanticUnits']} 段，首尾共 {a['waveformSamples']} 次波形定位，最大偏差 {a['maxSecondsDeviation']:.6f} 秒。",'- 完整音视频解码、H.264/AAC 编码、1920×1080、十个章节标记通过。','- 所有页面的状态及习题答案画面均制作联系表并查看；额外 ASR 抽查首中尾 54 秒。','- 未声称人工逐分钟完整听审。','- 工程包使用白名单，扫描密钥与业务空间标识形态并验证 ZIP CRC。','',f'成片 SHA-256：`{video_hash}`','',f"工程包 SHA-256：`{report['archiveSha256']}`",'']
    (DEL/'验收说明.md').write_text('\n'.join(rows),encoding='utf8')
    print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
