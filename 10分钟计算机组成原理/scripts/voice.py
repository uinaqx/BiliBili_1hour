"""Bailian TTS for every beat, then build src/timeline.json.

Credentials are read only from DASHSCOPE_API_KEY / SFM_WORKSPACE_ID and never written to disk.
"""
import base64, concurrent.futures, hashlib, json, math, os, pathlib, re, subprocess, sys, time
import requests

sys.stdout.reconfigure(encoding='utf-8')
ROOT = pathlib.Path(__file__).resolve().parents[1]
AUDIO = ROOT / 'public' / 'audio'
MODEL = 'qwen-audio-3.1-tts-plus'
VOICE = 'xunanchuan_v3.1'
RATE = 1.05
INSTRUCTION = '你是一位讲解清晰、语气从容的计算机老师，正在为大学生做一段十分钟的计算机组成原理速览。英文缩写、数字与公式清楚准确发音。使用沉稳亲切、自然流畅的普通话男声，语速前后一致。只朗读正文，不朗读提示词。'
FPS = 30
LEAD = {'intro': 3.6}
DEFAULT_LEAD = 2.2
GAP = 0.5
TAIL = 1.2


def redact(message, cred):
    text = str(message)
    for v in cred.values():
        if v:
            text = text.replace(v, '[REDACTED]')
    return text


def duration(path):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                          '-of', 'default=nw=1:nk=1', str(path)], text=True).strip())


def sse_events(response):
    parts = []
    for line in response.iter_lines():
        if not line:
            if parts:
                raw = b'\n'.join(parts); parts = []
                if raw.strip() != b'[DONE]':
                    yield json.loads(raw)
        elif line.startswith(b'data:'):
            parts.append(line[5:].lstrip())
    if parts:
        raw = b'\n'.join(parts)
        if raw.strip() != b'[DONE]':
            yield json.loads(raw)


def synth(key, text, cred):
    fingerprint = hashlib.sha256((text + VOICE + MODEL + str(RATE) + INSTRUCTION).encode()).hexdigest()
    media = AUDIO / f'{key}.mp3'; meta = AUDIO / f'{key}.json'
    if media.exists() and meta.exists():
        cached = json.loads(meta.read_text(encoding='utf-8'))
        if cached.get('fingerprint') == fingerprint and media.stat().st_size > 100:
            return cached['duration'], 'cached'
    if not cred['api_key'] or not cred['workspace_id']:
        raise RuntimeError(f'{key}: no cache; set DASHSCOPE_API_KEY and SFM_WORKSPACE_ID')
    endpoint = f"https://{cred['workspace_id']}.cn-beijing.maas.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer"
    body = {'model': MODEL, 'input': {'text': text, 'voice': VOICE, 'format': 'mp3', 'sample_rate': 24000,
                                      'rate': RATE, 'volume': 50, 'instruction': INSTRUCTION,
                                      'language_hints': ['zh'], 'seed': 2026}}
    for attempt in range(4):
        try:
            chunks = []; last_url = None
            with requests.post(endpoint, json=body, stream=True, timeout=(20, 180), headers={
                    'Authorization': 'Bearer ' + cred['api_key'], 'Content-Type': 'application/json',
                    'X-DashScope-SSE': 'enable'}) as r:
                if r.status_code != 200:
                    try:
                        e = r.json(); msg = f"HTTP {r.status_code}: {e.get('code', '')} {e.get('message', '')}"
                    except Exception:
                        msg = f'HTTP {r.status_code}'
                    raise RuntimeError(msg)
                for ev in sse_events(r):
                    if ev.get('code'):
                        raise RuntimeError(ev.get('message', ev['code']))
                    audio = ev.get('output', {}).get('audio', {})
                    if audio.get('data'):
                        chunks.append(base64.b64decode(audio['data']))
                    if audio.get('url'):
                        last_url = audio['url']
            if not chunks and last_url:
                d = requests.get(last_url, timeout=180); d.raise_for_status(); chunks = [d.content]
            if not chunks:
                raise RuntimeError('TTS returned no audio')
            tmp = AUDIO / f'{key}.partial.mp3'; tmp.write_bytes(b''.join(chunks))
            secs = duration(tmp)
            if secs < 0.8:
                raise RuntimeError('audio too short')
            tmp.replace(media)
            meta.write_text(json.dumps(dict(fingerprint=fingerprint, duration=secs, voice=VOICE, model=MODEL,
                                            rate=RATE, text=text), ensure_ascii=False, indent=2), encoding='utf-8')
            return secs, 'new'
        except Exception as exc:
            if attempt == 3:
                raise RuntimeError(f'{key}: {redact(exc, cred)}') from None
            print(f'{key}: retry {attempt + 1}: {redact(exc, cred)}', flush=True)
            time.sleep(2 + attempt * 3)


def estimate(text):
    """Placeholder length for a beat that has no audio yet (about 4.6 Chinese characters per second)."""
    han = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    words = len(re.findall(r'[A-Za-z0-9]+', text))
    pauses = len(re.findall(r'[，、；：]', text)) * 0.18 + len(re.findall(r'[。！？]', text)) * 0.35
    return han / 4.6 + words * 0.32 + pauses + 0.2


def build_timeline(script, durations, voiced):
    scenes = []; cursor = 0
    for s in script['scenes']:
        t = LEAD.get(s['id'], DEFAULT_LEAD); beats = []
        for i, b in enumerate(s['beats']):
            key = f"{s['id']}_{i:02}"; d = durations[key]
            beats.append({'text': b['text'], 'audio': f'audio/{key}.mp3' if key in voiced else None,
                          'from': round(t * FPS), 'dur': math.ceil(d * FPS)})
            t += d + GAP
        length = math.ceil((t - GAP + TAIL) * FPS)
        scenes.append({'id': s['id'], 'title': s['title'], 'en': s.get('en', ''), 'from': cursor,
                       'duration': length, 'beats': beats})
        cursor += length
    out = {'fps': FPS, 'total': cursor, 'voiced': len(voiced), 'beats': len(durations), 'scenes': scenes}
    (ROOT / 'src' / 'timeline.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    print('TOTAL', cursor, 'frames =', round(cursor / FPS / 60, 2), 'min;', f'voiced {len(voiced)}/{len(durations)}')
    for s in scenes:
        print(f"  {s['id']:<11}{s['duration'] / FPS:6.1f}s")


def main():
    AUDIO.mkdir(parents=True, exist_ok=True)
    cred = dict(api_key=os.environ.get('DASHSCOPE_API_KEY', ''), workspace_id=os.environ.get('SFM_WORKSPACE_ID', ''))
    script = json.loads((ROOT / 'content' / 'script.json').read_text(encoding='utf-8'))
    jobs = [(f"{s['id']}_{i:02}", b.get('say', b['text'])) for s in script['scenes'] for i, b in enumerate(s['beats'])]

    if '--placeholder' in sys.argv:
        durations = {}; voiced = set()
        for key, text in jobs:
            media = AUDIO / f'{key}.mp3'
            if media.exists() and (AUDIO / f'{key}.json').exists():
                durations[key] = duration(media); voiced.add(key)
            else:
                durations[key] = estimate(text)
        build_timeline(script, durations, voiced)
        return

    if '--test' in sys.argv:
        jobs = jobs[:1]

    def work(job):
        secs, how = synth(job[0], job[1], cred)
        print('VOICE', job[0], round(secs, 2), how, flush=True)
        return job[0], secs

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        durations = dict(pool.map(work, jobs))
    if '--test' in sys.argv:
        return
    build_timeline(script, durations, set(durations))


if __name__ == '__main__':
    main()
