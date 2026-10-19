"""Verify full standalone programs, including screen fragments' complete context."""
import concurrent.futures,json,pathlib,subprocess,sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=pathlib.Path(__file__).resolve().parents[1];DEL=ROOT/'out';BUILD=ROOT/'build'/'examples';BUILD.mkdir(parents=True,exist_ok=True)
EX=DEL/'示例与习题';EX.mkdir(exist_ok=True)
course=json.loads((ROOT/'public/course.json').read_text(encoding='utf-8'))
local=ROOT/'content/approved_examples.json'
cases=json.loads(local.read_text(encoding='utf-8'))
for c in course['chapters']:
    for s in c['scenes']:
        for pi,p in enumerate(s.get('panels',[])):
            cases.append({'key':s['key']+'-panel-'+str(pi+1),'code':p['code'],'kind':'run','error':None,'output':p['output']})
        if s['section']=='04-3' and s['kind']=='answer':cases.append({'key':'04-3-fixed','code':s['code'],'kind':'run','error':None,'output':s['output']})
(ROOT/'content/example_manifest.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2),encoding='utf-8')
def verify(s):
    folder=EX/('错误示例' if s['kind']=='error' else '运行时恐慌示例' if s['kind']=='panic' else '正常示例');folder.mkdir(exist_ok=True)
    path=folder/(s['key']+'.rs');path.write_text(s['code'],encoding='utf-8')
    exe=BUILD/(s['key']+'.exe');compiled=subprocess.run(['rustc','--edition=2024','--crate-name','teaching_example',str(path),'-o',str(exe)],capture_output=True,text=True,encoding='utf-8',errors='replace')
    r={'key':s['key'],'kind':s['kind'],'expectedError':s['error'],'compileExitCode':compiled.returncode,'stderr':compiled.stderr,'passed':False}
    if s['kind']=='error':r['passed']=compiled.returncode!=0 and s['error'] in compiled.stderr
    elif compiled.returncode==0:
        ran=subprocess.run([str(exe)],capture_output=True,text=True,encoding='utf-8',errors='replace');r.update(output=ran.stdout,runExitCode=ran.returncode,runStderr=ran.stderr)
        r['passed']=(ran.returncode!=0 and 'panicked' in ran.stderr) if s['kind']=='panic' else ran.returncode==0 and ran.stdout==s['output']
    return r
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(verify,cases))
(ROOT/'build/verification.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
(EX/'验证详情.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# 初学者版示例验证','','环境：'+subprocess.check_output(['rustc','--version'],text=True).strip()+'；Rust 2024 Edition。','','跨屏代码在完整上下文中编译。正常示例核对输出；错误示例核对错误编号；panic 示例核对运行失败。','','| 示例 | 类型 | 结果 |','|---|---|---|']
lines.extend(f"| {r['key']} | {r['kind']} | {'通过' if r['passed'] else '失败'} |" for r in results)
(EX/'验证结果.md').write_text('\n'.join(lines),encoding='utf-8')
for r in results:
    if not r['passed']:print(json.dumps(r,ensure_ascii=False))
print(f'VERIFIED={sum(r["passed"] for r in results)}/{len(results)}',flush=True)
if not all(r['passed'] for r in results):sys.exit(1)
