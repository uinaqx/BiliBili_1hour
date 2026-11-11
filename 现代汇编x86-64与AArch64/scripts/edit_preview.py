"""Render still previews from the course's silent editing timeline."""
import json
from pathlib import Path
import draw

ROOT = Path(__file__).resolve().parents[1]

def main():
    timeline = json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'))
    course = json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))
    if hasattr(draw, 'prepare_formulas'):
        draw.prepare_formulas(course)
    if hasattr(draw, 'init'):
        draw.init(timeline)
    output = ROOT/'out/edit-preview'
    output.mkdir(parents=True,exist_ok=True)
    for scene in timeline['scenes']:
        draw.render(scene,0).save(output/(scene['key']+'.png'))
    print('PREVIEW_PAGES', len(timeline['scenes']))

if __name__=='__main__':
    main()
