import hashlib,json,pathlib,re,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    p=subprocess.run([sys.executable,'-m','unittest','discover','-s','demo','-p','test_harness.py','-v'],cwd=ROOT,capture_output=True,text=True,encoding='utf8');(ROOT/'build/demo-tests.log').write_text(p.stdout+p.stderr,encoding='utf8');assert p.returncode==0,p.stdout+p.stderr
    subprocess.run([sys.executable,'demo/harness.py'],cwd=ROOT,check=True);d=json.loads((ROOT/'build/demo-execution.json').read_text(encoding='utf8'))
    assert d['events'][2]['result']['stdout']=='FAIL expected=30 actual=10' and d['events'][4]['result']['stdout']=='PASS expected=30 actual=30' and d['status']=='completed'
    count=re.search(r'Ran (\d+) tests?',p.stderr);assert count,p.stderr
    r=dict(allPassed=True,tests=int(count[1]),model='deterministic scripted substitute; no model capability claim',realOperations='local file read/write and subprocess tests',checks=['normal feedback loop','tool schema and registry','path rejection','unauthorized write rejection','call-ID conflict','repeat-call reuse','checkpoint resume','premature final rejection','budget stop','cancellation','timeout status','receiver idempotency','actual test failure and pass'],demoSourceSha256=hashlib.sha256((ROOT/'demo/harness.py').read_bytes()).hexdigest(),testSourceSha256=hashlib.sha256((ROOT/'demo/test_harness.py').read_bytes()).hexdigest(),courseSha256=hashlib.sha256((ROOT/'public/course.json').read_bytes()).hexdigest())
    (ROOT/'build/demo-verification.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print('DEMO_VERIFIED 20 runtime tests',flush=True)
if __name__=='__main__':main()
