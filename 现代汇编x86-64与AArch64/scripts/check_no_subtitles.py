"""Verify the subtitle-only variant against the original timing and AAC packets."""
import bisect,hashlib,json,pathlib,subprocess
import numpy as np
from PIL import Image,ImageDraw
import draw
from render_no_subtitles import FINAL,BUILD
from render_spoken import FINAL as ORIGINAL
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_chapters','-show_format','-of','json',str(p)]))
def pts(p):
 data=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(p)]))
 return [round(float(f['best_effort_timestamp_time'])*30000) for f in data['frames']]
def audio_hash(p):return subprocess.check_output(['ffmpeg','-v','error','-i',str(p),'-map','0:a:0','-c:a','copy','-f','hash','-hash','sha256','-'],text=True).strip()
def main():
 t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));manifest=json.loads((BUILD/'render-manifest.json').read_text(encoding='utf8'));assert sha(ORIGINAL)==manifest['referenceVideoSha256'] and sha(ROOT/'public/timeline.json')==manifest['referenceTimelineSha256']
 a,b=probe(ORIGINAL),probe(FINAL);assert abs(float(a['format']['duration'])-float(b['format']['duration']))<.002
 assert len(a['chapters'])==len(b['chapters'])==10
 for x,y in zip(a['chapters'],b['chapters']):assert x['tags']['title']==y['tags']['title'] and abs(float(x['start_time'])-float(y['start_time']))<.001 and abs(float(x['end_time'])-float(y['end_time']))<.001
 streams=b['streams'];assert len([x for x in streams if x['codec_type']=='video'])==len([x for x in streams if x['codec_type']=='audio'])==1 and not any(x['codec_type']=='subtitle' for x in streams)
 ah,bh=audio_hash(ORIGINAL),audio_hash(FINAL);assert ah==bh,'AAC packets changed'
 original_pts=pts(ORIGINAL);actual_pts=pts(FINAL);assert original_pts==actual_pts,'Display timestamps changed';starts=[s['startFrame'] for s in t['scenes']];samples=set()
 for s in t['scenes']:
  for cap in s['captions']:
   frame=(cap['begin']+cap['end'])//2;absolute=(s['startFrame']+frame)*1000;samples.add(bisect.bisect_right(actual_pts,absolute)-1)
  for p in s['parts']:samples.add(bisect.bisect_right(actual_pts,(s['startFrame']+p['begin'])*1000)-1)
 indices=sorted(samples);script=BUILD/'review-select.ffscript';script.write_text("select='"+'+'.join(f'eq(n,{i})' for i in indices)+"',scale=480:270",encoding='ascii')
 proc=subprocess.Popen(['ffmpeg','-v','error','-threads','2','-i',str(FINAL),'-an','-filter_script:v',str(script),'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-threads','1','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE);errors=[];bands=[];contacts={};rows=0
 for count,index in enumerate(indices):
  raw=bytearray();size=480*270*3
  while len(raw)<size:
   chunk=proc.stdout.read(size-len(raw));assert chunk;raw.extend(chunk)
  actual=np.frombuffer(raw,dtype=np.uint8).reshape(270,480,3);frame=round(actual_pts[index]/1000);source=t['scenes'][bisect.bisect_right(starts,frame)-1];scene=dict(source,subtitles=False);local=frame-scene['startFrame'];expected=np.asarray(draw.render(scene,local).resize((480,270)));diff=np.abs(actual.astype(float)-expected.astype(float));error=float(diff.mean());band=float(diff[249:].mean());assert error<4 and band<3,(scene['key'],frame,error,band)
  large=int((diff[249:].max(axis=2)>70).sum());assert large<(50 if scene['key']=='ma-01-01' else 5),(scene['key'],'Unexpected subtitle pixels',large)
  if scene['code']:
   selected=draw.current(scene,local)['codeLines']
   for line in range(1,len(scene['code'])+1):
    y=round((270+(line-1)*39+18)/4);pixel=actual[y,303:308].mean(axis=0);assert (np.linalg.norm(pixel-[38,55,75])<np.linalg.norm(pixel-[16,36,58]))==(line in selected);rows+=1
  errors.append(error);bands.append(band)
  if scene['key'] not in contacts:contacts[scene['key']]=Image.fromarray(actual.copy())
  if count%200==0:print('NO_SUBTITLE_STATES_CHECKED',count,'/',len(indices),flush=True)
 assert not proc.stdout.read(1);err=proc.stderr.read().decode(errors='replace');assert proc.wait()==0,err
 for first in range(0,len(t['scenes']),12):
  sheet=Image.new('RGB',(1440,1184),draw.BG);d=ImageDraw.Draw(sheet)
  for j,s in enumerate(t['scenes'][first:first+12]):
   x=j%3*480;y=j//3*296;sheet.paste(contacts[s['key']],(x,y));d.text((x+8,y+273),s['key'],font=draw.font(18),fill='white')
  sheet.save(BUILD/f'contact-{first//12+1:02}.jpg',quality=94)
 with (BUILD/'decode.log').open('w',encoding='utf8') as log:r=subprocess.run(['ffmpeg','-v','error','-xerror','-threads','2','-i',str(FINAL),'-map','0:v:0','-an','-fps_mode','passthrough','-threads','2','-f','null','-'],stdout=log,stderr=subprocess.STDOUT)
 assert r.returncode==0
 report=dict(allPassed=True,variant='no subtitles; original timeline and AAC copied',duration=float(b['format']['duration']),chapters=10,displayTimestampsIdentical=True,displayFrames=len(actual_pts),audioPacketsIdentical=True,audioPacketSha256=bh,sampledEncodedStates=len(indices),checkedHighlightRows=rows,maxPixelMAE=max(errors),maxSubtitleBandMAE=max(bands),completeVideoDecode=True,videoSha256=sha(FINAL),referenceVideoSha256=sha(ORIGINAL),referenceTimelineSha256=sha(ROOT/'public/timeline.json'))
 (BUILD/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('NO_SUBTITLES_VERIFIED',len(indices),rows,max(errors),flush=True)
if __name__=='__main__':main()
