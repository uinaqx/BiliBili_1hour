"""Collect the voiced deliverables without copying account configuration."""
import json,pathlib,re,shutil,sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'production';OUT=ROOT/'out'
t=json.loads((P/'timeline.json').read_text(encoding='utf-8'))
acceptance=json.loads((P/'build/acceptance.json').read_text(encoding='utf-8'))
assert all(c['passed'] for c in acceptance['checks'])
(P/'production_state.json').write_text(json.dumps(dict(status='complete',durationSeconds=t['duration'],scenes=60,chapters=11,audioClips=180,subtitleCues=len(t['captions']),audio='synthesized_and_muxed',subtitle='aligned_to_tts_word_timestamps',validation='passed',source='user_supplied_svg_project',apiCredentialsStored=False),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def stamp(f):
    sec=f//30;h,sec=divmod(sec,3600);m,s=divmod(sec,60);return f'{h:02}:{m:02}:{s:02}'
rows=['# 两小时学习计算机组成原理：配音分段讲稿','','按照所提供原稿分离读题与答案，少数结束页补充口头答案。各段时间以实际配音版时间轴为准。','']
for s in t['scenes']:
    rows.append(f"\n## {stamp(s['startFrame'])} · {s['id']} {s['title']}")
    for part,c in zip(s['voiceParts'],s['clips']):
        role={'lesson':'讲解','question':'读题','answer':'答案与解释'}[part['kind']]
        rows.extend([f"\n### {stamp(s['startFrame']+c['startFrame'])} {role}", '\n'+part['narration']])
        if part['kind']=='question':rows.append('\n【独立思考】读题结束后 6 秒无新旁白，再显示答案。')
(OUT/'完整讲稿.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
shutil.copy2(P/'README.md',OUT/'制作说明.md')
for p in (ROOT/'docs').glob('05_*.md'):shutil.copy2(p,OUT/'课后实验与答案.md')
shutil.copy2(ROOT/'output/完整讲义.html',OUT/'完整讲义.html')
patterns=[rb'sk-[A-Za-z0-9._-]{24,}',rb'llm-[A-Za-z0-9]{10,}']
for folder in [P,OUT]:
    for p in folder.rglob('*'):
        if not p.is_file() or p.suffix.lower() not in {'.py','.js','.md','.json','.txt','.srt','.html','.log'}:continue
        assert not any(re.search(pattern,p.read_bytes()) for pattern in patterns),'Account identifier detected; file withheld'
print('DELIVERY_DOCUMENTS_DONE; no API key or workspace ID patterns found')
for p in OUT.iterdir():
    if p.is_file():print(p.name,round(p.stat().st_size/1024/1024,2),'MiB')
