import json,pathlib,subprocess,tempfile
from verify_examples import ENV
ROOT=pathlib.Path(__file__).resolve().parents[1];APP=ROOT/'examples/完整项目'
def main():
 b=subprocess.run(['dotnet','build',str(APP/'ExpenseCourse.csproj'),'--nologo','-v','quiet','--disable-build-servers','-p:MSBuildEnableWorkloadResolver=false'],capture_output=True,text=True,encoding='utf8',env=ENV);assert b.returncode==0,(b.stdout,b.stderr)
 checks=[];transcripts=[]
 with tempfile.TemporaryDirectory(prefix='csharp-course-') as d:
  path=pathlib.Path(d)/'expenses.json'
  def run(stdin):
   r=subprocess.run(['dotnet',str(APP/'bin/Debug/net8.0/ExpenseCourse.dll'),str(path)],cwd=d,input=stdin,capture_output=True,text=True,encoding='utf8',env=ENV,timeout=20);assert r.returncode==0,r.stderr;transcripts.append(r.stdout);return r.stdout
  out=run('2\n1\n午餐\n12\n1\n交通\n8\n2\n0\n');assert '共 0 笔，总额 0.00 元' in out and '共 2 笔，总额 20.00 元' in out;checks+=['initial empty state','add two records and sum']
  data=json.loads(path.read_text(encoding='utf8'));assert [i['Name'] for i in data]==['午餐','交通'];checks.append('actual JSON persistence')
  out=run('2\n3\n1\n2\n0\n');assert '共 2 笔，总额 20.00 元' in out and '共 1 笔，总额 8.00 元' in out;checks+=['reload persisted records','delete by id and resave']
  out=run('9\n1\n\n1\n错误\n-1\n1\n错误\nabc\n1\n赠品\n0\n2\n0\n');assert '请选择 0、1、2、3' in out and '请输入名称' in out and '十进制数' in out and '共 2 笔，总额 8.00 元' in out;checks+=['invalid menu, blank name, negative and nonnumeric input','zero amount accepted']
  path.write_text('broken',encoding='utf8');out=run('1\n恢复\n2.5\n2\n0\n');assert '读取记录失败' in out and '2.50' in out and list(path.parent.glob('expenses.json.invalid-*.json'));checks.append('invalid JSON backed up and recoverable')
  path.write_text('[{"Id":1,"Name":"","Amount":12}]',encoding='utf8');out=run('2\n0\n');assert '读取记录失败' in out and '共 0 笔' in out;checks.append('reject malformed saved fields')
  out=run('');assert '已保存' in out;checks.append('end-of-input exits cleanly')
 (ROOT/'build/project-console-transcript.txt').write_text('\n\n'.join(transcripts),encoding='utf8')
 (ROOT/'build/project-verification.json').write_text(json.dumps(dict(allPassed=True,checks=checks),ensure_ascii=False,indent=2),encoding='utf8');print('CSHARP_PROJECT_VERIFIED',len(checks),flush=True)
if __name__=='__main__':main()
