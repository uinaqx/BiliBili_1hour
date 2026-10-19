import concurrent.futures,json,pathlib,re,subprocess,sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build/examples';BUILD.mkdir(parents=True,exist_ok=True)
DEL=ROOT/'out/示例与习题';DEL.mkdir(parents=True,exist_ok=True)
cases=json.loads((ROOT/'content/example_manifest.json').read_text(encoding='utf-8'))
def run(cmd,cwd):
    return subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,encoding='utf-8',errors='replace')
def verify(c):
    key=c['key'];kind=c['kind'];folder=BUILD/key;folder.mkdir(exist_ok=True)
    out=DEL/key;out.mkdir(exist_ok=True)
    source=c.get('files') or {'main.rs':c['code']}
    for name,text in source.items():
        for target in (folder/name,out/name):target.parent.mkdir(parents=True,exist_ok=True);target.write_text(text,encoding='utf-8')
    cargo=kind.startswith('clippy')
    if cargo:
        manifest='[package]\nname="teaching_example"\nversion="0.1.0"\nedition="2024"\n\n[[bin]]\nname="example"\npath="main.rs"\n'
        (folder/'Cargo.toml').write_text(manifest,encoding='utf-8');(out/'Cargo.toml').write_text(manifest,encoding='utf-8')
        result=run(['cargo','clippy','--offline','--']+(['-W','clippy::useless_vec'] if kind=='clippy_warn' else ['-D','warnings']),folder)
        has_lint='useless_vec' in result.stderr or 'useless-vec' in result.stderr
        passed=result.returncode==0 and (has_lint if kind=='clippy_warn' else not has_lint)
        ran=run(['cargo','run','--offline','--quiet'],folder)
        passed=passed and ran.returncode==0 and ran.stdout=='3\n'
        r=dict(key=key,kind=kind,passed=passed,compileExitCode=result.returncode,stderr=result.stderr,output=ran.stdout,runExitCode=ran.returncode)
    elif kind.startswith('test_'):
        manifest='[package]\nname="teaching_example"\nversion="0.1.0"\nedition="2024"\n\n[lib]\npath="main.rs"\n'
        for target in (folder/'Cargo.toml',out/'Cargo.toml'):target.write_text(manifest,encoding='utf-8')
        result=run(['cargo','test','--offline','--','--test-threads=1'],folder)
        passed=(result.returncode==0 and 'test result: ok.' in result.stdout) if kind=='test_pass' else result.returncode!=0 and 'FAILED' in result.stdout
        r=dict(key=key,kind=kind,passed=passed,output=result.stdout,stderr=result.stderr,runExitCode=result.returncode)
    else:
        exe=folder/'example.exe';cmd=['rustc','--edition=2024','--crate-name','teaching_example','main.rs','-o',str(exe)]
        if kind.startswith('test_'):cmd.insert(1,'--test')
        compiled=run(cmd,folder)
        r=dict(key=key,kind=kind,passed=False,compileExitCode=compiled.returncode,stderr=compiled.stderr)
        if kind=='error':r['passed']=compiled.returncode!=0 and c['error'] in compiled.stderr
        elif compiled.returncode==0:
            ran=run([str(exe)]+(['--test-threads=1'] if kind.startswith('test_') else []),folder)
            r.update(output=ran.stdout,runStderr=ran.stderr,runExitCode=ran.returncode)
            if kind=='panic':r['passed']=ran.returncode!=0 and 'panicked' in ran.stderr
            elif kind=='test_pass':r['passed']=ran.returncode==0 and 'test result: ok.' in ran.stdout
            elif kind=='test_fail':r['passed']=ran.returncode!=0 and 'FAILED' in ran.stdout
            else:r['passed']=ran.returncode==0 and ran.stdout in (c['output'] if isinstance(c['output'],list) else [c['output']])
    return r
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(verify,cases))
(ROOT/'build/verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
(DEL/'验证详情.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for r in results:
    if not r['passed']:print(json.dumps(r,ensure_ascii=False))
print(f'VERIFIED={sum(r["passed"] for r in results)}/{len(results)}',flush=True)
if not all(r['passed'] for r in results):sys.exit(1)
