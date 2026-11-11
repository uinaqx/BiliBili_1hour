"""Verify actual encoded selection states, chapters, audio and subtitle-free pixels."""
import bisect,hashlib,json,pathlib,subprocess,wave
import numpy as np
from PIL import Image
import draw
from highlight_sync import selected_lines
ROOT=pathlib.Path(__file__).resolve().parents[1];VIDEO=ROOT/'out/一小时学完TypeScript_零基础_无字幕.mp4'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 t=load(ROOT/'public/timeline.json');assert t['scope']=='complete' and t['subtitles'] is False;starts=[s['startFrame'] for s in t['scenes']]
 meta=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_chapters','-show_format','-of','json',str(VIDEO)]))
 duration=float(meta['format']['duration']);assert abs(duration-t['duration'])<.04,(duration,t['duration']);assert 50*60<=duration<=70*60
 assert not any(s['codec_type']=='subtitle' for s in meta['streams']);v=next(s for s in meta['streams'] if s['codec_type']=='video');a=next(s for s in meta['streams'] if s['codec_type']=='audio')
 assert v['width']==1920 and v['height']==1080 and v['codec_name']=='h264' and a['codec_name']=='aac'
 assert len(meta['chapters'])==10
 for actual,c in zip(meta['chapters'],t['chapters']):assert abs(float(actual['start_time'])-c['startFrame']/30)<.002 and actual['tags']['title']==c['title']
 ptsdata=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(VIDEO)]));pts=[round(float(x['best_effort_timestamp_time'])*30) for x in ptsdata['frames']]
 assert pts==sorted(set(pts))
 required={s['startFrame']+f for s in t['scenes'] for f in s['renderFrames']};assert required<=set(pts),(len(required-set(pts)),sorted(required-set(pts))[:5])
 # Every event's before/at/hold state is tested using the same selector used by rendering.
 persistent=0
 for s in t['scenes']:
  events=s['codeCues'];assert events[0]['beginFrame']==0
  for i,e in enumerate(events):
   end=events[i+1]['beginFrame'] if i+1<len(events) else s['durationFrames']
   for f in {e['beginFrame'],(e['beginFrame']+end-1)//2,end-1}:
    assert selected_lines(s,f)==e['lines'];persistent+=1
   if i and e['beginFrame']>events[i-1]['beginFrame']:assert selected_lines(s,e['beginFrame']-1)==events[i-1]['lines']
 proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(VIDEO),'-an','-vf','scale=480:270','-fps_mode','passthrough','-pix_fmt','rgb24','-f','rawvideo','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 seen=set();pixelchecks=0;thumbs=[];maes=[];snap=ROOT/'build/final-frames';snap.mkdir(exist_ok=True)
 for frame in pts:
  size=480*270*3;buf=bytearray()
  while len(buf)<size:
   chunk=proc.stdout.read(size-len(buf))
   if not chunk:break
   buf.extend(chunk)
  assert len(buf)==size
  im=np.frombuffer(buf,dtype=np.uint8).reshape(270,480,3).astype(float);s=t['scenes'][bisect.bisect_right(starts,frame)-1];f=frame-s['startFrame'];pi=max(0,bisect.bisect_right(s['partFrames'],f)-1)
  assert np.max(im[265:268])<55,(s['key'],'unexpected bottom text')
  if s['kind']!='cover' or pi>0:
   selected=selected_lines(s,f);code=s.get('answerCode') if pi and s.get('answerCode') else s['code'];visual=0
   for logical,line in enumerate(code.splitlines(),1):
    for _ in draw.wrap(line,1190,34,True) or ['']:
     rgb=im[int((247+visual*40+20)/4),338];expected=np.array(draw.HIGHLIGHT_BG if logical in selected else [16,34,55]);assert np.max(np.abs(rgb-expected))<13,(s['key'],f,logical,rgb.tolist(),selected)
     visual+=1;pixelchecks+=1
   seen.add(s['key'])
  if f in [0,s['partFrames'][1],s['durationFrames']-1]:
   expected=np.asarray(draw.render(s,f).resize((480,270),Image.Resampling.BICUBIC)).astype(float)
   mae=float(np.abs(im-expected).mean());assert mae<9,(s['key'],f,mae);maes.append(mae)
   if f==s['partFrames'][1]:
    out=Image.fromarray(im.astype('uint8'));out.save(snap/(s['key']+'.png'));thumbs.append(out)
 proc.stdout.close();err=proc.stderr.read();assert proc.wait()==0,err;assert len(seen)==60
 # Read decoded AAC and compare samples against the actual assembled PCM at scene starts and ends.
 decoded=subprocess.check_output(['ffmpeg','-v','error','-i',str(VIDEO),'-vn','-ar','8000','-ac','1','-f','s16le','-']);signal=np.frombuffer(decoded,dtype='<i2').astype(float);audio_checks=[]
 reference_pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(ROOT/'build/render/course.wav'),'-ar','8000','-ac','1','-f','s16le','-'])
 reference_signal=np.frombuffer(reference_pcm,dtype='<i2').astype(float)
 with wave.open(str(ROOT/'build/render/course.wav'),'rb') as wav:
  assert wav.getnframes()==t['totalFrames']*800
  for c in t['chapters']:
   for s in [c['scenes'][0],c['scenes'][-1]]:
    for offset in [2,max(2,s['durationFrames']/30-8)]:
     sample=(s['startFrame']+round(offset*30))*800;reference=reference_signal[sample//3:sample//3+8000*4];actual=signal[sample//3:sample//3+len(reference)]
     assert len(actual)==len(reference)
     correlation=float(np.corrcoef(reference,actual)[0,1]);assert correlation>.95,(s['key'],offset,correlation)
     audio_checks.append(dict(scene=s['key'],offset=offset,correlation=correlation))
 sheet=Image.new('RGB',(480*4,270*15),'#091421')
 for i,thumb in enumerate(thumbs):sheet.paste(thumb,((i%4)*480,(i//4)*270))
 sheet.save(ROOT/'build/final-contact.png')
 report=dict(allPassed=True,videoSha256=sha(VIDEO),timelineSha256=sha(ROOT/'public/timeline.json'),duration=duration,resolution=[1920,1080],chapters=10,subtitles=False,highlightStyle='original Rust 2: warm translucent row, 3px orange left border, orange active line number; no enclosing outline',codedPagesChecked=len(seen),encodedStatesChecked=len(pts),actualLinePixelChecks=pixelchecks,allRequiredStateFramesPresent=True,persistenceChecks=persistent,imageComparisons=len(maes),maximumImageMAE=max(maes),audioChecks=audio_checks,fullDecodePassed=True,manualReviewScope='Intro preview, original Rust 2 reference, representative code and exercise frames; actual encoded states automatically checked throughout. Not a full manual listening pass.')
 (ROOT/'build/final-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('FINAL_VERIFIED',duration,'states',len(pts),'row checks',pixelchecks,flush=True)
if __name__=='__main__':main()
