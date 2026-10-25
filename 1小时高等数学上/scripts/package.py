"""Explicit-include editable course with sanitized reusable voice metadata."""
import hashlib,json,pathlib,shutil,zipfile
from safe_delivery import pack,secrets_from_env
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for data in iter(lambda:f.read(1024*1024),b''):h.update(data)
    return h.hexdigest()
def main():
    t=load(ROOT/'public/timeline.json');r=load(BUILD/'final-validation.json');a=load(BUILD/'audio-placement.json');preview=load(BUILD/'preview-validation.json');video=DEL/'一小时学完高等数学上_期末基础题型.mp4';vh=digest(video);th=digest(ROOT/'public/timeline.json');assert t['scope']=='complete-course'
    for data in [r,a]:assert data['allPassed'] and data['videoSha256']==vh and data['timelineSha256']==th
    assert preview['allPassed'] and preview['timelineSha256']==th and r['courseSha256']==digest(ROOT/'public/course.json')
    includes=['README.md','LICENSE','.gitignore','.env.example','requirements.txt','requirements.lock.txt','public/course.json','public/timeline.json']
    for name in ['content','scripts','docs','references']:
        includes.extend(p.relative_to(ROOT).as_posix() for p in (ROOT/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    for name in ['alignment','formulas']:includes.extend(p.relative_to(ROOT).as_posix() for p in (BUILD/name).glob('*') if p.is_file())
    includes.extend('build/'+name for name in ['math-verification.json','formula-review.json','audio-settings.json','audio-preparation.json','layout-review.json','preflight-validation.json','preview-validation.json','final-validation.json','encoded-frame-checks.json','audio-placement.json','speech-spotcheck.json','chapters.ffmetadata','render-manifest.json'])
    for s in t['scenes']:
        for extension in ['.wav','.json']:includes.append('public/audio/'+s['key']+extension)
    stage=BUILD/'package-source'/ROOT.name;assert stage.resolve().is_relative_to(BUILD.resolve());stage.mkdir(parents=True,exist_ok=True)
    for name in sorted(set(includes)):
        source=ROOT/name;assert source.is_file() and not source.is_symlink();dest=stage/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
    clips=0
    for s in t['scenes']:
        for i,p in enumerate(s['parts']):
            key=s['key']+f'-p{i:02}';source=ROOT/'public/audio_original'/(key+'.mp3');m=load(source.with_suffix('.json'));assert m['narration']==p['text'];folder=stage/'public/audio_original';folder.mkdir(parents=True,exist_ok=True);shutil.copy2(source,folder/source.name)
            safe={k:m[k] for k in ['fingerprint','duration','voice','model','rate','words','narration']};safe['cacheMetadataSanitized']=True;(folder/(key+'.json')).write_text(json.dumps(safe,ensure_ascii=False,indent=2),encoding='utf8');includes.extend(['public/audio_original/'+key+ext for ext in ['.mp3','.json']]);clips+=1
    manifest=dict(videoSha256=vh,timelineSha256=th,files=[dict(path=n,sha256=digest(stage/n),bytes=(stage/n).stat().st_size) for n in sorted(set(includes))],excluded=['real account values','private account loaders','request identifiers and raw service responses','rendered frame caches','dependency caches','temporary logs','conversation records'])
    name='docs/交付文件清单.json';(stage/name).write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');includes.append(name)
    archive=DEL/'高等数学上_可编辑工程.zip';report=pack(stage,sorted(set(includes)),archive,secrets_from_env(['DASHSCOPE_API_KEY','SFM_WORKSPACE_ID']));assert report['allPassed'],report
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    report.update(archiveSha256=digest(archive),archiveBytes=archive.stat().st_size,finalPageAudioFiles=len(t['scenes']),reusableVoiceClips=clips,voiceMetadata='only explicit reuse fields; no raw responses or request IDs')
    (BUILD/'delivery-safety.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');shutil.copy2(BUILD/'delivery-safety.json',DEL/'工程安全检查.json');print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
