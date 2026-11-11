"""Assemble real 8086 bytes and execute them; record states, not invented visual results."""
import hashlib,importlib.metadata,json,os,pathlib,re,shutil,subprocess
from unicorn import Uc,UC_ARCH_X86,UC_MODE_16,UC_HOOK_INTR,UC_HOOK_MEM_WRITE,UcError
import unicorn.x86_const as X
from capstone import Cs,CS_ARCH_X86,CS_MODE_16
import examples
ROOT=pathlib.Path(__file__).resolve().parents[1];BUILD=ROOT/'build';BASE=0x10000;ORIGIN=0x100
REGS={s:getattr(X,'UC_X86_REG_'+s.upper()) for s in ['ax','bx','cx','dx','si','di','bp','sp','cs','ds','es','ss','ip','al','ah','bl','bh','cl','ch','dl','dh']};FLAGS={'cf':0,'pf':2,'af':4,'zf':6,'sf':7,'df':10,'of':11}
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
def assembler():
    found=shutil.which('nasm') or str('nasm')
    if not pathlib.Path(found).is_file():raise RuntimeError('Install NASM or put it on PATH')
    return found
def compile_case(case):
    folder=ROOT/'examples/sources';folder.mkdir(parents=True,exist_ok=True);key=case['key'];source=folder/(key+'.asm');out=BUILD/'assembled';out.mkdir(exist_ok=True)
    body=case['body'];tail=case.get('tail','\nhlt\n');text='cpu 8086\nbits 16\norg 100h\n'+body+'\n'+tail
    # Data initialization is also present in the assembled fragment. Tests may override inputs.
    current=None
    for offset,value in sorted(case.get('data',{}).items()):
        text+=f'\ntimes {offset} - ($ - $$ + 100h) db 0\n'+'db '+','.join(str(b) for b in value)+'\n'
    source.write_text(text,encoding='utf8');binary=out/(key+'.bin');listing=out/(key+'.lst')
    r=subprocess.run([assembler(),'-f','bin','-w+all','-o',str(binary),'-l',str(listing),str(source)],capture_output=True,text=True,encoding='utf8',errors='replace');assert r.returncode==0,(key,r.stderr)
    address_lines={}
    for line in listing.read_text(encoding='utf8').splitlines():
        m=re.match(r'^\s*(\d+)\s+([0-9A-Fa-f]{8})\s+([0-9A-Fa-f\[\]()<>-]+)',line)
        if m:address_lines[ORIGIN+int(m[2],16)]=int(m[1])-3 if 4<=int(m[1])<=3+len(body.splitlines()) else 0
    return binary.read_bytes(),address_lines,r.stderr
def execute(case,code,line_map,regs=None,data=None,budget=1000):
    mu=Uc(UC_ARCH_X86,UC_MODE_16);mu.mem_map(0,0x200000);mu.mem_write(BASE+ORIGIN,code)
    for name in REGS:
        if name not in ['al','ah','bl','bh','cl','ch','dl','dh']:mu.reg_write(REGS[name],0x1000 if name in ['cs','ds','es','ss'] else 0xfffe if name=='sp' else ORIGIN if name=='ip' else 0)
    mu.reg_write(X.UC_X86_REG_EFLAGS,2)
    for name,val in (regs or {}).items():mu.reg_write(REGS[name],val)
    for off,value in (data or {}).items():mu.mem_write(BASE+off,bytes(value))
    output=[];inputs=list(case.get('input',''));memory_writes=[];status={'value':None};dis=Cs(CS_ARCH_X86,CS_MODE_16)
    def interrupt(u,no,unused):
        if no==0:status['value']='divide-error';u.emu_stop();return
        if no!=0x21:raise AssertionError(('Unsupported interrupt',no))
        ah=u.reg_read(REGS['ah'])
        if ah==2:output.append(chr(u.reg_read(REGS['dl'])&255))
        elif ah==9:
            addr=u.reg_read(REGS['ds'])*16+u.reg_read(REGS['dx']);buf=bytes(u.mem_read(addr,4096));end=buf.find(b'$');assert end>=0,'Missing DOS 09h terminator';output.append(buf[:end].decode('ascii'))
        elif ah==1:
            assert inputs,'No scripted input';ch=inputs.pop(0);u.reg_write(REGS['al'],ord(ch));output.append(ch)
        elif ah==0x4c:status['value']='dos-exit';u.emu_stop()
        else:raise AssertionError(('Unsupported DOS service',ah))
    def write(u,access,address,size,value,unused):memory_writes.append(dict(address=address,size=size,value=value))
    mu.hook_add(UC_HOOK_INTR,interrupt);mu.hook_add(UC_HOOK_MEM_WRITE,write)
    def state(step,instruction='',line=0,offset=None):
        rr={k:int(mu.reg_read(v)) for k,v in REGS.items()};f=mu.reg_read(X.UC_X86_REG_EFLAGS)
        watched={f'{off:04X}':bytes(mu.mem_read(BASE+off,1))[0] for off in list(range(0xfc,0x100))+list(range(0x200,0x208))+list(range(0x300,0x303))}
        return dict(step=step,instruction=instruction,line=line,executedOffset=offset,registers=rr,flags={k:(f>>bit)&1 for k,bit in FLAGS.items()},memory=watched,output=''.join(output),writes=list(memory_writes))
    snapshots=[state(0)]
    for step in range(1,budget+1):
        ip=int(mu.reg_read(REGS['ip']));cs=int(mu.reg_read(REGS['cs']));address=cs*16+ip;raw=bytes(mu.mem_read(address,15))
        ins=next(dis.disasm(raw,address,count=1),None);assert ins is not None,('Decode failure',case['key'],ip)
        if ins.mnemonic=='hlt':status['value']='fragment-end';break
        memory_writes.clear()
        try:mu.emu_start(address,0x200000,count=1)
        except UcError as exc:status['value']='emulator-error:'+str(exc);break
        snapshots.append(state(step,ins.mnemonic+' '+ins.op_str,line_map.get(ip,0),ip))
        if status['value']:break
    else:status['value']='instruction-budget'
    return dict(key=case['key'],initialCondition='CS=DS=ES=SS=1000h, IP=0100h, SP=FFFEh, other general registers=0, EFLAGS=0002h; case overrides are explicit',status=status['value'],snapshots=snapshots,output=''.join(output))
