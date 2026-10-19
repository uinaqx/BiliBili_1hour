"""Final independent checks on course, browser evidence and actual media files."""
import json
import re
import subprocess
import unittest
from pathlib import Path
from .render import probe

ROOT=Path(__file__).resolve().parents[1]

def main():
    suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
    result=unittest.TextTestRunner(verbosity=1).run(suite)
    course=json.loads((ROOT/'data/course.json').read_text())
    browser=json.loads((ROOT/'output/browser_audit.json').read_text())
    report=dict(unit_tests=dict(run=result.testsRun,failures=len(result.failures),errors=len(result.errors)),
                course=dict(scenes=len(course['scenes']),duration=course['duration'],narration_chars=sum(s['narration_chars'] for s in course['scenes'])),
                browser=dict(page_errors=browser['page_errors'],out_of_bounds=browser['out_of_bounds'],deterministic_seek=browser['deterministic_seek'],navigation=browser['navigation'],playback=browser['playback']),media=[])
    failed=not result.wasSuccessful() or bool(browser['page_errors']) or bool(browser['out_of_bounds'])
    for name,duration in [('silent_preview.mp4',30),('course_120min_silent.mp4',7200)]:
        f=ROOT/'output'/name
        if not f.exists():
            report['media'].append(dict(file=name,status='missing'));failed=True;continue
        metadata=probe(f);video=next(s for s in metadata['streams'] if s['codec_type']=='video')
        actual=float(metadata['format']['duration'])
        stream_duration=float(video['duration'])
        checks=dict(duration=abs(actual-duration)<=1/30+.001 and abs(stream_duration-duration)<=1/30+.001,resolution=(video['width'],video['height'])==(1920,1080),codec=video['codec_name']=='h264',pixel_format=video['pix_fmt']=='yuv420p',silent=not any(s['codec_type']=='audio' for s in metadata['streams']))
        if duration==30:checks['constant_30fps']=video['r_frame_rate']==video['avg_frame_rate']=='30/1'
        else:
            checks['chapters']=len(metadata.get('chapters',[]))==11
            packets=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','packet=pts_time,duration_time','-of','json',str(f)]))['packets']
            pts=[float(p['pts_time']) for p in packets]
            checks['timeline_coverage']=pts[0]==0 and pts[-1]>7199.9 and max(b-a for a,b in zip(pts,pts[1:]))<8.1
        decoded=[]
        for offset in (0,duration/2,max(0,duration-1)):
            p=subprocess.run(['ffmpeg','-v','error','-ss',str(offset),'-i',str(f),'-frames:v','1','-f','null','-'],capture_output=True,text=True)
            decoded.append(dict(second=offset,ok=p.returncode==0 and not p.stderr.strip(),error=p.stderr.strip()))
        checks['decode_samples']=all(s['ok'] for s in decoded)
        if duration==7200:
            full_decode=subprocess.run(['ffmpeg','-v','error','-xerror','-err_detect','explode','-i',str(f),'-map','0:v:0','-fps_mode','passthrough','-f','null','-'],capture_output=True,text=True)
            checks['full_video_decode']=full_decode.returncode==0 and not full_decode.stderr.strip()
        failed|=not all(checks.values())
        report['media'].append(dict(file=name,status='pass' if all(checks.values()) else 'fail',duration=actual,video_duration=stream_duration,frames=video.get('nb_frames'),nominal_frame_rate=video['r_frame_rate'],average_frame_rate=video['avg_frame_rate'],bytes=f.stat().st_size,checks=checks,decode=decoded))
    text=(ROOT/'output/manuscript_estimated.srt').read_text();timestamps=re.findall(r'(\d\d):(\d\d):(\d\d),(\d\d\d) --> (\d\d):(\d\d):(\d\d),(\d\d\d)',text)
    last=0;ordered=True
    for stamp in timestamps:
        nums=list(map(int,stamp));a=nums[0]*3600+nums[1]*60+nums[2]+nums[3]/1000;b=nums[4]*3600+nums[5]*60+nums[6]+nums[7]/1000
        if a<last-.001 or b<a or b>7200.001:ordered=False
        last=b
    report['reading_cues']=dict(count=len(timestamps),ordered=ordered,last_end=last,status='estimated_manuscript_not_voice_aligned')
    failed|=not ordered or abs(last-7200)>.001
    report['overall']='pass' if not failed else 'fail'
    (ROOT/'output/validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    if not failed:
        state=json.loads((ROOT/'output/production_state.json').read_text());state.update(video='full_7200s_silent_rendered_and_probed',preview='30s_frame_rendered_and_probed',audio='deferred_by_user',validation='pass')
        (ROOT/'output/production_state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n')
        coverage=json.loads((ROOT/'output/coverage.json').read_text())
        for s in coverage:s['review']='four_browser_states_rendered_and_bounds_checked; review_frame_exported'
        (ROOT/'output/coverage.json').write_text(json.dumps(coverage,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if failed:raise SystemExit(1)

if __name__=='__main__':main()
