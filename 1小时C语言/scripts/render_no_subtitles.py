"""Re-encode existing caption-free source frames; copy original audio and chapters unchanged."""
import concurrent.futures,hashlib,json,pathlib,subprocess,sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out';BUILD=ROOT/'build/no-subtitles';BUILD.mkdir(exist_ok=True)
SOURCE=DEL/'一小时学习C语言_零基础.mp4';FINAL=DEL/'一小时学习C语言_零基础_无字幕.mp4'
T=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf-8'))
def run(args,log):
    with (BUILD/log).open('w',encoding='utf-8') as f:r=subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','warning',*args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    if r.returncode:raise RuntimeError((BUILD/log).read_text(encoding='utf-8',errors='replace')[-2000:])
def chapter(c):
    key=c['key'];dest=BUILD/(key+'.mp4');tag=BUILD/(key+'.hash');rows=['ffconcat version 1.0']
    for e in c['images']:
        image=ROOT/'public'/e['path'];assert image.is_file()
        rows.extend([f"file '{image.as_posix()}'",'option framerate 30',f"duration {e['frames']/30:.9f}"])
    rows.extend([f"file '{(ROOT/'public'/c['images'][-1]['path']).as_posix()}'",'option framerate 30'])
    text='\n'.join(rows)+'\n';fingerprint=hashlib.sha256(text.encode()+pathlib.Path(__file__).read_bytes()).hexdigest()
    if dest.exists() and tag.exists() and tag.read_text()==fingerprint:print('CACHED',key,flush=True);return
    listing=BUILD/(key+'.ffconcat');listing.write_text(text,encoding='utf-8')
    run(['-f','concat','-safe','0','-i',str(listing),'-an','-fps_mode','vfr','-enc_time_base','1:30','-t',f"{c['durationFrames']/30:.9f}",'-c:v','libx264','-preset','fast','-crf','20','-bf','0','-g','30','-pix_fmt','yuv420p','-threads','4','-video_track_timescale','30000','-movflags','+faststart',str(dest)],key+'.log')
    tag.write_text(fingerprint);print('NO_SUBTITLES_CHAPTER',key,flush=True)
def main():
    assert SOURCE.is_file()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(chapter,T['chapters']))
    listing=BUILD/'chapters.ffconcat';listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{c['key']}.mp4'\nduration {c['durationFrames']/30:.9f}\n" for c in T['chapters']),encoding='utf-8')
    temp=FINAL.with_name(FINAL.stem+'.rendering.mp4')
    run(['-f','concat','-safe','0','-i',str(listing),'-i',str(SOURCE),'-map','0:v:0','-map','1:a:0','-map_metadata','1','-map_chapters','1','-c','copy','-t',f"{T['duration']:.9f}",'-video_track_timescale','30000','-movflags','+faststart',str(temp)],'mux.log')
    temp.replace(FINAL);print('NO_SUBTITLES_DONE',str(FINAL),flush=True)
if __name__=='__main__':main()
