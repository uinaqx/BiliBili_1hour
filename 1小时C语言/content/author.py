import textwrap
CHAPTERS=[];CHECKS=[]
def chapter(key,title,english,minutes):
    row=dict(key=key,title=title,english=english,targetMinutes=minutes,scenes=[]);CHAPTERS.append(row);return row
def scene(c,key,title,narration,code='',output=None,notes=None,diagram=None,kind='lesson',full=None,stdin='',runs=None,files=None,expectedFiles=None,verify='run',filename='main.c',excerpt=None,focus=None):
    if key.endswith('-a') and kind=='lesson':kind='answer'
    clean=lambda s:textwrap.dedent(s).strip('\n')
    code=clean(code);speech='\n\n'.join(p.strip().replace('\n','') for p in clean(narration).split('\n\n') if p.strip())
    if excerpt is None:excerpt=bool(code and not code.startswith('#include'))
    row=dict(key='c-'+key,section=key,title=title,sourceNarration=speech,narration=speech,code=code,output=output,notes=notes or [],diagram=diagram,kind=kind,error=None,panic=False,testFailed=False,hold=4 if kind=='question' else 2,focus=focus or [],panels=[],filename=filename,excerpt=excerpt)
    c['scenes'].append(row)
    if code and verify:
        source=clean(full) if full else code if code.startswith('#include') else '#include <stdio.h>\n#include <string.h>\n#include <stdbool.h>\nint main(void) {\n'+textwrap.indent(code,'    ')+'\n    return 0;\n}\n'
        CHECKS.append(dict(key=key,source=source,kind=verify,output=output,stdin=stdin,runs=runs,files=files or {},expectedFiles=expectedFiles or {}))
    return row
