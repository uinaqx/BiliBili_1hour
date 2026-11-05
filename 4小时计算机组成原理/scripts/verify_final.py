"""Verify the actual complete, anonymous, subtitle-free lecture release."""
import bisect,hashlib,json,pathlib,subprocess,wave
import numpy as np
from PIL import Image,ImageDraw
import draw
from render import FINAL
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'build/final-review'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(exist_ok=True);t=load(ROOT/'public/timeline.json');c=load(ROOT/'public/course.json');inputs=load(ROOT/'build/release-inputs.json');assert t['scope']=='complete' and len(t['scenes'])==253 and not t['subtitles'];assert inputs['courseSha256']==sha(ROOT/'public/course.json')
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_chapters','-show_format','-of','json',str(FINAL)]));vs=[x for x in probe['streams'] if x['codec_type']=='video'];au=[x for x in probe['streams'] if x['codec_type']=='audio'];assert len(vs)==len(au)==1 and not any(x['codec_type']=='subtitle' for x in probe['streams'])
 assert (vs[0]['width'],vs[0]['height'])==(1920,1080) and vs[0]['codec_name']=='h264' and au[0]['codec_name']=='aac';assert abs(float(probe['format']['duration'])-t['duration'])<.05 and len(probe['chapters'])==10
 for ch,p in zip(t['chapters'],probe['chapters']):assert ch['title']==p['tags']['title'] and abs(ch['startFrame']/30-float(p['start_time']))<.002
 frames=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(FINAL)]))['frames'];pts=[round(float(f['best_effort_timestamp_time'])*30) for f in frames];planned={s['startFrame']+f for s in t['scenes'] for f in s['renderFrames']};assert pts[0]==0 and all(a<b for a,b in zip(pts,pts[1:])) and planned<=set(pts)
 proc=subprocess.Popen(['ffmpeg','-v','error','-threads','2','-i',str(FINAL),'-an','-vf','scale=480:270','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-threads','1','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE);starts=[s['startFrame'] for s in t['scenes']];errors=[];bands=[];items=[];seen=set()
 for i,frame in enumerate(pts):
  raw=bytearray();size=480*270*3
  while len(raw)<size:
   block=proc.stdout.read(size-len(raw));assert block,('Missing encoded frame',i);raw.extend(block)
  actual=np.frombuffer(raw,dtype=np.uint8).reshape(270,480,3);s=t['scenes'][bisect.bisect_right(starts,frame)-1];local=frame-s['startFrame'];expected=np.asarray(draw.render(s,local).resize((480,270)));diff=np.abs(actual.astype(float)-expected.astype(float));err=float(diff.mean());band=float(diff[252:].mean());assert err<4 and band<3,(s['id'],local,err,band);errors.append(err);bands.append(band)
  beat=max(0,bisect.bisect_right(s['beatFrames'],local)-1);key=(s['id'],beat)
  if key not in seen:seen.add(key);items.append((s['id'],beat,Image.fromarray(actual.copy())))
  if i%150==0:print('FINAL_FRAMES_CHECKED',i,'/',len(pts),flush=True)
 assert not proc.stdout.read(1);error=proc.stderr.read().decode(errors='replace');assert proc.wait()==0,error;assert len(seen)==519
 for first in range(0,len(items),12):
  sheet=Image.new('RGB',(1440,1184),draw.BG);d=ImageDraw.Draw(sheet)
  for j,(key,beat,img) in enumerate(items[first:first+12]):
   x=j%3*480;y=j//3*296;sheet.paste(img,(x,y));d.text((x+8,y+273),key+' / '+str(beat+1),font=draw.font(18),fill='white')
  sheet.save(OUT/f'contact-{first//12+1:03}.jpg',quality=93)
 audio=[]
 for ch in t['chapters']:
  s=ch['scenes'][len(ch['scenes'])//2];offset=2;seconds=8;source=ROOT/'public'/s['audio']
  reference_data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(offset),'-i',str(source),'-t',str(seconds),'-ar','48000','-ac','1','-f','s16le','-']);reference=np.frombuffer(reference_data,dtype='<i2').astype(float)
  start=(s['startFrame']+s['leadFrames'])/30+offset;actual_data=subprocess.check_output(['ffmpeg','-v','error','-ss',f'{start:.9f}','-i',str(FINAL),'-vn','-t',str(seconds),'-ar','48000','-ac','1','-f','s16le','-']);actual=np.frombuffer(actual_data,dtype='<i2').astype(float);n=min(len(reference),len(actual));reference=reference[:n];actual=actual[:n];reference-=reference.mean();actual-=actual.mean();corr=float(np.dot(reference,actual)/np.sqrt(np.dot(reference,reference)*np.dot(actual,actual)));assert corr>.96,(ch['key'],s['id'],'Audio position mismatch',corr);audio.append(dict(chapter=ch['key'],scene=s['id'],seconds=seconds,zeroLagCorrelation=corr))
 with (OUT/'decode.log').open('w',encoding='utf8') as log:r=subprocess.run(['ffmpeg','-v','error','-xerror','-threads','2','-i',str(FINAL),'-fps_mode','passthrough','-threads','2','-f','null','-'],stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode==0,(OUT/'decode.log').read_text(encoding='utf8',errors='replace')[-1500:]
 report=dict(allPassed=True,video=FINAL.name,duration=t['duration'],chapters=10,scenes=253,narrationClips=519,sourceSlidesAccountedFor=920,reviewedAssets=392,plannedDisplayEvents=len(planned),encodedFrames=len(pts),checkedEncodedStates=len(errors),checkedNarrationVisualStates=len(seen),maxPixelMAE=max(errors),maxBottomBandMAE=max(bands),audioComparisons=audio,completeAVDecode=True,subtitles=False,voice=dict(model='qwen-audio-3.1-tts-plus',voice='xunanchuan_v3.1',nativeRate=1.05,postTempo=1.0),videoSha256=sha(FINAL),courseSha256=sha(ROOT/'public/course.json'),timelineSha256=sha(ROOT/'public/timeline.json'),drawingSha256=sha(ROOT/'scripts/draw.py'),privacyInputReportSha256=sha(ROOT/'build/release-inputs.json'),scope='Every encoded visual state compared with the approved asset renderer; chapter audio-position samples and full AV decode. Previous source privacy review is hash-bound; does not claim real-time manual listening to the entire lecture.')
 (ROOT/'build/final-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('FINAL_VERIFIED',len(pts),len(seen),max(errors),flush=True)
if __name__=='__main__':main()
