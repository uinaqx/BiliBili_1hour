import functools,http.server,json,pathlib,socketserver,subprocess,threading
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1];APP=ROOT/'examples/完整项目'
class Quiet(http.server.SimpleHTTPRequestHandler):
 def log_message(self,*a):pass
def main():
 subprocess.run(['node',str(ROOT/'node_modules/typescript/lib/tsc.js'),'-p',str(APP/'tsconfig.json')],check=True)
 executable=sorted((pathlib.Path.home()/'AppData/Local/ms-playwright').glob('chromium_headless_shell-*/chrome-headless-shell-win64/chrome-headless-shell.exe'))[-1]
 checks=[]
 with socketserver.TCPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(APP))) as server:
  threading.Thread(target=server.serve_forever,daemon=True).start()
  with sync_playwright() as p:
   b=p.chromium.launch(headless=True,executable_path=str(executable));page=b.new_page(viewport=dict(width=1200,height=850));errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(f'http://127.0.0.1:{server.server_address[1]}/');assert page.locator('#total').inner_text()=='0.00';checks.append('initial empty state')
   def add(name,amount):page.locator('#name').fill(name);page.locator('#amount').fill(amount);page.get_by_role('button',name='添加记录').click()
   add('午餐','12');add('交通','8');assert page.locator('#total').inner_text()=='20.00' and page.locator('li').count()==2;checks.append('two successful additions and total')
   page.locator('li').first.get_by_role('button').click();assert page.locator('#total').inner_text()=='8.00';checks.append('delete by identity')
   page.reload();assert page.locator('li').count()==1 and page.locator('#total').inner_text()=='8.00';checks.append('persistence and reload')
   add('','12');assert '请输入开销名称' in page.locator('#message').inner_text();add('午餐','-1');assert '有限数字' in page.locator('#message').inner_text();add('午餐','abc');assert page.locator('li').count()==1;checks.append('invalid name, negative amount and nonnumeric input')
   add('赠品','0');assert page.locator('li').count()==2 and page.locator('#total').inner_text()=='8.00';checks.append('zero amount accepted')
   page.screenshot(path=str(ROOT/'build/完整项目运行截图.png'))
   page.evaluate("localStorage.setItem('typescript-course-expenses-v1','broken')");page.reload();assert page.locator('li').count()==0;add('新记录','1');assert page.locator('#total').inner_text()=='1.00';checks.append('recover after invalid JSON')
   page.evaluate("localStorage.setItem('typescript-course-expenses-v1',JSON.stringify([{id:1,name:'错误',amount:'12'}]))");page.reload();assert page.locator('li').count()==0 and '格式' in page.locator('#message').inner_text();checks.append('reject malformed saved fields')
   assert not errors,errors;b.close()
  server.shutdown()
 (ROOT/'build/project-verification.json').write_text(json.dumps(dict(allPassed=True,checks=checks,browserErrors=errors),ensure_ascii=False,indent=2),encoding='utf8');print('BROWSER_PROJECT_VERIFIED',len(checks),flush=True)
if __name__=='__main__':main()
