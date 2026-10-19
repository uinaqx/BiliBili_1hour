"""Bailian TTS. Credentials stay in process memory; no credentials in cache."""
import argparse, base64, concurrent.futures, hashlib, json, os, pathlib, subprocess, sys, time
import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
AUDIO = ROOT / 'public' / 'audio'
MODEL = os.environ.get('TTS_MODEL','qwen-audio-3.0-tts-plus')
VOICE = os.environ.get('TTS_VOICE','longanlufeng')
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
                    raise RuntimeError(msg.replace(credentials['api_key'],'[REDACTED]'))
                for event in sse_events(response):
                    if event.get('code'):
                        raise RuntimeError(str(event.get('message',event['code'])).replace(credentials['api_key'],'[REDACTED]'))
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
            if attempt == 3: raise RuntimeError(f'{key}: {type(exc).__name__}: {str(exc).replace(credentials["api_key"],"[REDACTED]")}') from None
            print(f'{key}: retry {attempt+1}: {type(exc).__name__}',flush=True)
            time.sleep(2 + attempt * 2)

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--test',action='store_true'); parser.add_argument('--limit',type=int); parser.add_argument('--rate',type=float,default=1.0); parser.add_argument('--workers',type=int,default=2)
    parser.add_argument('--confirm-quota',action='store_true',help='Confirm that you checked this model quota, expiration and billing protection.')
    parser.add_argument('--dry-run',action='store_true',help='Show the job size without credentials or API requests.')
    args=parser.parse_args()
    if args.test:
        scenes=[{'key':'bailian-test','narration':'同学们好。今天我们用一小时学习 Rust 的基础知识。我们先保存一个分数，再一步一步学习怎样使用这份数据。每次只理解一个新点，先看例子，再看原因。'}]
    else:
        course=json.loads((ROOT/'public'/'course.json').read_text(encoding='utf-8')); scenes=[s for c in course['chapters'] for s in c['scenes']]
    if args.limit: scenes=scenes[:args.limit]
    if args.dry_run:
        print(f'DRY_RUN: {len(scenes)} clips; {sum(len(s["narration"]) for s in scenes)} characters; model={MODEL}; no API requests.');return
    if not args.confirm_quota:parser.error('Check this model free quota, expiry and billing protection first; then use --confirm-quota.')
    if not os.environ.get('DASHSCOPE_API_KEY') or not os.environ.get('SFM_WORKSPACE_ID'):
        parser.error('Set your own DASHSCOPE_API_KEY and SFM_WORKSPACE_ID process environment variables.')
    credentials={'api_key':os.environ['DASHSCOPE_API_KEY'],'workspace_id':os.environ['SFM_WORKSPACE_ID'],'model':MODEL}
    total=0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures=[pool.submit(synth,s,credentials,args.rate) for s in scenes]
        for i,f in enumerate(concurrent.futures.as_completed(futures),1):
            key,sec,state=f.result(); total+=sec
            print(f'[{i}/{len(scenes)}] {key}: {sec:.2f}s ({state})',flush=True)
    print(f'AUDIO_TOTAL_SECONDS={total:.2f}',flush=True)

if __name__=='__main__': main()
