"""Explicit whitelist package, sanitized voice metadata and offline cache proof."""
import json,pathlib,shutil,subprocess,sys,zipfile
from safe_delivery import pack,secrets_from_env
from check import digest
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def main():
    t=load(ROOT/'public/timeline.json');r=load(BUILD/'final-validation.json');a=load(BUILD/'audio-placement.json');preview=load(BUILD/'preview-validation.json');video=DEL/'15分钟讲清AgentHarness_底层原理_正常语速版.mp4';vh=digest(video);th=digest(ROOT/'public/timeline.json');assert t['scope']=='complete-course'
    for data in [r,a]:assert data['allPassed'] and data['videoSha256']==vh and data['timelineSha256']==th
    assert preview['allPassed'] and preview['timelineSha256']==th and r['courseSha256']==digest(ROOT/'public/course.json') and r['drawingSourceSha256']==digest(ROOT/'scripts/draw.py')
    includes=['README.md','LICENSE','.gitignore','.env.example','requirements.txt','requirements.lock.txt','public/course.json','public/timeline.json']
    for name in ['content','scripts','docs','references','demo']:includes.extend(p.relative_to(ROOT).as_posix() for p in (ROOT/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    includes.extend(p.relative_to(ROOT).as_posix() for p in (BUILD/'alignment').glob('*.json'))
    includes.extend('build/'+name for name in ['demo-execution.json','demo-verification.json','visual-verification.json','audio-settings.json','audio-preparation.json','layout-review.json','preflight-validation.json','preview-validation.json','final-validation.json','encoded-frame-checks.json','encoded-motion-checks.json','audio-placement.json','speech-spotcheck.json','chapters.ffmetadata','render-manifest.json','original-speed-check.json'])
    for s in t['scenes']:
        for ext in ['.wav','.json']:includes.append('public/audio/'+s['key']+ext)
    stage=BUILD/'package-source'/ROOT.name;assert stage.resolve().is_relative_to(BUILD.resolve());stage.mkdir(parents=True,exist_ok=True)
    for name in sorted(set(includes)):
        source=ROOT/name;assert source.is_file() and not source.is_symlink();dest=stage/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
    clips=0
    for s in t['scenes']:
        for i,p in enumerate(s['parts']):
            key=s['key']+f'-p{i:02}';source=ROOT/'public/audio_original'/(key+'.mp3');m=load(source.with_suffix('.json'));assert m['narration']==p['text'];folder=stage/'public/audio_original';folder.mkdir(parents=True,exist_ok=True);shutil.copy2(source,folder/source.name)
            safe={k:m[k] for k in ['fingerprint','duration','voice','model','rate','words','narration']};safe['cacheMetadataSanitized']=True;(folder/(key+'.json')).write_text(json.dumps(safe,ensure_ascii=False,indent=2),encoding='utf8');includes.extend(['public/audio_original/'+key+ext for ext in ['.mp3','.json']]);clips+=1
    p=subprocess.run([sys.executable,'-X','utf8','scripts/check_voice_cache.py'],cwd=stage,capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;cache=json.loads(p.stdout);assert cache['allPassed'] and cache['clips']==clips and cache['networkDisabled']
    (BUILD/'offline-cache-check.json').write_text(json.dumps(cache,ensure_ascii=False,indent=2),encoding='utf8');shutil.copy2(BUILD/'offline-cache-check.json',stage/'build/offline-cache-check.json');includes.append('build/offline-cache-check.json')
    p=subprocess.run([sys.executable,'-X','utf8','scripts/check_original_speed.py'],cwd=stage,capture_output=True,text=True,encoding='utf8');assert p.returncode==0,p.stderr;offline_speed=json.loads(p.stdout);assert offline_speed['allPassed'] and offline_speed['speechClipsCompared']==clips and offline_speed['wholeCourseTempo']==1.0
    (BUILD/'offline-original-speed-check.json').write_text(json.dumps(offline_speed,ensure_ascii=False,indent=2),encoding='utf8');shutil.copy2(BUILD/'offline-original-speed-check.json',stage/'build/offline-original-speed-check.json');includes.append('build/offline-original-speed-check.json')
    # Preserve the original repair's baseline provenance after the portable recheck.
    shutil.copy2(BUILD/'original-speed-check.json',stage/'build/original-speed-check.json')
    manifest=dict(videoSha256=vh,timelineSha256=th,files=[dict(path=n,sha256=digest(stage/n),bytes=(stage/n).stat().st_size) for n in sorted(set(includes))],excluded=['real account values','private account loaders','request identifiers and raw service responses','rendered frame caches','dependency caches','temporary logs','conversation records'])
    name='docs/交付文件清单.json';(stage/name).write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8');includes.append(name)
    archive=DEL/'AgentHarness十五分钟_正常语速版_可编辑工程.zip';report=pack(stage,sorted(set(includes)),archive,secrets_from_env(['DASHSCOPE_API_KEY','SFM_WORKSPACE_ID']));assert report['allPassed'],report
    with zipfile.ZipFile(archive) as z:assert z.testzip() is None
    report.update(archiveSha256=digest(archive),archiveBytes=archive.stat().st_size,videoSha256=vh,timelineSha256=th,finalPageAudioFiles=len(t['scenes']),reusableVoiceClips=clips,offlineCacheVerified=cache,offlineOriginalSpeedVerified=offline_speed,voiceMetadata='explicit reuse fields only; no request IDs or raw responses')
    (BUILD/'delivery-safety.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');shutil.copy2(BUILD/'delivery-safety.json',DEL/'工程安全检查.json');print(json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
