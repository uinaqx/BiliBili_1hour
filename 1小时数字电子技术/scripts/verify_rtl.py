"""Compile actual Verilog-2005, simulate self-checking benches, retain real VCD events."""
import hashlib,json,os,pathlib,re,shutil,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'examples'))
from catalog import DESIGNS,TESTS,SPECIALS,bench
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def tools():
 bin=pathlib.Path(os.environ.get('IVERILOG_BIN',str(ROOT/'tools/iverilog/bin')))
 iv=shutil.which('iverilog') or str(bin/'iverilog.exe');vvp=shutil.which('vvp') or str(bin/'vvp.exe')
 if not pathlib.Path(iv).exists():raise RuntimeError('Install Icarus Verilog or set IVERILOG_BIN to its bin directory')
 return iv,vvp
def parse_vcd(p):
 text=p.read_text(encoding='utf8');scope=[];ids={};signals={};active=False;time=0;units=1
 match=re.search(r'\$timescale\s+(\d+)\s*(s|ms|us|ns|ps|fs)',text)
 if match:units=int(match[1])*dict(s=1e9,ms=1e6,us=1e3,ns=1,ps=.001,fs=.000001)[match[2]]
 for line in text.splitlines():
  line=line.strip()
  if line.startswith('$scope'):scope.append(line.split()[2])
  elif line.startswith('$upscope'):scope.pop()
  elif line.startswith('$var') and scope==['tb']:
   x=line.split();ids.setdefault(x[3],[]).append(x[4]);signals[x[4]]=dict(width=int(x[2]),events=[])
  elif line.startswith('$enddefinitions'):active=True
  elif active and line.startswith('#'):time=int(line[1:])*units
  elif active and line and not line.startswith('$'):
   if line[0] in 'bBrR':x=line.split();value=x[0][1:];code=x[1]
   elif line[0] in '01xXzZ':value=line[0].lower();code=line[1:]
   else:continue
   for name in ids.get(code,[]):
    events=signals[name]['events'];item=[round(time,6),value.lower()]
    if events and events[-1][0]==item[0]:events[-1]=item
    elif not events or events[-1][1]!=item[1]:events.append(item)
 return dict(endNs=time,signals=signals,timeUnit='ns',sourceSha256=hashlib.sha256(p.read_bytes()).hexdigest())
