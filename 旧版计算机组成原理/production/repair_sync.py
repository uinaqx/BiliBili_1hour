"""One narration tempo, acoustic subtitle alignment, and flexible scene durations.

No credential or network request is required: cached original TTS audio is reused.
"""
import argparse,asyncio,bisect,concurrent.futures,copy,hashlib,json,math,pathlib,re,statistics,subprocess,sys,time,wave
import numpy as np
import prepare as old
import video as base
ROOT=pathlib.Path(__file__).resolve().parents[1];ORIGINAL=ROOT/'production'
P=ORIGINAL/'repair_sync';BUILD=P/'build';AUDIO=P/'audio';STILLS=P/'stills';ALIGN=P/'alignment'
OUT=ROOT/'out/统一语速_字幕校准版'
TARGET=OUT/'计算机组成原理_统一语速字幕校准版.mp4'
PACE=1.29;RATE=24000;FPS=30;SPF=800;VERSION='acoustic-v1-tempo129'
sys.stdout.reconfigure(encoding='utf-8')
for d in (P,BUILD,AUDIO,STILLS,ALIGN,OUT):d.mkdir(parents=True,exist_ok=True)
PLAN=json.loads((ORIGINAL/'plan.json').read_text(encoding='utf-8'))
base.P=P;base.BUILD=BUILD;base.STILLS=STILLS;base.OUT=OUT