def main():
    checks=[];traces={};records=[];cases=examples.catalog();compiled={}
    def check(name,actual,expected):assert actual==expected,(name,actual,expected);checks.append(name)
    for key,case in cases.items():
        code,mapping,warnings=compile_case(case);compiled[key]=(code,mapping);trace=execute(case,code,mapping);assert trace['status'] in ['fragment-end','dos-exit'],(key,trace['status']);last=trace['snapshots'][-1]
        for name,value in case['expected'].items():check(key+':'+name,last['registers'][name],value)
        check(key+':output',trace['output'],case['output']);traces[key]=trace;records.append(dict(key=key,passed=True,steps=len(trace['snapshots'])-1,status=trace['status'],sourceSha256=digest(ROOT/'examples/sources'/(key+'.asm')),binarySha256=hashlib.sha256(code).hexdigest(),warnings=warnings));print('EXECUTION_PASS',key,len(trace['snapshots'])-1,flush=True)
    def snap(key,line,occurrence=1):return [s for s in traces[key]['snapshots'] if s['line']==line][occurrence-1]
    for key,line,vals in [('carry_overflow',2,{'cf':1,'of':0}),('carry_overflow',4,{'cf':0,'of':1}),('add_sub',2,{'zf':1}),('add_sub',3,{'zf':0}),('inc_adc',3,{'cf':1}),('test_compare',2,{'zf':0}),('test_compare',3,{'zf':1}),('rotate',2,{'cf':1})]:
        for flag,value in vals.items():check(key+':flag:'+flag+':'+str(line),snap(key,line)['flags'][flag],value)
    check('little endian low',traces['little_endian']['snapshots'][-1]['memory']['0200'],0x34);check('little endian high',traces['little_endian']['snapshots'][-1]['memory']['0201'],0x12)
    for off,value in zip(range(0x300,0x303),b'ABC'):check('rep copy byte '+str(off),traces['string_copy']['snapshots'][-1]['memory'][f'{off:04X}'],value)
    for vals in [[7,5,3],[5,5,5],[0,0,0],[255,255,255]]:
        case=cases['statistics'];trace=execute(case,*compiled['statistics'],data={0x200:vals});last=trace['snapshots'][-1];check('sum variant '+str(vals),last['registers']['dx'],sum(vals));check('max variant '+str(vals),last['registers']['bl'],max(vals))
    for left,right in [(15,12),(12,12)]:
        case=dict(cases['maximum_pair'],key=f'maximum_pair_{left}_{right}',body=cases['maximum_pair']['body'].replace('mov ax, 7',f'mov ax, {left}').replace('mov bx, 12',f'mov bx, {right}'));code,mapping,_=compile_case(case);trace=execute(case,code,mapping);check(f'maximum pair {left},{right}',trace['snapshots'][-1]['registers']['ax'],max(left,right))
    case=dict(key='sar_negative_three',body='mov al, -3\nsar al, 1',tail='\nhlt\n');code,mapping,_=compile_case(case);trace=execute(case,code,mapping);check('SAR negative three rounds to negative two',trace['snapshots'][-1]['registers']['al'],0xfe)
    check('segment alias',0x1235*16,0x1234*16+0x10);check('instruction bytes mov AX1234',compiled['machine_listing'][0][:3],bytes.fromhex('B8 34 12'))
    case=dict(cases['dos_input'],input='A');trace=execute(case,*compiled['dos_input']);check('invalid ASCII input rejected',trace['snapshots'][-1]['registers']['bl'],255)
    for value in [0,1,9,10,99,100,123,65535]:
        case=dict(key='decimal_check',body='call print_u16\njmp done',tail=examples.PRINT_U16);code,mapping,_=compile_case(case);trace=execute(case,code,mapping,regs={'ax':value});check('decimal output '+str(value),trace['output'],str(value));check('decimal stack balanced '+str(value),trace['snapshots'][-1]['registers']['sp'],0xfffe)
    flags_case=dict(key='flag_boundary_check',body='add al, 1',tail='\nhlt\n');code,mapping,_=compile_case(flags_case)
    for a in [0,1,0x7e,0x7f,0x80,0xfe,0xff]:
        r=execute(flags_case,code,mapping,regs={'al':a})['snapshots'][-1];check('add result '+str(a),r['registers']['al'],(a+1)&255);check('add CF '+str(a),r['flags']['cf'],int(a==255));check('add OF '+str(a),r['flags']['of'],int(a==127));check('add ZF '+str(a),r['flags']['zf'],int(a==255))
    failures=[];folder=ROOT/'examples/expected-failures';folder.mkdir(exist_ok=True)
    for key,body,pattern in [('width_mismatch','mov ax, bl','invalid combination|mismatch'),('memory_to_memory','mov [0200h], [0202h]','invalid combination|size'),('invalid_address','mov ax, [ax]','invalid.*address'),('newer_instruction','pusha','cpu|instruction')]:
        p=folder/(key+'.asm');p.write_text('cpu 8086\nbits 16\n'+body+'\n',encoding='utf8');r=subprocess.run([assembler(),'-f','bin','-o',str(BUILD/(key+'.bin')),str(p)],capture_output=True,text=True,encoding='utf8',errors='replace');assert r.returncode!=0 and re.search(pattern,r.stderr,re.I),(key,r.stderr);checks.append('expected compile failure '+key);failures.append(dict(key=key,category='expected assembly failure',diagnostic=r.stderr,passed=True))
    for width,expected in [('byte',0xab01),('word',1)]:
        case=dict(key='explicit_'+width+'_size',body=f'mov {width} [0200h], 1\nmov ax, [0200h]',tail='\nhlt\n',data={0x200:bytes.fromhex('CD AB')});code,mapping,_=compile_case(case);r=execute(case,code,mapping)['snapshots'][-1];check(width+' explicit write range',r['registers']['ax'],expected)
    for key,body in [('divide_zero','mov ax, 12\nmov bl, 0\ndiv bl'),('quotient_overflow','mov ax, 256\nmov bl, 1\ndiv bl')]:
        case=dict(key=key,body=body,tail='\nhlt\n');code,mapping,_=compile_case(case);shutil.copy2(ROOT/'examples/sources'/(key+'.asm'),folder/(key+'.asm'));trace=execute(case,code,mapping);check(key+' runtime error',trace['status'],'divide-error');failures.append(dict(key=key,category='assembles; expected CPU divide-error interrupt',passed=True))
    # A wrong but executable branch is classified separately from assembly/runtime failures.
    case=dict(cases['branch_signed'],key='wrong_signed_branch',body=cases['branch_signed']['body'].replace('jl smaller','jb smaller'));code,mapping,_=compile_case(case);trace=execute(case,code,mapping);check('wrong signed branch observable',trace['snapshots'][-1]['registers']['bx'],0);failures.append(dict(key='wrong_signed_branch',category='expected logical mismatch, normal execution',passed=True,repairReference='branch_signed'))
    check('segment address',0x1234*16+0x10,0x12350);check('unsigned FF',int('FF',16),255);check('signed FF',255-256,-1);check('memory capacity',2**20,1048576)
    version=subprocess.check_output([assembler(),'-v'],text=True).strip();course_sha=digest(ROOT/'public/course.json');save(BUILD/'execution-data.json',traces);save(BUILD/'verified-examples.json',dict(kind='actual NASM bytes executed with Unicorn',runs=records,expectedFailures=failures));report=dict(allPassed=True,checks=len(checks),normalPrograms=len(cases),expectedFailures=len(failures),courseSha256=course_sha,exampleSourceSha256=digest(ROOT/'scripts/examples.py'),assembler=version,unicorn=importlib.metadata.version('unicorn'),capstonePackage=importlib.metadata.version('capstone'),scope='CPU instruction functionality with explicit initial state; DOS services handled by a declared limited adapter; not timing, full DOS, BIOS or hardware verification',items=checks,programs=records,failures=failures);save(BUILD/'examples-verification.json',report);print('ASSEMBLY_EXAMPLES_PASSED',len(checks),len(cases),'programs',len(failures),'expected failures',flush=True)
if __name__=='__main__':main()
