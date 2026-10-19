"""Run complete scripts independently, including deliberate syntax and runtime errors."""
import concurrent.futures,json,pathlib,subprocess,sys
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build/examples';BUILD.mkdir(parents=True,exist_ok=True);DEL=ROOT/'out/Python示例';DEL.mkdir(parents=True,exist_ok=True)
cases=json.loads((ROOT/'content/example_manifest.json').read_text(encoding='utf-8'))
def local(folder,name):
    p=(folder/name).resolve();assert p.parent==folder.resolve();return p
def check(c):
    folder=BUILD/c['key'];folder.mkdir(exist_ok=True);out=DEL/c['key'];out.mkdir(exist_ok=True)
    for p in (folder/'main.py',out/'main.py'):p.write_text(c['source'],encoding='utf-8')
    for name,text in c['fixtures'].items():
        for base in (folder,out):local(base,name).write_text(text,encoding='utf-8')
    compile=subprocess.run([sys.executable,'-I','-X','utf8','-c','import py_compile; py_compile.compile("main.py", doraise=True)'],cwd=folder,capture_output=True,text=True,encoding='utf-8',timeout=10)
    trials=[]
    if c['kind']=='syntax_error':passed=compile.returncode!=0 and c['diagnostic'] in compile.stderr
    else:
        passed=compile.returncode==0
        if passed:
            for trial in c.get('runs') or [dict(stdin=c['stdin'],expected=c['expected'],exitCode=0)]:
                r=subprocess.run([sys.executable,'-s','-E','-X','utf8','main.py'],cwd=folder,input=trial['stdin'],capture_output=True,text=True,encoding='utf-8',timeout=5)
                ok=(r.returncode!=0 and c['diagnostic'] in r.stderr) if c['kind']=='runtime_error' else (r.returncode==trial.get('exitCode',0) and r.stdout==trial['expected'])
                actual_files={name:local(folder,name).read_text(encoding='utf-8') if local(folder,name).exists() else None for name in c['files']}
                ok=ok and actual_files==c['files'];passed=passed and ok;trials.append(dict(passed=ok,input=trial['stdin'],output=r.stdout,expected=trial['expected'],stderr=r.stderr,exitCode=r.returncode,files=actual_files))
    (out/'预期行为.json').write_text(json.dumps({k:c[k] for k in ('kind','expected','stdin','runs','diagnostic','fixtures','files')},ensure_ascii=False,indent=2),encoding='utf-8')
    return dict(key=c['key'],kind=c['kind'],passed=passed,syntaxExitCode=compile.returncode,diagnostics=compile.stderr,runs=trials)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(check,cases))
report=dict(allPassed=all(x['passed'] for x in results),cases=len(results),normalPrograms=sum(x['kind']=='run' for x in results),expectedSyntaxErrors=sum(x['kind']=='syntax_error' for x in results),expectedRuntimeExceptions=sum(x['kind']=='runtime_error' for x in results),runCases=sum(len(x['runs']) for x in results),interpreter=sys.version.split()[0],results=results)
(ROOT/'build/example-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
for r in results:
    if not r['passed']:print(json.dumps(r,ensure_ascii=False))
print('PYTHON_VERIFIED',sum(x['passed'] for x in results),'/',len(results),flush=True)
if not report['allPassed']:sys.exit(1)
