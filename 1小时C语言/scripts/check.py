"""Validate encoded timing, actual burned captions, chapter audio and strict decoding."""
import bisect,json,pathlib,subprocess,sys,wave,re
import numpy as np
from scipy.signal import correlate
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';DEL=ROOT/'out';FINAL=DEL/'一小时学习C语言_零基础.mp4'
T=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf-8'))
def probe(path,*args):return json.loads(subprocess.check_output(['ffprobe','-v','error',*args,'-of','json',str(path)],encoding='utf-8'))
def pcm(path,start,length):
    return np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-ss',str(start),'-i',str(path),'-t',str(length),'-vn','-ac','1','-ar','8000','-f','s16le','-']),dtype='<i2').astype(float)
def main():
    info=probe(FINAL,'-show_streams','-show_format','-show_chapters');v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
    assert(v['width'],v['height'],v['codec_name'],a['codec_name'],a['sample_rate'])==(1920,1080,'h264','aac','48000')
    assert abs(float(info['format']['duration'])-T['duration'])<.05
    assert len(info['chapters'])==len(T['chapters'])==12
    for actual,c in zip(info['chapters'],T['chapters']):
        assert abs(float(actual['start_time'])-c['startFrame']/30)<.002
        with wave.open(str(BUILD/(c['key']+'.wav')),'rb') as f:assert f.getnframes()==c['durationFrames']*1600 and f.getframerate()==48000
    packets=probe(FINAL,'-select_streams','v:0','-show_packets','-show_entries','packet=pts_time,duration_time')['packets']
    expected=[(c['startFrame']+e['frame'],e['frames']) for c in T['chapters'] for e in c['images']]
    assert len(packets)==len(expected),(len(packets),len(expected))
    for p,(frame,length) in zip(packets,expected):
        assert abs(float(p['pts_time'])*30-frame)<.002,(p,frame)
        assert abs(float(p['duration_time'])*30-length)<.002,(p,length)
    print('VIDEO_TIMING_PASSED',len(packets),flush=True)
    # Decode every distinct encoded image, including every subtitle change.
    command=['ffmpeg','-v','error','-i',str(FINAL),'-an','-vf','crop=1740:110:90:955,scale=580:37,format=gray','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','gray','-']
    proc=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE);size=580*37;index=0;bad=[]
    starts=[c['startFrame'] for c in T['captions']]
    while True:
        data=bytearray()
        while len(data)<size:
            block=proc.stdout.read(size-len(data))
            if not block:break
            data.extend(block)
        if not data:break
        assert len(data)==size and index<len(expected)
        frame=expected[index][0];j=bisect.bisect_right(starts,frame)-1
        wanted=j>=0 and frame<T['captions'][j]['endFrame'];pixels=int(np.count_nonzero(np.frombuffer(data,dtype=np.uint8)>170));visible=pixels>5
        if wanted!=visible:bad.append(dict(index=index,frame=frame,wanted=wanted,whitePixels=pixels))
        index+=1
    error=proc.stderr.read().decode(errors='replace');assert proc.wait()==0,error
    assert index==len(expected) and not bad,(index,bad[:12])
    print('BURNED_CAPTIONS_PASSED',index,flush=True)
    correlations=[]
    for c in T['chapters']:
        for position,start in [('start',2.0),('middle',c['durationFrames']/60),('end',c['durationFrames']/30-6)]:
            source=pcm(BUILD/(c['key']+'.wav'),start,3);actual=pcm(FINAL,c['startFrame']/30+start-.25,3.5)
            conv=correlate(actual,source,mode='valid',method='fft');best=int(np.argmax(conv));segment=actual[best:best+len(source)]
            score=float(np.dot(segment,source)/(np.linalg.norm(segment)*np.linalg.norm(source)));lag=best/8000-.25
            assert abs(lag)<.05 and score>.85,(c['key'],position,lag,score)
            correlations.append(dict(chapter=c['key'],position=position,lagSeconds=lag,correlation=score))
    print('AUDIO_SYNC_PASSED',len(correlations),'chapter waveform samples',flush=True)
    blocks=(DEL/'中文字幕.srt').read_text(encoding='utf-8-sig').strip().split('\n\n')
    assert len(blocks)==len(T['captions'])
    def srt_time(value):
        h,m,s,ms=map(int,re.split('[:,]',value));return h*3600+m*60+s+ms/1000
    for block,cap in zip(blocks,T['captions']):
        rows=block.splitlines();a,b=rows[1].split(' --> ')
        assert abs(srt_time(a)-cap['start'])<=.00051 and abs(srt_time(b)-cap['end'])<=.00051
        assert ''.join(rows[2:])==cap['text']
    for s in T['scenes']:
        meta=json.loads((ROOT/'public/audio'/(s['key']+'.json')).read_text(encoding='utf-8'))
        clean=lambda text:''.join(ch for ch in text if ch.isalnum())
        assert clean(''.join(x['text'] for x in meta['captions']))==clean(''.join(x['text'] for x in meta['words']))
        assert all(x['end']==meta['captions'][i+1]['start'] for i,x in enumerate(meta['captions'][:-1]))
        assert abs(meta['captions'][-1]['end']-meta['duration'])<.0001
        if s['kind']=='question':assert s['durationFrames']-s['leadFrames']-s['speechFrames']-s['sentenceTailFrames']==120
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(FINAL),'-map','0:v:0','-map','0:a:0','-f','null','-'],check=True,stdout=subprocess.DEVNULL)
    examples=json.loads((BUILD/'example-validation.json').read_text(encoding='utf-8'));properties=json.loads((BUILD/'property-validation.json').read_text(encoding='utf-8'))
    assert examples['allPassed'] and properties['allPassed']
    assert 3000<=T['duration']<=4200
    question_count=sum(s['kind']=='question' for s in T['scenes']);assert question_count==10 and sum(s['kind']=='answer' for s in T['scenes'])==10
    report=dict(allPassed=True,durationSeconds=T['duration'],chapters=len(T['chapters']),scenes=len(T['scenes']),compiledExamples=examples['compiledExamples'],runCases=examples['runCases'],propertyAssertionGroups=properties['assertionGroups'],encodedStates=len(packets),actualSubtitleStatesChecked=index,captions=len(T['captions']),questionHolds=question_count,strictDecodePassed=True,audioCorrelation=correlations,tempo=T['audioSettings']['wholeCourseTempo'],subtitleMethod='known-transcript acoustic alignment, waveform onset refinement; final burned presence checked on every encoded display state')
    (BUILD/'final-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');(DEL/'验收报告.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print('FINAL_VALIDATION_PASSED',flush=True)
if __name__=='__main__':main()
