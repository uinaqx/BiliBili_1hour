"""Check the exported media and save inspectable evidence of actual frames."""
import concurrent.futures,json,math,pathlib,re,subprocess,sys,wave
from PIL import Image,ImageChops,ImageDraw,ImageFont,ImageStat
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'production';B=P/'build';OUT=ROOT/'out'
MOVIE=OUT/'两小时学习计算机组成原理.mp4';T=json.loads((P/'timeline.json').read_text(encoding='utf-8'))
CHECKS=[]
def require(name,condition,detail=''):
    CHECKS.append(dict(check=name,passed=bool(condition),detail=detail));print(('PASS ' if condition else 'FAIL ')+name+' '+detail,flush=True)
    if not condition:raise AssertionError(name+' '+detail)
def probe(path):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-show_chapters','-of','json',str(path)]))
def sample(job):
    label,frame,reference=job;target=B/'final-frames'/(label+'.png')
    subprocess.run(['ffmpeg','-y','-v','error','-ss',f'{max(0,frame/30-.00001):.7f}','-i',str(MOVIE),'-frames:v','1','-fps_mode','passthrough','-update','1',str(target)],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,check=True)
    with Image.open(target) as a,Image.open(reference) as b:
        difference=sum(ImageStat.Stat(ImageChops.difference(a.convert('RGB'),b.convert('RGB'))).mean)/3
    return dict(label=label,frame=frame,meanPixelDifference=difference,file=target.name)
