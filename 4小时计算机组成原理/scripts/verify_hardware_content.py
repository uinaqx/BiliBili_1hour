"""Independent arithmetic checks for hardware chapter examples, no online services."""
import collections,json,pathlib,math,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def hamming(data,odd=False):
 a=[0]*8
 for p,v in zip([3,5,6,7],data):a[p]=int(v)
 for p in [1,2,4]:a[p]=sum(a[i] for i in range(1,8) if i&p and i!=p)%2^int(odd)
 return a
def syndrome(a):return sum(p*(sum(a[i] for i in range(1,8) if i&p)%2) for p in [1,2,4])
def cache(seq,policy):
 slots=[];arrival={};last={};freq={};hits=0;replaced=[]
 for t,v in enumerate(seq):
  if v in slots:hits+=1;last[v]=t;freq[v]+=1;continue
  if len(slots)==4:
   old=min(slots,key=lambda x:(arrival[x] if policy=='FIFO' else last[x] if policy=='LRU' else (freq[x],arrival[x])))
   slots.remove(old);replaced.append(old)
  slots.append(v);arrival[v]=last[v]=t;freq[v]=1
 return dict(hits=hits,misses=len(seq)-hits,blocks=slots,evicted=replaced)
def nesting(masks):
 names='ABCD';pending=set(names);stack=[];entered=[];done=[]
 while pending or stack:
  mask=masks[stack[-1]] if stack else '0000'
  allowed=[x for i,x in enumerate(names) if x in pending and mask[i]=='0']
  if allowed:
   x=allowed[0];pending.remove(x);stack.append(x);entered.append(x)
  else:done.append(stack.pop())
 return ''.join(entered),''.join(done)
def main():
 checks=[]
 def check(name,actual,expected):
  assert actual==expected,(name,actual,expected);checks.append(dict(name=name,result=actual))
 check('extension-32bits',(2**(32-24)-250)*2**12,24576)
 feasible=lambda L:(2**(L-18)-29)*2**6>=107 and 2**(L-18)>=29
 minimum=next(L for L in range(18,40) if feasible(L));check('instruction-bit-lower-bound',minimum,23);check('instruction-byte-length',math.ceil(minimum/8)*8,24)
 check('relative-target',hex(0x2000+2+6),'0x2008')
 check('chip-expansion',(64*8)//(16*1),32);check('mixed-expansion',(4*8)//(1*4),8)
 ranges=[(0xf0000+i*8192,0xf0000+(i+1)*8192-1) for i in range(8)]
 check('eprom-coverage',sum(b-a+1 for a,b in ranges),65536);check('eprom-last-range',list(map(hex,ranges[-1])),['0xfe000','0xfffff'])
 for data,expected in [('0101','0100101'),('0011','1000011')]:check('hamming-even-'+data,''.join(map(str,hamming(data)[1:])),expected)
 check('hamming-odd-0011',''.join(map(str,hamming('0011',True)[1:])),'0101011')
 for received,expected in [('0100111',6),('0101101',4)]:check('hamming-syndrome-'+received,syndrome([0]+list(map(int,received))),expected)
 for n in range(16):
  a=hamming(f'{n:04b}');assert syndrome(a)==0
  for p in range(1,8):
   b=a[:];b[p]^=1;s=syndrome(b);b[s]^=1;assert b==a
 checks.append(dict(name='all-16-hamming-words-with-7-single-bit-errors',result='112 single-error corrections passed'))
 check('concentrated-refresh-us',128*.5,64);check('refresh-percentage',128*.5/2000*100,3.2);check('distributed-refresh-row-spacing-us',2000/128,15.625)
 check('four-bank-T-equals-4tau-fourwords-in-tau',4+3,7)
 check('pipeline-six-level-nine-instructions-time',6+9-1,14)
 check('pipeline-speedup-rounded',round(54/14,6),3.857143);check('pipeline-efficiency-percent',round(9/14*100,6),64.285714)
 seq=[22,11,22,19,7,16,4,3]
 for pol,blocks,evicted in [('FIFO',{16,4,3,7},[22,11,19]),('LRU',{16,4,3,7},[11,22,19])]:
  r=cache(seq,pol);check(pol+'-hits',r['hits'],1);check(pol+'-evicted',r['evicted'],evicted);assert set(r['blocks'])==blocks
 r=cache([22,11,22,19,11,16,22,4,3],'LFU');check('LFU-hits',r['hits'],3);check('LFU-evicted',r['evicted'],[19,16]);assert set(r['blocks'])=={22,11,4,3}
 check('FIFO-thrashing-misses',cache([22,11,19,7,16,22,11,19],'FIFO')['misses'],8)
 check('original-masks-entry-and-completion',list(nesting(dict(A='1111',B='0111',C='0011',D='0001'))),['ABCD','ABCD'])
 check('new-masks-entry-and-completion',list(nesting(dict(A='1111',B='0100',C='0110',D='0111'))),['ABCD','ADCB'])
 files=[ROOT/'content'/f'module_{n}.json' for n in ['06','07','08','09','10']]
 report=dict(allPassed=True,checks=len(checks),scope='independent numerical and algorithmic checks for selected worked examples; full source-page coverage is recorded in module files',moduleSha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},items=checks)
 (ROOT/'build/hardware-content-checks.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k not in ['items','moduleSha256']},ensure_ascii=False))
if __name__=='__main__':main()
