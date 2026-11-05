"""Independent numeric/finite-code checks for modules 02 and 03.

These calculations verify the explicitly stated representation models. They do
not claim to execute the legacy C slides or every compiler's evaluation mode.
"""
import fractions,hashlib,itertools,json,math,pathlib,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
def run():
 checks=[]
 def check(name,actual,expected):
  assert actual==expected,(name,actual,expected)
  checks.append(dict(name=name,actual=actual,expected=expected))
 def remainder(value,g):
  while value.bit_length()>=g.bit_length():value^=g<<(value.bit_length()-g.bit_length())
  return value
 def encode(value,g):
  shifted=value<<(g.bit_length()-1);return shifted^remainder(shifted,g)
 def f32(x):return struct.unpack('>f',struct.pack('>f',x))[0]
 def bits32(x):return struct.unpack('>I',struct.pack('>f',x))[0]
 def hamming(data):
  h=[0]*8
  for j,pos in enumerate([3,5,6,7]):h[pos]=(data>>j)&1
  for p in [1,2,4]:h[p]=sum(h[j] for j in range(1,8) if j&p and j!=p)%2
  return sum(h[j]<<(j-1) for j in range(1,8))
 def syndrome(value):
  result=0
  for p in [1,2,4]:
   if sum((value>>(j-1))&1 for j in range(1,8) if j&p)%2:result|=p
  return result
 check('ASCII_0',ord('0'),0x30);check('ASCII_5',ord('5'),0x35)
 check('GB2312_middle_example',list('中'.encode('gb2312')),[0xD6,0xD0])
 check('GB2312_region_to_internal',[54+0xA0,48+0xA0],[0xD6,0xD0])
 check('32x32_monochrome_glyph_bytes',32*32//8,128)
 check('hex_F96_decimal',int('F96',16),3990)
 check('binary10011100_integer_oct',oct(int('10011100',2)),'0o234')
 check('2010_binary',format(2010,'b'),'11111011010')
 check('17_over_128',fractions.Fraction(17,128)==sum(fractions.Fraction(int(ch),2**(i+1)) for i,ch in enumerate('0010001')),True)
 frac=fractions.Fraction(3,5);s=''
 for _ in range(8):frac*=2;q=frac.numerator//frac.denominator;s+=str(q);frac-=q
 check('0.6_first8_binary',s,'10011001')
 check('1TB_in_GiB_round1',round(10**12/2**30,1),931.3)
 check('2.5TiB_byte_address_bits',(int(2.5*2**40)-1).bit_length(),42)
 check('8bit_twos_minus3',(-3)&255,253)
 check('8bit_signed_values',[(x&255)-256 if x&128 else x&255 for x in [127,128,129,257]],[127,-128,-127,1])
 check('double_sign_add_fixed',(11+(-5))%64,6)
 check('double_sign_sub_fixed',(11-(-5))%64,16)
 check('sign_extended_sum',0x55C3-100,0x555F)
 check('biased_plus21',format(32+21,'06b'),'110101')
 check('biased_minus21',format(32-21,'06b'),'001011')
 check('BCD8_plus7_corrected',8+7+6,0x15)
 check('float3.3_bits',f'{bits32(3.3):08X}','40533333')
 check('float1.1_bits',f'{bits32(1.1):08X}','3F8CCCCD')
 check('double3.3_over1.1',3.3/1.1,2.9999999999999996)
 check('double_ratio_int',int(3.3/1.1),2)
 check('binary32_div_round',f32(f32(3.3)/f32(1.1)),3.0)
 check('wider_div_then_int',int(f32(3.3)/f32(1.1)),2)
 check('binary32_min_subnormal',f32(2**-149),2**-149)
 check('binary64_min_subnormal',math.ldexp(1.0,-1074),5e-324)
 check('integer_float_counterexample',int(f32(16777217)),16777216)
 check('float_integer_counterexample',f32(int(f32(1.5))),1.0)
 check('NaN_double_negation_equality',float('nan')==-(-float('nan')),False)
 check('cancellation_counterexample',(1e20+1)-1e20,0.0)
 h=[hamming(x) for x in range(16)]
 check('hamming_1101_code',format(hamming(0b1101),'07b'),'1100110')
 check('hamming_min_distance',min((x^y).bit_count() for x,y in itertools.combinations(h,2)),3)
 for x in h:
  check('hamming_valid_syndrome',syndrome(x),0)
  for position in range(1,8):
   bad=x^(1<<(position-1));s=syndrome(bad)
   check('hamming_single_error_position',s,position)
   check('hamming_single_error_restoration',bad^(1<<(s-1)),x)
 ext=[x|((x.bit_count()%2)<<7) for x in h]
 check('extended_hamming_min_distance',min((x^y).bit_count() for x,y in itertools.combinations(ext,2)),4)
 check('CRC1100_1011',format(encode(0b1100,0b1011),'07b'),'1100010')
 check('CRC1101_1011',format(encode(0b1101,0b1011),'07b'),'1101001')
 crc_models=[]
 for g,k,expected_distance in [(0b1011,4,3),(0b11101,3,4),(0b1101111,16,4)]:
  r=g.bit_length()-1;n=k+r;codes=[encode(x,g) for x in range(1<<k)]
  check('CRC_all_codewords_divisible',all(remainder(x,g)==0 for x in codes),True)
  check('CRC_linear_minimum_weight',min(x.bit_count() for x in codes if x),expected_distance)
  singles={remainder(1<<j,g) for j in range(n)}
  doubles={remainder((1<<i)|(1<<j),g) for i,j in itertools.combinations(range(n),2)}
  check('CRC_all_single_distinct',len(singles),n)
  check('CRC_single_double_overlap',bool(singles&doubles),expected_distance==3)
  crc_models.append(dict(generator=f'{g:b}',dataBits=k,parityBits=r,length=n,codewordsEnumerated=len(codes),minimumDistance=expected_distance,singleAndDoubleDisjoint=not bool(singles&doubles)))
 paths=[ROOT/'content'/f'module_{n}.json' for n in ['02','03']]
 result=dict(allPassed=True,checks=len(checks),scope='independent numeric representations, stated IEEE binary32/binary64 models, exhaustive finite Hamming and CRC codewords; does not execute legacy C source or certify all compiler modes',moduleSha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},crcModels=crc_models,items=checks)
 out=ROOT/'build/data-example-verification.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in result.items() if k!='items'},ensure_ascii=False))
if __name__=='__main__':run()
