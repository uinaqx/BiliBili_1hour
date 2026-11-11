"""Check final encoded PTS, persistent selections, caption boundaries and real audio."""
import bisect,hashlib,json,pathlib,subprocess,wave
import numpy as np
from PIL import Image,ImageDraw
import draw
from render_spoken import FINAL
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'build/final-review'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir(exist_ok=True);t=load(ROOT/'public/timeline.json');probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_chapters','-show_format','-of','json',str(FINAL)]))
 vs=[s for s in probe['streams'] if s['codec_type']=='video'];au=[s for s in probe['streams'] if s['codec_type']=='audio']
 assert len(vs)==len(au)==1 and vs[0]['codec_name']=='h264' and au[0]['codec_name']=='aac'
 assert (vs[0]['width'],vs[0]['height'])==(1920,1080) and abs(float(probe['format']['duration'])-t['duration'])<.05
 assert len(probe['chapters'])==10
 for c,p in zip(t['chapters'],probe['chapters']):assert abs(float(p['start_time'])-c['startFrame']/30)<.002 and p['tags']['title']==c['title']
 fp=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(FINAL)]))
 pts=[round(float(f['best_effort_timestamp_time'])*30) for f in fp['frames']];assert pts[0]==0 and all(a<b for a,b in zip(pts,pts[1:]))
 planned={s['startFrame']+f for s in t['scenes'] for f in s['renderFrames']};assert planned<=set(pts),('Missing display events',len(planned-set(pts)))
 samples=set();starts=[s['startFrame'] for s in t['scenes']]
 for s in t['scenes']:
  origin=s['startFrame'];end=s['durationFrames'];local={0,end-1}
  for p in s['parts']:
   local.update([p['begin'],min(end-1,p['end']+1),max(0,p['begin']-1)])
   for cue in p.get('cues',[]):local.update([max(0,cue['begin']-1),cue['begin'],cue['motion']['end'],min(end-1,cue['begin']+75)])
  for cap in s['captions']:local.update([max(0,cap['begin']-1),cap['begin'],max(0,cap['end']-1),min(end-1,cap['end'])])
  if s['thinkStart'] is not None:local.update(s['thinkStart']+j*30 for j in range(4))
  samples.update(bisect.bisect_right(pts,origin+f)-1 for f in local)
 indices=sorted(samples);expression='+'.join(f'eq(n,{i})' for i in indices);select=OUT/'select.ffscript';select.write_text(f"select='{expression}',scale=480:270",encoding='ascii')
 proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(FINAL),'-an','-filter_script:v',str(select),'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-threads','1','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
 errors=[];highlight_rows=0;contacts={};chunksize=480*270*3
 for ni,index in enumerate(indices):
  raw=bytearray()
  while len(raw)<chunksize:
   block=proc.stdout.read(chunksize-len(raw));assert block,('Missing decoded review frame',index);raw.extend(block)
  actual=np.frombuffer(raw,dtype=np.uint8).reshape(270,480,3);absolute=pts[index];s=t['scenes'][bisect.bisect_right(starts,absolute)-1];local=absolute-s['startFrame'];expected=np.asarray(draw.render(s,local).resize((480,270)));diff=np.abs(actual.astype(float)-expected.astype(float));err=float(diff.mean());assert err<4,(s['key'],local,err);errors.append(err)
  if s['code']:
   selected=draw.current(s,local)['codeLines']
   for line in range(1,len(s['code'])+1):
    y=round((270+(line-1)*39+18)/4);pixel=actual[y,303:308].mean(axis=0);on=np.linalg.norm(pixel-np.array([38,55,75]));off=np.linalg.norm(pixel-np.array([16,36,58]));assert (on<off)==(line in selected),(s['key'],local,line,selected,pixel.tolist());highlight_rows+=1
  if s['key'] not in contacts:contacts[s['key']]=Image.fromarray(actual.copy())
  if ni%600==0:print('ENCODED_STATES_CHECKED',ni,'/',len(indices),flush=True)
 assert not proc.stdout.read(1),'Unexpected decoded review frame';err=proc.stderr.read().decode(errors='replace');assert proc.wait()==0,err
 for first in range(0,len(t['scenes']),12):
  sheet=Image.new('RGB',(1440,1184),draw.BG);d=ImageDraw.Draw(sheet)
  for j,s in enumerate(t['scenes'][first:first+12]):
   x=j%3*480;y=j//3*296;sheet.paste(contacts[s['key']],(x,y));d.text((x+8,y+273),s['key'],font=draw.font(18),fill='white')
  sheet.save(OUT/f'encoded-contact-{first//12+1:02}.jpg',quality=94)
 audio_checks=[]
 for key in ['ma-01-03','ma-05-03','ma-10-03']:
  s=next(s for s in t['scenes'] if s['key']==key);offset=2;seconds=8
  with wave.open(str(ROOT/'public'/s['audio']),'rb') as f:f.setpos(offset*24000);reference=np.frombuffer(f.readframes(seconds*24000),dtype='<i2').astype(float)
  data=subprocess.check_output(['ffmpeg','-v','error','-ss',f'{(s["startFrame"]+s["leadFrames"])/30+offset:.9f}','-i',str(FINAL),'-vn','-t',str(seconds),'-ar','24000','-ac','1','-f','s16le','-'])
  actual=np.frombuffer(data,dtype='<i2').astype(float);n=min(len(actual),len(reference));reference=reference[:n];actual=actual[:n];reference-=reference.mean();actual-=actual.mean()
  corr=float(np.dot(reference,actual)/np.sqrt(np.dot(reference,reference)*np.dot(actual,actual)));assert corr>.96,(key,'Audio mismatch',corr)
  audio_checks.append(dict(scene=key,seconds=seconds,zeroLagCorrelation=corr));(OUT/(key+'-audio.wav')).write_bytes(b'') if False else None
 with (OUT/'decode.log').open('w',encoding='utf8') as f:r=subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(FINAL),'-f','null','-'],stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(OUT/'decode.log').read_text(encoding='utf8')[-1500:]
 report=dict(allPassed=True,video=str(FINAL.name),duration=t['duration'],chapters=10,codec='H.264/AAC',dimensions=[1920,1080],videoFrames=len(pts),plannedDisplayEvents=len(planned),sampledEncodedStates=len(indices),checkedHighlightRows=highlight_rows,maxPixelMAE=max(errors),audioPCMComparisons=audio_checks,completeDecode=True,videoSha256=sha(FINAL),courseSha256=sha(ROOT/'public/course.json'),timelineSha256=sha(ROOT/'public/timeline.json'),drawingSha256=sha(ROOT/'scripts/draw.py'),scope='All planned display events, every caption edge and cue/hold boundaries sampled from encoded MP4; three 8-second AAC/PCM comparisons; does not claim manual real-time listening of the entire course.')
 (ROOT/'build/final-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('FINAL_CHECKED',len(indices),highlight_rows,max(errors),flush=True)
if __name__=='__main__':main()
