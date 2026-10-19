"""Add exactly 0.100 s after internal Chinese full stops, preserving comma pauses."""
import argparse,bisect,concurrent.futures,copy,hashlib,json,pathlib,shutil,subprocess,sys,wave
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1];AUDIO=ROOT/'public/audio';RAW=ROOT/'public/audio_original';RAW.mkdir(exist_ok=True)
parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);args=parser.parse_args()
course=json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'));scenes=[s for c in course['chapters'] for s in c['scenes']]
if args.limit:scenes=scenes[:args.limit]
PAUSE=.1;RATE=24000
def process(scene):
    key=scene['key'];dst=AUDIO/(key+'.mp3');meta=AUDIO/(key+'.json');source=RAW/(key+'.mp3');rawmeta=RAW/(key+'.json')
    current=json.loads(meta.read_text(encoding='utf-8'))
    original=current.get('sourceFingerprint',current['fingerprint'])
    if not rawmeta.exists() or json.loads(rawmeta.read_text(encoding='utf-8'))['fingerprint']!=original:
        if 'sourceFingerprint' in current:raise ValueError('Missing immutable original: '+key)
        shutil.copy2(dst,source);shutil.copy2(meta,rawmeta)
    m=json.loads(rawmeta.read_text(encoding='utf-8'));words=m['words'];cuts=[]
    for i,w in enumerate(words):
        if '。' not in w['text']:continue
        if i==len(words)-1 and not any(ch.isalnum() for ch in w['text']):continue
        prefix=w['text'].lstrip('“”\"\' ')
        if prefix.startswith('。'):
            if i:cuts.append((words[i-1]['end_time']+w['begin_time'])/2)
        elif w['text'].rstrip('“”\"\' ').endswith('。'):
            if i+1<len(words):cuts.append((w['end_time']+words[i+1]['begin_time'])/2)
        else:raise ValueError('Ambiguous sentence boundary: '+key)
    cuts=sorted({round(t,3) for t in cuts if 1<t<words[-1]['end_time']-1})
    if len(cuts)!=scene['narration'].count('。')-1:raise ValueError('Source sentence count differs: '+key)
    fingerprint=hashlib.sha256((m['fingerprint']+';internal-full-stop-pause=0.100;v2').encode()).hexdigest()
    if current.get('fingerprint')==fingerprint:return dict(key=key,count=len(cuts),cached=True,duration=current['duration'])
    pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-f','s16le','-ac','1','-ar',str(RATE),'-'])
    cursor=0;parts=[];silence=bytes(round(PAUSE*RATE)*2)
    for t in cuts:
        sample=round(t/1000*RATE)*2
        if sample<cursor or sample>len(pcm):raise ValueError('Invalid cut: '+key)
        parts.extend([pcm[cursor:sample],silence]);cursor=sample
    parts.append(pcm[cursor:]);newpcm=b''.join(parts)
    assert len(newpcm)-len(pcm)==len(cuts)*len(silence)
    tempdir=ROOT/'build/audio-pauses';tempdir.mkdir(exist_ok=True)
    wav=tempdir/(key+'.pause.wav');temp=tempdir/(key+'.pause.mp3')
    with wave.open(str(wav),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(newpcm)
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(wav),'-c:a','libmp3lame','-b:a','128k',str(temp)],check=True)
    temp.replace(dst);wav.unlink()
    adjusted=copy.deepcopy(m)
    def shift(w):
        w['begin_time']+=bisect.bisect_right(cuts,w['begin_time'])*PAUSE*1000
        w['end_time']+=bisect.bisect_left(cuts,w['end_time'])*PAUSE*1000
    for w in adjusted['words']:shift(w)
    for sentence in adjusted.get('sentences',[]):
        for w in sentence.get('words',[]):shift(w)
    duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(dst)],text=True).strip())
    if abs(duration-m['duration']-len(cuts)*PAUSE)>.08:raise ValueError('Pause duration mismatch: '+key)
    adjusted.update(fingerprint=fingerprint,sourceFingerprint=m['fingerprint'],duration=duration,originalDuration=m['duration'],sentencePauseSeconds=PAUSE,pauseCutsMs=cuts,addedPauseSeconds=len(cuts)*PAUSE)
    meta.write_text(json.dumps(adjusted,ensure_ascii=False,indent=2),encoding='utf-8')
    return dict(key=key,count=len(cuts),duration=duration,addedSeconds=len(cuts)*PAUSE)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(process,scenes))
report=dict(extraFullStopPauseSeconds=PAUSE,commaPauseChanged=False,clips=len(results),insertedPauses=sum(r['count'] for r in results),addedSeconds=sum(r['count']*PAUSE for r in results),results=results)
(ROOT/'build/sentence-pauses.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='results'},ensure_ascii=False))
