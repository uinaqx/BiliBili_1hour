"""Deterministic teaching models, not hardware measurements or a complete ISA."""
from dataclasses import dataclass
import math, struct


def width(bits):
    if type(bits) is not int or bits <= 0:
        raise ValueError('bits must be a positive integer')
    return (1 << bits) - 1


def to_unsigned(value, bits):
    return int(value) & width(bits)


def to_signed(value, bits):
    v = to_unsigned(value, bits)
    return v - (1 << bits) if v & (1 << (bits - 1)) else v


def add_n(a, b, bits=8, carry=0):
    mask = width(bits)
    if carry not in (0, 1): raise ValueError('carry must be 0/1')
    a, b = a & mask, b & mask
    total = a + b + carry
    result = total & mask
    signed_total = to_signed(a, bits) + to_signed(b, bits) + carry
    return dict(a=a, b=b, bits=bits, result=result, signed=to_signed(result,bits),
                carry=int(total > mask), overflow=not -(1 << (bits-1)) <= signed_total < (1 << (bits-1)))


def full_adders():
    return [dict(a=a,b=b,cin=c,sum=(a^b^c),cout=(a&b)|(a&c)|(b&c))
            for a in range(2) for b in range(2) for c in range(2)]


def multiply(a,b,bits=4):
    mask=width(bits)
    if not (0 <= a <= mask and 0 <= b <= mask): raise ValueError('unsigned operands out of range')
    total=0; events=[]
    for i in range(bits):
        partial=(a << i) if (b >> i)&1 else 0
        total += partial
        events.append(dict(step=i,bit=(b>>i)&1,shifted=a<<i,partial=partial,total=total))
    return dict(a=a,b=b,result=total,events=events)


def divide(n,d,bits=4):
    mask=width(bits)
    if d==0: raise ZeroDivisionError('division by zero')
    if not (0 <= n <= mask and 0 < d <= mask): raise ValueError('unsigned operands out of range')
    q=0;r=0;events=[]
    for i in reversed(range(bits)):
        shifted=(r<<1)|((n>>i)&1);trial=shifted-d
        bit=int(trial>=0);r=trial if bit else shifted;q|=bit<<i
        events.append(dict(input_bit=i,shifted_remainder=shifted,trial=trial,restored=not bool(bit),remainder=r,quotient=q))
    return dict(dividend=n,divisor=d,quotient=q,remainder=r,events=events)


def binary32(value):
    return struct.unpack('>f',struct.pack('>f',value))[0]


def float_record(value):
    f=binary32(value);u=struct.unpack('>I',struct.pack('>f',f))[0];e=(u>>23)&255;fraction=u&0x7fffff
    category=('infinity' if fraction==0 else 'NaN') if e==255 else ('zero' if fraction==0 else 'subnormal') if e==0 else 'normal'
    return dict(value=str(f),hex=f'0x{u:08X}',bits=f'{u:032b}',sign=u>>31,exponent=e,fraction=fraction,category=category)


