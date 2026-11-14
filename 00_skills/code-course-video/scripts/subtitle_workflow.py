"""Offline, version-bound subtitles and CFR-before-ASS burn-in. Never calls TTS."""
import argparse
import json
import pathlib
import subprocess
import sys
import tempfile
from subtitle_sync import build_project, load, sha, validate, write_tracks, timing_metrics


def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-show_chapters','-of','json',str(path)],encoding='utf8'))


def verify_source(plan, video):
    info = probe(video)
    if abs(float(info['format']['duration'])-plan['duration']) > .08:
        raise ValueError('Selected video and timeline have different durations')
    actual = info.get('chapters', [])
    if len(actual) != len(plan['chapters']) or any(abs(float(a['start_time'])-b['startFrame']/plan['fps'])>.04 for a,b in zip(actual,plan['chapters'])):
        raise ValueError('Selected video and timeline have different chapter boundaries')
    v = next(s for s in info['streams'] if s['codec_type']=='video')
    if (v['width'],v['height']) != (1920,1080):
        raise ValueError('This course subtitle style requires a 1920x1080 master')
    return info


def build(project, video, out, **settings):
    plan = build_project(project, **settings)
    source_info=verify_source(plan,video)
    if any(x['codec_type']=='subtitle' for x in source_info['streams']):
        raise ValueError('Master contains a subtitle stream')
    from subtitle_verify import verify_pcm_placement, frame_rate_kind
    plan['sourcePCMCheck']=verify_pcm_placement(video,plan)
    plan['sourceFrameRateKind']=frame_rate_kind(video,plan['fps'])
    plan['sourceVideo'] = str(pathlib.Path(video).resolve())
    plan['sourceVideoSha256'] = sha(video)
    plan['rendererSha256'] = sha(__file__)
    verifier=pathlib.Path(__file__).with_name('subtitle_verify.py')
    plan['inputs'].append(dict(path=str(verifier.resolve()),sha256=sha(verifier)))
    plan['sourceMustBeSubtitleFree'] = True
    write_tracks(plan, out)
    return plan


def burn(plan_path, output, start=0., duration=None):
    plan_path = pathlib.Path(plan_path).resolve();plan = load(plan_path)
    source = pathlib.Path(plan['sourceVideo']);output = pathlib.Path(output).resolve()
    if plan.get('rendererSha256') != sha(__file__):
        raise ValueError('Subtitle renderer changed; rebuild the subtitle plan')
    if source == output:
        raise ValueError('Output must not overwrite the source master')
    if output.exists():
        raise ValueError('Output exists; choose a new revision filename')
    if sha(source) != plan['sourceVideoSha256']:
        raise ValueError('Video changed since subtitle build')
    for item in plan['inputs']:
        if sha(item['path']) != item['sha256']:
            raise ValueError('Subtitle inputs changed; rebuild before encoding: '+pathlib.Path(item['path']).name)
    validate(plan['cues'],plan['duration'])
    verify_source(plan,source)
    from subtitle_verify import verify_export
    regenerated=timing_metrics(plan['cues'])
    if regenerated!=plan['timing'] or regenerated['earlyCount']:
        raise ValueError('Subtitle ends before speech')
    length = min(plan['duration']-start, duration if duration is not None else plan['duration']-start)
    if start < 0 or length <= 0:
        raise ValueError('Invalid sample range')
    output.parent.mkdir(parents=True,exist_ok=True)
    # Generate ASS anew from the bound plan; an edited, stale .ass is never reused.
    with tempfile.TemporaryDirectory(prefix='subtitle-burn-') as temp:
        work = pathlib.Path(temp)
        sample = dict(plan,cues=[dict(c,start=max(0,c['start']-start),end=min(length,c['end']-start),
                                     spokenEnd=min(length,c['spokenEnd']-start))
                               for c in plan['cues'] if c['end']>start and c['start']<start+length])
        write_tracks(sample,work)
        full=start==0 and duration is None
        if full:
            for name in ('subtitles.ass','subtitles.srt'):
                if sha(work/name)!=sha(plan_path.parent/name):
                    raise ValueError(f'{name} differs from the plan')
        pending=output.with_name(output.stem+'.rendering.mp4')
        # Crucial: sample-and-hold to 30fps BEFORE ASS evaluates cue boundaries.
        # Output -r alone duplicates already-burned images and cannot fix stale text.
        args=['ffmpeg','-y','-v','warning']
        if start:args += ['-ss',str(start)]
        args += ['-i',str(source),'-map','0:v:0','-map','0:a:0','-map_metadata','0',
                 '-map_chapters','0' if start==0 and duration is None else '-1',
                 '-vf',f"fps=fps={plan['fps']}:round=up,settb=1/1000000,setpts=PTS+1,ass=filename=subtitles.ass,setpts=PTS-1",
                 '-fps_mode','cfr','-c:v','libx264','-preset','veryfast','-crf','19',
                 '-threads','8','-pix_fmt','yuv420p','-c:a','copy','-sn','-t',str(length),
                 '-movflags','+faststart',str(pending)]
        with output.with_suffix('.encode.log').open('w',encoding='utf8') as log:
            subprocess.run(args,cwd=work,stdout=log,stderr=subprocess.STDOUT,check=True)
        info=probe(pending)
        if abs(float(info['format']['duration'])-length) > .1:
            raise ValueError('Encoded subtitle video has unexpected duration')
        if full:
            checks=verify_export(pending,source,plan,work/'subtitles.ass')
        else:
            subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(pending),'-f','null','-'],check=True)
            checks=dict(decodePassed=True,scope='sample')
        receipt=dict(video=str(output),sha256=sha(pending),sourceSha256=plan['sourceVideoSha256'],
                     planSha256=sha(plan_path),ASSsha256=sha(work/'subtitles.ass'),
                     SRTsha256=sha(work/'subtitles.srt'),duration=length,rangeStart=start,
                     fps=plan['fps'],formula=plan['formula'],endPolicy=plan['endPolicy'],
                     tailSeconds=plan['tailSeconds'],timing=plan['timing'],
                     sourceFrameRateKind=plan['sourceFrameRateKind'],
                     filter='fps BEFORE ass; output CFR',audio='stream copy',checks=checks,
                     speechReview='ASR and manual samples are recorded separately')
        pending.replace(output)
        output.with_suffix('.receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
    return output


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    b=sub.add_parser('build');b.add_argument('--project',required=True);b.add_argument('--video',required=True,help='Existing subtitle-free master');b.add_argument('--out',required=True)
    e=sub.add_parser('burn');e.add_argument('--plan',required=True);e.add_argument('--output',required=True);e.add_argument('--start',type=float,default=0);e.add_argument('--duration',type=float)
    b.add_argument('--font-size',type=int,default=38)
    b.add_argument('--line-width',type=int,default=30)
    b.add_argument('--tail',type=float,default=.12)
    b.add_argument('--hold',action='store_true')
    a=p.parse_args()
    if a.command=='build':
        plan=build(a.project,a.video,a.out,font_size=a.font_size,max_chars=a.line_width,tail=a.tail,hold=a.hold);print('SUBTITLES_BUILT',len(plan['cues']),flush=True)
    else:print('BURN_DONE',burn(a.plan,a.output,a.start,a.duration),flush=True)


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf8');main()
