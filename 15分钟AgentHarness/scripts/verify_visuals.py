"""Validate topology and actual diagram motion/holds, not just a nonempty frame list."""
import hashlib,json,pathlib,sys
import numpy as np
from PIL import ImageColor
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'content'))
from visuals import GRAPHS
def main():
    t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));draw.init(t);records=[];holds=0
    for name,g in GRAPHS.items():
        ids={n['id'] for n in g['nodes']};assert len(ids)==len(g['nodes']);edges=set(g['edges']);assert all(a in ids and b in ids for a,b in edges)
        for phase,paths in g['paths'].items():
            assert len(paths)==2
            for p in paths:assert len(p)>=2 and set(zip(p,p[1:]))<=edges,(name,phase,p)
    for s in t['scenes']:
        for u in s['units']:
            previous=0
            for m in u['motions']:
                assert u['begin']<=m['begin']<m['end']<=u['end'] and previous==m['fromProgress'];previous=m['toProgress']
                images=[]
                for q in [.25,.5,.75]:
                    f=m['begin']+round((m['end']-m['begin'])*q);im=draw.render(s,f);images.append(np.asarray(im.crop((70,225,1235,915))).astype(np.int16))
                diffs=[float(np.mean(abs(a-b))) for a,b in zip(images,images[1:])]
                assert min(diffs)>.003,('Claimed motion is static',s['key'],u['index'],m['anchor'],diffs)
                records.append(dict(key=s['key'],part=u['index'],anchor=m['anchor'],seconds=(m['end']-m['begin'])/30,changes=diffs))
            if u['motions']:
                until=s['units'][u['index']+1]['begin']-1 if u['index']+1<len(s['units']) else s['durationFrames']-1
                assert draw.state(s,until)[0]==u['index'] and abs(draw.state(s,until)[1]-u['motions'][-1]['toProgress'])<1e-8;holds+=1
    # Independent picture invariants for the semantics of the hand-authored case.
    by={s['key']:s for s in t['scenes']}
    def fixed(key,index,progress):
        s=dict(by[key]);s['units']=[dict(index=index,begin=0,end=100,motions=[dict(begin=0,end=1,fromProgress=progress,toProgress=progress)])];return draw.render(s,2)
    a=np.asarray(fixed('ah-08-01',0,0).crop((120,385,800,510)));b=np.asarray(fixed('ah-08-01',0,.5).crop((120,385,800,510)));c=np.asarray(fixed('ah-08-01',0,1).crop((120,385,800,510)))
    assert np.array_equal(a,b),'First patch appeared before its operation';assert not np.array_equal(b,c),'Patch did not change the displayed actual file'
    im=fixed('ah-07-01',0,1);assert im.getpixel((70+292,225+536))==ImageColor.getrgb(draw.BLUE),'Parallel read B was never confirmed before join'
    im=fixed('ah-06-02',0,1);assert im.getpixel((70+585,225+135))==ImageColor.getrgb(draw.GRID),'Unrecorded completion was incorrectly confirmed before reconciliation'
    r=dict(allPassed=True,graphTopologies=len(GRAPHS),diagramKinds=19,continuousMotionIntervals=len(records),persistentUnitHolds=holds,actualContinuousSeconds=sum(x['seconds'] for x in records),minimumPictureChange=min(min(x['changes']) for x in records),scope='actual rendered quarter/half/three-quarter geometry and persistent holds, plus independently specified semantic invariants; not an audio or final codec check',courseSha256=hashlib.sha256((ROOT/'public/course.json').read_bytes()).hexdigest(),drawingSourceSha256=hashlib.sha256((ROOT/'scripts/draw.py').read_bytes()).hexdigest(),records=records)
    (ROOT/'build/visual-verification.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in r.items() if k!='records'},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
