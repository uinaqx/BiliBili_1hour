import copy,re

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
