"""Subtitle timing contract: whole tokens on FINAL audio, seconds, half-open cues.

No proportional text allocation, token-time interpolation, or speech-end clipping.
This file is standalone so a course can vendor it when packaging its project.
"""
import bisect
import hashlib
import json
import math
import pathlib
import re
import wave

VERSION = 'final-pcm-course-contract-v2'


def load(path):
    return json.loads(pathlib.Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    h = hashlib.sha256()
    with pathlib.Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def compact(text):
    return ''.join(c.lower() for c in text if c.isalnum())


def check_transcript(project, words, authored, provider=None):
    spoken = ''.join(w['text'] for w in words)
    normalized = compact(spoken)
    target = compact(authored)
    alias_path = project / 'content/subtitle-aliases.json'
    if alias_path.exists():
        for alias in load(alias_path):
            normalized = normalized.replace(compact(alias['spoken']), compact(alias['written']))
            target = target.replace(compact(alias['spoken']), compact(alias['written']))
    if normalized != target:
        # A provider can spell 128 as 一百二十八. Preserve that exact returned
        # sequence, backed by the original request AND token sequence, rather
        # than apportioning the manuscript over it by character length.
        if not (provider and compact(provider['narration']) == compact(authored)
                and compact(''.join(w['text'] for w in provider['words'])) == compact(spoken)):
            raise ValueError('Transcript mismatch; add an explicit reviewed spelling alias or realign')
    # Keep the actual spoken form. Do not redistribute display text across cues.
    return spoken


def normalized_words(words, unit='milliseconds'):
    factor = {'milliseconds': .001, 'seconds': 1}[unit]
    result = []
    for i, w in enumerate(words):
        a = float(w.get('begin_time', w.get('start', -1))) * factor
        b = float(w.get('end_time', w.get('end', -1))) * factor
        if not math.isfinite(a + b) or a < 0 or b < 0:
            raise ValueError(f'Invalid word interval at token {i}')
        result.append(dict(text=w['text'], start=a, end=b, token=i))
    return result


def mapped_words(words, cuts, pause, sample_rate):
    """Map pre-pause words through the exact number of inserted PCM samples."""
    samples = [round(c * sample_rate) for c in cuts]
    delays = [round(x * sample_rate) for x in pause]
    if len(samples) != len(delays) or samples != sorted(set(samples)) or any(x < 0 for x in samples+delays):
        raise ValueError('Invalid pause manifest')
    prefix = [0]
    for delay in delays:
        prefix.append(prefix[-1]+delay)
    mapped = []
    for w in words:
        start = w['start'] + prefix[bisect.bisect_right(samples, round(w['start']*sample_rate))]/sample_rate
        end = w['end'] + prefix[bisect.bisect_left(samples, round(w['end']*sample_rate))]/sample_rate
        mapped.append(dict(w, start=start, end=end if w['end']>w['start'] else start))
    return mapped


def protected_ends(authored, terms):
    """Return character positions inside written terms, identifiers and paths."""
    protected=set()
    for term in terms:
        for match in re.finditer(re.escape(term),authored):
            protected.update(range(match.start()+1,match.end()))
    for match in re.finditer(r'[零一二三四五六七八九十百千万两〇]+',authored):
        protected.update(range(match.start()+1,match.end()))
    for match in re.finditer(r'[A-Za-z0-9_]+(?:[./\\@:+%~-][A-Za-z0-9_]+)*',authored):
        protected.update(range(match.start()+1,match.end()))
    return protected


def authored_words(words, authored, aliases, terms=()):
    """Project exact authored spans onto indivisible timing tokens."""
    source = ''.join(w['text'] for w in words)
    src = compact(source)
    positions = [i for i,c in enumerate(authored) if c.isalnum()]
    target = compact(authored)
    cuts = [0]*(len(src)+1)
    i=j=0
    rules = [(compact(a['spoken']),compact(a['written'])) for a in aliases]
    if any(not a or not b for a,b in rules):
        raise ValueError('Empty pronunciation alias')
    rules.sort(key=lambda x:-len(x[0]))
    protected = []
    while i<len(src) and j<len(target):
        match = next(((a,b) for a,b in rules if src.startswith(a,i) and target.startswith(b,j)), None)
        if match:
            a,b=match
            protected.append((i,i+len(a)))
            for k in range(i+1,i+len(a)):
                cuts[k]=j
            i+=len(a)
            j+=len(b)
        elif src[i]==target[j]:
            i+=1
            j+=1
        else:
            break
        cuts[i]=j
    if i!=len(src) or j!=len(target):
        raise ValueError(f'Authored cue and aligned words disagree near {authored[positions[j] if j<len(positions) else len(authored):][:24]!r}')
    # Each author token owns its closing punctuation. Whitespace remains in the
    # original text so code names and punctuation are emitted verbatim.
    def boundary(number):
        if number==0:
            return 0
        if number==len(positions):
            return len(authored)
        # Code punctuation (e.g. slash or dot) binds to the adjacent token.
        return positions[number]

    written_protected=protected_ends(authored,terms)
    result=[]
    group=[]
    offset=0
    begin=0
    protected_i=0
    for w in words:
        offset+=len(compact(w['text']))
        if not compact(w['text']):
            continue
        group.append(w)
        while protected_i<len(protected) and offset>=protected[protected_i][1]:
            protected_i+=1
        if protected_i<len(protected) and protected[protected_i][0]<offset<protected[protected_i][1]:
            continue
        if boundary(cuts[offset]) in written_protected:
            continue
        valid=[x for x in group if x['end']>x['start']]
        result.append(dict(text=authored[boundary(cuts[begin]):boundary(cuts[offset])],
                           start=valid[0]['start'] if valid else group[0]['start'],
                           end=max(w['end'] for w in valid) if valid else group[0]['start'],
                           token=group[0]['token']))
        begin=offset
        group=[]
    if group or ''.join(w['text'] for w in result)!=authored:
        raise ValueError('Authored cue coverage is incomplete')
    return result


def merge_untimed(words):
    result=[]
    head=''
    for w in words:
        if w['end']<=w['start']:
            if result:
                result[-1]['text']+=w['text']
            else:
                head+=w['text']
        else:
            result.append(dict(w,text=head+w['text']))
            head=''
    if not result:
        raise ValueError('No words with positive timing')
    return result


def captions_from_words(words, *, duration, max_chars=36, tail=.12, hold=False):
    """Use actual token envelopes; punctuation alone owns no speech interval.

    Overlapping adjacent cues are merged, never shortened or shifted into the
    following spoken phrase. Length limits are soft at indivisible tokens.
    """
    if not 0<=tail<=.12:
        raise ValueError('Subtitle tail must be within 0–0.12 seconds')
    atoms = []
    for w in merge_untimed(words):
        text = w['text']
        prefix = re.match(r'^[\s，。！？；：、,.!?;:]+', text)
        if prefix and atoms:
            atoms[-1]['text'] += prefix[0]
            text = text[len(prefix[0]):]
        if not compact(text):
            if atoms:
                atoms[-1]['text'] += text
            continue
        if w['end'] > duration + .002:
            raise ValueError('Word timestamp exceeds final audio duration')
        atoms.append(dict(w, text=text))
    if not atoms:
        raise ValueError('No spoken tokens')
    groups, group = [], []

    def flush():
        if group:
            groups.append(dict(text=''.join(x['text'] for x in group).strip(),
                               start=min(x['start'] for x in group),
                               spokenEnd=max(x['end'] for x in group),
                               tokens=[x['token'] for x in group]))
            group.clear()

    def width(text):
        return sum(.6 if c.isascii() else 1 for c in text)

    for atom in atoms:
        if group:
            txt = ''.join(x['text'] for x in group)
            gap = atom['start'] - max(x['end'] for x in group)
            # Never split a contiguous English identifier or number.
            identifier = re.search(r'[A-Za-z0-9_./+\-\\@%]$', txt) and re.match(r'^[A-Za-z0-9_./+\-\\@%]', atom['text'])
            if not identifier and (re.search(r'[。！？!?；;][”"\s]*$', txt)
                    or (re.search(r'[，,：:][”"\s]*$', txt) and len(txt) >= 12)
                    or width(txt + atom['text']) > max_chars or gap >= .5):
                flush()
        group.append(atom)
    flush()
    merged = []
    for c in groups:
        # Zero-time fragments and overlapping token envelopes have no safe split.
        while merged and (c['start'] < merged[-1]['spokenEnd'] - 1e-9
                          or merged[-1]['spokenEnd'] <= merged[-1]['start']
                          or c['spokenEnd'] <= c['start']):
            p = merged.pop()
            c = dict(text=p['text'] + c['text'], start=min(p['start'], c['start']),
                     spokenEnd=max(p['spokenEnd'], c['spokenEnd']), tokens=p['tokens'] + c['tokens'])
        merged.append(c)
    for i, c in enumerate(merged):
        if c['spokenEnd'] <= c['start']:
            raise ValueError('Zero-duration spoken phrase needs realignment')
        next_start = merged[i+1]['start'] if i+1 < len(merged) else duration
        clearance = next_start if hold and i+1<len(merged) else c['spokenEnd']+tail
        c['end'] = max(c['spokenEnd'], min(clearance, next_start, duration))
    validate(merged, duration)
    return merged


def validate(cues, duration):
    previous = 0.0
    for i, c in enumerate(cues):
        a, b = c['start'], c['end']
        if not math.isfinite(a+b) or a < previous - 1e-8 or b <= a or b > duration + .002:
            raise ValueError(f'Invalid/overlapping subtitle interval {i}: {a}, {b}')
        if b < c.get('spokenEnd', b) - 1e-8 or not c['text'].strip():
            raise ValueError(f'Subtitle {i} cuts off its spoken words')
        previous = b


def pcm_file(path):
    with wave.open(str(path),'rb') as f:
        return f.readframes(f.getnframes()), (f.getframerate(),f.getnchannels(),f.getsampwidth())


def pause_schedule(metadata,part,index,defaults):
    refinements=[x for x in metadata.get('pauseRefinements',[]) if x.get('part',0)==index]
    by_cut={}
    for item in refinements:
        where=item.get('rawSeconds',item.get('acousticSeconds'))
        if where is None or where in by_cut:
            raise ValueError('Invalid or duplicate pause refinement')
        by_cut[where]=item
    cuts=part.get('cutsSeconds', sorted(by_cut))
    if by_cut and sorted(by_cut)!=cuts:
        raise ValueError('Cut positions and pause refinements disagree')
    amount=next((source[key] for source in (part,metadata,*defaults)
                 for key in ('sentencePauseSeconds','fullStopExtraSeconds')
                 if key in source),None)
    pauses=[by_cut.get(c,{}).get('addedSeconds',amount) for c in cuts]
    if any(p is None or not math.isfinite(p) or p<0 for p in pauses):
        raise ValueError('Missing or invalid declared pause length')
    return cuts,pauses


def scene_words(project,scene,defaults=(), *, require_hashes=False, revisions=None):
    audio=project/'public'/scene['audio']
    metadata=audio.with_suffix('.json')
    m=load(metadata)
    pcm,fmt=pcm_file(audio)
    rate,channels,width=fmt
    stride=channels*width
    digest=sha(audio)
    if require_hashes and not (m.get('sha256') and scene.get('audioSha256')):
        raise ValueError(f'{scene["key"]}: missing final PCM binding')
    if any(expected and digest!=expected for expected in (m.get('sha256'),scene.get('audioSha256'))):
        raise ValueError(f'{scene["key"]}: stale final PCM')
    if m.get('samples')!=len(pcm)//stride:
        raise ValueError('Final audio sample count changed')
    if m.get('timeBase')!='final-audio':
        raise ValueError('Unsupported timebase: migrate and verify this version first')
    files=[audio,metadata]
    duration=len(pcm)/stride/rate
    if 'parts' not in m:
        if 'insertedPauseSamples' in m:
            raise ValueError('Legacy sample-cut metadata needs a version-specific adapter')
        return [(normalized_words(m['words']),0.,duration,m['narration'])], files
    if len(scene.get('parts',m['parts']))!=len(m['parts']):
        raise ValueError('Narration part count changed')
    parts=[]
    prev=0
    for i,part in enumerate(m['parts']):
        key=part.get('rawKey',scene['key']+f'-p{i:02}')
        aligned_path=project/'build/alignment'/f'{key}.json'
        aligned=load(aligned_path)
        files.append(aligned_path)
        if require_hashes and not part.get('alignmentSha256'):
            raise ValueError(f'{key}: no hash binding to alignment')
        if part.get('alignmentSha256') and part['alignmentSha256']!=sha(aligned_path):
            raise ValueError(f'{key}: alignment changed; rebuild final metadata')
        authored=scene['parts'][i]['text'] if 'parts' in scene else part['cue']
        if authored!=part['cue'] or (aligned.get('narration') is not None and authored!=aligned['narration']):
            raise ValueError(f'{key}: formal narration changed')
        scaled=project/'public/audio'/f'{key}.scaled.wav'
        raw,rawfmt=pcm_file(scaled)
        files.append(scaled)
        if rawfmt!=fmt or abs(len(raw)/stride/rate-aligned['duration'])>.003:
            raise ValueError(f'{key}: alignment PCM duration or format mismatch')
        cuts,pauses=pause_schedule(m,part,i,defaults)
        positions=[round(c*rate) for c in cuts]
        if any(not 0<=pos<=len(raw)//stride for pos in positions):
            raise ValueError(f'{key}: out-of-bounds cut')
        entry=(revisions or {}).get(key)
        aligned_words=normalized_words(aligned['words'])
        if entry:
            bindings=dict(alignmentSha256=sha(aligned_path),audioSha256=digest,
                          metadataSha256=sha(metadata),prePausePcmSha256=sha(scaled))
            if any(entry.get(name)!=value for name,value in bindings.items()):
                raise ValueError(f'{key}: stale acoustic revisions')
            for token,patch in entry['words'].items():
                aligned_words[int(token)].update(patch)
        words=mapped_words(aligned_words,cuts,pauses,rate)
        segments=[]
        cursor=0
        for pos,pause in zip(positions,pauses):
            segments.extend([raw[cursor*stride:pos*stride],bytes(round(pause*rate)*stride)])
            cursor=pos
        segments.append(raw[cursor*stride:])
        start,end=round(part['start']*rate),round(part['end']*rate)
        if not prev<=start<end<=len(pcm)//stride or b''.join(segments)!=pcm[start*stride:end*stride]:
            raise ValueError(f'{key}: pause assembly does not reconstruct final PCM')
        prev=end
        parts.append((words,start/rate,(end-start)/rate,authored))
    return parts,files


def timing_metrics(cues):
    values=[c['end']-c['spokenEnd'] for c in cues]
    return dict(count=len(values), minEndMinusSpokenEndSeconds=min(values),
                earlyCount=sum(x< -1e-8 for x in values),
                earlyOver100msCount=sum(x<-.1-1e-8 for x in values))


def build_project(project, *, font_size=38, max_chars=30, tail=.12, hold=False, use_revisions=True):
    project=pathlib.Path(project).resolve()
    path=project/'public/timeline.json'
    timeline=load(path)
    fps=timeline['fps']
    if not isinstance(fps,(int,float)) or not math.isfinite(fps) or fps<=0:
        raise ValueError('Invalid FPS in project timeline')
    files=[path,pathlib.Path(__file__).resolve()]
    defaults=[timeline]
    audio_report=project/'build/audio-preparation.json'
    if audio_report.exists():
        defaults.append(load(audio_report))
        files.append(audio_report)
    alias_path=project/'content/subtitle-aliases.json'
    aliases=load(alias_path) if alias_path.exists() else []
    if aliases:
        files.append(alias_path)
    terms_path=project/'content/subtitle-terms.json'
    terms=load(terms_path) if terms_path.exists() else []
    if terms:
        files.append(terms_path)
    revision_path=project/'build/subtitle-word-revisions.json'
    revisions=load(revision_path) if use_revisions and revision_path.exists() else {}
    if revisions:
        files.append(revision_path)
    cues=[]
    placements=[]
    for scene in timeline['scenes']:
        if not 0<=scene['leadFrames']<scene['durationFrames'] or scene['startFrame']<0:
            raise ValueError('Invalid scene coordinates')
        parts,paths=scene_words(project,scene,defaults,require_hashes=True,revisions=revisions)
        files.extend(paths)
        base=(scene['startFrame']+scene['leadFrames'])/fps
        placements.append(dict(audio=str((project/'public'/scene['audio']).resolve()),start=base,
              limit=(scene['startFrame']+scene['durationFrames'])/fps,key=scene['key']))
        for i,(words,offset,duration,authored) in enumerate(parts):
            located=authored_words(words,authored,aliases,terms)
            caps=captions_from_words(located,duration=duration,max_chars=max_chars,tail=tail,hold=hold)
            if compact(''.join(c['text'] for c in caps))!=compact(authored):
                raise ValueError(f'{scene["key"]}: subtitle coverage differs from formal narration')
            for c in caps:
                cues.append(dict(c,start=base+offset+c['start'],end=base+offset+c['end'],
                    spokenEnd=base+offset+c['spokenEnd'],scene=scene['key'],part=i))
    validate(cues,timeline['duration'])
    return dict(version=VERSION,timeBase='final-pcm-to-course',timeUnit='seconds',fps=fps,
                duration=timeline['duration'],project=str(project),fontSize=font_size,
                formula='(scene.startFrame + scene.leadFrames) / fps + part.start + mappedWordTime',
                tailSeconds=tail,endPolicy='hold-within-part' if hold else 'spoken-tail',
                inputs=[dict(path=str(p),sha256=sha(p)) for p in dict.fromkeys(files)],
                placements=placements,cues=cues,timing=timing_metrics(cues),
                chapters=[{k:c[k] for k in ('title','startFrame','durationFrames')} for c in timeline['chapters']])


def quantize(cues, tick):
    result = []
    for c in cues:
        # Same rightward rounding for starts/ends: no early endings or overlap.
        a = math.ceil(c['start']/tick - 1e-8)
        b = math.ceil(c['end']/tick - 1e-8)
        if b <= a:
            raise ValueError('Cue too short for output time grid; merge or realign')
        result.append(dict(c, startTick=a, endTick=b))
    return result


def timestamp(ticks, ass=False):
    scale = 100 if ass else 1000
    h, v = divmod(ticks, 3600*scale)
    m, v = divmod(v, 60*scale)
    s, sub = divmod(v, scale)
    return f'{h}:{m:02}:{s:02}.{sub:02}' if ass else f'{h:02}:{m:02}:{s:02},{sub:03}'


def write_tracks(plan, folder):
    folder = pathlib.Path(folder); folder.mkdir(parents=True, exist_ok=True)
    srt = []
    for i,c in enumerate(quantize(plan['cues'], .001), 1):
        srt.extend([str(i), f"{timestamp(c['startTick'])} --> {timestamp(c['endTick'])}", c['text'], ''])
    (folder/'subtitles.srt').write_text('\n'.join(srt)+'\n', encoding='utf-8-sig')
    header = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Microsoft YaHei,38,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,0,0,0,0,100,100,0,0,1,2,0,2,120,120,35,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    events = []
    for c in quantize(plan['cues'], .01):
        text = ass_text(c['text'])
        events.append(f"Dialogue: 0,{timestamp(c['startTick'],True)},{timestamp(c['endTick'],True)},Default,,0,0,0,,{text}")
    header=header.replace('Microsoft YaHei,38,',f"Microsoft YaHei,{plan.get('fontSize',38)},")
    (folder/'subtitles.ass').write_text(header+'\n'.join(events)+'\n', encoding='utf-8-sig')
    (folder/'subtitle-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8')



def ass_text(text):
    # WORD JOINER interrupts ASS control sequences without visible substitution.
    return (text.replace('\\','\\\u2060').replace('{','\\{').replace('}','\\}')
                .replace('\n','\\N'))
