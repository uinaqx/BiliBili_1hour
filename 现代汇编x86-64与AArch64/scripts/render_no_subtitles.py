"""Disable the subtitle layer only, preserve every display timestamp, copy original AAC."""
import concurrent.futures,hashlib,json,pathlib,subprocess
import render_spoken as base
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build/no-subtitles'
FINAL=base.DEL/'一小时讲完现代汇编_x86-64与AArch64_无字幕.mp4'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def chapter(c):
 base.BUILD=BUILD
 base.chapter(c)
def main():
 BUILD.mkdir(parents=True,exist_ok=True)
 original=base.FINAL;assert original.exists()
 timeline=base.load(ROOT/'public/timeline.json');assert timeline['audio'] and timeline['subtitles']
 original_timeline_hash=digest(ROOT/'public/timeline.json');timeline['subtitles']=False
 source=hashlib.sha256((base.source_hash()+digest(pathlib.Path(__file__))+'subtitle-layer-disabled-only').encode()).hexdigest()
 for c in timeline['chapters']:
  for s in c['scenes']:s['subtitles']=False
  c['fingerprint']=hashlib.sha256((source+json.dumps(c,ensure_ascii=False,sort_keys=True)).encode()).hexdigest()
 manifest=dict(sourceHash=source,referenceVideo=original.name,referenceVideoSha256=digest(original),referenceTimelineSha256=original_timeline_hash,subtitles=False,copyOriginalAAC=True,chapters=timeline['chapters'])
 (BUILD/'render-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
 with concurrent.futures.ProcessPoolExecutor(max_workers=4) as pool:list(pool.map(chapter,timeline['chapters']))
 listing=BUILD/'videos.ffconcat';listing.write_text('ffconcat version 1.0\n'+''.join(f"file '{c['key']}.mp4'\nduration {c['durationFrames']/30:.9f}\n" for c in timeline['chapters']),encoding='utf8')
 pending=FINAL.with_name(FINAL.stem+'.rendering.mp4')
 with (BUILD/'mux.log').open('w',encoding='utf8') as log:
  result=subprocess.run(['ffmpeg','-y','-v','warning','-f','concat','-safe','0','-i',str(listing),'-i',str(original),'-map','0:v:0','-map','1:a:0','-map_metadata','1','-map_chapters','1','-c','copy','-sn','-video_track_timescale','30000','-movflags','+faststart',str(pending)],stdout=log,stderr=subprocess.STDOUT)
 assert result.returncode==0,(BUILD/'mux.log').read_text(encoding='utf8',errors='replace')[-1500:]
 assert digest(ROOT/'public/timeline.json')==original_timeline_hash,'The primary timeline was changed'
 pending.replace(FINAL);print('NO_SUBTITLES_DONE',str(FINAL),FINAL.stat().st_size,flush=True)
if __name__=='__main__':main()
