"""Resolve the reviewed semantic plan against final, sample-mapped word times."""
import hashlib,json,math,pathlib,re,sys
def normal(text):return ''.join(c.casefold() for c in text if c.isalnum())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def apply_highlights(root,timeline):
    sys.path.insert(0,str(root/'content'))
    from highlight_plan import PLAN,DISPLAY_OVERRIDES
    keys={s['key'] for s in timeline['scenes']}
    assert keys<=set(PLAN),'Semantic plan must cover every page'
    if timeline['scope']=='complete':assert set(PLAN)==keys
    audit=[]
    for s in timeline['scenes']:
        if s['key'] in DISPLAY_OVERRIDES:s.update(DISPLAY_OVERRIDES[s['key']])
        plan=PLAN[s['key']];n=len(s['code'].splitlines());events=[]
        if s['kind']=='cover':
            s['codeCues']=[];audit.append(dict(scene=s['key'],reason=plan['reason'],events=[]));continue
        assert plan['initial']
        events=[dict(beginFrame=0,lines=plan['initial'],anchor='page initial selection',method='authored semantic plan')]
        path=root/'public'/s['audio'];m=json.loads(path.with_suffix('.json').read_text(encoding='utf8'));assert sha(path)==s['audioSha256']==m['sha256']
        for cue in plan['cues']:
            part=m['parts'][cue['part']];needle=normal(cue['anchor']);authored=normal(part['cue'])
            assert authored.count(needle)==1,('Missing/ambiguous authored anchor',s['key'],cue)
            chars=[];times=[]
            for w in part['words']:
                for char in normal(w['text']):chars.append(char);times.append(w['begin_time']/1000)
            text=''.join(chars);at=text.find(needle)
            assert at>=0 and text.find(needle,at+1)<0,('Missing/ambiguous audio anchor',s['key'],cue)
            seconds=part['start']+times[at];frame=s['leadFrames']+math.ceil(seconds*timeline['fps']-1e-6)
            assert 0<=frame<s['durationFrames']
            assert frame>=events[-1]['beginFrame'],('Authored cue order',s['key'],cue,frame,events[-1])
            if frame==events[-1]['beginFrame']:
                assert cue['lines']==events[-1]['lines'],('Conflicting same-frame cues',s['key'],cue)
            events.append(dict(beginFrame=frame,lines=cue['lines'],anchor=cue['anchor'],part=cue['part'],finalAudioSeconds=seconds,method='authored phrase resolved to final audio tokens'))
        for e in events:
            assert e['lines'] and all(1<=line<=n and s['code'].splitlines()[line-1].strip() for line in e['lines']),(s['key'],e)
        s['codeCues']=events
        s['renderFrames']=sorted(set(s['renderFrames'])|{e['beginFrame'] for e in events})
        audit.append(dict(scene=s['key'],audioSha256=m['sha256'],events=events,distinctSelections=len({tuple(e['lines']) for e in events})))
    lookup={s['key']:s for s in timeline['scenes']}
    for c in timeline['chapters']:c['scenes']=[lookup[s['key']] for s in c['scenes']]
    report=dict(allPassed=True,planSha256=sha(root/'content/highlight_plan.py'),pages=len(audit),authoredEvents=sum(len(a['events']) for a in audit),scenes=audit)
    (root/'build/highlight-resolution.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    return timeline
def selected_lines(scene,frame):
    if scene['kind']=='cover':return []
    events=scene['codeCues'];assert events and events[0]['beginFrame']==0
    import bisect
    return events[bisect.bisect_right([e['beginFrame'] for e in events],frame)-1]['lines']
if __name__=='__main__':
    root=pathlib.Path(__file__).resolve().parents[1]
    t=json.loads((root/'public/timeline.json').read_text(encoding='utf8'));t=apply_highlights(root,t)
    (root/'public/timeline-highlighted.json').write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf8')
    print('AUTHORED_HIGHLIGHTS_RESOLVED',sum(len(s['codeCues']) for s in t['scenes']),flush=True)
