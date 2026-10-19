import textwrap
CHAPTERS=[];CHECKS=[]
def chapter(key,title,english,minutes):
    c=dict(key=key,title=title,english=english,targetMinutes=minutes,scenes=[]);CHAPTERS.append(c);return c
def scene(c,key,title,narration,code='',output=None,notes=None,diagram='roadmap',kind='lesson',before='',after='',full=None,stdin='',runs=None,verify='run',diagnostic=None,focus=None,filename='main.py',fixtures=None,files=None):
    clean=lambda x:textwrap.dedent(x).strip('\n')
    code=clean(code);speech='\n\n'.join(x.strip().replace('\n','') for x in clean(narration).split('\n\n') if x.strip())
    if key.endswith('-a') and kind=='lesson':kind='answer'
    row=dict(key='python-'+key,section=key,title=title,sourceNarration=speech,narration=speech,code=code,output=output,notes=notes or [],diagram=diagram,kind=kind,error=diagnostic if verify=='syntax_error' else None,panic=verify=='runtime_error',testFailed=False,hold=4 if kind=='question' else 1.5,focus=focus or [],panels=[],filename=filename,excerpt=bool(before or after or full and full.strip()!=code.strip()) and filename!='终端命令')
    c['scenes'].append(row)
    if code and verify:
        source=clean(full) if full else '\n'.join(x for x in (clean(before),code,clean(after)) if x)+'\n'
        CHECKS.append(dict(key=key,source=source,kind=verify,expected=output,stdin=stdin,runs=runs,diagnostic=diagnostic,fixtures=fixtures or {},files=files or {}))
    return row
