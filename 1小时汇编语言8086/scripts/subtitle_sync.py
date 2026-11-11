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

VERSION = 'final-audio-whole-token-v1'


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
        if not math.isfinite(a + b) or a < 0 or b < a:
            raise ValueError(f'Invalid word interval at token {i}')
        result.append(dict(text=w['text'], start=a, end=b, token=i))
    return result


def mapped_words(words, cuts, pause=.1):
    """Cuts are in the input audio. Start is right-continuous; end is left-continuous."""
    if cuts != sorted(set(cuts)) or any(c < 0 for c in cuts):
        raise ValueError('Pause cuts must be unique ordered seconds')
    # PCM assembly cuts at integer samples. Float comparison can add a spurious
    # 100 ms when 3800 ms becomes 3.8000000000000003 seconds.
    samples = [round(c*24000) for c in cuts]
    return [dict(w, start=w['start'] + pause * bisect.bisect_right(samples, round(w['start']*24000)),
                 end=w['end'] + pause * bisect.bisect_left(samples, round(w['end']*24000))) for w in words]


def captions_from_words(words, *, duration, max_chars=36, tail=.12):
    """Use actual token envelopes; punctuation alone owns no speech interval.

    Overlapping adjacent cues are merged, never shortened or shifted into the
    following spoken phrase. Length limits are soft at indivisible tokens.
    """
    atoms = []
    for w in words:
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

    for atom in atoms:
        if group:
            txt = ''.join(x['text'] for x in group)
            gap = atom['start'] - max(x['end'] for x in group)
            # Never split a contiguous English identifier or number.
            identifier = re.search(r'[A-Za-z0-9_./+\-]$', txt) and re.match(r'^[A-Za-z0-9_./+\-]', atom['text'])
            if not identifier and (re.search(r'[。！？!?；;][”"\s]*$', txt)
                    or (re.search(r'[，,：:][”"\s]*$', txt) and len(txt) >= 12)
                    or len(txt + atom['text']) > max_chars or gap >= .5):
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
        c['end'] = max(c['spokenEnd'], min(c['spokenEnd'] + tail, next_start, duration))
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


def read_pcm(path):
    with wave.open(str(path), 'rb') as f:
        if (f.getnchannels(), f.getsampwidth(), f.getframerate()) != (1, 2, 24000):
            raise ValueError('Expected final mono PCM16 24000 Hz')
        return f.readframes(f.getnframes())


