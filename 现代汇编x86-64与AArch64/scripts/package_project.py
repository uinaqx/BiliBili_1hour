"""Explicitly package the editable spoken release, excluding accounts and render caches."""
import json,pathlib
from safe_delivery import pack
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out'
def main():
 scripts=['audio.py','audio_timing.py','build_course.py','build_docs.py','check_spoken.py','draw.py','examples.py','package_project.py','prepare_spoken.py','preview_spoken.py','render_spoken.py','safe_delivery.py','speech_spotcheck.py','timeline_spoken.py','timing_utils.py','verify_examples.py']
 includes=['README.md','LICENSE','.gitignore','requirements.txt','requirements.lock.txt','requirements-alignment.txt','content','docs','examples','references','public/course.json','public/timeline.json','public/audio_original','build/assembled','build/alignment','build/native','build/native-build.json','build/execution-data.json','build/examples-verification.json','build/audio-preparation.json','build/spoken-preview-review.json','build/final-review.json','build/spoken/render-manifest.json','build/chapters-spoken.ffmetadata']
 includes+=['scripts/'+name for name in scripts]+['build/offline-voice-cache.json','build/speech-spotcheck.json']
 course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))
 for c in course['chapters']:
  for s in c['scenes']:
   includes.extend(['public/audio/'+s['key']+'.wav','public/audio/'+s['key']+'.json'])
 target=DEL/'现代汇编_x86-64与AArch64_可编辑工程.zip'
 report=pack(ROOT,includes,target);(DEL/'工程安全检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');assert report['allPassed'];print('PACKAGE_DONE',report['filesScanned'],target.stat().st_size,flush=True)
if __name__=='__main__':main()
