"""Assemble x86-64/A64 machine code and record actual instruction-by-instruction state."""
import copy,hashlib,importlib.metadata,json,os,pathlib,re,shutil,subprocess,struct
from unicorn import *
import unicorn.x86_const as X
import unicorn.arm64_const as A
from capstone import *
from keystone import Ks,KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN,KsError
from examples import CASES,ERRORS,DATA
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';CODE=0x100000;STOP=CODE+0xf00;STACK=0x400000
NASM=pathlib.Path(os.environ.get('MODERN_ASM_NASM') or shutil.which('nasm') or 'nasm')
XR={n:getattr(X,'UC_X86_REG_'+n.upper()) for n in ['rax','rbx','rcx','rdx','rsi','rdi','rbp','rsp','rip','r8','r9','r10','r11','r12','r13','r14','r15','eax','ebx','ecx','edx','al','ax']}
AR={n:getattr(A,'UC_ARM64_REG_'+n.upper()) for n in ['sp','pc']+[f'x{i}' for i in range(31)]+[f'w{i}' for i in range(31)]}
def save(p,d):p.parent.mkdir(exist_ok=True,parents=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
def assemble(case):
 key=case['key'];arch=case['arch'];lines=case['code'] if isinstance(case['code'],list) else case['code'].splitlines();folder=ROOT/'examples'/('x86_64' if arch=='x64' else 'aarch64');folder.mkdir(parents=True,exist_ok=True)
 source=folder/(key+('.asm' if arch=='x64' else '.s'));binary=BUILD/'assembled'/(key+'.bin');binary.parent.mkdir(exist_ok=True)
 if arch=='x64':
  source.write_text('bits 64\ndefault rel\norg 0x100000\n'+'\n'.join(lines)+'\n',encoding='utf8');listing=binary.with_suffix('.lst');r=subprocess.run([str(NASM),'-f','bin',str(source),'-o',str(binary),'-l',str(listing)],capture_output=True)
  if r.returncode:raise ValueError(r.stderr.decode('utf8',errors='replace'))
  raw=binary.read_bytes();mapping={}
  for row in listing.read_text().splitlines():
   m=re.match(r'\s*(\d+)\s+([0-9A-F]{8})\s+[0-9A-F\[\]()+-]+\s+',row)
   if m:mapping[CODE+int(m[2],16)]=int(m[1])-3
 else:
  source.write_text('.text\n'+'\n'.join(lines)+'\n',encoding='utf8');raw=Ks(KS_ARCH_ARM64,KS_MODE_LITTLE_ENDIAN).asm('\n'.join(lines),addr=CODE,as_bytes=True)[0];binary.write_bytes(raw);mapping={};offset=0
  for i,line in enumerate(lines,1):
   line=re.sub(r'^\s*[A-Za-z_][\w.]*:\s*','',line).strip()
   if line:mapping[CODE+offset]=i;offset+=4
  assert offset==len(raw),(key,offset,len(raw))
 cs=Cs(CS_ARCH_X86,CS_MODE_64) if arch=='x64' else Cs(CS_ARCH_ARM64,CS_MODE_LITTLE_ENDIAN)
 instructions={i.address:dict(address=i.address,size=i.size,instruction=i.mnemonic+(' '+i.op_str if i.op_str else ''),line=mapping[i.address],bytes=i.bytes.hex()) for i in cs.disasm(raw,CODE)}
 assert sum(i['size'] for i in instructions.values())==len(raw),(key,'Undecoded bytes')
 return raw,instructions
def execute(case,raw,instructions):
 arch=case['arch'];uc=Uc(UC_ARCH_X86,UC_MODE_64) if arch=='x64' else Uc(UC_ARCH_ARM64,UC_MODE_ARM)
 regs=XR if arch=='x64' else AR;ip='rip' if arch=='x64' else 'pc';sp='rsp' if arch=='x64' else 'sp'
 uc.mem_map(CODE,0x1000);uc.mem_map(DATA,0x10000);uc.mem_map(STACK,0x10000);uc.mem_write(CODE,raw);uc.mem_write(DATA,bytes.fromhex(case.get('data','')) or bytes(64))
 uc.reg_write(regs[sp],STACK+0xffe8 if arch=='x64' else STACK+0xfff0)
 if arch=='x64':uc.mem_write(STACK+0xffe8,struct.pack('<Q',STOP));uc.reg_write(X.UC_X86_REG_EFLAGS,2)
 else:uc.reg_write(AR['x30'],STOP);uc.reg_write(A.UC_ARM64_REG_NZCV,0)
 for n,value in case.get('initial',{}).items():uc.reg_write(regs[n],value&((1<<64)-1))
 def state(step,inst=None):
  values={n:uc.reg_read(v) for n,v in regs.items()};f=uc.reg_read(X.UC_X86_REG_EFLAGS) if arch=='x64' else uc.reg_read(A.UC_ARM64_REG_NZCV);flags={n:(f>>shift)&1 for n,shift in (dict(cf=0,zf=6,sf=7,of=11) if arch=='x64' else dict(n=31,z=30,c=29,v=28)).items()};at=values[sp];stack=[]
  for a in [at,at+8]:
   if STACK<=a<STACK+0x10000-7:stack.append(dict(address=a,value=int.from_bytes(uc.mem_read(a,8),'little')))
  return dict(step=step,line=inst['line'] if inst else 0,instruction=inst['instruction'] if inst else 'initial state',registers=values,flags=flags,memory=bytes(uc.mem_read(DATA,64)).hex(),stack=stack)
 uc.reg_write(regs[ip],CODE);snaps=[state(0)];alignment=[]
 for k in range(500):
  pc=uc.reg_read(regs[ip])
  if pc==STOP:break
  assert pc in instructions,(case['key'],'Unexpected instruction address',hex(pc));inst=instructions[pc]
  if arch=='x64' and inst['instruction'].startswith('call '):alignment.append(uc.reg_read(regs[sp])%16==0)
  if arch=='a64':alignment.append(uc.reg_read(regs[sp])%16==0)
  uc.emu_start(pc,CODE+0x1000,count=1);snaps.append(state(len(snaps),inst))
 else:raise AssertionError('Execution step limit exceeded')
 assert all(alignment),(case['key'],'ABI stack alignment')
 return dict(key=case['key'],arch=arch,source=case['code'],snapshots=snaps,binarySha256=hashlib.sha256(raw).hexdigest(),returnSentinel=STOP,stackAlignmentChecked=bool(alignment))
def main():
 traces={};checks=[]
 for key,case in CASES.items():
  raw,ins=assemble(case);run=execute(case,raw,ins);final=run['snapshots'][-1];values={**final['registers'],**final['flags']}
  for n,value in case['expected'].items():assert values[n]==value,(key,n,values[n],value);checks.append(key+':'+n)
  traces[key]=run;checks.append(key+':completed');print('EXECUTED',key,len(run['snapshots'])-1,flush=True)
 variants=[('x_max',dict(rdi=(1<<64)-2,rsi=1),dict(rax=1)),('a_max',dict(x0=(1<<64)-2,x1=1),dict(x0=1)),('x_sum',dict(rdi=DATA,rsi=0),dict(rax=0)),('a_sum',dict(x0=DATA,x1=0),dict(x0=0)),('x_stats',dict(rdi=DATA,rsi=0),dict(rax=0,rdx=0)),('a_stats',dict(x0=DATA,x1=0),dict(x0=0,x1=0))]
 for base,initial,expected in variants:
  c=copy.deepcopy(CASES[base]);c['initial']=initial;raw,ins=assemble(c);r=execute(c,raw,ins)
  for n,value in expected.items():assert r['snapshots'][-1]['registers'][n]==value;checks.append(base+':variant:'+n)
 for base,out in [('x_stats',['rax','rdx']),('a_stats',['x0','x1'])]:
  for values in [[0,9,2],[9,9,9],[7,5,3],[0xffffffff,1,0]]:
   c=copy.deepcopy(CASES[base]);c['data']=struct.pack('<3I',*values).hex();raw,ins=assemble(c);r=execute(c,raw,ins);v=r['snapshots'][-1]['registers'];assert [v[n] for n in out]==[sum(values),max(values)];checks.append(base+':array:'+str(values))
 failures=[]
 for case in ERRORS:
  try:
   raw,ins=assemble(case)
   if case['stage']=='assemble':raise AssertionError('Expected assembly rejection')
   execute(case,raw,ins)
   raise AssertionError('Expected execution fault')
  except (KsError,ValueError) as e:
   assert case['stage']=='assemble';failures.append(dict(key=case['key'],stage=case['stage'],type=type(e).__name__))
  except UcError as e:
   assert case['stage']=='execute' and e.errno==(UC_ERR_EXCEPTION if case['key']=='x_divzero' else UC_ERR_READ_UNMAPPED),(case['key'],e.errno);failures.append(dict(key=case['key'],stage=case['stage'],errno=e.errno))
  path=ROOT/'examples/expected-failures';path.mkdir(exist_ok=True);(path/(case['key']+'.txt')).write_text(case['code']+'\n',encoding='utf8')
 save(BUILD/'execution-data.json',traces);save(BUILD/'examples-verification.json',dict(allPassed=True,normalPrograms=len(traces),expectedFailures=len(failures),checks=len(checks),items=checks,failures=failures,toolVersions={n:importlib.metadata.version(n) for n in ['unicorn','capstone','keystone-engine']},scope='Real assembled bytes executed in a CPU emulator; explicit memory fixtures and ABI entry stack. No guest operating system, native OS process or hardware performance claim.'))
 print('VERIFICATION_DONE',len(traces),len(checks),len(failures),flush=True)
if __name__=='__main__':main()
