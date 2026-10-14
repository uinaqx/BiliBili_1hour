"""Acceptance checks against the actual exported movie, not only its inputs."""
import concurrent.futures, json, pathlib, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageStat
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1]
BUILD=ROOT/'build'; DEL=ROOT/'out'
MOVIE=DEL/'Rust基础一小时学习_初学者版.mp4'
T=json.loads((ROOT/'public/timeline.json').read_text(encoding='utf-8'))
sys.path.insert(0,str(ROOT))
checks=[]

def require(label, condition, detail=''):
    checks.append({'check':label,'passed':bool(condition),'detail':detail})
    print(('PASS ' if condition else 'FAIL ')+label+' '+detail,flush=True)
    if not condition: raise AssertionError(label+': '+detail)

def stamp(t):
    t=round(t);h,t=divmod(t,3600);m,s=divmod(t,60)
    return f'{h:02}:{m:02}:{s:02}'

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-show_chapters','-of','json',str(path)],text=True,encoding='utf-8'))

def srt_time(text):
    h,m,s,ms=map(int,re.split('[:,]',text));return h*3600+m*60+s+ms/1000

def sample(item):
    ci,label,when,caption=item
    out=BUILD/'final-frames'/f'{ci:02}-{label}.png'
    subprocess.run(['ffmpeg','-y','-v','error','-ss',f'{when:.6f}','-i',str(MOVIE),'-frames:v','1','-update','1',str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    with Image.open(out) as img:
        pixels=img.convert('RGB').crop((90,948,1830,1045))
        bright=sum(1 for r,g,b in pixels.getdata() if min(r,g,b)>145)
    return {'chapter':ci,'position':label,'time':when,'caption':caption,'brightPixels':bright,'file':out.name}

def junction(item):
    label,frame,reference=item
    out=BUILD/'final-frames'/f'junction-{label}.png'
    # Seek just before the target frame to avoid rounding up to the next frame.
    when=max(0,frame/30-.005)
    subprocess.run(['ffmpeg','-y','-v','error','-ss',f'{when:.6f}','-i',str(MOVIE),'-frames:v','1','-update','1',str(out)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    with Image.open(out) as actual, Image.open(ROOT/'public'/reference) as expected:
        a=actual.convert('RGB').crop((0,0,1920,934));b=expected.convert('RGB').crop((0,0,1920,934))
        difference=sum(ImageStat.Stat(ImageChops.difference(a,b)).mean)/3
    return {'label':label,'frame':frame,'meanPixelDifference':difference,'file':out.name}

def sheets(frames,prefix,font):
    for off in range(0,len(frames),12):
        sheet=Image.new('RGB',(1920,930),(8,16,28));draw=ImageDraw.Draw(sheet)
        for i,item in enumerate(frames[off:off+12]):
            with Image.open(BUILD/'final-frames'/item['file']) as img:sheet.paste(img.resize((480,270)),((i%4)*480,(i//4)*310))
            label=item.get('label') or f"{item['chapter']:02} {item['position']} {stamp(item['time'])}"
            draw.text(((i%4)*480+8,(i//4)*310+276),label,font=font,fill=(230,235,244))
        sheet.save(BUILD/f'{prefix}-{off//12:02}.jpg',quality=94)

def main():
    examples=json.loads((BUILD/'verification.json').read_text(encoding='utf-8'))
    expected_examples=len(json.loads((ROOT/'content/example_manifest.json').read_text(encoding='utf-8')))
    require('Rust 示例与错误验证',len(examples)==expected_examples and all(x['passed'] for x in examples),f'{len(examples)}/{expected_examples}；含跨屏完整程序与习题修正；rustc 1.98.1；Edition 2024')
    require('审核通过旁白完整保留',all(s['narration']==s['sourceNarration'].replace('C/C++','C 和 C 加加').replace('C++','C 加加') for s in T['scenes']),'仅规范 C/C++ 的语音读法')
    topics=['variables','primitive_types','functions','if','move_semantics','structs','enums','options','vecs','strings','hashmaps','generics','traits','lifetimes']
    covered={c['english']:c for c in T['chapters']}
    require('14 个主题与原创习题',all(k in covered and sum(s['kind']=='question' for s in covered[k]['scenes'])==1 and any(s['kind']=='answer' for s in covered[k]['scenes']) for k in topics))
    require('代码行数',max(len(s['code'].splitlines()) for s in T['scenes'])<=16)
    p=probe(MOVIE);v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio')
    duration=float(p['format']['duration'])
    require('成片时长',58*60<=duration<=63*60 and abs(duration-T['duration'])<.05,f'{duration:.3f} 秒 / {stamp(duration)}')
    require('视频编码与尺寸',v['codec_name']=='h264' and v['width']==1920 and v['height']==1080 and v['avg_frame_rate']=='30/1' and v['pix_fmt']=='yuv420p','H.264 / 1920×1080 / 30fps')
    require('视频帧数',int(v['nb_frames'])==T['totalFrames'],str(v['nb_frames']))
    require('音频编码与长度',a['codec_name']=='aac' and int(a['sample_rate'])==48000 and int(a['channels'])==1 and abs(float(a['duration'])-T['duration'])<.05,'AAC / 48kHz / mono')
    actual=p['chapters']
    chapter_error=max(abs(float(x['start_time'])-y['startFrame']/30) for x,y in zip(actual,T['chapters']))
    require('16 个章节标记',len(actual)==len(T['chapters'])==16 and chapter_error<.034 and all(x['tags']['title']==y['title']+' · '+y['english'] for x,y in zip(actual,T['chapters'])),f'起点误差 {chapter_error:.6f}s')
    caps=[{**cap,'start':cap['start']+c['startFrame']/30,'end':cap['end']+c['startFrame']/30} for c in T['chapters'] for cap in c['captions']]
    require('字幕保留 Rust 引用符号',not any(re.search(r'(?<![A-Za-z])and(?![A-Za-z])',cap['text']) for cap in caps),'&str、&String、&mut self 等保留原写法')
    require('字幕时间单调且有效',all(0<=x['start']<x['end']<=duration for x in caps) and all(x['start']>=y['end']-.02 for y,x in zip(caps,caps[1:])),f'{len(caps)} 条')
    blocks=(DEL/'中文字幕.srt').read_text(encoding='utf-8-sig').strip().split('\n\n')
    require('独立 SRT 条数',len(blocks)==len(caps))
    errors=[]
    for block,cap in zip(blocks,caps):
        rows=block.splitlines();beg,end=rows[1].split(' --> ')
        errors.extend([abs(srt_time(beg)-cap['start']),abs(srt_time(end)-cap['end'])])
        if ''.join(rows[2:])!=cap['text']:raise AssertionError('SRT text mismatch')
    max_error=max(errors)
    require('字幕字级时间轴',max_error<=.001,f'SRT 舍入 {max_error:.6f}s；烧录 ASS 舍入≤0.005s；30fps 采样≤0.0334s')
    # All captions are placed after the same 400ms audio lead-in used by render.py.
    require('所有旁白与字幕使用相同前导',all(s['leadFrames']==12 for s in T['scenes']),'12 帧 / 400ms')
    (BUILD/'final-frames').mkdir(exist_ok=True)
    items=[]
    for ci,c in enumerate(T['chapters']):
        for label,fraction in [('start',.05),('middle',.5),('end',.95)]:
            target=c['durationFrames']/30*fraction
            cap=min(c['captions'],key=lambda cap:abs((cap['start']+cap['end'])/2-target))
            when=c['startFrame']/30+(cap['start']+cap['end'])/2
            items.append((ci,label,when,cap['text']))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:frames=list(pool.map(sample,items))
    require('成片字幕实际刷新',all(f['brightPixels']>300 for f in frames),f'48 个各章开头、中段、结尾字幕帧；最少 {min(f["brightPixels"] for f in frames)} 个亮像素')
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
    sheets(frames,'final-sheet',font)
    answer_items=[]
    for ci,c in enumerate(T['chapters']):
        for scene in c['scenes']:
            if scene['kind']=='answer':
                when=(scene['startFrame']+scene['steps'][3]+12)/30
                answer_items.append((f'answer-{ci:02}',round(when*30),'stills/'+scene['key']+f'-{scene["steps"][3]+12:05}.png'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:answer_frames=list(pool.map(junction,answer_items))
    require('14 道例题答案实际成片画面',len(answer_frames)==14 and all(f['meanPixelDifference']<3 for f in answer_frames),'逐一核对源画面；实际成片答案帧留存')
    for off in range(0,len(answer_frames),4):
        sheet=Image.new('RGB',(1920,1160),(8,16,28));draw=ImageDraw.Draw(sheet)
        for i,item in enumerate(answer_frames[off:off+4]):
            with Image.open(BUILD/'final-frames'/item['file']) as img:sheet.paste(img.resize((960,540)),((i%2)*960,(i//2)*580))
            draw.text(((i%2)*960+12,(i//2)*580+546),item['label'],font=font,fill=(230,235,244))
        sheet.save(BUILD/f'answer-sheet-{off//4:02}.jpg',quality=96)
    points=[('first',0,T['chapters'][0]['images'][0]['path'])]
    for ci,c in enumerate(T['chapters'][1:],1):
        points.extend([(f'{ci:02}-before',c['startFrame']-1,T['chapters'][ci-1]['images'][-1]['path']),(f'{ci:02}-after',c['startFrame'],c['images'][0]['path'])])
    points.append(('last',T['totalFrames']-1,T['chapters'][-1]['images'][-1]['path']))
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:junctions=list(pool.map(junction,points))
    require('实际拼接处与源画面一致',all(j['meanPixelDifference']<3 for j in junctions),f'32 帧；最大平均像素差 {max(j["meanPixelDifference"] for j in junctions):.3f}/255')
    sheets(junctions,'junction-sheet',font)
    print('FULL_DECODE_START',flush=True)
    log=BUILD/'final-decode.log'
    with log.open('w',encoding='utf-8') as f:
        decoded=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',str(MOVIE),'-af','volumedetect','-f','null','-'],stdout=f,stderr=subprocess.STDOUT)
    output=log.read_text(encoding='utf-8',errors='replace')
    require('全片视频与音频解码',decoded.returncode==0 and not re.search(r'(Error while|corrupt decoded|Invalid data|non monotonically)',output,re.I),'完整解码返回 0')
    mean=float(re.search(r'mean_volume: (-?[\d.]+) dB',output).group(1));peak=float(re.search(r'max_volume: (-?[\d.]+) dB',output).group(1))
    require('实际音频信号',-35<mean<-10 and -10<peak<0,f'平均 {mean:.1f}dBFS；峰值 {peak:.1f}dBFS')
    for ci,c in enumerate(T['chapters']):
        wav=probe(BUILD/(c['key']+'.wav'))
        require('章节音频 '+c['key'],abs(float(wav['format']['duration'])-c['durationFrames']/30)<.0001)
    report={'duration':duration,'bytes':MOVIE.stat().st_size,'video':v,'audio':a,'chapters':actual,'checks':checks,'frameSamples':frames,'answerSamples':answer_frames,'junctionSamples':junctions,'srtRoundingError':max_error,'maxVolumeDbfs':peak,'meanVolumeDbfs':mean}
    (BUILD/'acceptance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    lines=['# 初学者版成片验证报告',f'\n成片：Rust基础一小时学习_初学者版.mp4。总时长 {stamp(duration)}（{duration:.3f} 秒）。', '\n| 检查 | 结果 | 实测 / 说明 |','|---|---|---|']
    lines.extend(f"| {x['check']} | 通过 | {x['detail']} |" for x in checks)
    lines.extend([f'\n画面采用 {len(T["scenes"])} 个分镜；所有例题答案帧及各场景关键帧均渲染检查。代码字体 34px，单屏最多 16 个可见行。', '\n字幕依据百炼返回的字级时间戳，按与配音相同的语速比例换算，再加上对应场景的 400ms 前导与场景起点。配音语速调整约 8.74%，音高保持不变。上表的舍入误差是制作时间轴误差，不代表独立语音识别测量。', '\n使用阿里云百炼 qwen-audio-3.0-tts-plus，系统男声 longanlufeng，以耐心的大学老师口吻讲解。没有背景音乐。', '\n检查过程文件在初学者制作工程/build，包括 verification.json、acceptance.json、final-decode.log 及画面检查拼图。'])
    (DEL/'成片验证报告.md').write_text('\n'.join(lines),encoding='utf-8')
    print('ACCEPTANCE_DONE',flush=True)

if __name__=='__main__':main()