def main():
 iv,vvp=tools();build=ROOT/'build/sim';build.mkdir(parents=True,exist_ok=True)
 tmp=ROOT/'build/tmp';tmp.mkdir(exist_ok=True);env={**os.environ,'TMP':'build/tmp','TMPDIR':'build/tmp','TEMP':'build/tmp','PATH':str(pathlib.Path(iv).resolve().parent)+os.pathsep+os.environ.get('PATH','')}
 lib=pathlib.Path(iv).resolve().parent.parent/'lib/ivl'
 iv_cmd=[iv]+(['-B',os.path.relpath(lib,ROOT)] if lib.is_dir() else [])
 def compile(args):
  args=[os.path.relpath(a,ROOT) if pathlib.Path(str(a)).is_absolute() and pathlib.Path(str(a)).is_relative_to(ROOT) else str(a) for a in args]
  return subprocess.run([*iv_cmd,*args],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf8',errors='replace')
 designs=ROOT/'examples/rtl';designs.mkdir(exist_ok=True);tbs=ROOT/'examples/testbenches';tbs.mkdir(exist_ok=True)
 for key,code in DESIGNS.items():(designs/(key+'.v')).write_text(code+'\n',encoding='utf8')
 traces={};records=[];checks=0
 for t in TESTS:
  key=t['key'];tb=tbs/('tb_'+key+'.v');tb.write_text(bench(t),encoding='utf8');out=build/key;out.mkdir(exist_ok=True)
  args=['-g2005','-Wall','-s','tb','-o',str(out/'run.vvp'),*[str(designs/(d+'.v')) for d in t['dependencies']],str(tb)]
  c=compile(args);assert c.returncode==0,(key,c.stderr)
  r=subprocess.run([vvp,'-M',os.path.relpath(lib,ROOT),os.path.relpath(out/'run.vvp',ROOT)],cwd=ROOT,env=env,capture_output=True,text=True,errors='replace',timeout=20);assert r.returncode==0 and 'PASS' in r.stdout and 'FAIL' not in r.stdout,(key,r.stdout,r.stderr)
  shutil.copy2(ROOT/'wave.vcd',out/'wave.vcd')
  n,e=map(int,re.search(r'CHECKS (\d+) ERRORS (\d+)',r.stdout).groups());assert n==t['checks'] and e==0
  trace=parse_vcd(out/'wave.vcd');trace['selectedSignals']=t['signals'];traces[key]=trace;checks+=n;records.append(dict(key=key,checks=n,stdout=r.stdout,compilerWarnings=c.stderr,passed=True));print('SIMULATION_PASS',key,n,flush=True)
 for key,code in SPECIALS.items():
  tb=tbs/('tb_'+key+'.v');tb.write_text(code,encoding='utf8');out=build/key;out.mkdir(exist_ok=True)
  c=compile(['-g2005','-s','tb','-o',str(out/'run.vvp'),str(tb)]);assert c.returncode==0,c.stderr
  r=subprocess.run([vvp,'-M',os.path.relpath(lib,ROOT),os.path.relpath(out/'run.vvp',ROOT)],cwd=ROOT,env=env,capture_output=True,text=True,errors='replace');assert 'PASS' in r.stdout and 'ERRORS 0' in r.stdout,(key,r.stdout,r.stderr)
  checks+=3;records.append(dict(key=key,checks=3,stdout=r.stdout,passed=True))
 errors={'missing_endmodule':'module broken(input wire a, output wire y); assign y=a;','missing_module':'module tb; unknown_device dut(); endmodule'}
 for key,code in errors.items():
  p=ROOT/'examples/expected-failures'/(key+'.v');p.parent.mkdir(exist_ok=True);p.write_text(code+'\n',encoding='utf8')
  c=compile(['-g2005','-o',str(build/(key+'.vvp')),str(p)])
  assert c.returncode!=0 and re.search('syntax|error|Unknown module',c.stderr,re.I),(key,c.stderr)
  records.append(dict(key=key,category='expected compile/elaboration failure',passed=True,diagnostic=c.stderr));checks+=1
 wrong=ROOT/'examples/expected-failures/wrong_and.v';wrong.write_text(DESIGNS['and_gate'].replace('a & b','a | b')+'\n',encoding='utf8')
 c=compile(['-g2005','-s','tb','-o',str(build/'wrong_and.vvp'),str(wrong),str(tbs/'tb_and_gate.v')]);assert c.returncode==0,c.stderr
 r=subprocess.run([vvp,'-M',os.path.relpath(lib,ROOT),os.path.relpath(build/'wrong_and.vvp',ROOT)],cwd=ROOT,env=env,capture_output=True,text=True,errors='replace')
 assert 'FAIL' in r.stdout and 'CHECKS 4 ERRORS 2' in r.stdout and 'PASS' not in r.stdout
 records.append(dict(key='wrong_and',category='expected functional test failure, compiles successfully',passed=True,stdout=r.stdout,repairReference='and_gate'));checks+=1
 course=ROOT/'public/course.json';report=dict(allPassed=True,checks=checks,normalSimulations=len(TESTS)+len(SPECIALS),expectedFailures=len(errors)+1,courseSha256=hashlib.sha256(course.read_bytes()).hexdigest(),toolVersion=compile(['-V']).stdout.splitlines()[0],scope='Verilog-2005 compile and self-checking RTL simulation; not synthesis, timing closure or board verification',examples=records)
 save(ROOT/'build/simulation-data.json',traces);save(ROOT/'build/rtl-verification.json',report)
 print('ALL_EXAMPLES_PASS',checks,report['toolVersion'],flush=True)
if __name__=='__main__':main()
