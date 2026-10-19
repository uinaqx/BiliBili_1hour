"""Uniformly accelerate the finished movie, preserving video payload and pitch."""
import hashlib,json,pathlib,re,subprocess,sys
from fractions import Fraction
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCE=ROOT/'out'
OUT=SOURCE/'正常语速版';OUT.mkdir(exist_ok=True)
BUILD=ROOT/'production/build/speedup-1.1';BUILD.mkdir(exist_ok=True)
MOVIE=SOURCE/'两小时学习计算机组成原理.mp4'
TARGET=OUT/'计算机组成原理_正常语速版.mp4'
SPEED=Fraction(11,10)

def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_chapters','-show_format','-of','json',str(path)]))
def run(args,name):
    with (BUILD/name).open('w',encoding='utf-8') as f:r=subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','warning',*args],stdout=f,stderr=subprocess.STDOUT)
    if r.returncode:raise RuntimeError((BUILD/name).read_text(encoding='utf-8',errors='replace')[-3000:])
def clock(ms,sep=','):
    h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02}{sep}{ms:03}'
def srt_ms(text):
    h,m,s,ms=map(int,re.split('[:,]',text));return ((h*60+m)*60+s)*1000+ms
def packets(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_packets','-show_entries','packet=pts,dts,duration,data_hash','-show_data_hash','sha256','-of','json',str(path)]))['packets']

def main():
    source=probe(MOVIE);v=next(s for s in source['streams'] if s['codec_type']=='video')
    original_tb=Fraction(v['time_base']);new_tb=original_tb/SPEED
    expected=Fraction(source['format']['duration'])/SPEED
    source_hash=hashlib.sha256(MOVIE.read_bytes()).hexdigest()
    retimed=BUILD/'retimed-video.mp4'
    print('RETIMING_VIDEO',flush=True)
    run(['-i',str(MOVIE),'-map','0:v:0','-an','-map_metadata','-1','-map_chapters','-1','-c:v','copy','-bsf:v',f'setts=ts=TS:duration=DURATION:time_base={new_tb.numerator}/{new_tb.denominator}','-video_track_timescale',str(new_tb.denominator),'-movflags','+faststart',str(retimed)],'video-retime.log')
    first=probe(retimed);rv=next(s for s in first['streams'] if s['codec_type']=='video')
    assert abs(float(rv['duration'])-float(expected))<.01,(rv['duration'],float(expected))
    assert rv['nb_frames']==v['nb_frames']
    metadata=[';FFMETADATA1','title=计算机组成原理：正常语速版','artist=中文计算机课程','comment=Uniform 1.10x speed; pitch-preserved audio; original video payload retained']
    for c in source['chapters']:
        start=round(Fraction(c['start_time'])/SPEED/new_tb);end=round(Fraction(c['end_time'])/SPEED/new_tb)
        metadata.extend(['[CHAPTER]',f'TIMEBASE={new_tb.numerator}/{new_tb.denominator}',f'START={start}',f'END={end}',"title="+c['tags']['title']])
    meta=BUILD/'chapters.ffmetadata';meta.write_text('\n'.join(metadata)+'\n',encoding='utf-8')
    print('ACCELERATING_AUDIO_AND_MUXING',float(expected),'seconds',flush=True)
    staged=OUT/'计算机组成原理_正常语速版.rendering.mp4'
    run(['-i',str(retimed),'-i',str(MOVIE),'-f','ffmetadata','-i',str(meta),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-af','atempo=1.1,asetpts=N/SR/TB,apad','-t',f'{float(expected):.9f}','-c:a','aac','-b:a','128k','-ar','48000','-ac','1','-video_track_timescale',str(new_tb.denominator),'-movflags','+faststart',str(staged)],'audio-mux.log')
    staged.replace(TARGET)
    old_srt=(SOURCE/'中文字幕.srt').read_text(encoding='utf-8-sig')
    pattern=r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})'
    new_srt=re.sub(pattern,lambda m:clock(round(Fraction(srt_ms(m[1]))/SPEED))+' --> '+clock(round(Fraction(srt_ms(m[2]))/SPEED)),old_srt)
    (OUT/'中文字幕.srt').write_text(new_srt,encoding='utf-8-sig')
    rows=['# 计算机组成原理：正常语速版章节目录','',f'原片整体加速 1.10 倍，时长约 {clock(round(expected*1000))}。','', '| 起点 | 章节 |','|---|---|']
    for c in source['chapters']:rows.append(f"| {clock(round(Fraction(c['start_time'])*1000/SPEED)).split(',')[0]} | {c['tags']['title']} |")
    (OUT/'章节目录.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    manuscript=(SOURCE/'完整讲稿.md').read_text(encoding='utf-8')
    def heading(m):
        h,minutes,s=map(int,m[2].split(':'));new=round(Fraction((h*3600+minutes*60+s)*1000)/SPEED)
        return m[1]+clock(new).split(',')[0]
    manuscript=re.sub(r'(?m)^(#{2,3} )(\d{2}:\d{2}:\d{2})',heading,manuscript)
    manuscript=manuscript.replace('读题结束后 6 秒无新旁白','读题结束后约 5.45 秒无新旁白')
    manuscript=manuscript.replace('# 两小时学习计算机组成原理：配音分段讲稿','# 计算机组成原理：正常语速版讲稿',1)
    (OUT/'完整讲稿.md').write_text(manuscript,encoding='utf-8')
    (OUT/'调整说明.md').write_text('# 正常语速版\n\n原片整体加速至 1.10 倍，声音保持原音调，视频不重新绘制或压缩。字幕、章节标记、章节目录及讲稿中的时间同步缩短。所有原始显示状态和内容完整保留；原有六秒思考段加速后约为 5.45 秒。\n\n画面内原有的课程时间码和文字保持原样，可用于对应原稿；播放器章节和本目录中的字幕、讲稿时间对应加速版。原两小时版保留在上一级目录。\n',encoding='utf-8')
    print('VERIFYING',flush=True)
    final=probe(TARGET);fv=next(s for s in final['streams'] if s['codec_type']=='video');fa=next(s for s in final['streams'] if s['codec_type']=='audio')
    assert max(abs(float(final['format']['duration'])-float(expected)),abs(float(fv['duration'])-float(expected)),abs(float(fa['duration'])-float(expected)))<.01
    assert fv['codec_name']=='h264' and (fv['width'],fv['height'])==(1920,1080)
    assert fa['codec_name']=='aac' and fa['sample_rate']=='48000'
    original=packets(MOVIE);updated=packets(TARGET);target_tb=Fraction(fv['time_base'])
    assert len(original)==len(updated)==int(v['nb_frames'])
    assert all(a['data_hash']==b['data_hash'] for a,b in zip(original,updated)),'Video picture payload changed'
    errors=[abs(Fraction(a['pts'])*original_tb/SPEED-Fraction(b['pts'])*target_tb) for a,b in zip(original,updated)]
    assert max(errors)<=target_tb
    assert len(final['chapters'])==len(source['chapters'])==11
    assert all(abs(Fraction(a['start_time'])/SPEED-Fraction(b['start_time']))<Fraction(1,1000) and a['tags']['title']==b['tags']['title'] for a,b in zip(source['chapters'],final['chapters']))
    assert len(re.findall(pattern,new_srt))==len(re.findall(pattern,old_srt))==2014
    assert hashlib.sha256(MOVIE.read_bytes()).hexdigest()==source_hash,'Original movie was modified'
    print('FULL_DECODE_START',flush=True)
    with (BUILD/'decode.log').open('w',encoding='utf-8') as f:
        result=subprocess.run(['ffmpeg','-hide_banner','-nostats','-xerror','-i',str(TARGET),'-af','volumedetect','-f','null','-'],stdout=f,stderr=subprocess.STDOUT)
    assert result.returncode==0,'Full decode failed'
    log=(BUILD/'decode.log').read_text(encoding='utf-8',errors='replace')
    assert not re.search(r'corrupt decoded|Error while|Invalid data|non.monoton',log,re.I)
    mean=float(re.search(r'mean_volume: (-?[\d.]+)',log).group(1));peak=float(re.search(r'max_volume: (-?[\d.]+)',log).group(1))
    report=dict(speed=float(SPEED),duration=final['format']['duration'],videoFrames=len(updated),videoPacketHashesIdentical=True,maxVideoTimestampErrorSeconds=float(max(errors)),chapters=11,subtitles=2014,originalUnchanged=True,fullDecodePassed=True,meanVolumeDbfs=mean,maxVolumeDbfs=peak)
    (BUILD/'acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'检查结果.md').write_text(f'# 正常语速版检查结果\n\n- 总时长：{clock(round(expected*1000))}\n- 加速比例：1.10 倍；音调保留\n- {len(updated)} 个视频显示状态完整保留，逐包 SHA-256 与原片一致\n- 全部显示时间按相同比例缩短，最大视频时间戳误差 {float(max(errors)):.8f} 秒\n- 11 个章节标记、2014 条字幕及讲稿时间已同步调整\n- 完整音视频解码通过；平均音量 {mean:.1f}dBFS，峰值 {peak:.1f}dBFS\n- 原两小时视频文件未改动\n',encoding='utf-8')
    print('SPEEDUP_DONE',str(TARGET),json.dumps(report,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
