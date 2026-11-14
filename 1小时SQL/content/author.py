import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
CHAPTERS = []

def chapter(title):
    item = dict(key=f'{len(CHAPTERS)+1:02}', title=title, scenes=[])
    CHAPTERS.append(item)
    return item

def speech(marked):
    pieces = re.split(r'\[([0-9, ]+)\]', marked)
    assert not pieces[0]
    text, cues = '', []
    for i in range(1,len(pieces),2):
        fragment = pieces[i+1]
        anchor = ''.join(c.casefold() for c in fragment if c.isalnum())[:18]
        assert len(anchor)>=6,(fragment,anchor)
        cues.append(dict(anchor=anchor,lines=[int(n) for n in pieces[i].split(',')]))
        text += fragment
    assert text.endswith('。'), text
    return dict(text=text,cues=cues)

def page(chapter,title,sql,notes,first,second,*,kind='lesson',expected=None,error=None):
    key=f"sq-{chapter['key']}-{len(chapter['scenes'])+1:02}"
    parts=[speech(first),speech(second)]
    parts[0].update(think=kind=='exercise',showOutput=False)
    parts[1].update(showOutput=True)
    code=sql.strip()
    assert len(code.splitlines())<=13, key
    for part in parts:
        for cue in part['cues']:
            assert all(1<=line<=len(code.splitlines()) for line in cue['lines']),(key,cue)
    chapter['scenes'].append(dict(key=key,title=title,code=code,notes=notes,kind=kind,
      filename='query.sql',parts=parts,expected=expected,diagnostic=error))

def build(draft=False):
    from verify_examples import verify
    if not draft:
        assert len(CHAPTERS)==10
        assert all(sum(s['kind']=='exercise' for s in c['scenes'])==1 for c in CHAPTERS)
    text=''.join(p['text'] for c in CHAPTERS for s in c['scenes'] for p in s['parts'])
    assert not re.search('不能说|这不等于|这不意味着|不代表|并不意味着|必须强调|需要注意的是',text)
    verify(CHAPTERS)
    (ROOT/'public/course.json').write_text(json.dumps(
        dict(title='一小时学完SQL',audience='零基础',subtitles=True,chapters=CHAPTERS),
        ensure_ascii=False,indent=2),encoding='utf8')
    print('COURSE',len(CHAPTERS),sum(len(c['scenes']) for c in CHAPTERS),
          'CJK',len(re.findall('[\u4e00-\u9fff]',text)),flush=True)
