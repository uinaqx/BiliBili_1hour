"""Compile and run the exact displayed C++ snippets in complete contexts."""
import concurrent.futures,json,pathlib,subprocess,sys
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build/examples';BUILD.mkdir(parents=True,exist_ok=True)
manifest=json.loads((ROOT/'content/example_manifest.json').read_text(encoding='utf-8'))
def norm(t):return '\n'.join(line.rstrip() for line in t.strip().splitlines())
def work(m):
    src=BUILD/(m['key']+'.cpp');exe=BUILD/(m['key']+'.exe');src.write_text(m['source'],encoding='utf-8')
    c=subprocess.run(['g++','-std=c++14','-O2','-Wall','-Wextra','-pedantic',str(src),'-o',str(exe)],capture_output=True,text=True,encoding='utf-8',errors='replace')
    if c.returncode:raise RuntimeError(m['key']+' compile: '+c.stderr[-1500:])
    r=subprocess.run([str(exe)],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=5)
    assert r.returncode==0 and norm(r.stdout)==norm(m['expected']),(m['key'],r.stdout,m['expected'],r.stderr)
    return dict(key=m['key'],compiled=True,ran=True,output=r.stdout,warnings=c.stderr)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(work,manifest))
(ROOT/'build/example-validation.json').write_text(json.dumps(dict(compiler='MinGW GCC 6.3, C++14',cases=len(results),allPassed=True,results=results),ensure_ascii=False,indent=2),encoding='utf-8')
print('EXAMPLES_PASSED',len(results))
