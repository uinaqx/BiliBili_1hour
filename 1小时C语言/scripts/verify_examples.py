"""Compile every complete C11 context and check outputs, input failures and file effects."""
import concurrent.futures,json,pathlib,subprocess,sys
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build/examples';BUILD.mkdir(parents=True,exist_ok=True)
DEL=ROOT/'out/C示例';DEL.mkdir(parents=True,exist_ok=True)
cases=json.loads((ROOT/'content/example_manifest.json').read_text(encoding='utf-8'))
def verify(c):
    folder=BUILD/c['key'];folder.mkdir(exist_ok=True);p=folder/'main.c';p.write_text(c['source'],encoding='utf-8');out=DEL/c['key'];out.mkdir(exist_ok=True);(out/'main.c').write_text(c['source'],encoding='utf-8')
    exe=folder/'example.exe';compiled=subprocess.run(['gcc','-std=c11','-Wall','-Wextra','-Werror','-pedantic','main.c','-o',str(exe)],cwd=folder,capture_output=True,text=True,encoding='utf-8',errors='replace')
    results=[];passed=compiled.returncode==0
    if passed:
        for trial in c.get('runs') or [dict(stdin=c['stdin'],output=c['output'],exitCode=0)]:
            for name,text in c['files'].items():
                target=folder/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8')
            ran=subprocess.run([str(exe)],cwd=folder,input=trial['stdin'],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=5)
            ok=ran.returncode==trial.get('exitCode',0) and ran.stdout==trial['output']
            for name,text in c['expectedFiles'].items():ok=ok and (folder/name).read_text(encoding='utf-8')==text
            passed=passed and ok;results.append(dict(passed=ok,stdin=trial['stdin'],output=ran.stdout,expected=trial['output'],exitCode=ran.returncode))
    for name,text in c['files'].items():(out/name).write_text(text,encoding='utf-8')
    (out/'测试输入与预期.json').write_text(json.dumps(c.get('runs') or [dict(stdin=c['stdin'],output=c['output'],exitCode=0)],ensure_ascii=False,indent=2),encoding='utf-8')
    return dict(key=c['key'],passed=passed,compileExitCode=compiled.returncode,diagnostics=compiled.stderr,runs=results)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(verify,cases))
report=dict(allPassed=all(r['passed'] for r in results),compiledExamples=len(results),runCases=sum(len(r['runs']) for r in results),compiler=subprocess.check_output(['gcc','--version'],text=True).splitlines()[0],standard='C11',results=results)
(ROOT/'build/example-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
for r in results:
    if not r['passed']:print(json.dumps(r,ensure_ascii=False))
print('C_EXAMPLES',sum(r['passed'] for r in results),'/',len(results),'run cases',report['runCases'],flush=True)
if not report['allPassed']:sys.exit(1)
