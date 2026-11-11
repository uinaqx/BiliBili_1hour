"""90-second internal spoken trial using the exact final PCM and visual states."""
import hashlib,io,json,pathlib,subprocess,wave
import numpy as np
from PIL import Image,ImageDraw
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build/preview-spoken';DEL=ROOT/'out'
def main():
 t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));BUILD.mkdir(exist_ok=True);rows=['ffconcat version 1.0'];schedule=[];pcm=bytearray();cursor=0
 clips=[(t['scenes'][0],0)]+[(next(s for s in t['scenes'] if s['run']==key),1) for key in ['x_width','a_width','a_nested','x_stats','a_stats']]
 for ci,(s,index) in enumerate(clips):
  start=s['parts'][index]['begin'];end=start+450;assert end<=s['durationFrames'];points=sorted({start,*[f for f in s['renderFrames'] if start<f<end]})
  for j,f in enumerate(points):
   path=BUILD/f'{ci}-{f:05}.png';draw.render(s,f).save(path,compress_level=1);stop=points[j+1] if j+1<len(points) else end;rows.extend([f"file '{path.as_posix()}'",'option framerate 30',f'duration {(stop-f)/30:.9f}'])
  with wave.open(str(ROOT/'public'/s['audio']),'rb') as w:raw=w.readframes(w.getnframes())
  page=bytes(s['leadFrames']*800*2)+raw;page+=bytes(s['durationFrames']*800*2-len(page));pcm.extend(page[start*1600:end*1600]);schedule.append(dict(scene=s['key'],fromFrame=start,previewStart=cursor,frames=450));cursor+=450
 rows.extend([f"file '{path.as_posix()}'",'option framerate 30']);listing=BUILD/'preview.ffconcat';listing.write_text('\n'.join(rows)+'\n',encoding='utf8');(BUILD/'schedule.json').write_text(json.dumps(schedule,ensure_ascii=False,indent=2),encoding='utf8')
 wav=BUILD/'preview.wav'
 with wave.open(str(wav),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(24000);w.writeframes(pcm)
 video=DEL/'90秒新版试片_含字幕.mp4'
 subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(listing),'-i',str(wav),'-vf','fps=30','-t','90','-frames:v','2700','-c:v','libx264','-preset','veryfast','-crf','19','-threads','3','-c:a','aac','-b:a','160k','-pix_fmt','yuv420p','-movflags','+faststart',str(video)],check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]));vs=[s for s in probe['streams'] if s['codec_type']=='video'];au=[s for s in probe['streams'] if s['codec_type']=='audio'];assert len(vs)==len(au)==1 and int(vs[0]['nb_frames'])==2700 and abs(float(probe['format']['duration'])-90)<.05
 sheet=Image.new('RGB',(1440,1184),draw.BG);d=ImageDraw.Draw(sheet);errors=[]
 for ci,((s,_),clip) in enumerate(zip(clips,schedule)):
  for j,off in enumerate([60,420]):
   data=subprocess.check_output(['ffmpeg','-v','error','-ss',str((clip['previewStart']+off)/30),'-i',str(video),'-frames:v','1','-f','image2pipe','-vcodec','png','-threads','1','-'])
   with Image.open(io.BytesIO(data)) as im:actual=im.convert('RGB').resize((480,270))
   expected=draw.render(s,clip['fromFrame']+off).resize((480,270));err=float(np.abs(np.asarray(actual,dtype=float)-np.asarray(expected,dtype=float)).mean());assert err<4,(s['key'],off,err);errors.append(err);i=ci*2+j;x=i%3*480;y=i//3*296;sheet.paste(actual,(x,y));d.text((x+8,y+273),s['key']+' '+str((clip['previewStart']+off)/30)+'s',font=draw.font(18),fill='white')
 sheet.save(BUILD/'encoded-contact.jpg',quality=94);(ROOT/'build/spoken-preview-review.json').write_text(json.dumps(dict(allPassed=True,duration=90,frames=2700,audio='AAC',sampledStates=12,maxPixelMAE=max(errors),videoSha256=hashlib.sha256(video.read_bytes()).hexdigest(),timelineSha256=hashlib.sha256((ROOT/'public/timeline.json').read_bytes()).hexdigest()),indent=2),encoding='utf8');print('SPOKEN_PREVIEW_CHECKED',max(errors),flush=True)
if __name__=='__main__':main()
