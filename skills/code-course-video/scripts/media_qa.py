"""Portable FFmpeg QA and presentation-time frame extraction. No online services."""
import argparse,bisect,hashlib,json,math,pathlib,subprocess,sys
if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')

def dump(path,data):
    path=pathlib.Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def probe(path,frames=False):
    options=['-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time,pts_time'] if frames else ['-show_format','-show_streams','-show_chapters']
    return json.loads(subprocess.check_output(['ffprobe','-v','error',*options,'-of','json',str(path)]))
def sha(path):
    h=hashlib.sha256()
    with pathlib.Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(8*1024*1024),b''):h.update(chunk)
    return h.hexdigest()
def audio_hash(path):
    return subprocess.check_output(['ffmpeg','-nostdin','-v','error','-i',str(path),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
def chapter_signature(meta):
    return [(round(float(c['start_time']),6),round(float(c['end_time']),6),c.get('tags',{})) for c in meta.get('chapters',[])]

def verify(path,reference=None,preserve_audio=False,decode=False,timeline=None,tolerance=.04):
    path=pathlib.Path(path);meta=probe(path);streams=meta['streams']
    video=next((s for s in streams if s['codec_type']=='video'),None)
    audio=next((s for s in streams if s['codec_type']=='audio'),None)
    checks={'hasVideo':video is not None,'hasAudio':audio is not None,'positiveDuration':float(meta['format'].get('duration',0))>0}
    report={'video':str(path.resolve()),'videoSha256':sha(path),'durationSeconds':float(meta['format'].get('duration',0)),
        'videoCodec':video.get('codec_name') if video else None,'width':video.get('width') if video else None,'height':video.get('height') if video else None,
        'subtitleStreams':sum(s['codec_type']=='subtitle' for s in streams),'chapterCount':len(meta.get('chapters',[])),
        'checks':checks,'notChecked':['spoken-reference semantics','burned-in subtitle visibility','subtitle-to-speech timing','highlight pixels']}
    if reference:
        old=probe(reference);old_video=next((s for s in old['streams'] if s['codec_type']=='video'),{})
        delta=abs(report['durationSeconds']-float(old['format']['duration']));report['referenceDurationDeltaSeconds']=delta
        checks['durationWithinTolerance']=delta<=tolerance
        checks['chapterTimesAndTagsMatch']=chapter_signature(old)==chapter_signature(meta)
        checks['dimensionsMatchReference']=video is not None and (video['width'],video['height'])==(old_video.get('width'),old_video.get('height'))
    if preserve_audio:
        if not reference:raise ValueError('--preserve-audio requires --reference')
        checks['audioBitstreamIdentical']=audio_hash(path)==audio_hash(reference)
    if decode:
        r=subprocess.run(['ffmpeg','-nostdin','-v','error','-xerror','-threads','2','-i',str(path),'-map','0:v:0','-map','0:a:0','-f','null','-'],capture_output=True)
        checks['strictDecodePassed']=r.returncode==0
        if r.returncode:report['decodeError']=r.stderr.decode('utf-8',errors='replace')[-2000:]
    else:report['notChecked'].append('full decode')
    if timeline:report['timelineSha256']=sha(timeline)
    report['allPerformedChecksPassed']=all(checks.values())
    return report

def extract(path,times,dest):
    if not times or any(not math.isfinite(t) or t<0 for t in times):raise ValueError('times must be nonnegative finite seconds')
    path=pathlib.Path(path);dest=pathlib.Path(dest)
    meta=probe(path);duration=float(meta['format']['duration'])
    frames=probe(path,True)['frames'];pts=[float(f.get('best_effort_timestamp_time',f.get('pts_time'))) for f in frames]
    if not pts or pts!=sorted(pts):raise ValueError('presentation timestamps missing or unordered')
    requests=[]
    for sec in times:
        if sec<pts[0] or sec>=duration:raise ValueError('requested time is outside displayed video')
        index=bisect.bisect_right(pts,sec+1e-9)-1
        requests.append({'requestedSeconds':sec,'frameIndex':index,'displayPtsSeconds':pts[index]})
    chosen=sorted(set(r['frameIndex'] for r in requests));expr='+'.join(f'eq(n,{n})' for n in chosen).replace(',',r'\,')
    dest.mkdir(parents=True,exist_ok=True)
    # Refuse to mix new evidence with a previous unrelated extraction.
    if list(dest.glob('frame-*.png')):raise ValueError('output already has extracted frames; choose a fresh evidence directory')
    subprocess.run(['ffmpeg','-nostdin','-y','-v','error','-threads','2','-i',str(path),'-an','-vf','select='+expr,'-fps_mode','passthrough',str(dest/'frame-%05d.png')],check=True)
    images=sorted(dest.glob('frame-*.png'))
    if len(images)!=len(chosen):raise ValueError('unexpected decoded frame count')
    lookup=dict(zip(chosen,images))
    for row in requests:row['image']=str(lookup[row['frameIndex']].resolve())
    result={'video':str(path.resolve()),'selection':'last displayed frame with PTS <= requested time','frames':requests}
    dump(dest/'positions.json',result);return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('extract');p.add_argument('video');p.add_argument('--times',required=True);p.add_argument('--output',required=True)
    p=sub.add_parser('verify');p.add_argument('video');p.add_argument('--reference');p.add_argument('--preserve-audio',action='store_true');p.add_argument('--decode',action='store_true');p.add_argument('--timeline');p.add_argument('--duration-tolerance',type=float,default=.04);p.add_argument('--output',required=True)
    args=parser.parse_args()
    if args.mode=='extract':result=extract(args.video,[float(x) for x in args.times.split(',')],args.output);success=True
    else:
        result=verify(args.video,args.reference,args.preserve_audio,args.decode,args.timeline,args.duration_tolerance)
        dump(args.output,result);success=result['allPerformedChecksPassed']
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0 if success else 1
if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,subprocess.CalledProcessError) as exc:print('QA_ERROR:',exc,file=sys.stderr);sys.exit(2)