class Cache:
    """Byte-addressed, write-back, write-allocate, LRU, little-endian accesses."""
    def __init__(self,capacity,block_size,ways=1,address_bits=32,memory=None):
        for n in (capacity,block_size,ways,address_bits):
            if type(n) is not int or n<=0: raise ValueError('positive integer configuration required')
        if capacity % (block_size*ways): raise ValueError('capacity must divide into sets')
        sets=capacity//(block_size*ways)
        if block_size & (block_size-1) or sets & (sets-1): raise ValueError('block and set count must be powers of two')
        self.block_size=block_size;self.ways=ways;self.set_count=sets;self.address_bits=address_bits
        self.offset_bits=block_size.bit_length()-1;self.index_bits=sets.bit_length()-1
        self.tag_bits=address_bits-self.offset_bits-self.index_bits
        if self.tag_bits < 0: raise ValueError('address too short')
        self.sets=[[] for _ in range(sets)];self.clock=0;self.memory=dict(memory or {})
        if any(type(v) is not int or not 0<=v<=255 for v in self.memory.values()):
            raise ValueError('backing memory must contain bytes')

    def fields(self,address):
        if type(address) is not int or not 0<=address<1<<self.address_bits: raise ValueError('address outside configured space')
        return dict(tag=address>>(self.offset_bits+self.index_bits),index=(address>>self.offset_bits)&(self.set_count-1),offset=address&(self.block_size-1))

    def snapshot(self,index):
        return [dict(tag=x['tag'],dirty=x['dirty'],last=x['last'],data=dict(x['data'])) for x in self.sets[index]]

    def access(self,address,operation='read',value=None,size=1):
        if operation not in ('read','write'): raise ValueError('operation must be read/write')
        f=self.fields(address)
        if size not in (1,2,4) or f['offset']+size>self.block_size:
            raise ValueError('access must fit one block; supported widths: 1/2/4 bytes')
        self.fields(address+size-1)
        if operation=='write' and type(value) is not int: raise ValueError('write requires an integer')
        rows=self.sets[f['index']];before=self.snapshot(f['index']);self.clock+=1
        line=next((x for x in rows if x['tag']==f['tag']),None);hit=line is not None;eviction=None;writeback=None
        if line is None:
            if len(rows)==self.ways:
                victim=min(rows,key=lambda x:x['last']);rows.remove(victim)
                eviction=dict(tag=victim['tag'],dirty=victim['dirty'])
                if victim['dirty']:
                    base=((victim['tag']*self.set_count)+f['index'])*self.block_size
                    for offset,data in victim['data'].items():self.memory[base+int(offset)]=data
                    writeback=dict(base=base,data=dict(victim['data']))
            base=address-f['offset']
            line=dict(tag=f['tag'],dirty=False,last=self.clock,data={o:self.memory.get(base+o,0) for o in range(self.block_size)})
            rows.append(line)
        line['last']=self.clock
        if operation=='write':
            line['dirty']=True
            for i in range(size): line['data'][f['offset']+i]=(value>>(8*i))&255
        loaded=sum(line['data'][f['offset']+i]<<(8*i) for i in range(size))
        return dict(address=address,operation=operation,size=size,value=loaded,**f,hit=hit,
                    eviction=eviction,writeback=writeback,before=before,after=self.snapshot(f['index']))


PROGRAM={0:('addi',1,0,256),4:('addi',2,0,0),8:('addi',3,0,4),12:('lw',4,1,0),
         16:('add',2,2,4),20:('addi',1,1,4),24:('addi',3,3,-1),28:('bne',3,0,12),32:('sw',2,0,512)}


