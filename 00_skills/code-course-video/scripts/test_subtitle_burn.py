"""Encode and decode real frames: regression for sparse VFR + libass ordering."""
import json
import pathlib
import subprocess
import tempfile
import numpy as np
from subtitle_sync import write_tracks, sha


def main():
    root=pathlib.Path(__file__).resolve().parents[1]
    report=root/'reports/subtitle-burn-regression.json'
    cues=[dict(start=.51,end=1.51,spokenEnd=1.4,text='第一句：完整显示。'),
          dict(start=2.01,end=3.01,spokenEnd=2.9,text='第二句：说完再结束。')]
    with tempfile.TemporaryDirectory(prefix='subtitle-test-') as d:
        work=pathlib.Path(d);write_tracks(dict(cues=cues),work)
        results={}
        for mode,vf in [('unsafe','ass=subtitles.ass'),('fixed','fps=fps=30:round=up,ass=subtitles.ass')]:
            video=work/(mode+'.mp4')
            subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i','color=black:s=1920x1080:r=1/4:d=8',
                            '-vf',vf+',scale=320:180','-r','30','-t','8','-c:v','libx264','-preset','ultrafast',
                            '-pix_fmt','yuv420p',str(video)],cwd=work,check=True)
            raw=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-f','rawvideo','-pix_fmt','gray','-'])
            images=np.frombuffer(raw,dtype=np.uint8).reshape(-1,180,320)
            active=(images[:,155:,:].max(axis=(1,2))>50)
            expected=np.array([any(c['start']<=f/30<c['end'] for c in cues) for f in range(len(images))])
            mismatches=np.flatnonzero(active!=expected).tolist()
            results[mode]=dict(frames=len(images),subtitleFrames=int(active.sum()),mismatchedFrames=mismatches,
                               videoSha256=sha(video))
        assert results['unsafe']['mismatchedFrames'], 'Regression fixture no longer reproduces missing transitions'
        assert not results['fixed']['mismatchedFrames'], results['fixed']
        assert results['fixed']['frames']==240
    report.parent.mkdir(exist_ok=True)
    report.write_text(json.dumps(dict(test='8-second sparse-frame burn/decode; every output frame checked',
                                     passed=True,results=results),ensure_ascii=False,indent=2),encoding='utf8')
    print('BURN_REGRESSION_PASSED',results['fixed']['frames'],'decoded frames')


if __name__=='__main__':main()
