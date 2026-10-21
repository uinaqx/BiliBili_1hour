"""Validate a course timeline or resolve hand-authored anchors against final-audio tokens.

Python 3.10+, standard library. No network, TTS, credentials or implicit fuzzy matching.
"""
import argparse,copy,hashlib,json,math,pathlib,sys
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')

def read(path):return json.loads(pathlib.Path(path).read_text(encoding='utf-8-sig'))
def write(path,value):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.tmp');temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(path)
def integer(v):return isinstance(v,int) and not isinstance(v,bool)
def norm(text):return ''.join(c for c in str(text).casefold() if c.isalnum())
def onset_frame(seconds,fps,lead=0):return lead+math.ceil(seconds*fps-1e-6)
def pages(scene):
    result=[dict(id='root',beginFrame=0,code=scene.get('code',''),initialCodeLines=scene.get('initialCodeLines',[]))]
    for p in scene.get('panels',[]):result.append({**p,'id':p.get('id',str(p['beginFrame']))})
    return result
def page_at(scene,frame):
    choices=[p for p in pages(scene) if p['beginFrame']<=frame]
    return max(choices,key=lambda p:p['beginFrame'])

def validate(course):
    errors=[];warnings=[];fps=course.get('fps',30);scenes=course.get('scenes',[])
    if not integer(fps) or fps<=0:return {'allPassed':False,'errors':['fps must be a positive integer'],'warnings':[]}
    seen=set();cursor=0;code_pages=0;cues_count=0
    def bad(where,message):errors.append(f'{where}: {message}')
    for s in scenes:
        key=s.get('key');where=str(key)
        if not key or key in seen:bad(where,'missing or duplicate scene key')
        seen.add(key);start=s.get('startFrame');duration=s.get('durationFrames');lead=s.get('leadFrames',0)
        if not integer(start) or start!=cursor:bad(where,'scene starts must be contiguous from frame zero')
        if not integer(duration) or duration<=0:bad(where,'invalid durationFrames');continue
        cursor=(start if integer(start) else cursor)+duration
        if not integer(lead) or not 0<=lead<duration:bad(where,'invalid leadFrames');lead=0
        panels=s.get('panels',[]);begins=[p.get('beginFrame') for p in panels]
        if any(not integer(f) or not 0<f<duration for f in begins) or begins!=sorted(set(begins)):
            bad(where,'panels must have unique ascending beginFrame inside the scene');continue
        ids=[p['id'] for p in pages(s)]
        if len(ids)!=len(set(ids)):bad(where,'duplicate panel id')
        def check_lines(lines,page,context):
            rows=page.get('code','').splitlines()
            if not isinstance(lines,list) or not lines or any(not integer(n) or not 1<=n<=len(rows) for n in lines):bad(context,'invalid or empty selected line numbers');return
            if not any(rows[n-1].strip() for n in lines):bad(context,'selection contains only blank lines')
        for page in pages(s):
            if page.get('code'):code_pages+=1;check_lines(page.get('initialCodeLines'),page,where+'/'+page['id'])
        last=-1
        for c in s.get('codeCues',[]):
            cues_count+=1;begin=c.get('beginFrame');end=c.get('endFrame')
            if not integer(begin) or not 0<=begin<duration:bad(where,'cue beginFrame outside scene');continue
            if begin<last:bad(where,'code cues not in chronological order')
            last=begin;page=page_at(s,begin)
            page_end=min([p['beginFrame'] for p in pages(s) if p['beginFrame']>begin]+[duration])
            if c.get('panelId',page['id'])!=page['id']:bad(where,'cue assigned to inactive panel')
            check_lines(c.get('lines'),page,where+'@'+str(begin))
            if end is not None and (not integer(end) or not begin<end<=duration):bad(where,'invalid diagnostic endFrame')
            elif end is not None and end>page_end:bad(where,'spoken code anchor crosses a code-panel boundary')
        if s.get('code') and not s.get('codeCues') and not s.get('noSwitchReason'):
            warnings.append(where+': no spoken switching anchors; review semantics or supply noSwitchReason')
        for c in s.get('diagramCues',[]):
            if not integer(c.get('beginFrame')) or not 0<=c['beginFrame']<duration:bad(where,'diagram onset outside scene')
            if not isinstance(c.get('patch'),dict) or not c['patch']:bad(where,'diagram cue needs a nonempty state patch')
            if 'endFrame' in c:bad(where,'persistent diagram emphasis must not expire at phrase ending')
            target=c.get('patch',{}).get('focus');allowed=s.get('diagramObjectIds')
            if target is not None and allowed and target not in allowed:bad(where,'diagram focus is not a declared object')
        last_end=-1.0
        for cap in s.get('captions',[]):
            a=cap.get('start');b=cap.get('end')
            if not isinstance(a,(float,int)) or not isinstance(b,(float,int)) or not math.isfinite(a+b) or not 0<=a<b or b*fps+lead>duration+1e-5:bad(where,'caption time outside scene');continue
            if a<last_end-1e-6:bad(where,'captions overlap or run backwards')
            last_end=b
        if s.get('kind')=='question' and 'speechFrames' in s:
            needed=lead+s['speechFrames']+s.get('sentenceTailFrames',0)+s.get('holdSeconds',4)*fps
            if needed>duration+1e-6:bad(where,'question does not contain the requested thinking hold')
    if not scenes:errors.append('course has no scenes')
    if 'totalFrames' in course and course['totalFrames']!=cursor:errors.append('totalFrames does not match scenes')
    chapters=course.get('chapters',[]);starts=[c.get('startFrame') for c in chapters]
    if chapters and (any(not integer(f) or f<0 or f>=cursor for f in starts) or starts!=sorted(set(starts)) or starts[0]!=0):errors.append('chapter starts must be unique, ordered and start at zero')
    return {'allPassed':not errors,'errors':errors,'warnings':warnings,'sceneCount':len(scenes),'codePages':code_pages,'codeCues':cues_count,'totalFrames':cursor,'semanticCorrectness':'requires page-by-page review'}

