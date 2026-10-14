"""Render changing Remotion frames + holds; encode captions and mux exact audio."""
import argparse, concurrent.futures, hashlib, json, pathlib, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1]; BUILD=ROOT/'build'; DEL=ROOT/'out'; FPS=30
T=json.loads((ROOT/'public'/'timeline.json').read_text(encoding='utf-8'))
def run(args,log):
    with log.open('w',encoding='utf-8') as f:
        result=subprocess.run(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(log.read_text(encoding='utf-8',errors='replace')[-2500:])
def write_images(events,path):
    lines=['ffconcat version 1.0']
    for item in events:
        image=(ROOT/'public'/item['path']).resolve()
        if not image.exists():raise FileNotFoundError(image)
        lines.extend(["file '"+image.as_posix().replace("'","'\\''")+"'",'option framerate 30',f"duration {item['frames']/FPS:.9f}"])
    lines.append("file '"+(ROOT/'public'/events[-1]['path']).resolve().as_posix()+"'")
    lines.append('option framerate 30')
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
def audio_for(scenes,path,total):
    samples=round(total*48000)
    fingerprint=hashlib.sha256(json.dumps([total,[(s['key'],s['durationFrames'],json.loads((ROOT/'public'/'audio'/(s['key']+'.json')).read_text(encoding='utf-8'))['fingerprint']) for s in scenes],'loudnorm I=-16 TP=-1.5 LRA=11; 48kHz mono; pad to exact samples v2'],ensure_ascii=False).encode()).hexdigest()
    cache=path.with_suffix('.wav.json')
    if path.exists() and cache.exists() and json.loads(cache.read_text()).get('hash')==fingerprint:return
    args=['ffmpeg','-y','-hide_banner','-loglevel','warning']
    filters=[]
    for i,s in enumerate(scenes):
        args.extend(['-i',str(ROOT/'public'/s['audio'])])
        filters.append(f"[{i}:a]aresample=48000,adelay=400:all=1,apad,atrim=duration={s['durationFrames']/FPS:.9f},asetpts=PTS-STARTPTS[a{i}]")
    filters.append(''.join(f'[a{i}]' for i in range(len(scenes)))+f'concat=n={len(scenes)}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,apad=whole_len={samples},atrim=end_sample={samples},asetpts=N/SR/TB[out]')
    args.extend(['-filter_complex',';'.join(filters),'-map','[out]','-c:a','pcm_s16le','-ac','1',str(path)])
    run(args,BUILD/(path.stem+'-audio.log'))
    cache.write_text(json.dumps({'hash':fingerprint}),encoding='utf-8')
def chapter(c):
    key=c['key']; seconds=c['durationFrames']/FPS
    audio=BUILD/f'{key}.wav'; video=BUILD/f'{key}.mp4'; concat=BUILD/f'{key}.ffconcat'
    audio_for(c['scenes'],audio,seconds)
    cache=BUILD/f'{key}-render.json'
    still_hash=json.loads((BUILD/'still-cache.json').read_text(encoding='utf-8'))
    fingerprint=hashlib.sha256(json.dumps([c,[(i['path'],still_hash.get(i['path'])) for i in c['images']],(BUILD/f'{key}.ass').read_text(encoding='utf-8-sig'),pathlib.Path(__file__).read_text(encoding='utf-8')],ensure_ascii=False).encode()).hexdigest()
    if video.exists() and cache.exists() and json.loads(cache.read_text()).get('hash')==fingerprint:
        print(f'CHAPTER {key}: cached',flush=True);return
    write_images(c['images'],concat)
    args=['ffmpeg','-y','-hide_banner','-loglevel','warning','-f','concat','-safe','0','-i',str(concat),'-vf',f'fps=30,ass=build/{key}.ass','-t',f'{seconds:.9f}','-r','30','-fps_mode','cfr','-an','-c:v','libx264','-preset','fast','-tune','stillimage','-crf','20','-threads','4','-pix_fmt','yuv420p','-movflags','+faststart',str(video)]
    run(args,BUILD/f'{key}-video.log')
    cache.write_text(json.dumps({'hash':fingerprint}),encoding='utf-8')
    print(f'CHAPTER {key}: done ({seconds:.1f}s)',flush=True)
def concat_list(items,path):
    lines=['ffconcat version 1.0']
    for name,seconds in items:lines.extend(["file '"+(BUILD/name).resolve().as_posix()+"'",f'duration {seconds:.9f}'])
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
def ass_time(t):
    cs=round(t*100);h,cs=divmod(cs,360000);m,cs=divmod(cs,6000);s,cs=divmod(cs,100)
    return f'{h}:{m:02}:{s:02}.{cs:02}'
def preview():
    limit=90*FPS; events=[]; scenes=[]; caps=[]
    for c in T['chapters']:
        position=c['startFrame']
        for item in c['images']:
            if position>=limit:break
            events.append({**item,'frames':min(item['frames'],limit-position)});position+=item['frames']
        for s in c['scenes']:
            if s['startFrame']<limit:scenes.append(s)
        for cap in c['captions']:
            offset=c['startFrame']/FPS
            if cap['start']+offset<90:caps.append({**cap,'start':cap['start']+offset,'end':min(90,cap['end']+offset)})
    audio=BUILD/'preview.wav';audio_for(scenes,audio,90)
    images=BUILD/'preview.ffconcat';write_images(events,images)
    header=(BUILD/'00.ass').read_text(encoding='utf-8-sig').split('Dialogue:')[0]
    ass=header+'\n'.join(f"Dialogue: 0,{ass_time(c['start'])},{ass_time(c['end'])},Default,,0,0,0,,{c['text'].replace('{','').replace('}','')}" for c in caps)+'\n'
    (BUILD/'preview.ass').write_text(ass,encoding='utf-8-sig')
    run(['ffmpeg','-y','-hide_banner','-loglevel','warning','-f','concat','-safe','0','-i',str(images),'-i',str(audio),'-vf','fps=30,ass=build/preview.ass','-map','0:v','-map','1:a','-t','90','-r','30','-fps_mode','cfr','-c:v','libx264','-preset','fast','-tune','stillimage','-crf','20','-threads','4','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-movflags','+faststart',str(DEL/'90秒试片.mp4')],BUILD/'preview-render.log')
    print('PREVIEW_DONE',flush=True)
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');parser.add_argument('--audio-only',action='store_true');parser.add_argument('--workers',type=int,default=2);parser.add_argument('--chapters',help='Comma-separated chapter keys to render; reuse other chapter videos');args=parser.parse_args()
    if T.get('previewOnly'):parser.error('Studio preview has estimated timing and no audio. Generate your own audio and run timeline.py before exporting a movie.')
    if args.preview:preview();return
    selected=T['chapters']
    if args.chapters:
        keys=set(args.chapters.split(','))
        unknown=keys-{c['key'] for c in T['chapters']}
        if unknown:parser.error('Unknown chapter keys: '+','.join(sorted(unknown)))
        selected=[c for c in T['chapters'] if c['key'] in keys]
        for c in T['chapters']:
            if c['key'] not in keys:
                for suffix in ('.mp4','.wav'):
                    if not (BUILD/(c['key']+suffix)).exists():raise FileNotFoundError('Render all chapters before using --chapters')
    def audio_chapter(c):
        if not (BUILD/(c['key']+'.mp4')).exists():raise FileNotFoundError('Render chapter video before --audio-only')
        audio_for(c['scenes'],BUILD/(c['key']+'.wav'),c['durationFrames']/FPS)
        print(f'CHAPTER_AUDIO {c["key"]}: done',flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:list(pool.map(audio_chapter if args.audio_only else chapter,selected))
    videos=BUILD/'videos.ffconcat'; audios=BUILD/'audios.ffconcat'
    concat_list([(c['key']+'.mp4',c['durationFrames']/FPS) for c in T['chapters']],videos)
    concat_list([(c['key']+'.wav',c['durationFrames']/FPS) for c in T['chapters']],audios)
    final=DEL/'Rust基础一小时学习_初学者版.mp4'
    run(['ffmpeg','-y','-hide_banner','-loglevel','warning','-f','concat','-safe','0','-i',str(videos),'-f','concat','-safe','0','-i',str(audios),'-i',str(BUILD/'chapters.ffmetadata'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-c:a','aac','-b:a','128k','-ar','48000','-ac','1','-t',f"{T['duration']:.9f}",'-movflags','+faststart',str(final)],BUILD/'final-mux.log')
    print(f'FINAL_DONE {final} ({T["duration"]:.3f}s)',flush=True)
if __name__=='__main__':main()
