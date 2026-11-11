"""Small explicit digital-electronics reference models. No physical timing claims."""
def unsigned(bits):return int(bits,2)
def signed(bits):return int(bits,2)-(1<<len(bits) if bits[0]=='1' else 0)
def bcd(n):return ''.join(f'{int(c):04b}' for c in str(n))
def gray(n):return n^(n>>1)
def majority(a,b,c):return (a&b)|(a&c)|(b&c)
def full_adder(a,b,ci):return a^b^ci,majority(a,b,ci)
def priority(inputs):
    active=[i for i,val in enumerate(inputs) if val];return (max(active),1) if active else (0,0)
def sr(s,r,q):
    if s and r:return None # forbidden NOR high-active input combination, not a valid next-state row
    return 1 if s else 0 if r else q
def jk(j,k,q):return (j&(1-q))|((1-k)&q)
def mod3(q):return (q+1)%3 if q<3 else 0
def mod3_d(q):
    q1,q0=(q>>1)&1,q&1;return ((1-q1)&q0)*2+((1-q1)&(1-q0))
def shift(q,d):return ((q<<1)|d)&15
def dac(code):
    if code not in range(8):raise ValueError('3-bit code required')
    return code
def adc_floor(vin):
    if not 0<=vin<8:raise ValueError('Teaching model domain: 0 <= Vin < 8 V')
    return int(vin)
def build_data():
    return dict(kind='ideal-functional-models',notes=['Finite checks establish the stated examples, not device electrical compliance.','ADC is an explicit floor-bin model, not a rounded quantizer.'],majority=[dict(abc=f'{n:03b}',f=int(n.bit_count()>=2)) for n in range(8)],mod3=[dict(current=f'{q:02b}',next=f'{mod3(q):02b}',d=f'{mod3_d(q):02b}') for q in range(4)],dac=[dict(code=f'{d:03b}',volts=dac(d)) for d in range(8)],adc=[dict(low=n,highExclusive=n+1,code=f'{n:03b}') for n in range(8)])
