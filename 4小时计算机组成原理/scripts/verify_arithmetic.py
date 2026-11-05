"""Independent exact arithmetic checks for source-derived worked examples."""
import fractions,json,pathlib,struct
F=fractions.Fraction
ROOT=pathlib.Path(__file__).resolve().parents[1]
def check(name,actual,expected,out):
 assert actual==expected,(name,actual,expected)
 out.append(dict(name=name,result=str(actual)))
def booth(x,y,n):
 # Signed full product, using one extra accumulator bit for the negative endpoint.
 aw=n+1;mask=(1<<aw)-1;A=0;Q=y&((1<<n)-1);old=0
 for _ in range(n):
  pair=((Q&1)<<1)|old
  if pair==1:A=(A+x)&mask
  elif pair==2:A=(A-x)&mask
  combined=(A<<(n+1))|(Q<<1)|old;width=2*n+2
  if combined&(1<<(width-1)):combined-=1<<width
  combined>>=1;old=combined&1;Q=(combined>>1)&((1<<n)-1);A=(combined>>(n+1))&mask
 raw=((A<<n)|Q)&((1<<(2*n))-1)
 return raw-(1<<(2*n)) if raw&(1<<(2*n-1)) else raw
def restoring(a,b,n):
 r=a;q=0
 for _ in range(n):
  r*=2;bit=int(r>=b)
  if bit:r-=b
  q=(q<<1)|bit
 return q,r
def nonrestoring(a,b,n):
 r=a-b;q=0
 for _ in range(n):
  r=2*r+(b if r<0 else -b);q=(q<<1)|int(r>=0)
 if r<0:r+=b
 return q,r
def main():
 out=[]
 for x in range(-8,8):
  for y in range(-8,8):assert booth(x,y,4)==x*y,(x,y)
 out.append(dict(name='4-bit Booth full signed input enumeration',combinations=256))
 for name,x,y,n,bits in [('Booth4a',3,-11,5,'111011111'),('Booth4b',13,-3,5,'111011001'),('Booth5',-23,5,6,'11110001101')]:
  check(name,booth(x,y,n),x*y,out)
  fractional_width=8 if n==5 else 10
  check(name+' fixed fraction bits',format((x*y)&((1<<(fractional_width+1))-1),f'0{fractional_width+1}b'),bits,out)
 for name,x,y in [('raw4a',14,13),('raw4b',13,10),('raw4c',13,11),('raw4d',13,3),('raw_two_bit',63,57)]:
  expected={'raw4a':182,'raw4b':130,'raw4c':143,'raw4d':39,'raw_two_bit':3591}[name];check(name,x*y,expected,out)
 for a,b,n,expected in [(11,13,4,(13,7)),(9,11,4,(13,1)),(22,31,5,(22,22)),(21,27,5,(24,24))]:
  check(f'restoring {a}/{b}',restoring(a,b,n),expected,out)
  check(f'nonrestoring {a}/{b}',nonrestoring(a,b,n),expected,out)
  q,r=expected;assert F(a,1<<n)==F(b,1<<n)*F(q,1<<n)+F(r,1<<(2*n))
 check('19/128 fixed ten fraction bits',format(int(F(19,128)*1024),'010b'),'0010011000',out)
 check('-58 fixed eleven bits',format((-58)&2047,'011b'),'11111000110',out)
 check('15-24 eight bits',(15-24)&255,247,out)
 check('overflow -97-41 eight bits',(-97-41)&255,118,out)
 check('signed right shift -26 by2',-26>>2,-7,out)
 check('float 002-095 exact',F(13,16)*2-F(10,16)*8,F(-27,8),out)
 check('float 002-099 exact',F(13,16)*4+F(11,16)*2,F(37,8),out)
 check('float 002-101 exact',F(-5,8)*F(1,32)-F(7,8)*F(1,16),F(-19,256),out)
 check('float 008-115 exact',F(219,256)*32-F(172,256)*128,F(-469,8),out)
 check('float 008-116 encoded truncate',F(-235,256)*64,F(-235,4),out)
 check('float 008-116 nearest even',F(round(F(-469,8)/F(1,4)),4),F(-117,2),out)
 a=struct.unpack('<f',struct.pack('<I',0x00c00000))[0];b=struct.unpack('<f',struct.pack('<I',0x00800000))[0]
 check('IEEE exact subnormal difference',struct.unpack('<I',struct.pack('<f',a-b))[0],0x00400000,out)
 coverage=[];scenes=beats=chars=0
 for p in sorted((ROOT/'content').glob('module_04*.json')):
  m=json.loads(p.read_text(encoding='utf8'));scenes+=len(m['scenes']);beats+=sum(len(s['beats']) for s in m['scenes']);chars+=sum(len(b['text']) for s in m['scenes'] for b in s['beats']);coverage.extend(x['source'] for x in m['coverage'])
 expected={f'input_002-{i:03}' for i in range(1,116)}|{f'input_008-{i:03}' for i in range(1,145)}
 assert set(coverage)==expected and len(coverage)==259
 report=dict(allPassed=True,checks=len(out),boothInputCombinations=256,sourceSlidesCovered=259,scenes=scenes,beats=beats,narrationCharacters=chars,items=out)
 (ROOT/'build').mkdir(exist_ok=True);(ROOT/'build/arithmetic-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps({k:v for k,v in report.items() if k!='items'},ensure_ascii=False))
if __name__=='__main__':main()