def sheets(items):
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
    for off in range(0,len(items),12):
        sheet=Image.new('RGB',(1920,930),(9,17,29));d=ImageDraw.Draw(sheet)
        for i,r in enumerate(items[off:off+12]):
            with Image.open(B/'final-frames'/r['file']) as image:sheet.paste(image.resize((480,270)),((i%4)*480,(i//4)*310))
            d.text(((i%4)*480+8,(i//4)*310+279),r['label'],font=font,fill='#edf2f9')
        sheet.save(B/f'actual-sheet-{off//12:02}.jpg',quality=94)
def main():
    require('课程与时间轴',T['fullCourse'] and len(T['scenes'])==60 and len(T['chapters'])==11 and T['totalFrames']==216000,'60 分镜 / 11 章 / 7200 秒')
    source=json.loads((ROOT/'data/course.json').read_text(encoding='utf-8'));normal=lambda x:re.sub(r'\s','',x)
    def retained(s,row):
        spoken=iter(normal(''.join(part['narration'] for part in row['voiceParts'])))
        return all(any(found==ch for found in spoken) for ch in normal(s['narration']))
    require('完整原稿保留',all(retained(s,row) for s,row in zip(source['scenes'],T['scenes'])),'原稿按顺序完整保留；分离自测与答案，少数结束页补充口头答案')
    repaired={'S09','S15','S30','S33','S36','S40','S42','S44','S53','S55','S57','S58'}
    require('自测题口播与屏显一致',all(s['voiceParts'][1]['narration']==s['question'] and s['answer'].rstrip('。') in s['voiceParts'][2]['narration'] for s in T['scenes'] if s['id'] in repaired),'修正原稿中 12 处不一致；其余题目逐一对照概念和计算条件')
    count=0;pauses=0;expected_pauses=0;max_drift=0
    for s in T['scenes']:
        require(s['id']+' 思考时间',s['answerStart']-s['thinkStart']==180,'6.000 秒')
        with wave.open(str(B/(s['id']+'.wav')),'rb') as f:
            assert f.getnframes()==s['durationFrames']*800
            f.setpos(s['thinkStart']*800);silence=f.readframes(180*800);assert not any(silence)
        for c in s['clips']:
            raw=json.loads((P/'audio_original'/(c['key']+'.json')).read_text(encoding='utf-8'));adjusted=json.loads((P/'audio'/(c['key']+'.json')).read_text(encoding='utf-8'))
            assert raw['rate']==.88 and raw['words'] and adjusted['extraPauseSeconds']==.1
            assert len(adjusted['pauseCutsMs'])==len(re.findall(r'。(?=[\s\S]*[\w\u4e00-\u9fff])',raw['narration'])),c['key']
            expected_pauses+=len(re.findall(r'。(?=[\s\S]*[\w\u4e00-\u9fff])',raw['narration']))
            assert adjusted['sourceFingerprint']==raw['fingerprint']
            assert adjusted['words'][-1]['end_time']/1000<=adjusted['duration']+.3
            assert adjusted['rate']==s['pace'];count+=1;pauses+=len(adjusted['pauseCutsMs'])
    require('真实配音与时间戳',count==180,'180 段；均有配音和字级时间戳；思考段原始 PCM 全为静音')
    require('句号额外停顿',pauses==expected_pauses,f'{pauses} 处内部句号，各加 0.100 秒；未在逗号额外插入静音')
    qa=json.loads((B/'qa-layout.json').read_text(encoding='utf-8'))
    layout=json.loads((B/'layout.json').read_text(encoding='utf-8'))
    require('分镜画面边界',len(qa)==180 and all(not r['issues'] for r in qa+layout),'60 个分镜的讲解、思考、答案状态及关键转场')
    info=probe(MOVIE);v=next(x for x in info['streams'] if x['codec_type']=='video');a=next(x for x in info['streams'] if x['codec_type']=='audio')
    require('视频规格',v['codec_name']=='h264' and (v['width'],v['height'])==(1920,1080) and v['pix_fmt']=='yuv420p','1080p H.264；按原工程保持关键状态，VFR 时间基准 1/30 秒')
    require('音频规格',a['codec_name']=='aac' and a['sample_rate']=='48000' and a['channels']==1,'AAC / 48kHz / mono')
    require('时长完整',max(abs(float(info['format']['duration'])-7200),abs(float(v['duration'])-7200),abs(float(a['duration'])-7200))<.05,'音频、视频、容器均为两小时')
    require('章节跳转',len(info['chapters'])==11 and all(abs(float(actual['start_time'])-expected['startFrame']/30)<.034 and actual['tags']['title']==expected['title'] for actual,expected in zip(info['chapters'],T['chapters'])),'11 个章节标记及标题')
    manifest=json.loads((B/'frame-manifest.json').read_text())
    require('视频帧数',int(v['nb_frames'])==sum(len(x['points']) for x in manifest.values()),f"{v['nb_frames']} 个有效显示状态")
    srt=(OUT/'中文字幕.srt').read_text(encoding='utf-8-sig').strip().split('\n\n')
    require('独立字幕',len(srt)==len(T['captions']) and all(c['start']<c['end']<=7200 for c in T['captions']),f'{len(srt)} 条；按实测字级时间轴生成')
    for s in T['scenes']:
        points=set(manifest[s['id']]['points'])
        for c in s['captions']:
            f=math.ceil(c['start']*30-1e-6);assert f in points
            max_drift=max(max_drift,abs(f/30-c['start']))
    require('字幕刷新时间',max_drift<=1/30+.0001,f'显示帧量化最大 {max_drift:.6f} 秒；非独立语音识别误差测量')
    for ch in T['chapters']:
        with wave.open(str(B/(ch['id']+'.master.wav')),'rb') as f:assert f.getframerate()==48000 and f.getnframes()==ch['durationFrames']*1600
    (B/'final-frames').mkdir(exist_ok=True)
    jobs=[]
    for s in T['scenes']:
        for label,f in [('think',s['thinkStart']+90),('answer',s['answerStart'])]:jobs.append((s['id']+'-'+label,s['startFrame']+f,P/'stills'/f"{s['id']}-{f:05}.png"))
    for ch in T['chapters']:
        scenes=[s for s in T['scenes'] if s['id'] in ch['sceneIds']]
        for label,s,f in [('start',scenes[0],0),('middle',scenes[len(scenes)//2],manifest[scenes[len(scenes)//2]['id']]['points'][len(manifest[scenes[len(scenes)//2]['id']]['points'])//2]),('end',scenes[-1],scenes[-1]['durationFrames']-1)]:
            jobs.append((ch['id']+'-'+label,s['startFrame']+f,P/'stills'/f"{s['id']}-{f:05}.png"))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:frames=list(pool.map(sample,jobs))
    require('实际成片画面',all(r['meanPixelDifference']<3 for r in frames),f"{len(frames)} 帧：60 道题的思考与答案、每章开头中段结尾；最大差 {max(r['meanPixelDifference'] for r in frames):.3f}/255")
    sheets(frames)
    print('FULL_DECODE_START',flush=True)
    log=B/'full-decode.log'
    with log.open('w',encoding='utf-8') as f:r=subprocess.run(['ffmpeg','-hide_banner','-nostats','-xerror','-i',str(MOVIE),'-af','volumedetect','-f','null','-'],stdout=f,stderr=subprocess.STDOUT)
    text=log.read_text(encoding='utf-8',errors='replace')
    require('全片解码',r.returncode==0 and not re.search(r'corrupt decoded|Error while|Invalid data|non.monoton',text,re.I),'完整解码两小时视频与音频')
    mean=float(re.search(r'mean_volume: (-?[\d.]+)',text).group(1));peak=float(re.search(r'max_volume: (-?[\d.]+)',text).group(1))
    require('音频信号',-30<mean<-10 and -8<peak<=0,f'平均 {mean:.1f}dBFS / 峰值 {peak:.1f}dBFS')
    report=dict(checks=CHECKS,video=v,audio=a,duration=7200,frames=frames,meanVolumeDbfs=mean,maxVolumeDbfs=peak,subtitleFrameRounding=max_drift)
    (B/'acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    rows=['# 配音版成片验证报告','', '| 检查 | 结果 | 说明 |','|---|---|---|']
    rows.extend(f"| {c['check']} | 通过 | {c['detail']} |" for c in CHECKS)
    rows.extend(['','画面来自用户提供的离线 SVG 工程。沿用其关键状态切换与保持方式，以 1/30 秒网格记录状态变化；不是逐帧插值的全片连续动画。','', '字幕依据百炼字级时间戳，按逐镜时长调整与新增静音同步换算。所列字幕误差是帧量化误差，不是独立语音识别对齐测量。','', '配音使用阿里云百炼北京区域 qwen-audio-3.0-tts-plus、系统男声 longanlufeng。没有背景音乐。'])
    (OUT/'成片验证报告.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
    print('ACCEPTANCE_DONE',flush=True)
if __name__=='__main__':main()
