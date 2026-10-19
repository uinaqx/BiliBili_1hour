"""Make a measured, voiced timeline; retain six seconds before every answer."""
import argparse,bisect,concurrent.futures,copy,hashlib,json,math,pathlib,re,subprocess,sys,wave
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1];P=ROOT/'production';BUILD=P/'build';AUDIO=P/'audio'
for p in (BUILD,AUDIO):p.mkdir(exist_ok=True)
FPS=30;RATE=24000;SPF=800

def boundaries(meta):
    words=[w for w in meta['words'] if w['text'].strip()];cuts=[]
    for i,w in enumerate(words):
        if '。' not in w['text']:continue
        if i==len(words)-1 and not any(ch.isalnum() for ch in w['text']):continue
        prefix=w['text'].lstrip('“”\"\' ');suffix=w['text'].rstrip('“”\"\' ')
        if prefix.startswith('。') and i:cuts.append((words[i-1]['end_time']+w['begin_time'])/2)
        elif suffix.endswith('。'):
            if i+1<len(words):cuts.append((w['end_time']+words[i+1]['begin_time'])/2)
        elif i==len(words)-1 and not any(ch.isalnum() for ch in w['text']):continue
        else:raise ValueError('Ambiguous full stop: '+w['text'])
    return sorted({round(t,3) for t in cuts if 1<t<words[-1]['end_time']-1})

def captions(words):
    result=[];group=[]
    def flush():
        nonlocal group
        if group:
            result.append(dict(start=group[0]['begin_time']/1000,end=group[-1]['end_time']/1000,text=''.join(w['text'] for w in group)))
        group=[]
    for raw in words:
        w=copy.copy(raw);text=w['text'];leading=re.match(r'^[，。！？；：、]+',text)
        if leading:
            mark=leading.group();text=text[len(mark):]
            if group:
                group[-1]['text']+=mark
                if any(p in mark for p in '。！？；') or sum(len(x['text']) for x in group)>=9:flush()
            elif result:result[-1]['text']+=mark
        if not text:continue
        if group and (sum(len(x['text']) for x in group)+len(text)>38 or w['begin_time']-group[0]['begin_time']>6500):flush()
        w['text']=text;group.append(w)
        if text[-1:] in '。！？；':flush()
    flush();return result

