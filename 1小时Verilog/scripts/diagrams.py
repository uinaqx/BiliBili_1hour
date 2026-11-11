"""Slow-motion views of actual self-checking Verilog VCD records and explicit circuit models."""
import functools,json,math,pathlib
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path(__file__).resolve().parents[1]
BG='#10243a';WHITE='#eff5ff';MUTED='#9fb2ca';BLUE='#70cfff';ORANGE='#ffbd68';GREEN='#8fe0b2';GRID='#31516c'
@functools.lru_cache(32)
def font(n):return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
@functools.lru_cache(1)
def data():return json.loads((ROOT/'build/simulation-data.json').read_text(encoding='utf8'))
def value_at(signal,t):
 result='x'
 for at,value in signal['events']:
  if at>t+1e-8:break
  result=value
 return result
def label(value,width):
 if any(c in value for c in 'xz'):return value
 return str(int(value,2)) if width>1 else value
def render(visual,phase,progress,size=(1165,310)):
 w,h=size;small=w<700;im=Image.new('RGB',size,BG);d=ImageDraw.Draw(im);p=max(0,min(1,float(progress)));fs=20 if small else 24
 def text(x,y,s,n=fs,color=WHITE,anchor='lt'):d.text((x,y),str(s),font=font(n),fill=color,anchor=anchor)
 def box(rect,s,color=BLUE):d.rounded_rectangle(rect,9,fill='#19384d',outline=color,width=2);text((rect[0]+rect[2])/2,(rect[1]+rect[3])/2,s,fs,color,'mm')
 kind=visual['kind']
 if kind=='wave':
  trace=data()[visual['trace']];signals=visual.get('signals') or trace['selectedSignals'];signals=[s for s in signals if s in trace['signals']][:5]
  end=trace['endNs'];cursor=end*p;left=92 if small else 125;right=w-24;top=47;bottom=h-42;step=(bottom-top)/max(1,len(signals));span=right-left
  text(8,8,'实际RTL仿真 · 放慢展示',18 if small else 24,ORANGE)
  for j in range(5):
   x=left+span*j/4;d.line((x,top-5,x,bottom),fill=GRID);text(x,h-29,f'{end*j/4:g}',16 if small else 21,MUTED,'mt')
  text(w-9,h-5,'ns',16 if small else 20,MUTED,'rs')
  for i,name in enumerate(signals):
   signal=trace['signals'][name];middle=top+i*step+step/2;amplitude=min(10,step*.26);text(left-8,middle,name,18 if small else 24,BLUE,'rm')
   def y(value):return middle if signal['width']>1 or any(c in value for c in 'xz') else middle+amplitude*(1-2*int(value,2))
   events=signal['events'];events=events+[[end,events[-1][1]]] if events else [[0,'x'],[end,'x']]
   for k,((a,v),(b,_)) in enumerate(zip(events,events[1:])):
    x1=left+span*a/end;x2=left+span*b/end;color=GREEN if a<=cursor else GRID
    if signal['width']==1:
     if any(c in v for c in 'xz'):
      d.rectangle((x1,middle-amplitude,x2,middle+amplitude),fill='#343747')
      if x2-x1>=12:text((x1+x2)/2,middle,v,16 if small else 21,MUTED,'mm')
     else:d.line((x1,y(v),x2,y(v)),fill=color,width=3)
     if k:d.line((x1,y(events[k-1][1]),x1,y(v)),fill=color,width=2)
    else:
     d.line((x1,middle-amplitude,x2,middle-amplitude),fill=color,width=2);d.line((x1,middle+amplitude,x2,middle+amplitude),fill=color,width=2)
     if k:d.line((x1,middle-amplitude,x1,middle+amplitude),fill=color,width=2)
     if x2-x1>28 or any(c in v for c in 'xz') and x2-x1>=12:text((x1+x2)/2,middle,label(v,signal['width']),16 if small else 21,color,'mm')
   current=label(value_at(signal,cursor),signal['width']);text(w-8,middle,current,17 if small else 22,ORANGE,'rm')
  x=left+span*p;d.line((x,top-8,x,bottom+2),fill=ORANGE,width=2)
 elif kind in ['gate','parallel','invert']:
  key={'gate':'and_gate','parallel':'parallel_gates','invert':'generate_inv'}[kind];trace=data()[key];t=trace['endNs']*p
  if kind=='invert':
   a=int(value_at(trace['signals']['a'],t),2);yy=int(value_at(trace['signals']['y'],t),2)
   for i in range(4):
    y=55+i*(h-70)/4;text(18,y,f'a[{i}]={(a>>i)&1}',fs,BLUE);box((w*.38,y-8,w*.61,y+30),'取反');text(w*.76,y,f'y[{i}]={(yy>>i)&1}',fs,GREEN);d.line((w*.2,y+12,w*.38,y+12),fill=BLUE,width=3);d.line((w*.61,y+12,w*.75,y+12),fill=GREEN,width=3)
  else:
   a=value_at(trace['signals']['a'],t);b=value_at(trace['signals']['b'],t)
   text(18,30,'当前仿真输入',fs,ORANGE);box((20,h*.35,w*.25,h*.7),f'a={a}  b={b}')
   for i,signal in enumerate(['y'] if kind=='gate' else ['y_and','y_or']):
    cy=h*.4+i*h*.35;box((w*.43,cy-25,w*.65,cy+35),'与门' if i==0 else '或门');d.line((w*.25,h*.52,w*.34,h*.52,w*.34,cy+5,w*.43,cy+5),fill=BLUE,width=3);d.line((w*.65,cy+5,w*.78,cy+5),fill=GREEN,width=3);text(w*.8,cy+5,f'{signal}={value_at(trace["signals"][signal],t)}',fs,GREEN,'lm')
 elif kind=='bits':
  example=visual.get('mode')=='width' and visual.get('narrationPart')==0
  n=10 if example else min(15,int(16*p));text(15,18,"4'b1010 = 4'hA = 十进制10" if example else f'四位无符号数：{n}（范围0～15）',fs,ORANGE)
  size=min((w-55)/4,130);x=(w-4*size)/2
  for i in range(4):
   bit=(n>>(3-i))&1;box((x+i*size+4,85,x+(i+1)*size-4,165),str(bit),GREEN if bit else BLUE);text(x+(i+.5)*size,190,f'权重 {2**(3-i)}',fs,MUTED,'mt')
  text(w/2,h-28,'高位 ← 位置与位宽 → 低位',fs,WHITE,'mm')
 elif kind=='shift':
  assert w>=1000,'Shift comparison uses the large concept panel'
  for row,(op,result,meaning) in enumerate([('>> 1','0110','无符号：12 → 6，左侧补0'),('>>> 1','1110','signed：−4 → −2，左侧补符号位1')]):
   y=27+row*143;text(15,y,meaning,24,ORANGE)
   for group,bits in enumerate(['1100',result]):
    start=165 if group==0 else 710
    for i,bit in enumerate(bits):
     x=start+i*78;box((x,y+43,x+66,y+89),bit,GREEN if group and i==0 else BLUE)
   a,b=510,685;cy=y+66;d.line((a,cy,b,cy),fill=GRID,width=3);text((a+b)/2,cy-26,op,23,WHITE,'mm')
   q=min(1,max(0,p*2-row));x=a+(b-a)*q;d.line((a,cy,x,cy),fill=ORANGE,width=4);d.polygon([(b,cy),(b-12,cy-7),(b-12,cy+7)],fill=ORANGE if q==1 else GRID)
  text(w-18,h-5,'同一位型；先确认有符号属性与表达式上下文',21,MUTED,'rs')
 elif kind=='flow':
  labels=['设计与测试','编译','运行仿真','检查结果'];active=min(3,int(p*4))
  for i,s in enumerate(labels):
   x=15+i*w/4;box((x,95,x+w/4-30,175),s,ORANGE if i<=active else GRID)
   if i<3:text(x+w/4-18,135,'→',fs,BLUE,'mm')
  text(20,225,'仿真验证行为；综合形成硬件结构；上板还需实现与时序检查',21 if small else 25,MUTED)
 elif kind=='fsm':
  trace=data()['fsm'];at=trace['endNs']*p;state=value_at(trace['signals']['state'],at);state=int(state,2) if set(state)<={'0','1'} else -1
  text(10,10,'实际仿真状态',18 if small else 24,ORANGE);text(w-12,12,f't={at:.1f}ns',18 if small else 23,MUTED,'rt')
  centers=[(w*.17,h*.49),(w*.5,h*.49),(w*.83,h*.49)];radius=min(62,w*.1)
  for i,(x,y) in enumerate(centers):d.ellipse((x-radius,y-radius,x+radius,y+radius),outline=ORANGE if i==state else BLUE,width=4,fill='#294b56' if i==state else BG);text(x,y,['空闲','运行','等待'][i],fs,WHITE,'mm')
  for i,s in enumerate(['go=1','done=1']):
   x,y=centers[i];xx=centers[i+1][0];d.line((x+radius+5,y,xx-radius-5,y),fill=GREEN,width=3);text((x+xx)/2,y-30,s,fs,GREEN,'mm')
  d.line((centers[2][0],h*.75,centers[0][0],h*.75),fill=BLUE,width=3);text(w/2,h*.87,'等待后下一拍返回空闲',fs,MUTED,'mm')
  d.line((15,h-9,w-15,h-9),fill=GRID,width=2);x=15+(w-30)*p;d.ellipse((x-4,h-13,x+4,h-5),fill=ORANGE)
 else:raise ValueError(kind)
 return im
