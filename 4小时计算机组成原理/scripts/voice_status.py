"""Inspect exact reusable narration cache without credentials or network access."""
import argparse,datetime,hashlib,json,pathlib
import audio
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--resume',action='store_true');a=parser.parse_args();clips=[];texts={}
 for f in sorted((ROOT/'content').glob('module_*.json')):
  m=json.loads(f.read_text(encoding='utf8'))
  for s in m['scenes']:
   for i,b in enumerate(s['beats']):texts[s['id']+f'-p{i:02}']=b['text']
 course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));compiled={b['key']:b['text'] for c in course['chapters'] for s in c['scenes'] for b in s['beats']};assert texts==compiled,'Module and compiled narration differ'
 for key,text in texts.items():
  media=ROOT/'public/audio_original'/(key+'.mp3');meta=media.with_suffix('.json');fingerprint=hashlib.sha256((text+audio.VOICE+audio.MODEL+'1.05'+audio.INSTRUCTION).encode()).hexdigest();valid=False
  if media.exists() and meta.exists():
   m=json.loads(meta.read_text(encoding='utf8'));valid=m.get('fingerprint')==fingerprint and m.get('narration')==text and m.get('model')==audio.MODEL and m.get('voice')==audio.VOICE and m.get('rate')==1.05 and media.stat().st_size>100
  item=dict(key=key,reusable=valid)
  if valid:item.update(duration=m['duration'],sha256=hashlib.sha256(media.read_bytes()).hexdigest())
  clips.append(item)
 cached=sum(x['reusable'] for x in clips);remaining=len(clips)-cached
 report=dict(onlineVoiceStatus='complete' if not remaining else ('user_restored' if a.resume else 'cache_audited'),reason='User explicitly restored narration on 2026-11-02; no subtitles.',automaticRetry=bool(a.resume and remaining),updatedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),total=len(clips),cached=cached,remaining=remaining,model=audio.MODEL,voice=audio.VOICE,nativeRate=1.05,postTempo=1.0,clips=clips)
 target=ROOT/'build/voice-resume-state.json';target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 if a.resume:(ROOT/'build/resume-cache-baseline.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print('VOICE_CACHE',len(clips),cached,remaining,report['onlineVoiceStatus'],flush=True)
if __name__=='__main__':main()
