"""Whitelist only reproducible source and final narration; omit all private/provider caches."""
import hashlib,json,pathlib,shutil,sys,zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def main():
    report=json.loads((ROOT/'build/final-validation.json').read_text(encoding='utf8'));final=DEL/'一小时学习Kotlin_零基础.mp4'
    assert report['allPassed'] and hashlib.sha256(final.read_bytes()).hexdigest()==report['videoSha256']
    assert hashlib.sha256((ROOT/'public/timeline.json').read_bytes()).hexdigest()==report['timelineSha256']
    selected=[]
    for folder in ['src','scripts','content','docs']:
        selected.extend(p for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
    for name in ['README.md','LICENSE','package.json','package-lock.json','tsconfig.json','requirements.txt','.gitignore','.env.example','public/course.json','public/timeline.json','build/audio-settings.json','build/chapters.ffmetadata','build/example-verification.json','build/audio-preparation.json','build/final-validation.json']:
        p=ROOT/name
        if p.exists():selected.append(p)
    timeline=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'))
    for s in timeline['scenes']:
        selected.extend([ROOT/'public'/s['audio'],(ROOT/'public'/s['audio']).with_suffix('.json')])
    assert all(p.name!='.env.local' and 'node_modules' not in p.parts and 'audio_original' not in p.parts for p in selected)
    dest=DEL/'Kotlin一小时_可编辑工程.zip';temp=dest.with_suffix('.packing.zip')
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED,compresslevel=5) as z:
        for p in sorted(set(selected)):z.write(p,'Kotlin一小时制作工程/'+p.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(temp) as z:assert z.testzip() is None
    import safe_delivery
    issues=safe_delivery.scan(temp,[])
    if isinstance(issues,dict):
        assert issues.get('allPassed'), 'Archive privacy audit failed'
    elif issues:raise RuntimeError('Archive privacy audit failed; inspect safe filenames only')
    temp.replace(dest)
    rows=['# Kotlin 课程制作与验收记录','',f"成片时长：{timeline['duration']:.3f} 秒。",'10 个章节、66 个片段、中文旁白、无底部字幕。','',f"实际检查源帧状态：{report['renderedStatesChecked']}；编码帧状态：{report['encodedStatesChecked']}。",'全部示例、预期编译错误与运行时错误按类别验证通过。','高亮逻辑穷举全片有代码的时间网格帧，并检查实际成片的选中像素、章节、格式和完整解码。','检查不声称逐分钟人工听完全部课程。','','成片 SHA-256：'+report['videoSha256'],'时间轴 SHA-256：'+report['timelineSha256'],'','工程用法、字体和工具链要求见压缩包内 README.md。','配音参数仅使用系统音色。包内不含 API Key、Workspace ID、私人配置、原始服务记录或对话日志。']
    (DEL/'制作说明.md').write_text('\n'.join(rows)+'\n',encoding='utf8')
    (DEL/'验收记录.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print('PACKAGE_DONE',len(set(selected)),dest.stat().st_size,flush=True)
if __name__=='__main__':main()
