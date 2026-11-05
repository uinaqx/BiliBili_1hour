"""Render authored course pages without credentials, speech caches, or estimated timing."""
import argparse
import json
import pathlib
import draw

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scene', help='For example m01-001; defaults to the first scene of every chapter')
    parser.add_argument('--beat', type=int, default=0)
    args = parser.parse_args()
    course = json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))
    selected = [(c,s) for c in course['chapters'] for s in c['scenes'] if s['id']==args.scene] if args.scene else [(c,c['scenes'][0]) for c in course['chapters']]
    if not selected:
        parser.error('Unknown scene ID')
    out = ROOT/'out/preview'
    out.mkdir(parents=True,exist_ok=True)
    for chapter,scene in selected:
        if not 0 <= args.beat < len(scene['beats']):
            parser.error('Beat index outside scene')
        # These indices select a static state only; no narrated timing is fabricated.
        view = dict(scene,chapter=chapter['title'],beatFrames=list(range(len(scene['beats']))))
        draw.render(view,args.beat).save(out/(scene['id']+f'-beat{args.beat}.png'))
    print('STATIC_PREVIEWS',len(selected),flush=True)


if __name__ == '__main__':
    main()
