"""Compile complete C++14 contexts; distinguish expected compile errors, warnings and runtime outputs."""
import concurrent.futures,json,pathlib,re,subprocess,sys
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build/examples';BUILD.mkdir(parents=True,exist_ok=True);DEL=ROOT/'out/C++示例';DEL.mkdir(parents=True,exist_ok=True)
cases=json.loads((ROOT/'content/example_manifest.json').read_text(encoding='utf-8'))
def check(c):
    folder=BUILD/c['key'];folder.mkdir(exist_ok=True);out=DEL/c['key'];out.mkdir(exist_ok=True)
    for target in (folder/'main.cpp',out/'main.cpp'):target.write_text(c['source'],encoding='utf-8')
    exe=folder/'example.exe';flags=['-std=c++14','-Wall','-Wextra','-Werror','-pedantic']
    if c['kind']=='reorder_warning':flags.append('-Wno-error=reorder')
    compile=subprocess.run(['g++',*flags,'main.cpp','-o',str(exe)],cwd=folder,capture_output=True,text=True,encoding='utf-8',errors='replace')
    runs=[]
    if c['kind']=='compile_error':passed=compile.returncode!=0 and c['diagnostic'] in compile.stderr
    else:
        passed=compile.returncode==0
        if c['kind']=='reorder_warning':passed=passed and 'reorder' in compile.stderr
        if passed:
            for trial in c.get('runs') or [dict(stdin=c['stdin'],expected=c['expected'],exitCode=0)]:
                r=subprocess.run([str(exe)],cwd=folder,input=trial['stdin'],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=5);ok=r.returncode==trial.get('exitCode',0) and r.stdout==trial['expected'];passed=passed and ok;runs.append(dict(passed=ok,input=trial['stdin'],output=r.stdout,expected=trial['expected'],exitCode=r.returncode))
    (out/'预期行为.json').write_text(json.dumps(dict(kind=c['kind'],expected=c['expected'],stdin=c['stdin'],runs=c['runs'],diagnostic=c['diagnostic']),ensure_ascii=False,indent=2),encoding='utf-8')
    return dict(key=c['key'],kind=c['kind'],passed=passed,compileExitCode=compile.returncode,diagnostics=compile.stderr,runs=runs)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(check,cases))
report=dict(allPassed=all(x['passed'] for x in results),cases=len(results),normalPrograms=sum(x['kind']!='compile_error' for x in results),expectedCompileErrors=sum(x['kind']=='compile_error' for x in results),runCases=sum(len(x['runs']) for x in results),compiler=subprocess.check_output(['g++','--version'],text=True).splitlines()[0],results=results)
(ROOT/'build/example-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
for x in results:
    if not x['passed']:print(json.dumps(x,ensure_ascii=False))
print('CPP_VERIFIED',sum(x['passed'] for x in results),'/',len(results),flush=True)
if not report['allPassed']:sys.exit(1)
