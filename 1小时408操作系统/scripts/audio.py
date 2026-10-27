"""Bailian TTS. Credentials stay in process memory; no credentials in cache."""
import argparse, base64, concurrent.futures, hashlib, json, os, pathlib, subprocess, sys, time
import requests
sys.stdout.reconfigure(encoding='utf-8')

ROOT = pathlib.Path(__file__).resolve().parents[1]
AUDIO = ROOT / 'public' / 'audio'
MODEL = 'qwen-audio-3.1-tts-plus'
VOICE = 'xunanchuan_v3.1'
INSTRUCTION = '你是一位耐心、擅长循序渐进讲解的大学老师。用清晰沉稳的普通话男声讲课，语气亲切平实，语速自然适中。具体例子讲得清楚，句间自然停顿，关键差异稍作强调，英文代码名称自然准确发音。不要播音式夸张，不要机械逐字朗读。'

def duration(path):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)],text=True).strip())

def sse_events(response):
    # SSE data can contain pretty-printed JSON across multiple data: lines.
    parts=[]
    for line in response.iter_lines():
        if not line:
            if parts:
                raw=b'\n'.join(parts); parts=[]
                if raw.strip()!=b'[DONE]': yield json.loads(raw)
        elif line.startswith(b'data:'):
            parts.append(line[5:].lstrip())
    if parts:
        raw=b'\n'.join(parts)
        if raw.strip()!=b'[DONE]': yield json.loads(raw)

def redact(message,credentials):
    text=str(message)
    for name in ('api_key','workspace_id'):
        if credentials.get(name):text=text.replace(credentials[name],'[REDACTED]')
    return text

def synth(scene, credentials, rate=1.0):
    AUDIO.mkdir(parents=True, exist_ok=True)
    key = scene['key']; text = scene['narration']
    fingerprint = hashlib.sha256((text + VOICE + MODEL + str(rate) + INSTRUCTION).encode()).hexdigest()
    media = AUDIO / f'{key}.mp3'; metadata = AUDIO / f'{key}.json'
    if media.exists() and metadata.exists():
        cached = json.loads(metadata.read_text(encoding='utf-8'))
        if (cached.get('fingerprint') == fingerprint or cached.get('sourceFingerprint') == fingerprint) and media.stat().st_size > 100:
            return key, cached['duration'], 'cached'
    endpoint = f"https://{credentials['workspace_id']}.cn-beijing.maas.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer"
    body = {'model': credentials.get('model', MODEL), 'input': {'text':text,'voice':VOICE,'format':'mp3','sample_rate':24000,'rate':rate,'volume':50,'word_timestamp_enabled':True,'instruction':INSTRUCTION,'language_hints':['zh'],'seed':2026}}
    for attempt in range(4):
        try:
            chunks = []; words = []; sentences = []; request_id = None; usage = {}; last_url = None
            with requests.post(endpoint, headers={'Authorization':'Bearer '+credentials['api_key'],'Content-Type':'application/json','X-DashScope-SSE':'enable'},json=body,stream=True,timeout=(20,180)) as response:
                if response.status_code != 200:
                    try:
                        error = response.json()
                        msg = f"HTTP {response.status_code}: {error.get('code','')} {error.get('message','')}"
                    except Exception:
                        msg = f'HTTP {response.status_code}'
                    raise RuntimeError(redact(msg,credentials))
                for event in sse_events(response):
                    if event.get('code'):
                        raise RuntimeError(redact(event.get('message',event['code']),credentials))
                    request_id = event.get('request_id', request_id)
                    output = event.get('output',{}); audio = output.get('audio',{})
                    if audio.get('data'): chunks.append(base64.b64decode(audio['data']))
                    if audio.get('url'): last_url = audio['url']
                    sentence = output.get('sentence',{})
                    if output.get('type') == 'sentence-end':
                        sentence_words = sentence.get('words') or []
                        words.extend(sentence_words)
                        sentences.append({'index':sentence.get('index'), 'text':output.get('original_text',''), 'words':sentence_words})
                    usage = event.get('usage', usage)
            if not chunks and last_url:
                download = requests.get(last_url,timeout=180); download.raise_for_status(); chunks=[download.content]
            if not chunks: raise RuntimeError('TTS returned no audio')
            temp = AUDIO / f'{key}.partial.mp3'; temp.write_bytes(b''.join(chunks))
            seconds = duration(temp)
            if seconds < 1: raise RuntimeError('TTS audio too short')
            temp.replace(media)
            data = dict(fingerprint=fingerprint,duration=seconds,voice=VOICE,model=MODEL,rate=rate,request_id=request_id,usage=usage,words=words,sentences=sentences,narration=text)
            metadata.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
            return key, seconds, f'{len(words)} timestamps'
        except Exception as exc:
            if attempt == 3: raise RuntimeError(f'{key}: {type(exc).__name__}: {redact(exc,credentials)}') from None
            print(f'{key}: retry {attempt+1}: {type(exc).__name__}',flush=True)
            time.sleep(2 + attempt * 2)

# Course CLI: scripts/voice.py
