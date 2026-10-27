"""Render every authored diagram state and prove phases differ visibly."""
import json, pathlib, sys

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import diagrams, examples


def main():
    out = ROOT / 'build' / 'diagram-preview'
    out.mkdir(parents=True, exist_ok=True)
    report = dict(allPassed=True, kinds=0, states=0, files=[], static=[], size=[1165, 310])
    for kind, phases in examples.VISUALS.items():
        report['kinds'] += 1
        images = {}
        for phase in phases:
            for t in (0.0, 0.5, 1.0):
                im = diagrams.render(dict(kind=kind), phase, t)
                assert im.size == (1165, 310), (kind, phase, im.size)
                path = out / f'{kind}-{phase}-{int(t * 100):03}.png'
                im.save(path)
                report['states'] += 1
                report['files'].append(path.name)
                images[(phase, t)] = np.asarray(im.convert('RGB')).astype(np.int16)
        if len(phases) >= 2:
            first = images[(phases[0], 1.0)]
            second = images[(phases[1], 1.0)]
            maes = [float(np.mean(abs(first - images[(phases[1], t_)]))) for t_ in (0.0, 0.5, 1.0)]
            assert max(maes) > 0.5, ('Phases look identical', kind, phases, maes)
        motion = max(float(np.mean(abs(images[(phase, 0.0)] - images[(phase, 1.0)]))) for phase in phases)
        if motion <= 0.01:
            report['static'].append(dict(kind=kind, mae=motion))
        report.setdefault('motion', []).append(dict(kind=kind, maxMae=motion))
    report['allPassed'] = report['allPassed'] and len(report['static']) < report['kinds']
    (ROOT / 'build' / 'diagram-check.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf8')
    print(json.dumps(dict(allPassed=report['allPassed'], kinds=report['kinds'], states=report['states'], static=report['static']), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
