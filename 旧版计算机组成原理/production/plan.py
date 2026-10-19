"""Preserve the supplied manuscript, separating the quiz before its answer."""
import json,pathlib,re,sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1]
course=json.loads((ROOT/'data/course.json').read_text(encoding='utf-8'))
rows=[];clips=[]
REPAIR_QUIZZES={'S09','S15','S30','S33','S36','S40','S42','S44','S53','S55','S57','S58'}
for s in course['scenes']:
    paragraphs=[p.strip() for p in s['narration'].splitlines() if p.strip()]
    lesson='\n'.join(paragraphs[:-1]);last=paragraphs[-1]
    if '？' in last and last.split('？',1)[1].strip():
        before,answer=last.split('？',1)
        split=before.rfind('。')+1
        if split:lesson+='\n'+before[:split]
        question=before[split:]+'？'
    else:
        question=s['question'];answer=last
        # A few closing scenes contain a summary rather than a spoken answer.
        plain=lambda t:re.sub(r'[\s，。；：、！？,.!?;:]','',t)
        if plain(s['answer']) not in plain(answer):answer='参考答案：'+s['answer'].rstrip('。')+'。'+answer
    if s['id'] in REPAIR_QUIZZES:
        # The supplied manuscript sometimes asks a different question from its
        # screen card. Keep that discussion in the lesson, then ask the card.
        lesson=s['narration'];question=s['question'];answer='参考答案：'+s['answer'].rstrip('。')+'。'
    parts=[]
    for kind,text in [('lesson',lesson),('question',question),('answer',answer)]:
        row=dict(key=s['id']+'-'+kind,scene=s['id'],kind=kind,narration=text.strip())
        parts.append(row);clips.append(row)
    rows.append(dict(**s,voiceParts=parts))
plan=dict(**{k:v for k,v in course.items() if k!='scenes'},scenes=rows,clips=clips)
(ROOT/'production/plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(scenes=len(rows),clips=len(clips),characters=sum(len(c['narration']) for c in clips)),ensure_ascii=False))
