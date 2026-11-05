"""Use returned word times and original PCM; insert only the agreed sentence pause."""
import argparse,bisect,copy,hashlib,json,pathlib,subprocess,wave
import timing_utils
ROOT=pathlib.Path(__file__).resolve().parents[1];RATE=24000
def load(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--available',action='store_true');parser.add_argument('--scenes');args=parser.parse_args();c=load(ROOT/'public/course.json');done=[]
 for chapter in c['chapters']:
  for scene in chapter['scenes']:
   if args.scenes and scene['id'] not in args.scenes.split(','):continue
   if args.available:
    def ready(b):
     path=ROOT/'public/audio_original'/(b['key']+'.json')
     try:return path.exists() and path.with_suffix('.mp3').exists() and load(path).get('narration')==b['text']
     except (ValueError,KeyError):return False
    if not all(ready(b) for b in scene['beats']):continue
   pcm=bytearray();parts=[]
   for b in scene['beats']:
    key=b['key'];raw=ROOT/'public/audio_original'/(key+'.mp3');meta=load(raw.with_suffix('.json'))
    assert meta['narration']==b['text'],('Voice cache changed; regenerate',key)
    output=ROOT/'public/audio'/(key+'.wav');tag=output.with_suffix('.json');fingerprint=hashlib.sha256((meta['fingerprint']+'sentence100-tempo1-v1').encode()).hexdigest()
    if output.exists() and tag.exists() and load(tag)['fingerprint']==fingerprint:
     p=load(tag)
     with wave.open(str(output)) as w:data=w.readframes(w.getnframes())
    else:
     decoded=subprocess.check_output(['ffmpeg','-v','error','-i',str(raw),'-ar',str(RATE),'-ac','1','-f','s16le','-c:a','pcm_s16le','-'])
     repaired=copy.deepcopy(meta);override=load(ROOT/'content/pause_overrides.json').get(key)
     if override:
      assert hashlib.sha256(raw.read_bytes()).hexdigest()==override['sourceMp3Sha256'],('Sentence repair source changed',key)
      matches=[i for i,w in enumerate(repaired['words']) if w['text']==override['originalWord']];assert len(matches)==1
      i=matches[0];word=repaired['words'][i];cut=override['cutMilliseconds'];assert word['begin_time']<cut<word['end_time']
      repaired['words'][i:i+1]=[dict(word,text=override['leftText'],end_time=cut),dict(word,text=override['rightText'],begin_time=cut)]
     cuts=[round(t/1000*RATE) for t in timing_utils.boundaries(repaired)]
     chunks=[];at=0
     for pos in cuts:
      assert at<=pos*2<=len(decoded);chunks.extend([decoded[at:pos*2],bytes(2400*2)]);at=pos*2
     chunks.extend([decoded[at:],bytes(2400*2)]);data=b''.join(chunks)
     with wave.open(str(output),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(data)
     p=dict(key=key,fingerprint=fingerprint,sourceMp3Sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),samples=len(data)//2,duration=len(data)/2/RATE,tempo=1.0,nativeRate=1.05,insertedPauseSeconds=.1,pauseCutsSamples=cuts,narration=b['text']);save(tag,p)
    start=len(pcm)/2/RATE;pcm.extend(data);pcm.extend(bytes(24000//5*2));parts.append(dict(**p,start=start,end=start+p['duration']))
   audio=ROOT/'public/audio'/(scene['id']+'.wav')
   with wave.open(str(audio),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(pcm)
   metadata=dict(key=scene['id'],samples=len(pcm)//2,duration=len(pcm)/2/RATE,sha256=hashlib.sha256(audio.read_bytes()).hexdigest(),parts=parts);save(audio.with_suffix('.json'),metadata);done.append(scene['id']);print('AUDIO_READY',scene['id'],round(metadata['duration'],2),flush=True)
 save(ROOT/'build/audio-preparation.json',dict(scenes=done,nativeRate=1.05,postTempo=1.0,sentencePauseSeconds=.1,source='Bailian native word timestamps; no timing-driven tempo adjustment'))
if __name__=='__main__':main()
