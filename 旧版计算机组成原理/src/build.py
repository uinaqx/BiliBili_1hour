"""Build the offline review player and deterministic evidence. No network required."""
import csv
import json
import re
from pathlib import Path
from .experiments import experiments
from .handout import build_handout

ROOT=Path(__file__).resolve().parents[1]

def dump(path,value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def wrap_captions(s,limit=61):
    chunks=[];line='';weight=0
    for c in s:
        w=.57 if ord(c)<128 else 1
        if weight+w>limit:
            chunks.append(line);line='';weight=0
        line+=c;weight+=w
    if line:chunks.append(line)
    return chunks

def srt_time(t):
    ms=round(t*1000);secs,ms=divmod(ms,1000);mins,secs=divmod(secs,60);hours,mins=divmod(mins,60)
    return f'{hours:02}:{mins:02}:{secs:02},{ms:03}'

def main():
    out=ROOT/'output';out.mkdir(exist_ok=True)
    course=json.loads((ROOT/'data/course.json').read_text())
    build_handout(ROOT,course)
    exp=experiments();dump(out/'experiments.json',exp)
    template=(ROOT/'src/player.html').read_text()
    def embed(data):return json.dumps(data,ensure_ascii=False,allow_nan=False).replace('</','<\\/')
    html=template.replace('__COURSE_JSON__',embed(course)).replace('__EXPERIMENTS_JSON__',embed(exp)).replace('__PLAYER_JS__',(ROOT/'src/player.js').read_text())
    (out/'index.html').write_text(html,encoding='utf-8')
    (out/'chapters.ffmetadata').write_text(';FFMETADATA1\ntitle=计算机组成原理：120分钟静音学习版\n'+''.join(f"\n[CHAPTER]\nTIMEBASE=1/1000\nSTART={c['start']*1000}\nEND={(c['start']+c['duration'])*1000}\ntitle={c['title']}\n" for c in course['chapters']))
    with (out/'shotlist.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f);writer.writerow(['镜头','标题','全局秒','段内秒','时长','阶段','执行说明'])
        for s in course['scenes']:
            for b in s['beats']:writer.writerow([s['id'],s['title'],s['start']+b['at'],b['at'],b['duration'],b['kind'],b['direction']])
    captions=[]
    for s in course['scenes']:
        paragraphs=[x for x in s['narration'].splitlines() if x];last=paragraphs.pop();first=''.join(paragraphs)
        for content,start,span in [(first,0,90),(s['question'],90,12),(last,102,18)]:
            chunks=wrap_captions(content);length=sum(map(len,chunks));used=0
            for chunk in chunks:
                duration=span*len(chunk)/length
                captions.append((s['start']+start+used,s['start']+start+used+duration,chunk));used+=duration
    (out/'manuscript_estimated.srt').write_text('\n\n'.join(f'{i}\n{srt_time(a)} --> {srt_time(b)}\n{txt}' for i,(a,b,txt) in enumerate(captions,1))+'\n',encoding='utf-8')
    (out/'字幕说明.txt').write_text('manuscript_estimated.srt 是完整文稿的估时阅读提示，与播放器阅读提示同步；没有进行真实语音对齐。主片已经烧录阅读提示，单独SRT供修改参考。配音按用户要求暂不处理。\n',encoding='utf-8')
    coverage=[]
    reused={1,2,59,4,9,25,30,39,33,34,35,40,42,43,58,46,47,48,51,52,53}
    for s in course['scenes']:
        coverage.append(dict(id=s['id'],title=s['title'],status='implemented',
            diagram='共享构图，按本镜条件与轨迹呈现' if int(s['id'][1:]) in reused else '专用机制图',
            review='awaiting_browser_visual_review',audio='deferred_by_user'))
    dump(out/'coverage.json',coverage)
    dump(out/'production_state.json',dict(duration=7200,scenes=60,narration_chars=sum(s['narration_chars'] for s in course['scenes']),
        content='complete',models='implemented',player='implemented',
        video='pending_render',audio='deferred_by_user',subtitle='estimated_manuscript_cues_not_audio_aligned',
        rendering_note='全长静音版可用离散状态画面保持，样片可逐帧动画；网页为连续时间动画。'))
    print(f"Built offline player, {len(coverage)} scene diagrams, experiment evidence, 300 shot cues.")

if __name__=='__main__':main()
