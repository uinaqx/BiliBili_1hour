"""Check encoded silent trial against the authored frames, including held highlights."""
import hashlib,io,json,pathlib,subprocess
import numpy as np
from PIL import Image,ImageDraw
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
 video=ROOT/'out/90秒画面试片_待配音.mp4'
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
 stream=probe['streams'];assert len(stream)==1 and stream[0]['codec_type']=='video'
 assert stream[0]['codec_name']=='h264' and (stream[0]['width'],stream[0]['height'])==(1920,1080)
 assert int(stream[0]['nb_frames'])==2700 and abs(float(probe['format']['duration'])-90)<.05
 t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));scenes={s['key']:s for s in t['scenes']}
 schedule=json.loads((ROOT/'build/preview/schedule.json').read_text(encoding='utf8'));errors=[];sheet=Image.new('RGB',(1440,1184),draw.BG);d=ImageDraw.Draw(sheet)
 for ci,clip in enumerate(schedule):
  for j,offset in enumerate([60,420]):
   at=(clip['previewStart']+offset)/30;s=scenes[clip['scene']];f=clip['fromFrame']+offset
   data=subprocess.check_output(['ffmpeg','-v','error','-ss',str(at),'-i',str(video),'-frames:v','1','-f','image2pipe','-vcodec','png','-threads','1','-'])
   with Image.open(io.BytesIO(data)) as im:actual=im.convert('RGB').resize((480,270))
   expected=draw.render(s,f).resize((480,270));error=float(np.abs(np.asarray(actual,dtype=float)-np.asarray(expected,dtype=float)).mean());assert error<4,(ci,offset,error)
   errors.append(dict(scene=s['key'],time=at,mae=error));i=ci*2+j;x=i%3*480;y=i//3*296;sheet.paste(actual,(x,y));d.text((x+8,y+273),s['key']+' '+str(at)+'s',fill='white',font=draw.font(18))
 sheet.save(ROOT/'build/preview/encoded-contact.jpg',quality=94)
 report=dict(allPassed=True,duration=90,frames=2700,audioStreams=0,checks=errors,videoSha256=hashlib.sha256(video.read_bytes()).hexdigest(),drawingSha256=hashlib.sha256((ROOT/'scripts/draw.py').read_bytes()).hexdigest())
 (ROOT/'build/preview-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('PREVIEW_CHECKED',len(errors),max(e['mae'] for e in errors),flush=True)
if __name__=='__main__':main()
