import textwrap
CHAPTERS=[];CHECKS=[]
HEADERS='import java.util.Scanner;\nimport java.util.ArrayList;\nimport java.util.HashMap;\n'
def chapter(key,title,english,minutes):
    c=dict(key=key,title=title,english=english,targetMinutes=minutes,scenes=[]);CHAPTERS.append(c);return c
def scene(c,key,title,narration,code='',output=None,notes=None,diagram='roadmap',kind='lesson',context='',members='',runner=None,placement='member',full=None,stdin='',runs=None,verify='run',diagnostic=None,focus=None,filename='Main.java'):
    clean=lambda x:textwrap.dedent(x).strip('\n')
    code=clean(code);speech='\n\n'.join(x.strip().replace('\n','') for x in clean(narration).split('\n\n') if x.strip())
    if key.endswith('-a') and kind=='lesson':kind='answer'
    row=dict(key='java-'+key,section=key,title=title,sourceNarration=speech,narration=speech,code=code,output=output,notes=notes or [],diagram=diagram,kind=kind,error=diagnostic if verify=='compile_error' else None,panic=verify=='runtime_error',testFailed=False,hold=4 if kind=='question' else 1.5,focus=focus or [],panels=[],filename=filename,excerpt=bool(code and not code.startswith('public class Main') and filename!='终端命令'))
    c['scenes'].append(row)
    if code and verify:
        top=clean(context);methods=clean(members)
        if full:source=clean(full)
        else:
            body=code if runner is None else clean(runner)
            if runner is not None:
                if placement=='type':top+='\n'+code
                else:methods+='\n'+code
            source=HEADERS+top+'\npublic class Main {\n'+methods+'\npublic static void main(String[] args) {\n'+body+'\n}\n}\n'
        CHECKS.append(dict(key=key,source=source,kind=verify,expected=output,stdin=stdin,runs=runs,diagnostic=diagnostic))
    return row
