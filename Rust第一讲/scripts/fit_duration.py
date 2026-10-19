"""Fit the complete approved narration by a small pitch-preserving tempo change."""
import argparse,copy,hashlib,json,math,pathlib,shutil,subprocess,sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1];AUDIO=ROOT/'public/audio';RAW=ROOT/'public/audio_original';RAW.mkdir(exist_ok=True)
parser=argparse.ArgumentParser();parser.add_argument('--target',type=float,default=3735);args=parser.parse_args()
course=json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'));scenes=[s for c in course['chapters'] for s in c['scenes']]
sources=[]
for s in scenes:
    key=s['key'];current=json.loads((AUDIO/(key+'.json')).read_text(encoding='utf-8'));raw_meta=RAW/(key+'.json');raw_audio=RAW/(key+'.mp3')
    if not raw_meta.exists() or json.loads(raw_meta.read_text(encoding='utf-8'))['fingerprint']!=current.get('sourceFingerprint',current['fingerprint']):
        shutil.copy2(AUDIO/(key+'.mp3'),raw_audio);raw_meta.write_text(json.dumps(current,ensure_ascii=False,indent=2),encoding='utf-8')
    sources.append(json.loads(raw_meta.read_text(encoding='utf-8')))
speech=sum(m['duration'] for m in sources);holds=sum(.4+s['hold'] for s in scenes)
natural=sum(math.ceil(m['duration']*30)/30+.4+s['hold'] for s,m in zip(scenes,sources))
tempo=1 if 58*60<=natural<=63*60 else speech/(args.target-holds)
if not .94<=tempo<=1.15:raise ValueError(f'Cannot fit the approved narration with a gentle tempo change ({tempo:.4f})')
for index,(s,m) in enumerate(zip(scenes,sources),1):
    key=s['key'];dst=AUDIO/(key+'.mp3');metadata=AUDIO/(key+'.json');current=json.loads(metadata.read_text(encoding='utf-8'))
    fingerprint=hashlib.sha256((m['fingerprint']+';atempo='+str(tempo)).encode()).hexdigest()
    if current.get('fingerprint')==fingerprint and dst.exists():continue
    if tempo==1:shutil.copy2(RAW/(key+'.mp3'),dst)
    else:
        temp=AUDIO/(key+'.tempo.mp3')
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(RAW/(key+'.mp3')),'-af',f'atempo={tempo:.10f}','-c:a','libmp3lame','-b:a','128k',str(temp)],check=True)
        temp.replace(dst)
    new=copy.deepcopy(m);new['sourceFingerprint']=m['fingerprint'];new['fingerprint']=fingerprint;new['tempo']=tempo;new['originalDuration']=m['duration']
    new['duration']=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(dst)],text=True))
    for word in new['words']:
        word['begin_time']/=tempo;word['end_time']/=tempo
    for sentence in new.get('sentences',[]):
        for word in sentence.get('words',[]):word['begin_time']/=tempo;word['end_time']/=tempo
    metadata.write_text(json.dumps(new,ensure_ascii=False,indent=2),encoding='utf-8')
    if index%20==0 or index==len(scenes):print(f'TEMPO {index}/{len(scenes)}',flush=True)
report={'naturalDuration':natural,'target':args.target,'tempo':tempo,'pitchPreserved':True,'approvedNarrationUncut':True,'originalClipsRetained':True}
(ROOT/'build/tempo.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False),flush=True)