def scene_words(project, scene):
    """Read supported measured-audio schemas; verify pause reconstruction byte for byte."""
    audio = project / 'public' / scene['audio']
    metadata = audio.with_suffix('.json')
    if not metadata.exists():
        raise ValueError(f'{scene["key"]}: missing timing metadata for CURRENT audio {audio.name}; do not reuse old filename metadata')
    m = load(metadata)
    pcm = read_pcm(audio)
    digest = sha(audio)
    for expected in (m.get('sha256'), scene.get('audioSha256')):
        if expected and expected != digest:
            raise ValueError(f'{scene["key"]}: stale audio/timing hash')
    if m['samples'] != len(pcm)//2:
        raise ValueError('Final audio sample count changed')
    records = [dict(path=str(audio), sha256=digest), dict(path=str(metadata), sha256=sha(metadata))]
    alias_path = project / 'content/subtitle-aliases.json'
    if alias_path.exists():
        records.append(dict(path=str(alias_path), sha256=sha(alias_path)))
    duration = len(pcm)/48000
    if 'words' in m:
        # Legacy acoustic.clip schema: words were already mapped through pauses.
        if 'insertedPauseSamples' not in m and m.get('timeBase') != 'final-audio':
            raise ValueError('Missing final-audio timebase')
        if 'insertedPauseSamples' in m:
            scaled = audio.with_name(scene['key'] + '.scaled.wav')
            raw = read_pcm(scaled)
            positions = m['insertedPauseSamples']
            if positions != sorted(set(positions)):
                raise ValueError('Invalid legacy pause positions')
            chunks, cursor = [], 0
            for pos in positions:
                chunks.extend([raw[cursor*2:pos*2], bytes(2400*2)])
                cursor = pos
            chunks.append(raw[cursor*2:])
            if b''.join(chunks) != pcm:
                raise ValueError('Legacy timing no longer reconstructs final audio')
            records.append(dict(path=str(scaled), sha256=sha(scaled)))
        words = normalized_words(m['words'])
        provider_path = project / 'public/audio_original' / (scene['key']+'.json')
        provider = load(provider_path) if provider_path.exists() else None
        if provider:
            records.append(dict(path=str(provider_path),sha256=sha(provider_path)))
        spoken = check_transcript(project, words, m['narration'], provider)
        return [(words, 0., duration, spoken)], records
    if m.get('timeBase') != 'final-audio':
        raise ValueError('Unsupported or unspecified timebase')
    parts = []
    for i, p in enumerate(m['parts']):
        key = p.get('rawKey', scene['key'] + f'-p{i:02}')
        aligned_path = project / 'build/alignment' / (key + '.json')
        aligned = load(aligned_path)
        records.append(dict(path=str(aligned_path), sha256=sha(aligned_path)))
        if p.get('alignmentSha256') and p['alignmentSha256'] != sha(aligned_path):
            raise ValueError('Alignment changed since audio assembly')
        scaled = project / 'public/audio' / (key + '.scaled.wav')
        raw = read_pcm(scaled)
        if abs(len(raw)/48000 - aligned['duration']) > .003:
            raise ValueError('Alignment duration does not match aligned PCM')
        if 'cutsSeconds' in p:
            cuts = p['cutsSeconds']
        else:
            cuts = [x['acousticSeconds'] for x in m['pauseRefinements'] if x['part'] == i]
        positions = [round(x*24000) for x in cuts]
        segments, cursor = [], 0
        for pos in positions:
            segments.extend([raw[cursor*2:pos*2], bytes(2400*2)])
            cursor = pos
        segments.append(raw[cursor*2:])
        reconstructed = b''.join(segments)
        start, end = round(p['start']*24000), round(p['end']*24000)
        if reconstructed != pcm[start*2:end*2]:
            raise ValueError(f'{key}: pause/tempo mapping does not reproduce FINAL audio')
        words = mapped_words(normalized_words(aligned['words']), cuts)
        provider_path = project / 'public/audio_original' / (key+'.json')
        provider = load(provider_path)
        records.append(dict(path=str(provider_path),sha256=sha(provider_path)))
        spoken = check_transcript(project, words, p['cue'], provider)
        if 'words' in p:
            saved = normalized_words(p['words'])
            if len(saved) != len(words) or any(abs(a['start']-b['start']) > .001 or abs(a['end']-b['end']) > .001 for a,b in zip(saved, words)):
                raise ValueError('Stored words and exact pause mapping disagree')
        parts.append((words, p['start'], p['end']-p['start'], spoken))
    return parts, records


def build_project(project):
    project = pathlib.Path(project).resolve()
    path = project / 'public/timeline.json'
    timeline = load(path)
    fps = timeline['fps']
    engine = pathlib.Path(__file__).resolve()
    cues, inputs = [], [dict(path=str(path), sha256=sha(path)), dict(path=str(engine),sha256=sha(engine))]
    for scene in timeline['scenes']:
        parts, records = scene_words(project, scene)
        inputs.extend(records)
        base = (scene['startFrame'] + scene['leadFrames']) / fps
        for i, (words, offset, duration, transcript) in enumerate(parts):
            caps = captions_from_words(words, duration=duration)
            if compact(''.join(c['text'] for c in caps)) != compact(transcript):
                raise ValueError('Subtitle coverage differs from spoken transcript')
            for c in caps:
                cues.append(dict(c, start=base+offset+c['start'], end=base+offset+c['end'],
                                 spokenEnd=base+offset+c['spokenEnd'], scene=scene['key'], part=i))
    validate(cues, timeline['duration'])
    return dict(version=VERSION, timeBase='video', timeUnit='seconds', fps=fps,
                duration=timeline['duration'], project=str(project), inputs=inputs,
                cues=cues, chapters=[{k:c[k] for k in ('title','startFrame','durationFrames')} for c in timeline['chapters']],
                accuracy='Exact transforms of cached alignment; acoustic word boundaries still require listening review')


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
        text = c['text'].replace('\\','＼').replace('{','｛').replace('}','｝').replace('\n','\\N')
        events.append(f"Dialogue: 0,{timestamp(c['startTick'],True)},{timestamp(c['endTick'],True)},Default,,0,0,0,,{text}")
    (folder/'subtitles.ass').write_text(header+'\n'.join(events)+'\n', encoding='utf-8-sig')
    (folder/'subtitle-plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf8')
