import textwrap
CHAPTERS=[]
CHECKS=[]
def chapter(key,title,english,minutes):
    c=dict(key=key,title=title,english=english,targetMinutes=minutes,scenes=[])
    CHAPTERS.append(c);return c
def scene(c,key,title,narration,code='',output=None,notes=None,diagram=None,kind='lesson',full=None,files=None,verify='run',error=None,expected=None,filename='main.rs',excerpt=False,focus=None):
    if key.endswith('-a') and kind=='lesson':kind='answer'
    code=textwrap.dedent(code).strip('\n')
    speech=textwrap.dedent(narration).strip()
    speech='\n\n'.join(p.strip().replace('\n','') for p in speech.split('\n\n') if p.strip())
    row=dict(key='a-'+key,section=key,title=title,code=code,sourceNarration=speech,narration=speech.replace('C/C++','C 和 C 加加').replace('C++','C 加加'),output=output,notes=notes or [],diagram=diagram,kind=kind,error=error if verify=='error' else None,panic=verify=='panic',hold=4 if kind=='question' else 2,focus=focus or [],panels=[],filename=filename,excerpt=excerpt)
    row['testFailed']=verify=='test_fail'
    c['scenes'].append(row)
    if code and kind!='question' and verify:
        ident=key
        CHECKS.append(dict(key=ident,code=textwrap.dedent(full).strip('\n') if full else code,files=files,kind=verify,error=error,output=expected if expected is not None else output,filename=filename))
    return row
