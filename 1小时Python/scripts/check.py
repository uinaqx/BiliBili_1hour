"""Check final timing, empty subtitle area, chapter audio and full strict decode."""
import json,pathlib,subprocess,sys,wave
import numpy as np
from scipy.signal import correlate
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out';FINAL=DEL/'一小时学习Python_零基础.mp4'
T=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf-8'))
def probe(path,*args):return json.loads(subprocess.check_output(['ffprobe','-v','error',*args,'-of','json',str(path)],encoding='utf-8'))
def pcm(path,start,length):return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-i',str(path),'-t',str(length),'-vn','-ac','1','-ar','8000','-f','s16le','-']),dtype='<i2').astype(float)
def main():
    info=probe(FINAL,'-show_streams','-show_format','-show_chapters');v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
    assert(v['width'],v['height'],v['codec_name'],a['codec_name'],a['sample_rate'])==(1920,1080,'h264','aac','48000')
    assert not any(s['codec_type']=='subtitle' for s in info['streams']) and not T['captions'] and all(not s['captions'] for s in T['scenes'])
    assert abs(float(info['format']['duration'])-T['duration'])<.05
    assert len(info['chapters'])==len(T['chapters'])==13
    for actual,c in zip(info['chapters'],T['chapters']):
        assert abs(float(actual['start_time'])-c['startFrame']/30)<.002
        assert c['title'] in actual['tags']['title']
        with wave.open(str(BUILD/(c['key']+'.wav')),'rb') as f:assert f.getnframes()==c['durationFrames']*1600 and f.getframerate()==48000
    packets=probe(FINAL,'-select_streams','v:0','-show_packets','-show_entries','packet=pts_time,duration_time')['packets'];expected=[(c['startFrame']+e['frame'],e['frames']) for c in T['chapters'] for e in c['images']]
    assert len(packets)==len(expected),(len(packets),len(expected))
    for p,(frame,length) in zip(packets,expected):
        assert abs(float(p['pts_time'])*30-frame)<.002,(p,frame)
        assert abs(float(p['duration_time'])*30-length)<.002,(p,length)
    print('VIDEO_TIMING_PASSED',len(packets),flush=True)
    regions='split=2[a][b];[a]crop=1740:110:90:955,scale=580:37[a1];[b]crop=450:26:300:912,scale=580:37[b1];[a1][b1]vstack,format=gray'
    command=['ffmpeg','-v','error','-i',str(FINAL),'-an','-vf',regions,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','gray','-']
    proc=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE);size=580*74;index=0
    while True:
        data=bytearray()
        while len(data)<size:
            block=proc.stdout.read(size-len(data))
            if not block:break
            data.extend(block)
        if not data:break
        assert len(data)==size
        pixels=int(np.count_nonzero(np.frombuffer(data,dtype=np.uint8)>80));assert pixels==0,('Unexpected subtitle or removed-footer content',index,pixels)
        index+=1
    error=proc.stderr.read().decode(errors='replace');assert proc.wait()==0,error;assert index==len(expected)
    print('NO_SUBTITLES_AND_REMOVED_FOOTER_CONFIRMED',index,flush=True)
    correlations=[]
    for c in T['chapters']:
        for position,start in [('start',2.0),('middle',c['durationFrames']/60),('end',c['durationFrames']/30-6)]:
            source=pcm(BUILD/(c['key']+'.wav'),start,3);actual=pcm(FINAL,c['startFrame']/30+start-.25,3.5)
            conv=correlate(actual,source,mode='valid',method='fft');best=int(np.argmax(conv));segment=actual[best:best+len(source)]
            score=float(np.dot(segment,source)/(np.linalg.norm(segment)*np.linalg.norm(source)));lag=best/8000-.25
            assert abs(lag)<.05 and score>.85,(c['key'],position,lag,score)
            correlations.append(dict(chapter=c['key'],position=position,lagSeconds=lag,correlation=score))
    print('AUDIO_SYNC_PASSED',len(correlations),flush=True)
    pause_count=0
    for s in T['scenes']:
        meta=json.loads((ROOT/'public/audio'/(s['key']+'.json')).read_text(encoding='utf-8'))
        with wave.open(str(ROOT/'public'/s['audio']),'rb') as f:
            assert f.getnframes()==meta['samples'];samples=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2')
        for i,position in enumerate(meta['insertedPauseSamples']):
            start=position+i*2400;assert len(samples[start:start+2400])==2400 and not np.any(samples[start:start+2400])
            pause_count+=1
        if s['kind']=='question':assert s['durationFrames']-s['leadFrames']-s['speechFrames']-s['sentenceTailFrames']==round(s['hold']*T['fps'])==120
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(FINAL),'-map','0:v:0','-map','0:a:0','-f','null','-'],check=True,stdout=subprocess.DEVNULL)
    examples=json.loads((BUILD/'example-validation.json').read_text(encoding='utf-8'));properties=json.loads((BUILD/'property-validation.json').read_text(encoding='utf-8'));assert examples['allPassed'] and properties['allPassed']
    questions=sum(s['kind']=='question' for s in T['scenes']);assert questions==11 and sum(s['kind']=='answer' for s in T['scenes'])==11
    assert 3000<=T['duration']<=4200
    report=dict(allPassed=True,durationSeconds=T['duration'],chapters=len(T['chapters']),scenes=len(T['scenes']),exampleCases=examples['cases'],normalPrograms=examples['normalPrograms'],expectedSyntaxErrors=examples['expectedSyntaxErrors'],expectedRuntimeExceptions=examples['expectedRuntimeExceptions'],runCases=examples['runCases'],propertyAssertionGroups=properties['assertionGroups'],encodedStates=len(packets),emptySubtitleAreaStatesChecked=index,subtitles=False,questionHolds=questions,verifiedExtraSentencePauses=pause_count,sentencePauseSeconds=.1,strictDecodePassed=True,audioCorrelation=correlations,tempo=T['audioSettings']['wholeCourseTempo'])
    report['removedFooterTextStatesChecked']=index
    for target in (BUILD/'final-validation.json',DEL/'验收报告.json'):target.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('FINAL_VALIDATION_PASSED',flush=True)
if __name__=='__main__':main()
