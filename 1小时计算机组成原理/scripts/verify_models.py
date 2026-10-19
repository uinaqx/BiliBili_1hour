"""Independent calculations and small hardware models for every numeric example family."""
import collections,json,math,pathlib,sys
sys.stdout.reconfigure(encoding='utf-8');ROOT=pathlib.Path(__file__).resolve().parents[1];checks=0;results=[]
def check(condition):
 global checks
 assert condition;checks+=1
def signed(x):return x-256 if x&128 else x
def ripple(a,b):
 carry=0;result=0
 for i in range(8):
  x=(a>>i)&1;y=(b>>i)&1;s=x^y^carry;carry=(x&y)|(x&carry)|(y&carry);result|=s<<i
 return result,carry
for a in range(256):
 for b in range(256):
  value,carry=ripple(a,b);check(value==(a+b)%256 and carry==(a+b)//256)
  overflow=bool((~(a^b)&(a^value))&128);check(overflow==(not(-128<=signed(a)+signed(b)<=127)))
check(signed(251)==-5);check(signed(255)==-1);check(signed(128)==-128)
check((248>>1)==124);check(signed((248>>1)|128)==-4);check(signed((253>>1)|128)==-2)
check(int('1101',2)==13 and int('10',16)==16);check(.5+.125==.625)
check(13+(13<<1)==39);check(13+signed((~7+1)&255)==6)
results.append(dict(topic='bit arithmetic',result='all 65536 eight-bit operand pairs checked against integer arithmetic; signed overflow checked separately'))
for a in range(2):
 for b in range(2):
  for c in range(2):check((a^b^c)+2*((a&b)|(a&c)|(b&c))==a+b+c)
check(2**13*8//8==8192);check(2**12*16//8==8192)
number=0x12345678;check(list(number.to_bytes(4,'little'))==[0x78,0x56,0x34,0x12]);check(list(number.to_bytes(4,'big'))==[0x12,0x34,0x56,0x78])
check(math.log2(4096//64)==6 and 32-6-6==20)
check(2+.1*40==.9*2+.1*42==6)
lines=[None,None];trace=[]
for block in [0,2,0]:
 index=block%2;hit=lines[index]==block;trace.append(hit);lines[index]=block
check(trace==[False,False,False] and lines==[0,None])
lru=collections.OrderedDict()
for name in ['A','B','A','C']:
 if name in lru:del lru[name]
 elif len(lru)==2:lru.popitem(last=False)
 lru[name]=True
check(list(lru)==['A','C'])
results.append(dict(topic='storage and cache',result='capacity, endianness, address fields, weighted average, conflict trace and LRU checked'))
memory=bytearray(512)
for address,value in [(100,13),(104,7)]:memory[address:address+4]=value.to_bytes(4,'little')
registers=[0]*4;pc=0;snapshots=[]
program=[('LOAD',1,100),('LOAD',2,104),('ADD',3,1,2),('STORE',3,108)]
for op,*args in program:
 if op=='LOAD':registers[args[0]]=int.from_bytes(memory[args[1]:args[1]+4],'little')
 elif op=='ADD':registers[args[0]]=registers[args[1]]+registers[args[2]]
 else:memory[args[1]:args[1]+4]=registers[args[0]].to_bytes(4,'little')
 pc+=4;snapshots.append(dict(pc=pc,registers=registers.copy(),memory108=int.from_bytes(memory[108:112],'little')))
check(snapshots[2]['registers'][3]==20 and snapshots[2]['memory108']==0 and snapshots[2]['pc']==12)
check(snapshots[3]['memory108']==20 and pc==16)
check(100+12==112)
check(1e9*2/2e9==1e9*4/4e9==1)
schedule=[[(i+j,j) for j in range(5)] for i in range(4)];check(max(c for row in schedule for c,j in row)+1==8);check(4*5/8==2.5)
check(abs(1/(.2+.8/4)-2.5)<1e-12)
check(64/8*200e6==1.6e9);check(256/(32/8)==64);check(abs(64/100e6-640e-9)<1e-20)
for va,frame,expected in [(0x1234,9,0x9234),(0x2567,9,0x9567)]:check((frame<<12)|(va&0xfff)==expected)
for offset in range(4096):check(((9<<12)|offset)&0xfff==offset)
results.append(dict(topic='CPU, performance, I/O and virtual memory',result='byte-addressed four-instruction emulator, pipeline schedule, time/rate units and all page offsets checked'))
report=dict(allPassed=True,assertions=checks,exampleFamilies=results,programSnapshots=snapshots)
(ROOT/'build/model-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('MODEL_CHECKS_PASSED',checks)