def clip_audio(part,pace):
    key=part['key'];src=P/'audio_original'/(key+'.mp3');meta=json.loads((P/'audio_original'/(key+'.json')).read_text(encoding='utf-8'))
    cuts=boundaries(meta);fingerprint=hashlib.sha256((meta['fingerprint']+f'co-voice-v2;pace={pace:.9f};pause=0.100').encode()).hexdigest()
    wav=AUDIO/(key+'.wav');target=AUDIO/(key+'.json')
    if target.exists() and wav.exists():
        cached=json.loads(target.read_text(encoding='utf-8'))
        if cached['fingerprint']==fingerprint and cached['pauseCutsMs']==cuts:return cached
    pcm=subprocess.check_output(['ffmpeg','-v','error','-i',str(src),'-af',f'atempo={pace:.9f}','-f','s16le','-ac','1','-ar',str(RATE),'-'])
    cursor=0;pieces=[];silence=bytes(round(.1*RATE)*2)
    for t in cuts:
        pos=round(t/pace/1000*RATE)*2
        assert cursor<=pos<=len(pcm),(key,pos,len(pcm))
        pieces.extend([pcm[cursor:pos],silence]);cursor=pos
    pieces.append(pcm[cursor:]);output=b''.join(pieces)
    with wave.open(str(wav),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(output)
    words=copy.deepcopy(meta['words'])
    for w in words:
        w['begin_time']=w['begin_time']/pace+bisect.bisect_right(cuts,w['begin_time'])*100
        w['end_time']=w['end_time']/pace+bisect.bisect_left(cuts,w['end_time'])*100
    data=dict(key=key,fingerprint=fingerprint,sourceFingerprint=meta['fingerprint'],rate=pace,samples=len(output)//2,duration=len(output)/2/RATE,frames=math.ceil(len(output)/2/SPF),pauseCutsMs=cuts,extraPauseSeconds=.1,words=words,captions=captions(words),narration=part['narration'])
    assert max(w['end_time'] for w in words)/1000<data['duration']+.3,(key,data['duration'],words[-1])
    target.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8');return data

def prepare_scene(s):
    raw=[json.loads((P/'audio_original'/(x['key']+'.json')).read_text(encoding='utf-8')) for x in s['voiceParts']]
    total=sum(m['duration'] for m in raw);pauses=sum(len(boundaries(m)) for m in raw)
    pace=max(.9,min(1.35,total/(108.6-pauses*.1)))
    clips=[clip_audio(part,pace) for part in s['voiceParts']]
    speech=sum(c['frames'] for c in clips);frames=max(3600,speech+12+180+60)
    free=frames-speech-12-180
    lesson_hold=max(15,round(free*.6));answer_hold=free-lesson_hold
    lesson_start=12;question_start=lesson_start+clips[0]['frames']+lesson_hold
    think_start=question_start+clips[1]['frames'];answer_start=think_start+180
    starts=[lesson_start,question_start,answer_start]
    wav=BUILD/(s['id']+'.wav');hashfile=BUILD/(s['id']+'.audiohash')
    audiohash=hashlib.sha256(json.dumps([[(c['fingerprint'],c['frames']) for c in clips],starts,frames],sort_keys=True).encode()).hexdigest()
    if not wav.exists() or not hashfile.exists() or hashfile.read_text()!=audiohash:
        buf=bytearray(frames*SPF*2)
        for c,start in zip(clips,starts):
            with wave.open(str(AUDIO/(c['key']+'.wav')),'rb') as f:pcm=f.readframes(f.getnframes())
            pos=start*SPF*2;buf[pos:pos+len(pcm)]=pcm
        with wave.open(str(wav),'wb') as f:f.setnchannels(1);f.setsampwidth(2);f.setframerate(RATE);f.writeframes(buf)
        hashfile.write_text(audiohash)
    caps=[]
    for c,start in zip(clips,starts):
        caps.extend({**cap,'start':cap['start']+start/FPS,'end':cap['end']+start/FPS,'part':c['key']} for cap in c['captions'])
    return dict(**s,durationFrames=frames,lessonStart=lesson_start,lessonEnd=lesson_start+clips[0]['frames'],questionStart=question_start,thinkStart=think_start,answerStart=answer_start,answerEnd=answer_start+clips[2]['frames'],pace=pace,internalPauses=pauses,clips=[dict(key=c['key'],startFrame=start,frames=c['frames'],duration=c['duration']) for c,start in zip(clips,starts)],captions=caps,audioHash=audiohash)

def stamp(sec):
    ms=round(sec*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{s:02},{ms:03}'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--limit',type=int);args=parser.parse_args()
    plan=json.loads((P/'plan.json').read_text(encoding='utf-8'));source=plan['scenes'][:args.limit] if args.limit else plan['scenes']
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:scenes=list(pool.map(prepare_scene,source))
    cursor=0;allcaps=[]
    for s in scenes:
        s['startFrame']=cursor
        for c in s['captions']:allcaps.append({**c,'start':c['start']+cursor/FPS,'end':c['end']+cursor/FPS})
        cursor+=s['durationFrames']
    chapters=[]
    for ch in plan['chapters']:
        part=[s for s in scenes if s['chapter']==ch['id']]
        if not part:continue
        start=part[0]['startFrame'];end=part[-1]['startFrame']+part[-1]['durationFrames']
        chapters.append(dict(**ch,startFrame=start,durationFrames=end-start,sceneIds=[s['id'] for s in part]))
    timeline=dict(title=plan['title'],fps=FPS,width=1920,height=1080,totalFrames=cursor,duration=cursor/FPS,scenes=scenes,chapters=chapters,captions=allcaps,fullCourse=len(scenes)==60)
    (P/'timeline.json').write_text(json.dumps(timeline,ensure_ascii=False,indent=2),encoding='utf-8')
    out=ROOT/'out';out.mkdir(parents=True,exist_ok=True)
    (out/'中文字幕.srt').write_text('\n\n'.join(f"{i}\n{stamp(c['start'])} --> {stamp(c['end'])}\n{c['text']}" for i,c in enumerate(allcaps,1))+'\n',encoding='utf-8-sig')
    metadata=[';FFMETADATA1','title=两小时学习计算机组成原理','artist=中文计算机课程','comment=Chinese synthesized narration; supplied SVG mechanism diagrams; six-second quiz pauses']
    table=['# 计算机组成原理：配音版章节目录','',f'总时长：{stamp(cursor/FPS)}','', '| 起点 | 章节 |','|---|---|']
    for ch in chapters:
        start=ch['startFrame'];end=start+ch['durationFrames']
        metadata.extend(['[CHAPTER]','TIMEBASE=1/30',f'START={start}',f'END={end}',"title="+ch['title']])
        table.append(f"| {stamp(start/FPS).split(',')[0]} | {ch['title']} |")
    (BUILD/'chapters.ffmetadata').write_text('\n'.join(metadata)+'\n',encoding='utf-8')
    (out/'章节目录.md').write_text('\n'.join(table)+'\n',encoding='utf-8')
    print(json.dumps(dict(scenes=len(scenes),seconds=cursor/FPS,captions=len(allcaps),paceMin=min(s['pace'] for s in scenes),paceMax=max(s['pace'] for s in scenes),internalFullStopPauses=sum(s['internalPauses'] for s in scenes)),ensure_ascii=False),flush=True)
if __name__=='__main__':main()
