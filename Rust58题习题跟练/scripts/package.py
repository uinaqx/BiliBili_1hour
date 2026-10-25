"""Whitelist an editable project, sanitizing voice-cache metadata before ZIP creation."""
import hashlib,json,pathlib,shutil,zipfile
from safe_delivery import pack,secrets_from_env
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def main():
    t=load(ROOT/'public/timeline.json');assert t['scope']=='complete-course'
    final=load(BUILD/'final-validation.json');audio=load(BUILD/'audio-placement.json');preview=load(BUILD/'preview-validation.json')
    video=DEL/'Rust基础58题_习题跟练.mp4';video_hash=digest(video);timeline_hash=digest(ROOT/'public/timeline.json')
    for r in [final,audio]:assert r['allPassed'] and r['videoSha256']==video_hash and r['timelineSha256']==timeline_hash
    assert preview['allPassed'] and preview['timelineSha256']==timeline_hash
    assert final['courseSha256']==digest(ROOT/'public/course.json')
    base=['README.md','LICENSE','.env.example','.gitignore','package.json','package-lock.json','tsconfig.json','requirements.txt','public/course.json','public/timeline.json']
    for folder in ['src','content','scripts','docs','references','exercises']:
        base.extend(p.relative_to(ROOT).as_posix() for p in (ROOT/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    base.extend('build/'+name for name in ['exercise-verification.json','audio-settings.json','audio-preparation.json','chapters.ffmetadata','render-inputs.json','preflight-validation.json','preview-validation.json','final-validation.json','encoded-frame-checks.json','audio-placement.json','speech-spotcheck.json'])
    base.extend(p.relative_to(ROOT).as_posix() for p in (BUILD/'alignment').glob('*.json'))
    for s in t['scenes']:
        for extension in ['.wav','.json']:base.append('public/audio/'+s['key']+extension)
    stage=BUILD/'package-source'/ROOT.name;assert stage.resolve().is_relative_to(BUILD.resolve());stage.mkdir(parents=True,exist_ok=True)
    for name in sorted(set(base)):
        source=ROOT/name;assert source.is_file() and not source.is_symlink()
        dest=stage/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
    # Original MP3 is reusable media; only the necessary, explicitly named
    # cache fields travel with it. Request IDs, usage records and raw provider
    # responses never enter the deliverable. Audio itself is unchanged.
    for s in t['scenes']:
        for i,p in enumerate(s['parts']):
            key=s['key']+f'-p{i:02}';source=ROOT/'public/audio_original'/(key+'.mp3');m=load(source.with_suffix('.json'));assert m['narration']==p['text']
            name='public/audio_original/'+key+'.mp3';dest=stage/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest);base.append(name)
            name='public/audio_original/'+key+'.json';safe={k:m[k] for k in ['fingerprint','duration','voice','model','rate','words','narration']}
            safe['cacheMetadataSanitized']=True;(stage/name).write_text(json.dumps(safe,ensure_ascii=False,indent=2),encoding='utf8');base.append(name)
    manifest=dict(videoSha256=video_hash,timelineSha256=timeline_hash,files=[dict(path=n,sha256=digest(stage/n),bytes=(stage/n).stat().st_size) for n in sorted(set(base))],excluded=['real account values','private account loaders','raw service responses and request IDs','node_modules','rendered still caches','temporary executables and logs','conversation records'])
    name='docs/交付文件清单.json';(stage/name).write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');base.append(name)
    known=secrets_from_env(['DASHSCOPE_API_KEY','SFM_WORKSPACE_ID']);out=DEL/'Rust习题跟练_可编辑工程.zip'
    r=pack(stage,sorted(set(base)),out,known);assert r['allPassed'],r
    exercises=DEL/'Rust习题跟练_习题与答案.zip'
    if exercises.exists():raise ValueError('Exercise ZIP already exists; choose a new version')
    small=[n for n in sorted(set(base)) if n.startswith('exercises/') or n in ['LICENSE','references/Rustlings-LICENSE.txt','references/原目录说明.md','docs/习题索引.md','docs/逐题解析与答案.md','docs/逐题时间目录.txt']]
    exercise_report=pack(stage,small,exercises,known);assert exercise_report['allPassed'],exercise_report
    for path in [out,exercises]:
        with zipfile.ZipFile(path) as z:assert z.testzip() is None
    r.update(archiveSha256=digest(out),archiveBytes=out.stat().st_size,exerciseArchiveSha256=digest(exercises),exerciseArchiveBytes=exercises.stat().st_size,reusableVoiceClips=247,finalPageAudioFiles=183,voiceMetadata='explicit safe fields only; request IDs and raw responses excluded')
    (BUILD/'delivery-safety.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');shutil.copy2(BUILD/'delivery-safety.json',DEL/'工程安全检查.json')
    print(json.dumps(r,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
