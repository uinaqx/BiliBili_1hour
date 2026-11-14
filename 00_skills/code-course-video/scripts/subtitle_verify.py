"""Check version PCM, stream preservation and decoded subtitle boundary frames."""
import bisect
import json
import math
import pathlib
import subprocess
from fractions import Fraction

import numpy as np

from subtitle_sync import pcm_file, quantize

def output(*args):
    return subprocess.check_output(list(map(str,args)))

def probe(path):
    return json.loads(output('ffprobe','-v','error','-show_format','-show_streams','-show_chapters',
                             '-of','json',path))

def video_info(info):
    return next(x for x in info['streams'] if x['codec_type']=='video')

def frame_rate_kind(path, fps):
    times=output('ffprobe','-v','error','-select_streams','v:0','-show_entries',
                 'packet=pts','-of','csv=p=0',path).splitlines()
    timebase=Fraction(video_info(probe(path))['time_base'])
    ticks=sorted(int(t) for t in times if t.strip())
    expected=Fraction(1)/Fraction(str(fps))/timebase
    return 'CFR' if ticks and all(abs((t-ticks[0])-i*expected)<=1 for i,t in enumerate(ticks)) else 'VFR'

def audio_hash(path):
    return output('ffmpeg','-v','error','-i',path,'-map','0:a:0','-c','copy',
                  '-f','hash','-hash','sha256','-').decode().strip()

def decode_audio(path,rate):
    return np.frombuffer(output('ffmpeg','-v','error','-xerror','-i',path,'-map','0:a:0',
                           '-ac','1','-ar',rate,'-f','s16le','-'),dtype='<i2')

def verify_pcm_placement(video,plan):
    info=probe(video)
    rate=int(next(s for s in info['streams'] if s['codec_type']=='audio')['sample_rate'])
    actual=decode_audio(video,rate)
    scores=[]
    for place in plan['placements']:
        raw,fmt=pcm_file(place['audio'])
        if fmt==(rate,1,2):
            source=np.frombuffer(raw,dtype='<i2')
        else:
            source=decode_audio(place['audio'],rate)
        start=round(place['start']*rate)
        if (start<0 or start+len(source)>len(actual)
            or place['start']+len(source)/rate>place['limit']+.001):
            raise ValueError(f'{place["key"]}: PCM exceeds its timeline slot')
        got=actual[start:start+len(source)]
        score=float(np.corrcoef(source.astype(np.float32),got.astype(np.float32))[0,1])
        if not math.isfinite(score) or score<.95:
            raise ValueError(f'{place["key"]}: audio does not match the master at its timeline position ({score})')
        scores.append(score)
    return dict(scenes=len(scores),minimumCorrelation=min(scores),sampleRate=rate)

def boundary_frames(video,master,plan,ass_file):
    fps=plan['fps']
    ticks=quantize(plan['cues'],.01)
    starts=[c['startTick']/100 for c in ticks]
    frames={}
    for i,c in enumerate(ticks):
        start,end=starts[i],c['endTick']/100
        first=math.ceil(start*fps-1e-8)
        stop=math.ceil(end*fps-1e-8)
        if first>=stop:
            raise ValueError(f'Cue {i+1} has no visible CFR frame')
        before=.05 if plan['endPolicy']=='hold-within-part' else .10
        for f in (max(first,math.floor((end-before)*fps+1e-8)),
                  min(math.floor((end+.10)*fps+1e-8),math.ceil(plan['duration']*fps)-1)):
            active=bisect.bisect_right(starts,f/fps+1e-10)-1
            if active>=0 and f/fps>=ticks[active]['endTick']/100-1e-10:
                active=-1
            frames[f]=active
    # Read a compact strip at every decoded frame and retain only selected
    # boundaries. The comparison image is independently rendered from the
    # master at the same time using the bound ASS, including adjacent cues.
    source=video_info(probe(master))
    height=source['height']
    width=source['width']
    box=min(height//3,210*height//1080)
    crop=f'crop={width}:{box}:0:{height-box},scale=320:36,format=gray'
    base_filter=f'fps=fps={fps}:round=up,settb=1/1000000,setpts=PTS+1'
    with_qa=f'{base_filter},ass=filename={ass_file.name},setpts=PTS-1,{crop}'

    def collect(path,filter_spec,cwd=None):
        args=['ffmpeg','-nostdin','-v','error','-xerror','-threads','4','-i',str(pathlib.Path(path).resolve()),
              '-an','-vf',filter_spec,'-fps_mode','passthrough','-f','rawvideo','-']
        captured={}
        with subprocess.Popen(args,cwd=cwd,stdout=subprocess.PIPE) as proc:
            for i in range(max(frames)+1):
                raw=proc.stdout.read(320*36)
                if len(raw)!=320*36:
                    raise ValueError(f'Missing boundary QA frame {i}')
                if i in frames:
                    captured[i]=np.frombuffer(raw,dtype=np.uint8).astype(np.int16)
            while proc.stdout.read(1024*1024):
                pass
            if proc.wait()!=0:
                raise ValueError('Final or QA reference video failed to decode')
        return captured
    actual=collect(video,crop)
    reference=collect(master,with_qa,cwd=ass_file.parent)
    max_mae=0
    checks=0
    for frame,active in frames.items():
        a,b=actual[frame],reference[frame]
        mae=float(np.abs(a-b).mean())
        max_mae=max(mae,max_mae)
        if active>=0:
            expected=b>90
            seen=a>75
            union=int((expected|seen).sum())
            overlap=float((expected&seen).sum())/max(union,1)
            if not expected.any() or overlap<.48:
                raise ValueError(f'Subtitle boundary {frame/fps:.3f}s does not display expected cue {active+1}: {overlap:.3f}')
        if mae>3.8:
            raise ValueError(f'Subtitle edge differs at {frame/fps:.3f}s: {mae:.2f}')
        checks+=1
    return dict(cues=len(ticks),boundarySamplesRequested=2*len(ticks),uniqueFramesChecked=checks,
                maxStripMeanAbsoluteError=max_mae,captionedFrames=sum(x>=0 for x in frames.values()))

def verify_export(output_file,source,plan,ass_file):
    new=probe(output_file)
    old=probe(source)
    signature=lambda m:[(x['start_time'],x['end_time'],x.get('tags',{})) for x in m.get('chapters',[])]
    if signature(new)!=signature(old):
        raise ValueError('Chapter times or titles changed')
    if any(s['codec_type']=='subtitle' for s in new['streams']):
        raise ValueError('Residual subtitle stream')
    if audio_hash(output_file)!=audio_hash(source):
        raise ValueError('Audio packet payload changed')
    if abs(float(new['format']['duration'])-float(old['format']['duration']))>.04:
        raise ValueError('Runtime changed')
    if frame_rate_kind(output_file,plan['fps'])!='CFR':
        raise ValueError('Output is not CFR at the planned frame rate')
    subprocess.run(['ffmpeg','-v','error','-xerror','-threads','4','-i',str(output_file),
                    '-map','0:a:0','-vn','-f','null','-'],check=True)
    frames=boundary_frames(output_file,source,plan,ass_file)
    return dict(chapters=len(new.get('chapters',[])),audioBitstreamIdentical=True,
                durationMatches=True,subtitleStreams=0,outputFrameRateKind='CFR',
                decodePassed=True,**frames)
