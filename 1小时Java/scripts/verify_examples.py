"""Compile complete Java programs; isolate compilation errors and runtime exceptions."""
import concurrent.futures,json,pathlib,subprocess,sys
from java_tools import command
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build/examples';BUILD.mkdir(parents=True,exist_ok=True);DEL=ROOT/'out/Java示例';DEL.mkdir(parents=True,exist_ok=True)
cases=json.loads((ROOT/'content/example_manifest.json').read_text(encoding='utf-8'));JAVAC=command('javac');JAVA=command('java')
def check(c):
    folder=BUILD/c['key'];folder.mkdir(exist_ok=True);out=DEL/c['key'];out.mkdir(exist_ok=True)
    for p in (folder/'Main.java',out/'Main.java'):p.write_text(c['source'],encoding='utf-8')
    compile=subprocess.run([JAVAC,'-J-Duser.language=en','-J-Duser.country=US','-encoding','UTF-8','--release','21','-Xlint:all','-Werror','Main.java'],cwd=folder,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=30)
    runs=[]
    if c['kind']=='compile_error':passed=compile.returncode!=0 and c['diagnostic'] in compile.stderr
    else:
        passed=compile.returncode==0
        if passed:
            for trial in c.get('runs') or [dict(stdin=c['stdin'],expected=c['expected'],exitCode=0)]:
                r=subprocess.run([JAVA,'-Dfile.encoding=UTF-8','-Dstdout.encoding=UTF-8','-Dstderr.encoding=UTF-8','-cp',str(folder),'Main'],cwd=folder,input=trial['stdin'],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=5)
                ok=(r.returncode!=0 and c['diagnostic'] in r.stderr) if c['kind']=='runtime_error' else (r.returncode==trial.get('exitCode',0) and r.stdout==trial['expected'])
                passed=passed and ok;runs.append(dict(passed=ok,input=trial['stdin'],output=r.stdout,expected=trial['expected'],stderr=r.stderr,exitCode=r.returncode))
    (out/'预期行为.json').write_text(json.dumps(dict(kind=c['kind'],expected=c['expected'],stdin=c['stdin'],runs=c['runs'],diagnostic=c['diagnostic']),ensure_ascii=False,indent=2),encoding='utf-8')
    return dict(key=c['key'],kind=c['kind'],passed=passed,compileExitCode=compile.returncode,diagnostics=compile.stderr,runs=runs)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(check,cases))
report=dict(allPassed=all(x['passed'] for x in results),cases=len(results),normalPrograms=sum(x['kind']=='run' for x in results),expectedCompileErrors=sum(x['kind']=='compile_error' for x in results),expectedRuntimeExceptions=sum(x['kind']=='runtime_error' for x in results),runCases=sum(len(x['runs']) for x in results),compiler=subprocess.check_output([JAVAC,'-version'],text=True,stderr=subprocess.STDOUT).strip(),results=results)
(ROOT/'build/example-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
for r in results:
    if not r['passed']:print(json.dumps(r,ensure_ascii=False))
print('JAVA_VERIFIED',sum(x['passed'] for x in results),'/',len(results),flush=True)
if not report['allPassed']:sys.exit(1)