def token_context(meta):
    if meta.get('timeBase')!='final-audio' or meta.get('timeUnit')!='seconds':raise ValueError('metadata must explicitly use timeBase=final-audio and timeUnit=seconds')
    chars=[];last=-1.0
    for word in meta.get('words',[]):
        text=norm(word['text']);a=float(word['start']);b=float(word['end'])
        if not math.isfinite(a+b) or a<last-1e-6 or not 0<=a<b:raise ValueError('invalid or unordered word timings')
        last=a
        for i,ch in enumerate(text):chars.append((ch,a,b,i==0))
    if not chars:raise ValueError('no timed spoken tokens')
    return ''.join(c[0] for c in chars),chars

def phrase_time(meta,cue):
    spoken,chars=token_context(meta)
    if cue.get('method')=='manual-audio-review':
        if not cue.get('reason'):raise ValueError('manual onset needs a review reason')
        a=float(cue['startSeconds']);b=float(cue['endSeconds'])
        if not 0<=a<b<=chars[-1][2]+1e-6:raise ValueError('manual time outside final speech')
        return a,b
    phrase=norm(cue.get('phrase',''))
    if not phrase:raise ValueError('empty spoken anchor')
    hits=[];pos=spoken.find(phrase)
    while pos>=0:hits.append(pos);pos=spoken.find(phrase,pos+1)
    if not hits:raise ValueError('spoken anchor not found')
    occurrence=cue.get('occurrence')
    if len(hits)>1 and occurrence is None:raise ValueError('ambiguous repeated phrase; supply 1-based occurrence')
    occurrence=occurrence if occurrence is not None else 1
    if not integer(occurrence) or not 1<=occurrence<=len(hits):raise ValueError('invalid occurrence')
    pos=hits[occurrence-1]
    if not chars[pos][3]:raise ValueError('anchor starts inside a timed token; quote a larger phrase or review audio manually')
    return chars[pos][1],chars[pos+len(phrase)-1][2]

def within(root,name):
    path=(root/name).resolve()
    if not path.is_relative_to(root):raise ValueError('metadata/audio path escapes project root')
    return path

def resolve(course,plan,root):
    out=copy.deepcopy(course);errors=[];alignment=[];root=pathlib.Path(root).resolve();entries=plan.get('scenes',{});known={s['key'] for s in out['scenes']}
    errors.extend(f'{k}: unknown scene in anchor plan' for k in entries if k not in known)
    for s in out['scenes']:
        key=s['key'];entry=entries.get(key)
        if entry is None:
            if s.get('code') or s.get('panels') or s.get('diagramObjectIds'):errors.append(f'{key}: missing authored anchor plan')
            continue
        try:
            meta=read(within(root,entry['audioMeta']));token_context(meta)
            if meta.get('audioSha256'):
                if not s.get('audio'):raise ValueError('hash provided but no scene audio path to verify')
                audio_hash=hashlib.sha256(within(root,s['audio']).read_bytes()).hexdigest()
                if audio_hash!=meta['audioSha256']:raise ValueError('final audio hash differs from timing metadata')
            else:audio_hash=None
            alignment.append({'scene':key,'audioSha256':audio_hash,'audioIdentityVerified':audio_hash is not None})
            if 'initialCodeLines' in entry:s['initialCodeLines']=entry['initialCodeLines']
            for p in s.get('panels',[]):
                pid=p.get('id',str(p['beginFrame']))
                if pid in entry.get('panelInitialCodeLines',{}):p['initialCodeLines']=entry['panelInitialCodeLines'][pid]
            cues=[];diagram_cues=[];last=-1.0
            for i,c in enumerate(entry.get('cues',[])):
                a,b=phrase_time(meta,c)
                if a<last-1e-6:raise ValueError(f'cue {i} is out of narration order')
                last=a;cue={'cue':c.get('phrase','manual review'),'beginFrame':onset_frame(a,out.get('fps',30),s.get('leadFrames',0)),
                    'startSeconds':a,'endSeconds':b}
                if 'patch' in c:
                    cue['patch']=c['patch']
                    if 'groupId' in c:cue['groupId']=c['groupId']
                    diagram_cues.append(cue)
                else:
                    cue.update(endFrame=onset_frame(b,out.get('fps',30),s.get('leadFrames',0)),lines=c['lines'])
                    if 'panelId' in c:cue['panelId']=c['panelId']
                    cues.append(cue)
            s['codeCues']=cues
            if diagram_cues:s['diagramCues']=diagram_cues
            if 'noSwitchReason' in entry:s['noSwitchReason']=entry['noSwitchReason']
        except (KeyError,ValueError,OSError) as exc:errors.append(f'{key}: {exc}')
    report=validate(out);report['errors']=errors+report['errors'];report['allPassed']=not report['errors'];report['alignment']=alignment
    return out,report

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('validate');p.add_argument('course');p.add_argument('--output')
    p=sub.add_parser('resolve');p.add_argument('course');p.add_argument('anchors');p.add_argument('--root',required=True);p.add_argument('--output',required=True)
    args=parser.parse_args();course=read(args.course)
    if args.mode=='validate':report=validate(course)
    else:
        output,report=resolve(course,read(args.anchors),args.root)
        if report['allPassed']:write(args.output,output)
    if args.mode=='validate' and args.output:write(args.output,report)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0 if report['allPassed'] else 1
if __name__=='__main__':sys.exit(main())
