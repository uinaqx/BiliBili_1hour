import json,pathlib,subprocess
import draw
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build/preview';DEL=ROOT/'out'
def clips(t):
 return [(t['scenes'][0],0)]+[(next(s for s in t['scenes'] if s['run']==key),1) for key in ['x_width','a_width','a_nested','x_stats','a_stats']]
def main():
 t=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf8'));BUILD.mkdir(exist_ok=True);rows=['ffconcat version 1.0'];schedule=[];cursor=0
 for ci,(s,index) in enumerate(clips(t)):
  start=s['parts'][index]['begin'];length=450;end=start+length;assert end<=s['durationFrames'];points=sorted({start,*[f for f in s['renderFrames'] if start<f<end]})
  for j,f in enumerate(points):
   path=BUILD/f'{ci}-{f:05}.png';draw.render(s,f).save(path,compress_level=1);stop=points[j+1] if j+1<len(points) else end;rows.extend([f"file '{path.as_posix()}'",'option framerate 30',f'duration {(stop-f)/30:.9f}'])
  schedule.append(dict(scene=s['key'],fromFrame=start,previewStart=cursor,frames=length));cursor+=length
 rows.extend([f"file '{path.as_posix()}'",'option framerate 30']);listing=BUILD/'preview.ffconcat';listing.write_text('\n'.join(rows)+'\n',encoding='utf8');(BUILD/'schedule.json').write_text(json.dumps(schedule,ensure_ascii=False,indent=2),encoding='utf8')
 subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(listing),'-an','-vf','fps=30','-t','90','-frames:v','2700','-c:v','libx264','-preset','veryfast','-crf','19','-threads','3','-pix_fmt','yuv420p','-movflags','+faststart',str(DEL/'90秒画面试片_待配音.mp4')],check=True);print('PREVIEW_DONE',flush=True)
if __name__=='__main__':main()
