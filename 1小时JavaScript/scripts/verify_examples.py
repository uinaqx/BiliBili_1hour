import concurrent.futures,http.server,json,pathlib,subprocess,threading,functools
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
def main():
    course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));scenes=[s for c in course['chapters'] for s in c['scenes']];results=[]
    for s in scenes:
        if s['kind']=='html':continue
        p=ROOT/'examples'/s['key'];r=subprocess.run(['node','main.mjs'],cwd=p,capture_output=True,text=True,encoding='utf8',timeout=10)
        expected=s['output'].replace('\\n','\n')+'\n';assert r.returncode==0 and r.stdout==expected,(s['key'],r.stdout,expected,r.stderr)
        results.append(dict(key=s['key'],passed=True,output=r.stdout,runtime='Node'))
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'examples')));threading.Thread(target=server.serve_forever,daemon=True).start();base=f'http://127.0.0.1:{server.server_port}'
    with sync_playwright() as pw:
        installed=sorted((pathlib.Path.home()/'AppData/Local/ms-playwright').glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'))
        browser=pw.chromium.launch(headless=True,**({'executable_path':str(installed[-1])} if installed else {}));page=browser.new_page();logs=[];page.on('console',lambda msg:logs.append(msg.text))
        for s in scenes:
            if s['kind']!='html':continue
            logs.clear();page.goto(base+'/'+s['key']+'/index.html');key=s['key']
            if key=='js-08-01':page.click('#add');actual=page.locator('#message').inner_text();expected='已记录'
            elif key=='js-08-02':page.click('#add');page.click('#add');actual=page.locator('#count').inner_text();expected='2'
            elif key=='js-08-03':page.click('#add');actual=page.locator('#message').inner_text();expected='20元'
            elif key=='js-08-05':page.click('button');actual=page.locator('#message').inner_text();expected='收到：午餐'
            else:actual='\n'.join(logs);expected={'js-01-03':'网页已打开'}.get(key,s['output'])
            assert actual==expected,(key,actual,expected);results.append(dict(key=key,passed=True,output=actual,runtime='Chromium'))
        page.goto(base+'/完整项目/');page.wait_for_function("document.querySelector('#summary').textContent.length > 0");page.click('#reset')
        def add(name,amount):page.fill('#name',name);page.fill('#amount',amount);page.click('#form button')
        add('午餐','12');add('交通','8');assert '总额：20元；余额：10元' in page.locator('#summary').inner_text(),(page.locator('#summary').inner_text(),page.locator('#message').inner_text(),logs)
        page.locator('#list button').first.click();assert '总额：8元；余额：22元' in page.locator('#summary').inner_text()
        page.reload();assert page.locator('#list li').count()==1 and '交通' in page.locator('#list').inner_text()
        for amount in ['', 'abc', '-1']:
            add('测试',amount);assert page.locator('#list li').count()==1
        add('免费','0');assert page.locator('#list li').count()==2
        add('<b>文字</b>','2');assert page.locator('#list b').count()==0
        page.evaluate('localStorage.setItem("javascript-course-expenses-v1", "broken")');page.reload();assert page.locator('#list li').count()==0 and page.locator('#message').inner_text()
        page.click('#reset');page.reload();assert '总额：0元' in page.locator('#summary').inner_text()
        page.screenshot(path=str(ROOT/'build/project-browser.png'),full_page=True)
        browser.close()
    server.shutdown();report=dict(allPassed=True,examples=len(results),nodeVersion=subprocess.check_output(['node','--version'],text=True).strip(),projectChecks=['add','delete','reload','empty','NaN','negative','zero','literal HTML text','corrupt storage','reset'],results=results)
    (ROOT/'build/example-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('EXAMPLES_VERIFIED',len(results),'PROJECT_CHECKS',10,flush=True)
if __name__=='__main__':main()
