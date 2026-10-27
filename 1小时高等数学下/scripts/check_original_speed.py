"""Compare all speech samples with an independent decode of the original 1.0x clips."""
import hashlib,json,pathlib,subprocess,wave
ROOT=pathlib.Path(__file__).resolve().parents[1];RATE=24000
def load(p):return json.loads(p.read_text(encoding='utf8'))
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pcm(p):
    with wave.open(str(p)) as w:
        assert w.getframerate()==RATE and w.getnchannels()==1 and w.getsampwidth()==2
        return w.readframes(w.getnframes())
def main():
    t=load(ROOT/'public/timeline.json');settings=load(ROOT/'build/audio-settings.json');assert settings['wholeCourseTempo']==1.0 and settings['automaticTempoAdjustment'] is False
    previous=ROOT/'build/revisions/before-normal-speed/baseline.json';baseline=load(previous) if previous.exists() else None
    if baseline:
        for name,path in [('courseSha256','public/course.json'),('drawingSha256','scripts/draw.py'),('topologySha256','content/visuals.py')]:assert baseline[name]==digest(ROOT/path),('Unrelated content changed',path)
    clips=[];pages=[]
    for s in t['scenes']:
        meta=load((ROOT/'public'/s['audio']).with_suffix('.json'));expected=bytearray()
        for i,p in enumerate(s['parts']):
            key=s['key']+f'-p{i:02}';source=ROOT/'public/audio_original'/(key+'.mp3');rawmeta=load(source.with_suffix('.json'))
            assert rawmeta['rate']==1.0 and rawmeta['narration']==p['text']
            if baseline:assert baseline['rawClips'][key]==digest(source)
            decoded=subprocess.check_output(['ffmpeg','-v','error','-i',str(source),'-ac','1','-ar',str(RATE),'-c:a','pcm_s16le','-f','s16le','-'])
            pre_pause=ROOT/'public/audio'/(key+'.scaled.wav')
            if pre_pause.exists():assert decoded==pcm(pre_pause),('Original speech was processed beyond direct decoding',key)
            aligned=load(ROOT/'build/alignment'/(key+'.json'));assert aligned['tempo']==1.0 and aligned['narration']==p['text']
            positions=[round(r['acousticSeconds']*RATE) for r in meta['pauseRefinements'] if r['part']==i];assert positions==sorted(set(positions));cursor=0
            assert abs(len(expected)/2/RATE-meta['parts'][i]['start'])<1/RATE
            for at in positions:
                assert cursor<=at*2<=len(decoded);expected.extend(decoded[cursor:at*2]);expected.extend(bytes(RATE//10*2));cursor=at*2
            expected.extend(decoded[cursor:]);assert abs(len(expected)/2/RATE-meta['parts'][i]['end'])<1/RATE
            if p.get('think'):expected.extend(bytes(RATE*4*2))
            if p['text'].endswith('。'):expected.extend(bytes(RATE//10*2))
            clips.append(dict(key=key,originalSha256=digest(source),decodedSamples=len(decoded)//2,tempo=1.0,unmodifiedSpeechSamples=True))
        target=ROOT/'public'/s['audio'];assert bytes(expected)==pcm(target),('Final page is not original speech plus agreed pauses',s['key'])
        pages.append(dict(key=s['key'],sha256=digest(target),allSamplesAccountedFor=True))
    report=dict(allPassed=True,wholeCourseTempo=1.0,automaticTempoAdjustment=False,rawClipsUnchanged=True if baseline else None,courseAndVisualsUnchanged=True if baseline else None,speechClipsCompared=len(clips),finalPagesCompared=len(pages),scope='final page PCM is sample-identical to an independent direct decode of original MP3 speech plus agreed 0.1-second sentence pauses (question thought holds are on the video timeline); existing pre-pause clip caches also compared; no TTS requests',timelineSha256=digest(ROOT/'public/timeline.json'),courseSha256=digest(ROOT/'public/course.json'),clips=clips,pages=pages)
    (ROOT/'build/original-speed-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k not in ['clips','pages']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