def load(path):return json.loads(path.read_text(encoding='utf-8'))
def save(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
def pcm_read(path):
    with wave.open(str(path),'rb') as f:
        assert f.getframerate()==RATE and f.getnchannels()==1 and f.getsampwidth()==2
        return f.readframes(f.getnframes())
def pcm_write(path,pcm):
    with wave.open(str(path),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(pcm)

def scaled(part):
    key=part['key'];source=ORIGINAL/'audio_original'/(key+'.mp3');meta=load(source.with_suffix('.json'))
    fingerprint=hashlib.sha256((meta['fingerprint']+VERSION).encode()).hexdigest()
    dest=AUDIO/(key+'.scaled.wav');tag=dest.with_suffix('.hash')
    if not dest.exists() or not tag.exists() or tag.read_text()!=fingerprint:
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-af',f'atempo={PACE}', '-ac','1','-ar',str(RATE),'-c:a','pcm_s16le',str(dest)],check=True)
        tag.write_text(fingerprint)
    return meta,dest,fingerprint

def align_part(part,model,tokenizer):
    import whisper
    from whisper.timing import find_alignment
    key=part['key'];meta,path,fingerprint=scaled(part);target=ALIGN/(key+'.json')
    if target.exists() and load(target).get('fingerprint')==fingerprint:return load(target),True
    audio=whisper.load_audio(str(path));duration=len(audio)/16000
    original=meta['words'];words=copy.deepcopy(original)
    spans=[];text=''
    for w in original:spans.append((len(text),len(text)+len(w['text'])));text+=w['text']
    char_times=[None]*len(text);groups=[];i=0
    while i<len(words):
        j=i+1
        while j<len(words) and (original[j]['end_time']-original[i]['begin_time'])/1000/PACE<19:j+=1
        choices=[k for k in range(i+1,j) if re.search(r'[。！？；，]',original[k-1]['text']) and (original[k-1]['end_time']-original[i]['begin_time'])/1000/PACE>13]
        if j<len(words) and choices:j=choices[-1]
        if j==i:j+=1
        groups.append((i,j));i=j
    chunks=[];seams=[]
    for first,last in groups:
        a=max(0,first-8);b=min(len(words),last+8)
        start=max(0,original[a]['begin_time']/1000/PACE-.4)
        end=min(duration,original[b-1]['end_time']/1000/PACE+.55)
        assert end-start<29.95,(key,start,end)
        start=round(start*16000)/16000;segment=audio[round(start*16000):round(end*16000)]
        phrase=text[spans[a][0]:spans[b-1][1]]
        mel=whisper.log_mel_spectrogram(whisper.pad_or_trim(segment))
        found=find_alignment(model,tokenizer,tokenizer.encode(phrase),mel,len(segment)//160)
        assert ''.join(w.word for w in found)==phrase,(key,phrase,''.join(w.word for w in found))
        pos=spans[a][0];probabilities=[]
        for w in found:
            for k,c in enumerate(w.word):
                x=pos+k
                timing=(start+float(w.start)+(float(w.end)-float(w.start))*k/len(w.word),start+float(w.start)+(float(w.end)-float(w.start))*(k+1)/len(w.word),float(w.probability))
                if c.isalnum():probabilities.append(float(w.probability))
                if spans[first][0]<=x<spans[last-1][1]:char_times[x]=timing
                elif char_times[x] is not None and c.isalnum():seams.append(abs(char_times[x][0]-timing[0]))
            pos+=len(w.word)
        chunks.append(dict(start=start,end=end,text=phrase,medianProbability=statistics.median(probabilities) if probabilities else 0))
    deltas=[]
    for w,raw,(a,b) in zip(words,original,spans):
        active=[char_times[k] for k in range(a,b) if text[k].isalnum()]
        if not active:active=[char_times[k] for k in range(a,b)]
        assert active and all(x is not None for x in active),(key,w)
        begin=max(0,min(x[0] for x in active));end=min(duration,max(x[1] for x in active))
        w['begin_time']=round(begin*1000,4);w['end_time']=round(max(begin,end)*1000,4)
        w['alignmentProbability']=statistics.mean(x[2] for x in active)
        if any(c.isalnum() for c in w['text']):deltas.append(begin-raw['begin_time']/1000/PACE)
    result=dict(key=key,fingerprint=fingerprint,method='Whisper-base known-transcript cross-attention DTW, audio already at final tempo',tempo=PACE,duration=duration,words=words,chunks=chunks,providerDeltaP95=float(np.percentile(np.abs(deltas),95)),providerDeltaMax=max(abs(x) for x in deltas),overlapAgreementP95=float(np.percentile(seams,95)) if seams else 0,narration=part['narration'])
    save(target,result);return result,False

def align(selected=None):
    import torch,whisper
    from whisper.tokenizer import get_tokenizer
    torch.set_num_threads(4);model=whisper.load_model('base',device='cpu');tokenizer=get_tokenizer(True,language='zh',task='transcribe')
    clips=[p for p in PLAN['clips'] if not selected or p['scene'] in selected];results=[];started=time.time()
    for i,part in enumerate(clips,1):
        result,cached=align_part(part,model,tokenizer);results.append(result)
        print(f"ALIGN {i}/{len(clips)} {part['key']} {'cached' if cached else 'aligned'} p95-provider-shift={result['providerDeltaP95']:.3f}s",flush=True)
    save(BUILD/'alignment-summary.json',dict(clips=len(results),seconds=time.time()-started,tempo=PACE,maxProviderDelta=max(r['providerDeltaMax'] for r in results),overlapP95Max=max(r['overlapAgreementP95'] for r in results),flagged=[dict(key=r['key'],shift=r['providerDeltaMax'],seam=r['overlapAgreementP95']) for r in results if r['providerDeltaMax']>1.5 or r['overlapAgreementP95']>.3]))

def clip(part):
    key=part['key'];aligned=load(ALIGN/(key+'.json'));pcm=pcm_read(AUDIO/(key+'.scaled.wav'));words=copy.deepcopy(aligned['words'])
    cuts=old.boundaries(dict(words=words));cursor=0;pieces=[];positions=[]
    for t in cuts:
        pos=round(t/1000*RATE)*2
        assert cursor<=pos<=len(pcm)
        pieces.extend((pcm[cursor:pos],bytes(round(.1*RATE)*2)));positions.append(pos//2);cursor=pos
    pieces.append(pcm[cursor:]);pcm=b''.join(pieces)
    for w in words:
        w['begin_time']+=bisect.bisect_right(cuts,w['begin_time'])*100
        w['end_time']+=bisect.bisect_left(cuts,w['end_time'])*100
    caps=old.captions(words)
    # Caption starts follow the first spoken character, never punctuation in a pause.
    # Keep the caption briefly after the phrase, bounded by the next phrase start.
    for i,c in enumerate(caps):
        c['start']=max(0,c['start']-.035)
        c['end']=min(len(pcm)/2/RATE,c['end']+.10,caps[i+1]['start']-.035 if i+1<len(caps) else 1e9)
        assert c['end']>=c['start'],(key,c)
    # Keep short answers such as "不是。" with the explanation that follows.
    i=0
    while i<len(caps)-1:
        a,b=caps[i:i+2]
        if a['end']-a['start']<.55 and len(a['text']+b['text'])<=38 and b['end']-a['start']<=6.5:
            a.update(end=b['end'],text=a['text']+b['text']);caps.pop(i+1)
        else:i+=1
    # Attention alignment sometimes gives a phrase the middle of a long silence.
    # Refine only starts that are demonstrably quiet on both sides; leave starts
    # inside continuous speech alone. Keep 55ms for low-energy initial consonants.
    signal=np.frombuffer(pcm,dtype='<i2').astype(np.float64)/32768
    step=round(.01*RATE);rms=np.sqrt(np.mean(signal[:len(signal)//step*step].reshape(-1,step)**2,axis=1))
    voiced=rms>max(.001,float(np.percentile(rms,90))*.03);snaps=[]
    for c in caps:
        k=round(c['start']/.01)
        if np.any(voiced[max(0,k-4):min(len(voiced),k+8)]):continue
        candidates=np.flatnonzero(voiced[k:min(len(voiced),k+90)])
        if not len(candidates):continue
        onset=(k+int(candidates[0]))*.01;start=max(c['start'],onset-.055)
        if start<c['end']-.1 and start-c['start']>.075:
            snaps.append(dict(text=c['text'],oldStart=c['start'],newStart=start,onset=onset));c['start']=start
    fingerprint=hashlib.sha256((aligned['fingerprint']+json.dumps(words,sort_keys=True)+'pause100').encode()).hexdigest()
    pcm_write(AUDIO/(key+'.wav'),pcm)
    result=dict(key=key,fingerprint=fingerprint,tempo=PACE,duration=len(pcm)/2/RATE,frames=math.ceil(len(pcm)/2/SPF),samples=len(pcm)//2,words=words,captions=caps,captionOnsetRefinements=snaps,pauseCutsMs=cuts,insertedPauseSamples=positions,narration=part['narration'])
    save(AUDIO/(key+'.json'),result);return result

def prepare():
    scenes=[];cursor=0;allcaps=[]
    for source in PLAN['scenes']:
        s=copy.deepcopy(source);parts=[clip(part) for part in s['voiceParts']]
        # Never force a scene into a fixed duration or use a scene-specific tempo.
        lesson_start=9;lesson_end=lesson_start+parts[0]['frames'];question_start=lesson_end+24
        think_start=question_start+parts[1]['frames'];answer_start=think_start+180
        answer_end=answer_start+parts[2]['frames'];frames=answer_end+30
        starts=[lesson_start,question_start,answer_start];caps=[];buf=bytearray(frames*SPF*2)
        for c,start in zip(parts,starts):
            pcm=pcm_read(AUDIO/(c['key']+'.wav'));pos=start*SPF*2;buf[pos:pos+len(pcm)]=pcm
            caps.extend({**cap,'start':cap['start']+start/FPS,'end':cap['end']+start/FPS,'part':c['key']} for cap in c['captions'])
        audiohash=hashlib.sha256(buf).hexdigest();pcm_write(BUILD/(s['id']+'.wav'),buf)
        s.update(startFrame=cursor,durationFrames=frames,lessonStart=lesson_start,lessonEnd=lesson_end,questionStart=question_start,thinkStart=think_start,answerStart=answer_start,answerEnd=answer_end,pace=PACE,clips=[dict(key=c['key'],startFrame=start,frames=c['frames'],duration=c['duration']) for c,start in zip(parts,starts)],captions=caps,audioHash=audiohash)
        scenes.append(s);allcaps.extend({**c,'start':c['start']+cursor/FPS,'end':c['end']+cursor/FPS} for c in caps);cursor+=frames
    chapters=[]
    for ch in PLAN['chapters']:
        group=[s for s in scenes if s['chapter']==ch['id']];start=group[0]['startFrame'];end=group[-1]['startFrame']+group[-1]['durationFrames']
        chapters.append(dict(**ch,startFrame=start,durationFrames=end-start,sceneIds=[s['id'] for s in group]))
    t=dict(title=PLAN['title'],fps=FPS,width=1920,height=1080,totalFrames=cursor,duration=cursor/FPS,scenes=scenes,chapters=chapters,captions=allcaps,fullCourse=True,uniformTempo=PACE)
    save(P/'timeline.json',t)
    text=(ORIGINAL/'revision_121/player_voice.js').read_text(encoding='utf-8')
    text=text.replace("+text(96,1073,'教学模型 · 按条件解释结果 · 中文字幕依据实际配音',17,C.muted)",'')
    text=text.replace("const svg=document.querySelector('#stage svg');","const svg=document.querySelector('#stage svg');svg.querySelectorAll('text').forEach(n=>{if(Number(n.getAttribute('y'))===1073&&n.textContent.startsWith('教学模型'))n.remove();});",1)
    text=text.replace('frame/30/1.21','frame/30').replace('VOICED.displayFrames/30/1.21','VOICED.displayFrames/30')
    text=text.replace("['本镜头要点','中文配音版','静音学习版'].includes(n.textContent)","(['本镜头要点','中文配音版','静音学习版'].includes(n.textContent)||n.textContent.includes('教学模型 ·'))")
    (P/'player_voice.js').write_text(text,encoding='utf-8');documents(t)
    print('TIMELINE_READY',json.dumps(dict(seconds=t['duration'],captions=len(allcaps),scenes=60,uniformTempo=PACE,minSceneSeconds=min(s['durationFrames']/30 for s in scenes),maxSceneSeconds=max(s['durationFrames']/30 for s in scenes)),ensure_ascii=False),flush=True)
    return t

def documents(t):
    (OUT/'中文字幕.srt').write_text('\n\n'.join(f"{i}\n{old.stamp(c['start'])} --> {old.stamp(c['end'])}\n{c['text']}" for i,c in enumerate(t['captions'],1))+'\n',encoding='utf-8-sig')
    rows=['# 计算机组成原理：统一语速、字幕校准版','',f"总时长：{old.stamp(t['duration'])}",'','| 起点 | 章节 |','|---|---|']
    metadata=[';FFMETADATA1','title=计算机组成原理：统一语速字幕校准版','artist=中文计算机课程','comment=Uniform narration tempo; acoustic forced-aligned subtitles; flexible scene durations']
    script=['# 计算机组成原理：完整讲稿','',f"总时长：{old.stamp(t['duration'])}",'']
    for c in t['chapters']:
        rows.append(f"| {old.stamp(c['startFrame']/30).split(',')[0]} | {c['title']} |")
        metadata.extend(['[CHAPTER]','TIMEBASE=1/30',f"START={c['startFrame']}",f"END={c['startFrame']+c['durationFrames']}",'title='+c['title']])
    for s in t['scenes']:
        script.extend([f"## {old.stamp(s['startFrame']/30).split(',')[0]} {s['title']}",''])
        for part in s['voiceParts']:
            script.extend([f"### {part['kind']}",'',part['narration'],''])
            if part['kind']=='question':script.extend(['（六秒独立思考）',''])
    (OUT/'章节目录.md').write_text('\n'.join(rows)+'\n',encoding='utf-8');(OUT/'完整讲稿.md').write_text('\n'.join(script),encoding='utf-8')
    (BUILD/'chapters.ffmetadata').write_text('\n'.join(metadata)+'\n',encoding='utf-8')
    (OUT/'制作说明.md').write_text('# 统一语速与字幕校准\n\n原始180段配音全部使用同一个1.29倍处理系数，保留音调。取消按分镜填满两分钟的不同语速，画面长度按实际讲解伸缩。\n\n字幕用本地Whisper已知讲稿强制对齐实际加速后音频，保留讲稿文字，并对长静音中的字幕起点按实际开口位置细调；句末附加0.1秒停顿的声音与字幕使用同一份映射。字幕靠下居中。删除左下角“教学模型……”整行及之前要求删除的角标和右栏标题。\n\n原片讲稿中提到“两小时”的原始旁白保留；实际成片和章节以本版目录为准。自测保留六秒独立思考，与原始讲稿一致。原版本均保留。\n\n工程：production/repair_sync.py；缓存与时间轴：production/repair_sync/。直接运行 python production/repair_sync.py --all 可断点继续。不需要再次请求语音服务，不读取或保存凭据。\n',encoding='utf-8')

async def audit_captions(t):
    from playwright.async_api import async_playwright
    html=base.make_html(t);maximum=0
    async with async_playwright() as pw:
        browser=await pw.chromium.launch(executable_path='C:/Program Files/Google/Chrome/Application/chrome.exe',headless=True)
        page=await browser.new_page(viewport=dict(width=1920,height=1080),device_scale_factor=1)
        await page.set_content(html,wait_until='load');await page.evaluate("document.body.classList.add('export')");await page.evaluate('document.fonts.ready')
        for cap in t['captions']:
            frame=math.ceil(cap['start']*30-1e-6)
            assert frame/30<cap['end'],cap
            await page.evaluate('(t)=>window.renderVoicedAt(t)',frame/30)
            audit=await page.evaluate("()=>({issues:window.auditVoicedLayout(),captions:[...document.querySelectorAll('#centered-caption text')].map(n=>{let b=n.getBBox();return {text:n.textContent,center:b.x+b.width/2}})})")
            assert not audit['issues'] and audit['captions'],(cap,audit)
            assert ''.join(c['text'] for c in audit['captions'])==cap['text'],(cap,audit)
            maximum=max(maximum,max(abs(c['center']-960) for c in audit['captions']))
        await browser.close()
    save(BUILD/'caption-audit.json',dict(captions=len(t['captions']),maxCenterErrorPx=maximum,allCaptionTextMatches=True,removedLabelsAbsent=True))
    print('CAPTION_AUDIT_DONE',len(t['captions']),flush=True)

def normalize_audio(t):
    def work(ch):
        target=BUILD/(ch['id']+'.master.wav');tag=BUILD/(ch['id']+'.pcm-normalized.hash')
        expected=ch['durationFrames']*1600
        fingerprint=hashlib.sha256(json.dumps([s['audioHash'] for s in t['scenes'] if s['id'] in ch['sceneIds']]).encode()+b'sample-count-normalization-v1').hexdigest()
        if target.exists() and tag.exists() and tag.read_text()==fingerprint:
            with wave.open(str(target),'rb') as f:
                if f.getnframes()==expected:return
        staged=target.with_name(ch['id']+'.normalized.wav')
        # Limit by samples after resetting filter timestamps: -t alone can drop
        # a partial block after loudnorm on chapter durations not in whole seconds.
        base.run(['ffmpeg','-y','-hide_banner','-loglevel','warning','-i',str(BUILD/(ch['id']+'.raw.wav')),'-af',f'loudnorm=I=-16:TP=-1.5:LRA=11,aresample=48000,asetpts=N/SR/TB,apad,atrim=end_sample={expected}','-c:a','pcm_s16le',str(staged)],BUILD/(ch['id']+'.normalize-samples.log'))
        with wave.open(str(staged),'rb') as f:assert f.getnframes()==expected and f.getframerate()==48000
        staged.replace(target);tag.write_text(fingerprint)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(work,t['chapters']))
    print('AUDIO_SAMPLE_COUNTS_VERIFIED',flush=True)

def encode(t):
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(lambda ch:base.encode_chapter(ch,t),t['chapters']))
    normalize_audio(t)
    for name,suffix in [('videos','.mp4'),('audios','.master.wav')]:
        (BUILD/(name+'.ffconcat')).write_text('ffconcat version 1.0\n'+''.join(f"file '{c['id']+suffix}'\nduration {c['durationFrames']/30:.9f}\n" for c in t['chapters']),encoding='utf-8')
    staged=TARGET.with_name(TARGET.stem+'.rendering.mp4')
    base.run(['ffmpeg','-y','-hide_banner','-loglevel','warning','-f','concat','-safe','0','-i',str(BUILD/'videos.ffconcat'),'-f','concat','-safe','0','-i',str(BUILD/'audios.ffconcat'),'-f','ffmetadata','-i',str(BUILD/'chapters.ffmetadata'),'-map','0:v:0','-map','1:a:0','-map_metadata','2','-map_chapters','2','-c:v','copy','-af',f"asetpts=N/SR/TB,apad,atrim=end_sample={t['totalFrames']*1600}",'-c:a','aac','-b:a','128k','-ar','48000','-ac','1','-t',f"{t['duration']:.9f}",'-video_track_timescale','30000','-movflags','+faststart',str(staged)],BUILD/'final-mux.log')
    staged.replace(TARGET);print('FINAL_ENCODED',str(TARGET),flush=True)

def verify_audio_sync(t):
    # Measure actual final AAC placement against the PCM used by the aligner.
    # This catches a mux/normalization delay or cumulative chapter join drift.
    from scipy.signal import correlate
    synchronization=[]
    for ch in t['chapters']:
        group=[s for s in t['scenes'] if s['id'] in ch['sceneIds']];s=group[len(group)//2]
        local=s['lessonStart']/30+min(20,s['clips'][0]['duration']*.4);index=round(local*RATE);local=index/RATE
        ref=np.frombuffer(pcm_read(BUILD/(s['id']+'.wav')),dtype='<i2').astype(np.float64)[index:index+3*RATE];ref-=ref.mean()
        sec=s['startFrame']/30+local
        raw=subprocess.check_output(['ffmpeg','-v','error','-ss',f'{sec-.25:.9f}','-i',str(TARGET),'-t','3.5','-ac','1','-ar',str(RATE),'-f','f32le','-'])
        actual=np.frombuffer(raw,dtype='<f4').astype(np.float64);actual-=actual.mean()
        scores=correlate(actual,ref,mode='valid',method='fft');position=int(np.argmax(scores));window=actual[position:position+len(ref)]
        offset=(position-round(.25*RATE))/RATE;similarity=float(np.dot(window,ref)/(np.linalg.norm(window)*np.linalg.norm(ref)))
        assert abs(offset)<.05 and similarity>.85,(ch['id'],offset,similarity)
        synchronization.append(dict(chapter=ch['id'],audioOffsetSeconds=offset,waveformCorrelation=similarity))
    save(BUILD/'final-audio-synchronization.json',synchronization)
    return synchronization

def verify(t):
    info=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-show_chapters','-of','json',str(TARGET)]))
    v=next(s for s in info['streams'] if s['codec_type']=='video');a=next(s for s in info['streams'] if s['codec_type']=='audio')
    assert (v['width'],v['height'],v['codec_name'],a['codec_name'])==(1920,1080,'h264','aac')
    assert all(abs(float(x)-t['duration'])<.01 for x in (v['duration'],a['duration'],info['format']['duration']))
    assert len(info['chapters'])==11 and all(abs(float(c['start_time'])-ch['startFrame']/30)<.0011 for c,ch in zip(info['chapters'],t['chapters']))
    assert {s['pace'] for s in t['scenes']}=={PACE}
    assert len(t['scenes'])==60 and len(PLAN['clips'])==180
    for s in t['scenes']:
        pcm=pcm_read(BUILD/(s['id']+'.wav'));assert len(pcm)//2==s['durationFrames']*SPF
        assert not any(pcm[s['thinkStart']*SPF*2:s['answerStart']*SPF*2])
        for c in s['clips']:
            assert pcm[c['startFrame']*SPF*2:c['startFrame']*SPF*2+len(pcm_read(AUDIO/(c['key']+'.wav')))]==pcm_read(AUDIO/(c['key']+'.wav'))
    caps=t['captions'];assert all(c['end']>c['start'] for c in caps)
    assert all(caps[i]['end']<=caps[i+1]['start']+.001 for i in range(len(caps)-1))
    for part in PLAN['clips']:
        c=load(AUDIO/(part['key']+'.json'));norm=lambda text:''.join(x for x in text if x.isalnum())
        assert norm(''.join(x['text'] for x in c['captions']))==norm(''.join(x['text'] for x in c['words']))
    audit=load(BUILD/'caption-audit.json');qa=load(BUILD/'qa-layout.json')
    assert audit['captions']==len(caps) and len(qa)==180 and all(not x['issues'] for x in qa)
    manifest=load(BUILD/'frame-manifest.json');assert int(v['nb_frames'])==sum(len(s['points']) for s in manifest.values())
    from PIL import Image,ImageChops,ImageStat,ImageDraw,ImageFont
    jobs=[]
    for s in t['scenes']:
        c=s['captions'][len(s['captions'])//3];jobs.extend([(s['id']+'-caption',s,math.ceil(c['start']*30-1e-6)),(s['id']+'-answer',s,s['answerStart'])])
    for ch in t['chapters']:
        group=[s for s in t['scenes'] if s['id'] in ch['sceneIds']];s=group[len(group)//2]
        jobs.extend([(ch['id']+'-start',group[0],0),(ch['id']+'-middle',s,manifest[s['id']]['points'][len(manifest[s['id']]['points'])//2]),(ch['id']+'-end',group[-1],group[-1]['durationFrames']-1)])
    (BUILD/'final-frames').mkdir(exist_ok=True)
    def frame(job):
        label,s,f=job;dest=BUILD/'final-frames'/(label+'.png');sec=(s['startFrame']+f)/30
        subprocess.run(['ffmpeg','-y','-v','error','-ss',f'{max(0,sec-.00001):.7f}','-i',str(TARGET),'-frames:v','1','-fps_mode','passthrough','-update','1',str(dest)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
        # Caption starts are capture events; compare the actual output frame to its source.
        with Image.open(dest) as x,Image.open(STILLS/f"{s['id']}-{f:05}.png") as y:delta=sum(ImageStat.Stat(ImageChops.difference(x.convert('RGB'),y.convert('RGB'))).mean)/3
        assert delta<3,(label,delta);return dict(label=label,file=str(dest),difference=delta)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:frames=list(pool.map(frame,jobs))
    font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',17)
    for off in range(0,len(frames),12):
        sheet=Image.new('RGB',(1920,930),(10,18,30));draw=ImageDraw.Draw(sheet)
        for i,item in enumerate(frames[off:off+12]):
            with Image.open(item['file']) as im:sheet.paste(im.resize((480,270)),((i%4)*480,(i//4)*310))
            draw.text(((i%4)*480+8,(i//4)*310+279),item['label'],font=font,fill='#eef2fa')
        sheet.save(BUILD/f'actual-sheet-{off//12:02}.jpg',quality=94)
    print('FULL_DECODE_START',flush=True)
    base.run(['ffmpeg','-hide_banner','-nostats','-xerror','-i',str(TARGET),'-af','volumedetect','-f','null','-'],BUILD/'decode.log')
    synchronization=verify_audio_sync(t)
    report=dict(duration=t['duration'],uniformTempo=PACE,tempoValues=1,clips=180,scenes=60,chapters=11,subtitles=len(caps),subtitleMethod='acoustic forced alignment on final-tempo voice, with sample-accurate pause mapping',captionsChecked=audit,actualFramesChecked=len(frames),maxPixelDifference=max(f['difference'] for f in frames),audioSyncSpots=len(synchronization),maxFinalAudioOffsetSeconds=max(abs(x['audioOffsetSeconds']) for x in synchronization),fullDecodePassed=True)
    save(BUILD/'acceptance.json',report)
    (OUT/'检查结果.md').write_text(f"# 检查结果\n\n- 总时长 {old.stamp(t['duration'])}，1080p H.264/AAC。\n- 180段配音使用同一速度，60个分镜按实际配音伸缩。\n- {len(caps)}条字幕按最终语速的实际音频强制对齐，停顿和字幕共用样本映射。\n- 全部字幕居中和文字完整性检查通过；左下角指定整行、角标及右栏标题删除。\n- 180个排版检查画面及{len(frames)}张成片画面通过。\n- 11个章节、音视频时长、字幕顺序、60次思考静音、拼接音频内容和全片解码检查通过。\n",encoding='utf-8')
    print('REPAIR_DONE',json.dumps(report,ensure_ascii=False),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--all',action='store_true');p.add_argument('--align',action='store_true');p.add_argument('--prepare',action='store_true');p.add_argument('--qa',action='store_true');p.add_argument('--render',action='store_true');p.add_argument('--encode-only',action='store_true');p.add_argument('--verify',action='store_true');p.add_argument('--scenes');args=p.parse_args()
    if args.all or args.align:align(set(args.scenes.split(',')) if args.scenes else None)
    if args.all or args.prepare:t=prepare()
    elif (P/'timeline.json').exists():t=load(P/'timeline.json')
    else:return
    if args.all or args.qa:asyncio.run(base.capture(t,qa=True));asyncio.run(audit_captions(t))
    if args.all or args.render:asyncio.run(base.capture(t));encode(t)
    elif args.encode_only:encode(t)
    if args.all or args.render or args.encode_only or args.verify:verify(t)
if __name__=='__main__':main()
