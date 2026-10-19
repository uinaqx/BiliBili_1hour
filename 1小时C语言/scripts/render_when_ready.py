"""Encode only chapters whose current-version frames are fully available."""
import json,pathlib,subprocess,sys,time
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1]
t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf-8'))
code="import fs from 'node:fs';import c from 'node:crypto';let t=JSON.parse(fs.readFileSync('public/timeline.json','utf8'));console.log(c.createHash('sha256').update(fs.readFileSync('src/video.tsx')).update(fs.readFileSync('src/diagrams.tsx')).update(JSON.stringify(t)).digest('hex'));"
expected=subprocess.check_output(['node','--input-type=module','-e',code],cwd=ROOT,text=True).strip()
for chapter in t['chapters']:
    start=time.monotonic();announced=False
    while True:
        try:cache=json.loads((ROOT/'build/still-cache.json').read_text())
        except (FileNotFoundError,json.JSONDecodeError):cache={}
        missing=[p['path'] for p in chapter['images'] if cache.get(p['path'])!=expected or not (ROOT/'public'/p['path']).exists()]
        if not missing:break
        if not announced:print('WAITING_FOR_CURRENT_CHAPTER_FRAMES',chapter['key'],flush=True);announced=True
        if time.monotonic()-start>1800:raise TimeoutError(chapter['key'])
        time.sleep(2)
    subprocess.run([sys.executable,'scripts/render.py','--chapter',chapter['key']],cwd=ROOT,check=True)
    if chapter['key']=='01':
        subprocess.run([sys.executable,'scripts/render.py','--preview'],cwd=ROOT,check=True)
        print('INTERNAL_PREVIEW_READY',flush=True)
subprocess.run([sys.executable,'scripts/render.py'],cwd=ROOT,check=True)
