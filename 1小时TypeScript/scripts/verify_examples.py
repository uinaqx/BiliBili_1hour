"""Export and genuinely compile/run each displayed original/corrected example."""
import concurrent.futures,json,pathlib,subprocess,sys,threading,http.server,socketserver,functools
ROOT=pathlib.Path(__file__).resolve().parents[1];EX=ROOT/'examples';COMPILER=ROOT/'node_modules/typescript/lib/tsc.js'
def load(p):return json.loads(p.read_text(encoding='utf8'))
def compile(folder,files,module='commonjs',out='out'):
 return subprocess.run(['node',str(COMPILER),'--strict','--noEmitOnError','--skipLibCheck','--target','ES2022','--module',module,'--outDir',out,*files],cwd=folder,capture_output=True,text=True,encoding='utf8')
def case(s):
 folder=EX/s['key'];folder.mkdir(parents=True,exist_ok=True);code=s['code']+'\n'
 files=['main.ts'];module='commonjs'
 if s['kind']=='module':
  budget,main=code.split('// main.ts\n');(folder/'budget.ts').write_text(budget,encoding='utf8');code=main;files+=['budget.ts']
 if s['kind']=='dom':module='ES2022'
 (folder/'main.ts').write_text(code+'\nexport {};\n',encoding='utf8')
 result=compile(folder,files,module);diagnostic=result.stdout+result.stderr
 if s.get('diagnostic'):
  assert result.returncode and s['diagnostic'] in diagnostic,(s['key'],'expected error',diagnostic)
  (folder/'expected-error.txt').write_text(diagnostic.replace(str(folder),'.'),encoding='utf8')
  (folder/'fixed.ts').write_text(s['answerCode']+'\nexport {};\n',encoding='utf8')
  result=compile(folder,['fixed.ts']);assert not result.returncode,(s['key'],result.stdout,result.stderr)
  entry='fixed.js'
 else:
  assert not result.returncode,(s['key'],result.stdout,result.stderr);entry='main.js'
 if module=='commonjs':
  run=subprocess.run(['node',str(folder/'out'/entry)],capture_output=True,text=True,encoding='utf8');assert not run.returncode,(s['key'],run.stderr)
  actual=run.stdout.strip();assert actual==s['output'].replace('\\n','\n'),(s['key'],actual,s['output'])
 else:
  (folder/'index.html').write_text('<!doctype html><meta charset="utf-8">'+s['fixtures']['html']+'<script type="module" src="out/main.js"></script>',encoding='utf8');actual='BROWSER_PENDING'
 (folder/'README.md').write_text('# '+s['title']+'\n\n'+''.join(p['text']+'\n\n' for p in s['parts'])+'## 本页总结\n\n'+''.join('- '+n+'\n' for n in s['notes'])+'\n## 预期输出\n\n```text\n'+s['output']+'\n```\n',encoding='utf8')
 return dict(key=s['key'],title=s['title'],kind=s['kind'],expectedError=s.get('diagnostic'),output=actual,passed=True)
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
def browser_cases(scenes,reports):
 from playwright.sync_api import sync_playwright
 executable=sorted((pathlib.Path.home()/'AppData/Local/ms-playwright').glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'))[-1]
 with socketserver.TCPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(EX))) as server:
  threading.Thread(target=server.serve_forever,daemon=True).start()
  with sync_playwright() as p:
   b=p.chromium.launch(headless=True,executable_path=str(executable));page=b.new_page()
   for s in scenes:
    if s['kind']!='dom':continue
    messages=[];errors=[];page.on('console',lambda m:messages.append(m.text));page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(f'http://127.0.0.1:{server.server_address[1]}/{s["key"]}/');page.wait_for_timeout(300)
    assert not errors and '\n'.join(messages)==s['output'],(s['key'],messages,errors)
    next(r for r in reports if r['key']==s['key'])['output']='\n'.join(messages)
   b.close()
  server.shutdown()
def main():
 scenes=[s for c in load(ROOT/'public/course.json')['chapters'] for s in c['scenes']]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:reports=list(pool.map(case,scenes))
 browser_cases(scenes,reports)
 data=dict(allPassed=True,typescriptVersion=subprocess.check_output(['node',str(COMPILER),'--version'],text=True).strip(),nodeVersion=subprocess.check_output(['node','--version'],text=True).strip(),cases=reports,compileErrorCases=sum(bool(x['expectedError']) for x in reports),browserCases=sum(x['kind']=='dom' for x in reports))
 (ROOT/'build/example-verification.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8');print('VERIFIED_EXAMPLES',len(reports),flush=True)
if __name__=='__main__':main()