class CPU:
    """Semantic subset; bne operand is an absolute byte target, no binary decoder."""
    def __init__(self,memory_size=1024):
        self.registers=[0]*32;self.memory=bytearray(memory_size);self.pc=0

    def check_word(self,address):
        if address%4:raise ValueError('unaligned word address')
        if not 0<=address<=len(self.memory)-4:raise ValueError('word address out of bounds')

    def load(self,address):
        self.check_word(address);return int.from_bytes(self.memory[address:address+4],'little')

    def store(self,address,value):
        self.check_word(address);self.memory[address:address+4]=to_unsigned(value,32).to_bytes(4,'little')

    def run(self,program,stop_pc=None,max_steps=1000):
        events=[]
        while self.pc!=stop_pc:
            if len(events)>=max_steps:raise RuntimeError('maximum steps exceeded')
            if self.pc%4 or self.pc not in program:raise ValueError('invalid instruction address')
            ins=program[self.pc];op,*v=ins
            if op not in ('addi','add','lw','sw','bne') or len(v)!=3:raise ValueError('unsupported semantic instruction')
            a,b,c=v
            if type(c) is not int: raise ValueError('integer operand required')
            for r in ([a,b,c] if op=='add' else [a,b]):
                if type(r) is not int or not 0<=r<32:raise ValueError('invalid register')
            if op in ('addi','lw','sw') and not -2048<=c<=2047:raise ValueError('signed 12-bit immediate required')
            before=self.pc;next_pc=before+4;change=None;access=None;branch=None;dest=None;value=0
            if op=='addi':dest=a;value=self.registers[b]+c
            elif op=='add':dest=a;value=self.registers[b]+self.registers[c]
            elif op=='lw':
                address=to_unsigned(self.registers[b]+c,32);value=self.load(address);dest=a
                access=dict(operation='read',address=address,value=value)
            elif op=='sw':
                address=to_unsigned(self.registers[b]+c,32);value=self.registers[a];self.store(address,value)
                access=dict(operation='write',address=address,value=value)
            elif op=='bne':
                branch=self.registers[a]!=self.registers[b];next_pc=c if branch else next_pc
                if next_pc%4:raise ValueError('unaligned branch target')
            if dest:
                value=to_unsigned(value,32);change=dict(register=dest,before=self.registers[dest],after=value);self.registers[dest]=value
            self.registers[0]=0;self.pc=next_pc
            events.append(dict(step=len(events)+1,before_pc=before,instruction=list(ins),register_change=change,
                               memory_access=access,after_pc=next_pc,branch_taken=branch,registers=list(self.registers)))
        return events


def sum_program():
    cpu=CPU()
    for i,v in enumerate([3,5,7,9]):cpu.store(256+i*4,v)
    trace=cpu.run(PROGRAM,stop_pc=36)
    return dict(events=trace,registers=cpu.registers,result=cpu.load(512),retired=len(trace),branches=[e['branch_taken'] for e in trace if e['branch_taken'] is not None])


def pipeline(instructions):
    """EX-input forwarding. Tuple (op,rd,rs1,rs2); load available MEM end.
    Columns show real frozen ID/IF and bubble occupancy. Stores/branches excluded.
    """
    rows=[];ready={};last_ex=2;stall_cycles=[]
    for index,ins in enumerate(instructions):
        op,rd,rs1,rs2=ins
        if op not in ('lw','add','sub','addi'):raise ValueError('pipeline subset only')
        nominal=last_ex+1
        need=max([ready.get(r,0)+1 for r in (rs1,rs2) if r] or [0])
        ex=max(nominal,need); stalls=ex-nominal
        # Fetch can be frozen behind prior instruction; ID is immediately prior EX except its own stall.
        id_start=nominal-1
        fetch_start=(rows[-1]['id_start'] if rows else 1)
        stages={str(c):'IF' for c in range(fetch_start,id_start)}
        stages.update({str(c):('ID / stall' if c<ex-1 else 'ID') for c in range(id_start,ex)})
        stages.update({str(ex):'EX',str(ex+1):'MEM',str(ex+2):'WB'})
        for c in range(nominal,ex):stall_cycles.append(c)
        if rd:ready[rd]=ex+1 if op=='lw' else ex
        rows.append(dict(instruction=list(ins),id_start=id_start,ex=ex,stalls=stalls,stages=stages))
        last_ex=ex
    return dict(rows=rows,cycles=last_ex+2 if rows else 0,stall_cycles=stall_cycles,
                assumptions='五级单发射，顺序，EX输入转发，I/D分离；仅lw/add/sub/addi，不含分支调度')


def translate(va,page_table,tlb):
    vpn,offset=divmod(va,4096)
    if vpn in tlb:return dict(vpn=vpn,offset=offset,tlb_miss=False,page_fault=False,physical=tlb[vpn]*4096+offset)
    pfn=page_table.get(vpn)
    return dict(vpn=vpn,offset=offset,tlb_miss=True,page_fault=pfn is None,physical=None if pfn is None else pfn*4096+offset)


