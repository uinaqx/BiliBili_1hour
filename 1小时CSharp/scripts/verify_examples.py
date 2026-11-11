"""Actually build and execute each independently runnable C# example."""
import concurrent.futures,json,os,pathlib,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[1];EX=ROOT/'examples'
PROJECT='''<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup><OutputType>Exe</OutputType><TargetFramework>net8.0</TargetFramework><LangVersion>12.0</LangVersion><ImplicitUsings>enable</ImplicitUsings><Nullable>enable</Nullable><EnableNETAnalyzers>false</EnableNETAnalyzers><EnableDefaultCompileItems>false</EnableDefaultCompileItems><MSBuildEnableWorkloadResolver>false</MSBuildEnableWorkloadResolver></PropertyGroup><ItemGroup><Compile Include="Program.cs" /><Compile Include="ConsoleEnvironment.cs" /></ItemGroup></Project>'''
ENV={**os.environ,'MSBuildEnableWorkloadResolver':'false','DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE':'true','DOTNET_CLI_TELEMETRY_OPTOUT':'1','DOTNET_CLI_UI_LANGUAGE':'en-US'}
def build(folder):
 return subprocess.run(['dotnet','build','--nologo','-v','quiet','--disable-build-servers','-p:MSBuildEnableWorkloadResolver=false'],cwd=folder,capture_output=True,text=True,encoding='utf8',env=ENV,timeout=120)
def write_project(folder,code):
 folder.mkdir(parents=True,exist_ok=True);(folder/'Program.cs').write_text(code+'\n',encoding='utf8');(folder/'Example.csproj').write_text(PROJECT,encoding='utf8')
 (folder/'ConsoleEnvironment.cs').write_text('''internal static class ConsoleEnvironment
{
    [System.Runtime.CompilerServices.ModuleInitializer]
    internal static void Initialize()
    {
        System.Console.InputEncoding = new System.Text.UTF8Encoding(false);
        System.Console.OutputEncoding = new System.Text.UTF8Encoding(false);
        System.Globalization.CultureInfo.CurrentCulture = System.Globalization.CultureInfo.InvariantCulture;
    }
}
''',encoding='utf8')
def execute(folder,stdin=''):
 return subprocess.run(['dotnet',str(folder/'bin/Debug/net8.0/Example.dll')],cwd=folder,input=stdin,capture_output=True,text=True,encoding='utf8',env=ENV,timeout=20)
def case(s):
 folder=EX/s['key'];write_project(folder,s['code']);b=build(folder);log=b.stdout+b.stderr
 if s.get('diagnostic'):
  assert b.returncode and s['diagnostic'] in log,(s['key'],'expected compile error',log)
  (folder/'expected-error.txt').write_text(log.replace(str(folder),'.'),encoding='utf8')
  fixed=folder/'corrected';write_project(fixed,s['answerCode'])
  # Exclude the nested corrected project from the original project's default glob.
  (folder/'Example.csproj').write_text(PROJECT.replace('</Project>','<ItemGroup><Compile Remove="corrected/**/*.cs" /></ItemGroup></Project>'),encoding='utf8')
  b=build(fixed);assert b.returncode==0,(s['key'],b.stdout,b.stderr);runfolder=fixed
 else:
  assert b.returncode==0,(s['key'],log);runfolder=folder
 stdin=s.get('fixtures',{}).get('stdin','');result=execute(runfolder,stdin);assert result.returncode==0,(s['key'],result.stderr)
 actual=result.stdout.strip();assert actual==s['output'].replace('\\n','\n'),(s['key'],actual,s['output'])
 if stdin:(folder/'input.txt').write_text(stdin,encoding='utf8')
 (folder/'expected-output.txt').write_text(actual+'\n',encoding='utf8')
 (folder/'README.md').write_text('# '+s['title']+'\n\n运行：`dotnet run --project '+('corrected' if s.get('diagnostic') else '.')+'`。\n\n'+('本页键盘输入：\n```text\n'+stdin+'```\n' if stdin else '')+'\n'+''.join(p['text']+'\n\n' for p in s['parts'])+'## 总结\n\n'+''.join('- '+n+'\n' for n in s['notes']),encoding='utf8')
 return dict(key=s['key'],title=s['title'],expectedError=s.get('diagnostic'),stdin=stdin,output=actual,passed=True)
def main():
 course=json.loads((ROOT/'public/course.json').read_text(encoding='utf8'));scenes=[s for c in course['chapters'] for s in c['scenes']]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:reports=list(pool.map(case,scenes))
 failure=EX/'补充验证/未捕获格式异常';write_project(failure,'int amount = int.Parse("abc");\nConsole.WriteLine(amount);');b=build(failure);assert not b.returncode,b.stdout
 r=execute(failure);assert r.returncode and 'System.FormatException' in r.stderr
 (failure/'expected-error.txt').write_text('预期运行时失败：System.FormatException。该目录用于对照第九章被 catch 处理的相同异常。\n',encoding='utf8')
 data=dict(allPassed=True,sdkVersion=subprocess.check_output(['dotnet','--version'],text=True,env=ENV).strip(),languageVersion='C# 12.0',targetFramework='net8.0',compileErrorCases=sum(bool(x['expectedError']) for x in reports),runtimeFailureCases=1,cases=reports)
 (ROOT/'build/example-verification.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8');print('CSHARP_EXAMPLES_VERIFIED',len(reports),flush=True)
if __name__=='__main__':main()
