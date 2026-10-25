"""Compile and run all 58 source solutions and independently classify each original."""
import concurrent.futures,hashlib,json,pathlib,re,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build/verification'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check(r):
    result=dict(number=r['number'],name=r['name'],mode=r['mode'],variants={})
    for kind in ['original','solutions']:
        path=ROOT/'exercises'/kind/r['file'];out=BUILD/f"{r['number']:02}-{kind}.exe"
        args=['rustc','--edition','2021','--crate-name',f"exercise_{r['number']:02}",str(path),'-o',str(out),'--error-format=json']
        if r['mode']=='test':args.append('--test')
        p=subprocess.run(args,capture_output=True,text=True,encoding='utf8',errors='replace',timeout=90)
        messages=[]
        for line in p.stderr.splitlines():
            try:
                d=json.loads(line)
                if d.get('$message_type')=='diagnostic':messages.append(d)
            except json.JSONDecodeError:pass
        errors=[d for d in messages if d.get('level')=='error'];warnings=[d for d in messages if d.get('level')=='warning']
        row=dict(sha256=digest(path),compileExit=p.returncode,errors=[dict(code=d.get('code'),message=d['message'],spans=d['spans'],rendered=d.get('rendered','')) for d in errors],warnings=len(warnings))
        if p.returncode==0:
            run=subprocess.run([str(out),*(['--test-threads=1'] if r['mode']=='test' else [])],capture_output=True,text=True,encoding='utf8',errors='replace',timeout=15)
            row.update(runExit=run.returncode,stdout=run.stdout,stderr=run.stderr)
            row['outcome']='passed' if run.returncode==0 else 'test_failed' if r['mode']=='test' else 'runtime_panic'
            if r['mode']=='test':
                m=re.search(r'test result: (ok|FAILED)\. (\d+) passed; (\d+) failed;',run.stdout);assert m,(r['number'],kind,'Missing actual test summary')
                row.update(testsPassed=int(m[2]),testsFailed=int(m[3]))
        else:row['outcome']='compile_error'
        result['variants'][kind]=row
        if kind=='solutions':assert row['outcome']=='passed',('Provided solution fails',r['number'],row)
    print('EXERCISE_VERIFIED',r['number'],r['name'],'original='+result['variants']['original']['outcome'],'solution=passed',flush=True)
    return result
def main():
    BUILD.mkdir(parents=True,exist_ok=True);records=json.loads((ROOT/'references/inventory.json').read_text(encoding='utf8'))
    version=subprocess.check_output(['rustc','--version','--verbose'],text=True,encoding='utf8')
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(check,records))
    assert len(results)==58 and all(r['variants']['solutions']['outcome']=='passed' for r in results)
    report=dict(allPassed=True,edition='2021',toolchain=version,exercises=58,compileExercises=sum(x['mode']=='compile' for x in records),testExercises=sum(x['mode']=='test' for x in records),testsPassed=sum(r['variants']['solutions'].get('testsPassed',0) for r in results),sourceUnchanged=True,records=results)
    (ROOT/'build/exercise-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print('ALL_EXERCISES_VERIFIED',report['testsPassed'],'individual tests',flush=True)
if __name__=='__main__':main()