def experiments():
    direct=Cache(16,4);two=Cache(16,4,2);lru=Cache(16,4,2)
    memory={256+4*i+j:(v>>(8*j))&255 for i,v in enumerate([3,5,7,9]) for j in range(4)}
    integrated=Cache(64,16,memory=memory)
    integrated_events=[integrated.access(x,size=4) for x in [256,260,264,268]]+[integrated.access(512,'write',24,size=4)]
    lru_events=[lru.access(0),lru.access(8,'write',42),lru.access(0),lru.access(16)]
    cpu=sum_program()
    return dict(
      representation=dict(negative5=to_unsigned(-5,8),signed80=to_signed(0x80,8),signedF0=to_signed(0xf0,8),fixedF0=to_signed(0xf0,8)/16,asr=to_signed(to_unsigned(-5,8),8)>>1,little_endian=list((0x12345678).to_bytes(4,'little'))),
      arithmetic=dict(additions=[add_n(120,20),add_n(255,1),add_n(127,1)],full_adders=full_adders(),multiply=multiply(13,11),divide=divide(13,3),alu=[dict(operation=k,result=v) for k,v in [('ADD',22),('AND',12&10),('OR',12|10),('XOR',12^10)]]),
      floating=dict(example=float_record(5.75),rounded=binary32(binary32(2**24)+binary32(1)),special=[float_record(x) for x in [0.0,-0.0,2**-149,float('inf'),float('nan')]],note='每次加法输入与输出显式转为binary32；Python float本身通常binary64；非完整IEEE运算实现'),
      memory=dict(expansion=dict(chips=8,bit_chips=2,groups=4,address_bits=13,internal_bits=11,select_bits=2),banks=[dict(address=a,bank=a%4) for a in [0,1,2,3,0,4,8,12]],translations=[translate(0x12345,{0x12:0xAB},{}),translate(0x22345,{}, {})]),
      cache=dict(fields=Cache(4096,16).fields(0x12345678),direct=[direct.access(a) for a in [0,16,0,16]],two_way=[two.access(a) for a in [0,16,0,16]],lru=lru_events,integrated=integrated_events,read_hit_rate=sum(e['hit'] for e in integrated_events[:4])/4,total_hit_rate=sum(e['hit'] for e in integrated_events)/5,cache_result=integrated_events[-1]['value'],backing_result=integrated.memory.get(512,0)),
      cpu=cpu,
      pipeline=dict(independent=pipeline([('addi',i,0,0) for i in range(1,11)]),forward=pipeline([('add',1,2,3),('sub',4,1,5)]),load_use=pipeline([('lw',1,2,0),('add',3,1,4)]),original=pipeline([('lw',4,1,0),('add',2,2,4),('addi',1,1,0)]),scheduled=pipeline([('lw',4,1,0),('addi',1,1,0),('add',2,2,4)])),
      performance=dict(amat_extra_ns=1+.05*50,amat_total_ns=.95*1+.05*50,amat_other_ns=2+.1*30,cpu_ms=[1e6*1.5/2e9*1000,2e6*2/1e9*1000,1e6*1.2/2e9*1000],cpi=1+.3*.05*40,amdahl=1/(.2+.8/4),amdahl_limit=1/.2,bandwidth_GB_s=64/8*100e6/1e9,rotation_ms=.5/(7200/60)*1000),
      io=dict(polling=[dict(check=i,ready=i==5) for i in range(1,6)],interrupt=[dict(lane=l,event=e) for l,e in [('CPU','运行程序'),('设备','发出请求'),('CPU','保存现场'),('CPU','服务设备'),('CPU','恢复现场')]],dma=[dict(lane=l,event=e) for l,e in [('CPU','配置DMA'),('DMA','读取设备'),('DMA','写入内存'),('设备','完成通知'),('CPU','处理中断')]],note='事件泳道为教学顺序，不是硬件实测时间'))
