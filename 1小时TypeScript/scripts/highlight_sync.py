"""Authored sentence/line relations resolved against final acoustic token times."""
import bisect,hashlib,json,math
def normal(t):return ''.join(c.casefold() for c in t if c.isalnum())
def apply_highlights(root,timeline):
 audit=[]
 for s in timeline['scenes']:
  audio=root/'public'/s['audio'];m=json.loads(audio.with_suffix('.json').read_text(encoding='utf8'))
  assert hashlib.sha256(audio.read_bytes()).hexdigest()==s['audioSha256']==m['sha256']
  events=[dict(beginFrame=0,lines=[] if s['kind']=='cover' else s['parts'][0]['cues'][0]['lines'],anchor='page initial selection',part=0)]
  for pi,(part,a) in enumerate(zip(s['parts'],m['parts'])):
   if s['kind']=='cover' and pi==0:continue
   if pi:events.append(dict(beginFrame=s['partFrames'][pi],lines=part['cues'][0]['lines'],anchor='new panel initial selection',part=pi))
   chars=[];times=[]
   for w in a['words']:
    for c in normal(w['text']):chars.append(c);times.append(w['begin_time']/1000)
   text=''.join(chars)
   n=len((s.get('answerCode') if pi and s.get('answerCode') else s['code']).splitlines())
   for cue in part['cues']:
    needle=normal(cue['anchor']);assert normal(part['text']).count(needle)==1,(s['key'],needle,'author anchor')
    at=text.find(needle);assert at>=0 and text.find(needle,at+1)<0,(s['key'],needle,'audio anchor')
    seconds=a['start']+times[at];frame=max(s['partFrames'][pi],s['leadFrames']+math.ceil(seconds*30-1e-6))
    assert frame>=events[-1]['beginFrame'],(s['key'],pi,frame,events[-1])
    assert all(1<=line<=n for line in cue['lines'])
    if frame==events[-1]['beginFrame']:events[-1]=dict(beginFrame=frame,lines=cue['lines'],anchor=needle,part=pi,finalAudioSeconds=seconds)
    else:events.append(dict(beginFrame=frame,lines=cue['lines'],anchor=needle,part=pi,finalAudioSeconds=seconds))
  s['codeCues']=events;s['renderFrames']=sorted(set(s['renderFrames'])|{e['beginFrame'] for e in events})
  audit.append(dict(scene=s['key'],audioSha256=m['sha256'],events=events,distinctSelections=len({tuple(e['lines']) for e in events})))
 lookup={s['key']:s for s in timeline['scenes']}
 for c in timeline['chapters']:c['scenes']=[lookup[s['key']] for s in c['scenes']]
 (root/'build/highlight-resolution.json').write_text(json.dumps(dict(allPassed=True,pages=len(audit),authoredEvents=sum(len(a['events']) for a in audit),scenes=audit),ensure_ascii=False,indent=2),encoding='utf8')
 return timeline
def selected_lines(s,f):
 if s['kind']=='cover' and f<s['partFrames'][1]:return []
 events=s['codeCues'];assert events[0]['beginFrame']==0
 return events[bisect.bisect_right([e['beginFrame'] for e in events],f)-1]['lines']
