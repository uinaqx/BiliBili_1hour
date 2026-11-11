"""Exhaustive finite-domain checks of the actual lesson examples, independently calculated."""
import hashlib,itertools,json,pathlib
import examples as e
ROOT=pathlib.Path(__file__).resolve().parents[1]
def main():
    checks=[]
    def check(name,actual,expected):
        assert actual==expected,(name,actual,expected);checks.append(name)
    check('1101 unsigned',e.unsigned('1101'),13);check('1101 4-bit signed',e.signed('1101'),-3);check('BCD thirteen',e.bcd(13),'00010011');check('BCD twenty-five',e.bcd(25),'00100101');check('hex A5',int('A5',16),int('10100101',2));check('4-bit carry',15+1,16);check('low four bits',(15+1)&15,0)
    for n in range(16):check('4-bit signed range '+str(n),e.signed(f'{n:04b}'),n if n<8 else n-16)
    codes=[e.gray(n) for n in range(4)];check('2-bit Gray order',codes,[0,1,3,2])
    for a,b in zip(codes,codes[1:]+codes[:1]):check(f'Gray adjacent {a} {b}',(a^b).bit_count(),1)
    for a,b in itertools.product(range(2),repeat=2):
        check(f'De Morgan NAND {a}{b}',1-(a&b),(1-a)|(1-b));check(f'De Morgan NOR {a}{b}',1-(a|b),(1-a)&(1-b));check(f'absorption {a}{b}',a|(a&b),a);s,c=a^b,a&b;check(f'half adder {a}{b}',s+2*c,a+b)
    for a,b,c in itertools.product(range(2),repeat=3):
        n=4*a+2*b+c;s,co=e.full_adder(a,b,c);check(f'full adder {n}',2*co+s,a+b+c);check(f'majority {n}',e.majority(a,b,c),int(a+b+c>=2));check(f'Kmap SOP {n}',((1-a)&c)|(a&b),int(n in {1,3,6,7}));check(f'Kmap edge wrap {n}',1-c,int(n in {0,2,4,6}));check(f'consensus steady-state {n}',(a&b)|((1-a)&c),(a&b)|((1-a)&c)|(b&c))
    for d0,d1,s in itertools.product(range(2),repeat=3):check(f'mux {d0}{d1}{s}',((1-s)&d0)|(s&d1),[d0,d1][s])
    for n in range(4):check(f'decoder {n}',[int(n==i) for i in range(4)].count(1),1)
    for n in range(16):
        inputs=[(n>>i)&1 for i in range(4)];code,valid=e.priority(inputs);expected=max([i for i,v in enumerate(inputs) if v],default=0);check(f'priority encoder {n}',(code,valid),(expected,int(n!=0)))
    check('seven segment digit2',set('abdeg'),set(['a','b','g','e','d']))
    for s,r,q in itertools.product(range(2),repeat=3):check(f'active-high NOR SR {s}{r}{q}',e.sr(s,r,q),None if s and r else 1 if s else 0 if r else q)
    for j,k,q in itertools.product(range(2),repeat=3):check(f'JK {j}{k}{q}',e.jk(j,k,q),q if j==k==0 else 0 if (j,k)==(0,1) else 1 if (j,k)==(1,0) else 1-q)
    for t,q in itertools.product(range(2),repeat=2):check(f'T {t}{q}',t^q,q if not t else 1-q)
    for q in range(4):check(f'mod3 next-state {q}',e.mod3_d(q),[1,2,0,0][q]);check(f'mod3 behavioral {q}',e.mod3(q),[1,2,0,0][q])
    check('timing sum ns',2+5+1,8);check('timing max MHz',1000/(2+5+1),125)
    for q in range(4):check(f'binary counter {q}',(q+1)&3,[1,2,3,0][q])
    for q in range(16):check(f'specified decade recovery {q}',q+1 if q<9 else 0,[1,2,3,4,5,6,7,8,9,0,0,0,0,0,0,0][q])
    q=0
    for i,(d,expected) in enumerate(zip([1,0,1],[1,2,5])):q=e.shift(q,d);check(f'shift lesson edge {i+1}',q,expected)
    for q in range(16):
        for d in range(2):check(f'shift old/new {q}:{d}',e.shift(q,d),(q%8)*2+d)
    for q in [1,2,4,8]:check(f'ring {q}',((q<<1)|(q>>3))&15,{1:2,2:4,4:8,8:1}[q])
    check('all-zero ring trap',((0<<1)|(0>>3))&15,0);check('1024x8 bits',1024*8,8192);check('1024x8 bytes',1024*8//8,1024);check('address count',2**10,1024);check('bit expansion',2*1024*4,1024*8);check('word expansion',2*1024*8,2048*8)
    for code in range(8):
        check(f'DAC transfer {code}',e.dac(code),8*code/8)
        for frac in [0,.1,.5,.9999]:check(f'ADC floor bin {code}:{frac}',e.adc_floor(code+frac),code)
    for vin in [-1,8,9]:
        try:e.adc_floor(vin)
        except ValueError:checks.append(f'ADC excludes out-of-domain {vin}')
        else:raise AssertionError(vin)
    data=e.build_data();(ROOT/'build/verified-examples.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    rtl=json.loads((ROOT/'build/rtl-verification.json').read_text(encoding='utf8'));assert rtl['allPassed']
    report=dict(allPassed=True,checks=len(checks),courseSha256=hashlib.sha256((ROOT/'public/course.json').read_bytes()).hexdigest(),exampleSourceSha256=hashlib.sha256((ROOT/'scripts/examples.py').read_bytes()).hexdigest(),scope='Finite reference models and numerical worked examples; actual RTL checked separately.',rtlReport='build/rtl-verification.json',items=checks)
    (ROOT/'build/examples-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print('DIGITAL_EXAMPLES_PASSED',len(checks),flush=True)
if __name__=='__main__':main()
