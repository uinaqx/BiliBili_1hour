"""Render editable code and answer stills with placeholder timing."""
import json
from pathlib import Path
import sys
import draw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'content'))

def main():
    course = json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))
    output = ROOT/'out/edit-preview'
    output.mkdir(parents=True,exist_ok=True)
    for chapter in course['chapters']:
        for source in chapter['scenes']:
            scene = dict(source, chapter=chapter['title'], partFrames=[0,300], thinkFrames=[])
            # These frames preview the opening and answer states. Narration drives final timing.
            if all('cues' in part for part in scene['parts']):
                lines = [part['cues'][0]['lines'] for part in scene['parts']]
            else:
                from highlight_plan import PLAN, DISPLAY_OVERRIDES
                scene.update(DISPLAY_OVERRIDES.get(scene['key'], {}))
                plan = PLAN[scene['key']]
                initial = plan.get('initial', [])
                answer = next((cue['lines'] for cue in plan['cues'] if cue['part']==1), initial)
                lines = [initial, answer]
            if scene['kind']=='cover':
                lines[0] = []
            scene['codeCues'] = [dict(beginFrame=frame, lines=selection)
                                 for frame,selection in zip(scene['partFrames'],lines)]
            for index, frame in enumerate(scene['partFrames']):
                draw.render(scene,frame).save(output/f"{scene['key']}-{index}.png")
    print('PREVIEW_PAGES', sum(len(c['scenes']) for c in course['chapters']))

if __name__=='__main__':
    main()
