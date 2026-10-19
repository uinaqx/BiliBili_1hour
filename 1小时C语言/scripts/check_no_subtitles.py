"""Verify removed captions, identical audio payload and unchanged picture/chapters/timing."""
import concurrent.futures,json,pathlib,subprocess,sys
import numpy as np
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out';BUILD=ROOT/'build/no-subtitles'
OLD=DEL/'一小时学习C语言_零基础.mp4';NEW=DEL/'一小时学习C语言_零基础_无字幕.mp4'
def probe(path,*args):return json.loads(subprocess.check_output(['ffprobe','-v','error',*args,'-of','json',str(path)]))
def audio_hash(path):return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-map','0:a:0','-c','copy','-f','hash','-hash','sha256','-'],text=True).strip()
def main():
    before=probe(OLD,'-show_format','-show_streams','-show_chapters');after=probe(NEW,'-show_format','-show_streams','-show_chapters')
    assert abs(float(before['format']['duration'])-float(after['format']['duration']))<.001
    assert before['chapters']==after['chapters'] and len(after['chapters'])==12
    assert not any(s['codec_type']=='subtitle' for s in after['streams'])
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:hashes=list(pool.map(audio_hash,[OLD,NEW]))
    assert hashes[0]==hashes[1];print('AUDIO_BITSTREAM_IDENTICAL',flush=True)
    options=['-select_streams','v:0','-show_packets','-show_entries','packet=pts_time,duration_time']
    a=probe(OLD,*options)['packets'];b=probe(NEW,*options)['packets'];assert a==b
    expected=len(a);print('UNCHANGED_VIDEO_TIMING_AND_CHAPTERS',expected,flush=True)
    command=['ffmpeg','-v','error','-xerror','-i',str(NEW),'-an','-vf','crop=1740:110:90:955,scale=580:37,format=gray','-fps_mode','passthrough','-f','rawvideo','-pix_fmt','gray','-']
    proc=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE);size=580*37;count=0;brightest=0
    while True:
        data=bytearray()
        while len(data)<size:
            block=proc.stdout.read(size-len(data))
            if not block:break
            data.extend(block)
        if not data:break
        assert len(data)==size
        value=int(np.max(np.frombuffer(data,dtype=np.uint8)));brightest=max(brightest,value);assert value<70,(count,value)
        count+=1
    error=proc.stderr.read();assert proc.wait()==0,error
    assert count==expected;print('NO_CAPTIONS_IN_ALL_DISPLAY_STATES',count,flush=True)
    # Compare every decoded frame above the dedicated caption strip. Framesync
    # sees identical PTS in both inputs, so moving highlights remain aligned.
    log=BUILD/'picture-compare.log';stats=BUILD/'picture-psnr.txt'
    with log.open('w',encoding='utf-8') as f:
        result=subprocess.run(['ffmpeg','-y','-hide_banner','-i',str(OLD),'-i',str(NEW),'-filter_complex',"[0:v]crop=1920:934:0:0,scale=480:234[a];[1:v]crop=1920:934:0:0,scale=480:234[b];[a][b]psnr=stats_file=build/no-subtitles/picture-psnr.txt",'-an','-fps_mode','passthrough','-f','null','-'],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    assert result.returncode==0
    values=[dict(token.split(':',1) for token in line.split()) for line in stats.read_text().splitlines()]
    assert len(values)==expected
    worst=max(float(row['mse_avg']) for row in values);assert worst<4,worst
    print('PICTURE_CONTENT_UNCHANGED',len(values),'frames; max MSE',worst,flush=True)
    subprocess.run(['ffmpeg','-v','error','-xerror','-i',str(NEW),'-map','0:v:0','-map','0:a:0','-f','null','-'],check=True,stdout=subprocess.DEVNULL)
    report=dict(allPassed=True,durationSeconds=float(after['format']['duration']),chapters=12,encodedDisplayStates=count,noBurnedCaptions=True,audioBitstreamHash=hashes[0],audioBitstreamIdentical=True,videoTimingIdentical=True,pictureFramesCompared=len(values),pictureMaxMseAboveCaptionStrip=worst,subtitleStripMaxPixel=brightest,strictDecodePassed=True)
    (BUILD/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('NO_SUBTITLES_VALIDATION_PASSED',flush=True)
if __name__=='__main__':main()
