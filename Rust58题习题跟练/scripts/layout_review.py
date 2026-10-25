"""Check layout-only PNGs. Synthetic timing cannot establish narration synchronization."""
import json,pathlib
from PIL import Image,ImageDraw,ImageFont
from check import pixels,expected,contacts
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));assert t['scope']=='layout-only'
    by={s['key']:s for s in t['scenes']}
    for j in t['renderJobs']:
        s=by[j['sceneKey']];local=j['frame']-s['startFrame']
        pixels(ROOT/'public'/j['path'],s,local,expected(s,local,measured=False))
    contacts(t,ROOT/'build/layout-qa')
    report=dict(allPassed=True,pages=len(t['scenes']),states=len(t['renderJobs']),scope='layout-only synthetic event positions; does not validate audio timing')
    (ROOT/'build/layout-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report),flush=True)
if __name__=='__main__':main()
