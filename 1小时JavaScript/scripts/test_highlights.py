"""Test the renderer's actual persistent selection and visible highlight pixels."""
import json,pathlib
import numpy as np
import draw
from highlight_sync import selected_lines
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    t=json.loads((ROOT/'public/timeline-highlighted.json').read_text(encoding='utf8'));states=0;changes=0;pauses=0;out=ROOT/'build/highlight-review';out.mkdir(exist_ok=True);entries=[]
    for s in t['scenes']:
        if s['kind']=='cover':continue
        cues=s['codeCues'];distinct={tuple(c['lines']) for c in cues};assert len(distinct)>1,(s['key'],'No dynamic selection')
        for i,c in enumerate(cues):
            assert selected_lines(s,c['beginFrame'])==c['lines']
            end=cues[i+1]['beginFrame'] if i+1<len(cues) else s['durationFrames']
            if end>c['beginFrame']:assert selected_lines(s,end-1)==c['lines']
            image=draw.render(s,c['beginFrame']);pixels=np.asarray(image);row=0
            for logical,line in enumerate(s['code'].splitlines(),1):
                for _ in draw.wrap(line,1190,34,True) or ['']:
                    rgb=pixels[247+row*40+20,1350].tolist();expected=[36,65,90] if logical in c['lines'] else [16,34,55]
                    assert rgb==expected,(s['key'],c['anchor'],logical,rgb,expected);row+=1
            states+=1
            if i and c['lines']!=cues[i-1]['lines']:changes+=1
            if s['key'] in ['js-03-01','js-05-02','js-09-05']:
                image.save(out/(s['key']+f'-{i:02}.png'))
            entries.append(dict(scene=s['key'],frame=c['beginFrame'],anchor=c['anchor'],selectedLines=c['lines']))
        for p in s['thinkFrames']:
            before=selected_lines(s,p['start']);assert selected_lines(s,p['end']-1)==before;pauses+=1
    report=dict(allPassed=True,visibleStates=states,selectionChanges=changes,thinkingIntervalsChecked=pauses,method='actual draw.render pixels and the same selected_lines implementation; authored semantic mapping reviewed separately',events=entries)
    (ROOT/'build/highlight-pixel-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('HIGHLIGHT_RENDERER_TESTED',states,changes,pauses,flush=True)
if __name__=='__main__':main()
