import concurrent.futures,json,pathlib,re,subprocess,sys,tempfile
from toolchain import ROOT,commands,java
sys.stdout.reconfigure(encoding='utf8')
def main():
    compiler,cp=commands();out=ROOT/'build/examples';out.mkdir(parents=True,exist_ok=True)
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'))
    expected={'kt-01-03':'你好，小林\n85','kt-03-06':'82\n10','kt-04-07':'7','kt-05-05':'80','kt-06-06':'90\n2','kt-07-05':'-1','kt-08-06':'90','kt-09-05':'[60, 62, 92]','kt-10-06':'你的成绩：0'}
    checks=[]
    for c in course['chapters']:
        for s in c['scenes']:
            if not s['code']:continue
            entry=dict(key=s['key'],source=s['source'],expected=expected[s['key']] if s['kind']=='question' and s['key'] in expected else s['output'],stdin=s['stdin'],mode='run')
            if s['key']=='kt-02-06':entry.update(mode='compile_error',diagnostic='VAL_REASSIGNMENT')
            checks.append(entry)
    checks.extend([
        dict(key='error-nullable',source='fun main() { val text: String? = null; println(text.length) }',mode='compile_error',diagnostic='UNSAFE_CALL'),
        dict(key='runtime-assertion',source='fun main() { val text: String? = null; println(text!!.length) }',mode='runtime_error',diagnostic='NullPointerException',stdin='')
    ])
    sources=[]
    for x in checks:
        d=out/x['key'];d.mkdir(exist_ok=True);p=d/'Main.kt'
        x['package']='lessons.'+x['key'].replace('-','_');p.write_text('package '+x['package']+'\n'+x['source']+'\n',encoding='utf8');x['path']=p
        if x['mode']!='compile_error':sources.append(str(p))
    jar=out/'examples.jar'
    args=compiler+['-no-stdlib','-no-reflect','-classpath',cp,'-jvm-target','17','-Xrender-internal-diagnostic-names','-d',str(jar),*sources]
    result=subprocess.run(args,capture_output=True,text=True,encoding='utf8',errors='replace')
    (out/'compile.txt').write_text(result.stdout+result.stderr,encoding='utf8')
    if result.returncode:print(result.stderr[-8000:]);raise RuntimeError('Normal examples failed to compile')
    records=[]
    for x in checks:
        if x['mode']=='compile_error':
            r=subprocess.run(compiler+['-no-stdlib','-no-reflect','-classpath',cp,'-Xrender-internal-diagnostic-names','-d',str(out/(x['key']+'.jar')),str(x['path'])],capture_output=True,text=True,encoding='utf8',errors='replace')
            good=r.returncode!=0 and x['diagnostic'] in r.stderr
            (x['path'].parent/'diagnostic.txt').write_text(r.stderr,encoding='utf8')
            records.append(dict(key=x['key'],kind=x['mode'],passed=good,diagnostic=x['diagnostic']))
        else:
            with tempfile.TemporaryDirectory(prefix='kotlin-lesson-',dir=out) as temp:
                r=subprocess.run([java(),'-Dfile.encoding=UTF-8','-Dstdout.encoding=UTF-8','-Dstderr.encoding=UTF-8','-cp',str(jar)+__import__('os').pathsep+cp,x['package']+'.MainKt'],cwd=temp,input=x.get('stdin',''),capture_output=True,text=True,encoding='utf8',errors='replace',timeout=15)
            output=r.stdout.replace('\r\n','\n').rstrip('\n')
            good=(r.returncode!=0 and x['diagnostic'] in r.stderr) if x['mode']=='runtime_error' else r.returncode==0 and output==x['expected']
            records.append(dict(key=x['key'],kind=x['mode'],passed=good,actual=output,expected=x.get('expected'),stderr=r.stderr if not good else ''))
        print('EXAMPLE',x['key'],'PASS' if good else 'FAIL',flush=True)
    report=dict(allPassed=all(r['passed'] for r in records),checks=len(records),results=records)
    (ROOT/'build/example-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    rows=['# 示例与习题答案','','每个目录包含 Main.kt。错误例子与正常程序分开，完整检查结果见制作记录。','']
    for x,r in zip(checks,records):
        rows.extend(['## '+x['key'],'','```kotlin',x['source'],'```','','预期类别：'+x['mode'],''])
        if x.get('expected') is not None:rows.extend(['```text',x['expected'],'```',''])
        if x.get('diagnostic'):rows.extend(['验证的错误类别：'+x['diagnostic'],''])
    text='\n'.join(rows);(ROOT/'content/示例与习题答案.md').write_text(text,encoding='utf8');(ROOT/'out/示例与习题答案.md').write_text(text,encoding='utf8')
    print('EXAMPLES_DONE',len(records),report['allPassed'],flush=True)
    if not report['allPassed']:raise SystemExit(1)
if __name__=='__main__':main()
