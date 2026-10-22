"""Compile and run every independent example; expected failures are separate."""
import concurrent.futures,json,os,pathlib,shutil,subprocess,tempfile,unicodedata
ROOT=pathlib.Path(__file__).resolve().parents[1]
DEL=ROOT/'out'
def norm(s):return s.replace('\r\n','\n').rstrip('\n')
def main():
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))
    go=ROOT/'build/toolchain/go/bin/go.exe'
    if not go.exists():go=shutil.which('go')
    if not go:raise RuntimeError('Install Go and add its bin folder to PATH')
    go=str(go);gofmt=str(pathlib.Path(go).with_name('gofmt.exe' if os.name=='nt' else 'gofmt'))
    temp_root=ROOT/'build/go-temp';temp_root.mkdir(parents=True,exist_ok=True)
    env=os.environ.copy();env.update(GOTOOLCHAIN='local',GOPROXY='off',GOCACHE=str(ROOT/'build/go-cache'),GOTMPDIR=str(temp_root))
    version=subprocess.check_output([go,'version'],env=env,text=True).strip()
    cases=[]
    for c in course['chapters']:
        for s in c['scenes']:
            if not s['verify']:continue
            # Check visual line length before any expensive rendering.
            for i,line in enumerate(s['code'].splitlines(),1):
                width=sum(2 if unicodedata.east_asian_width(x) in 'WF' else 1 for x in line)
                assert width<=60,('Display line too wide',s['key'],i,width)
            assert len(s['code'].splitlines())<=12,('Display too tall',s['key'])
            expected=s['answer'] if s['kind']=='question' else s['output']
            cases.append(dict(key=s['key'],source=s['source'],stdin=s['stdin'],mode=s['mode'],diagnostic=s['diagnostic'],expected=expected,lesson=True))
    def add(key,body,expected=None,mode='run',diagnostic=None,stdin=''):
        source='package main\nimport "fmt"\nfunc main(){\n'+body+'\n}\n'
        cases.append(dict(key=key,source=source,stdin=stdin,mode=mode,diagnostic=diagnostic,expected=expected,lesson=False))
    add('unused-local','value := 1\nfmt.Println("test")',mode='compile_error',diagnostic='declared and not used')
    add('repeat-short-declaration','score := 80\nscore := 90\nfmt.Println(score)',mode='compile_error',diagnostic='no new variables on left side of :=')
    add('non-bool-condition','if 1 { fmt.Println("yes") }',mode='compile_error',diagnostic='non-boolean condition')
    add('nil-map-write','var scores map[string]int\nscores["小林"]=85\nfmt.Println(scores)',mode='runtime_error',diagnostic='assignment to entry in nil map')
    add('nil-pointer','var score *int\nfmt.Println(*score)',mode='runtime_error',diagnostic='invalid memory address or nil pointer dereference')
    add('slice-out-of-range','scores:=[]int{80}\nindex:=2\nfmt.Println(scores[index])',mode='runtime_error',diagnostic='index out of range')
    original=next(x for x in cases if x['key']=='go-03-05')
    cases.append(dict(original,key='invalid-scan-input',stdin='hello\n',expected='请输入整数',lesson=False))
    binaries=ROOT/'build/example-bin';binaries.mkdir(parents=True,exist_ok=True)
    def verify(c):
        folder=ROOT/'examples'/('expected-failures' if c['mode']!='run' else 'normal')/c['key'];folder.mkdir(parents=True,exist_ok=True)
        source=folder/'main.go';source.write_text(c['source'],encoding='utf8')
        fmt=subprocess.run([gofmt,'-w',str(source)],capture_output=True,text=True,encoding='utf8',env=env,timeout=30)
        assert fmt.returncode==0,(c['key'],'gofmt',fmt.stderr)
        binary=binaries/(c['key']+('.exe' if os.name=='nt' else ''))
        build=subprocess.run([go,'build','-o',str(binary),str(source)],capture_output=True,text=True,encoding='utf8',env=env,timeout=180)
        if c['mode']=='compile_error':
            passed=build.returncode!=0 and c['diagnostic'] in build.stderr
            result=dict(key=c['key'],mode=c['mode'],passed=passed,diagnostic=c['diagnostic'],observed=build.stderr if not passed else 'expected compilation failure confirmed')
        else:
            assert build.returncode==0,(c['key'],'build',build.stderr)
            with tempfile.TemporaryDirectory(prefix='go-course-',dir=temp_root) as cwd:
                run=subprocess.run([str(binary)],input=c['stdin'],capture_output=True,text=True,encoding='utf8',cwd=cwd,env=env,timeout=15)
            if c['mode']=='runtime_error':
                passed=run.returncode!=0 and c['diagnostic'] in run.stderr
                result=dict(key=c['key'],mode=c['mode'],passed=passed,diagnostic=c['diagnostic'],observed=run.stderr if not passed else 'expected runtime panic confirmed')
            else:
                passed=run.returncode==0 and norm(run.stdout)==norm(c['expected'])
                result=dict(key=c['key'],mode=c['mode'],passed=passed,expected=c['expected'],actual=norm(run.stdout),stderr=run.stderr)
        print('EXAMPLE',c['key'],'PASS' if result['passed'] else 'FAIL',flush=True)
        return result
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(verify,cases))
    report=dict(allPassed=all(x['passed'] for x in results),toolchain=version,lessonCases=sum(x['lesson'] for x in cases),supplementalCases=sum(not x['lesson'] for x in cases),cases=results)
    (ROOT/'build/example-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    rows=['# Go 课程示例与习题答案','',version,'','每个 main.go 都是可独立运行的完整程序。错误示例放在 expected-failures 中。文件操作在临时目录验证。','']
    for c in cases:
        rows.extend(['## '+c['key'],'','```go',c['source'].strip(),'```',''])
        if c['stdin']:rows.extend(['标准输入：','```text',c['stdin'].strip(),'```',''])
        if c['mode']=='run':rows.extend(['预期输出：','```text',c['expected'],'```',''])
        else:rows.extend(['预期类别：'+c['mode']+'；关键诊断：'+c['diagnostic'],''])
    material='\n'.join(rows)+'\n'
    (ROOT/'content/示例与习题答案.md').write_text(material,encoding='utf8');(DEL/'示例与习题答案.md').write_text(material,encoding='utf8')
    print('VERIFICATION',len(results),report['allPassed'],version,flush=True)
    if not report['allPassed']:raise SystemExit(1)
if __name__=='__main__':main()
