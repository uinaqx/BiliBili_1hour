import textwrap
CHAPTERS=[];CHECKS=[]
HEADERS='#include <iostream>\n#include <string>\n#include <stdexcept>\nusing std::cout;\nusing std::cin;\nusing std::string;\n'
def chapter(key,title,english,minutes):
    c=dict(key=key,title=title,english=english,targetMinutes=minutes,scenes=[]);CHAPTERS.append(c);return c
def scene(c,key,title,narration,code='',output=None,notes=None,diagram='roadmap',kind='lesson',context='',runner=None,full=None,stdin='',runs=None,verify='run',diagnostic=None,focus=None):
    clean=lambda x:textwrap.dedent(x).strip('\n')
    code=clean(code);speech='\n\n'.join(p.strip().replace('\n','') for p in clean(narration).split('\n\n') if p.strip())
    if key.endswith('-a') and kind=='lesson':kind='answer'
    row=dict(key='cpp-'+key,section=key,title=title,sourceNarration=speech,narration=speech.replace('C++','C 加加'),code=code,output=output,notes=notes or [],diagram=diagram,kind=kind,error=diagnostic if verify=='compile_error' else None,panic=False,testFailed=False,hold=4 if kind=='question' else 1.5,focus=focus or [],panels=[],filename='main.cpp',excerpt=bool(code and not code.startswith('#include')))
    c['scenes'].append(row)
    if code and verify:
        source=clean(full) if full else HEADERS+clean(context)+'\n'+(code+'\nint main() {\n'+clean(runner)+'\n}\n' if runner is not None else 'int main() {\n'+code+'\n}\n')
        CHECKS.append(dict(key=key,source=source,kind=verify,expected=output,stdin=stdin,runs=runs,diagnostic=diagnostic))
    return row
