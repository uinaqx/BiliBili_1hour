"""Authored finite examples; animation changes emphasis, never the mathematical data."""
import functools,math,itertools
import numpy as np
from PIL import Image,ImageDraw,ImageFont
BG='#10243a';WHITE='#eff5ff';MUTED='#9fb2ca';BLUE='#70cfff';ORANGE='#ffbd68';GREEN='#8fe0b2';GRID='#31516c'
VERTICES={'A':(160,80),'B':(460,80),'C':(460,235),'D':(160,235)}
EDGES=[('A','B'),('B','C'),('C','D'),('D','A'),('A','C')]
WEIGHTS={('A','B'):1,('B','C'):2,('C','D'):3,('D','A'):8,('A','C'):5}
@functools.lru_cache(32)
def font(n):return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
def render(v,phase,progress,size=(1165,310)):
 w,h=size;im=Image.new('RGB',size,BG);d=ImageDraw.Draw(im);p=max(0,min(1,float(progress)));part=v.get('narrationPart',0);kind=v['kind']
 def text(x,y,s,n=25,color=WHITE,anchor='lt'):d.text((x,y),str(s),font=font(n),fill=color,anchor=anchor)
 def node(x,y,label,color=BLUE,r=27):d.ellipse((x-r,y-r,x+r,y+r),fill=BG,outline=color,width=3);text(x,y,label,25,color,'mm')
 def box(x,y,xx,yy,s,color=BLUE):d.rounded_rectangle((x,y,xx,yy),9,fill='#19384d',outline=color,width=2);text((x+xx)/2,(y+yy)/2,s,25,color,'mm')
 def arrow(a,b,color=BLUE,width=3):
  x,y=a;xx,yy=b;d.line((x,y,xx,yy),fill=color,width=width);theta=math.atan2(yy-y,xx-x);d.polygon([(xx,yy),(xx-13*math.cos(theta-.45),yy-13*math.sin(theta-.45)),(xx-13*math.cos(theta+.45),yy-13*math.sin(theta+.45))],fill=color)
 def pulse(a,b):
  x=a[0]+(b[0]-a[0])*p;y=a[1]+(b[1]-a[1])*p;d.ellipse((x-7,y-7,x+7,y+7),fill=ORANGE)
 def bar(label='按旁白逐步查看'):
  d.line((20,h-9,w-20,h-9),fill=GRID,width=2);x=20+(w-40)*p;d.ellipse((x-5,h-14,x+5,h-4),fill=ORANGE)
 if kind=='truth':
  op=v['op'];rows=[(1,1),(1,0),(0,1),(0,0)];heads={'basic':['p','q','非p','p且q','p或q'],'imp':['p','q','非p','p指向q','是否违反承诺'],'demorgan':['p','q','非(p且q)','非p或非q','是否相同']}[op];active=min(3,int(4*p))
  if op=='demorgan' and part==1:heads=['p','q','非(p或q)','非p且非q','是否相同']
  xs=[90,240,430,670,955]
  for x,label in zip(xs,heads):text(x,12,label,25,BLUE,'mt')
  for i,(a,b) in enumerate(rows):
   y=72+i*52
   if i==active:d.rounded_rectangle((25,y-9,w-25,y+34),7,fill='#263547')
   values=[a,b,1-a,a&b,a|b] if op=='basic' else [a,b,1-a,int(not a or b),'违反' if a and not b else '未违反'] if op=='imp' else [a,b,int(not(a and b)),int(not a or not b),'相同']
   if op=='demorgan' and part==1:values=[a,b,int(not(a or b)),int(not a and not b),'相同']
   for x,val in zip(xs,values):text(x,y,val,26,ORANGE if i==active else WHITE,'mt')
  bar('一行输入，对应一行结论')
 elif kind=='quantifier':
  grades=[72,85,48,91];active=min(3,int(p*4))
  for i,grade in enumerate(grades):
   x=110+i*245;box(x,70,x+160,180,f'{grade}分',ORANGE if i==active else GREEN if grade>=60 else BLUE);text(x+80,195,'及格' if grade>=60 else '不及格',25,GREEN if grade>=60 else ORANGE,'mt')
  text(30,250,'所有人及格：假（48分为反例）    至少有人及格：真',27);bar()
 elif kind=='venn':
  yy,xx=np.mgrid[:h,:w];a=((xx-400)/240)**2+((yy-150)/125)**2<=1;b=((xx-690)/240)**2+((yy-150)/125)**2<=1;inside=(xx>=80)&(xx<=1055)&(yy>=20)&(yy<=280)
  mode=v['mode']
  if mode=='operations':sel=(a|b) if part==0 and p<.5 else (a&b) if part==0 else a&~b;label='并集：1,2,3,4' if part==0 and p<.5 else '交集：3' if part==0 else 'A减B：1,2'
  elif mode=='complement':sel=inside&~a if part==0 else inside&~(a|b);label='A的补集：4,5' if part==0 else '并集的补集：5'
  else:sel=a|b;label='至少一项：11+7+8=26；都不喜欢：4'
  pix=np.asarray(im).copy();pix[sel]=[36,77,91];im=Image.fromarray(pix);d=ImageDraw.Draw(im);d.rectangle((80,20,1055,280),outline=GRID,width=2);d.ellipse((160,25,640,275),outline=BLUE,width=3);d.ellipse((450,25,930,275),outline=GREEN,width=3)
  text(185,34,'A',27,BLUE);text(880,34,'B',27,GREEN);text(98,32,'U',24,MUTED)
  for x,s in [(340,'11人' if mode=='count' else '1, 2'),(545,'7人' if mode=='count' else '3'),(760,'8人' if mode=='count' else '4'),(990,'4人' if mode=='count' else '5')]:text(x,150,s,29,WHITE,'mm')
  text(40,283,label,21,ORANGE);bar('阴影表示当前运算；对象位置保持')
 elif kind=='product':
  active=min(3,int(p*4))
  if part==0:
   text(30,15,'幂集的每个元素本身都是集合',26,ORANGE)
   for i,s in enumerate(['空集','{a}','{b}','{a,b}']):box(45+i*275,100,275+i*275,200,s,ORANGE if i==active else BLUE)
   text(40,245,'两个元素各有选或不选，共2²=4个子集',27)
  else:
   vals=list(itertools.product([1,2],['a','b']));text(30,15,'每个第一坐标，配上每个第二坐标',26,ORANGE)
   for i,(a,b) in enumerate(vals):box(45+i*275,100,275+i*275,200,f'({a}, {b})',ORANGE if i==active else BLUE)
   text(40,245,'2 × 2 = 4个有序对；(1,a)与(a,1)角色不同',27)
  bar()
 elif kind=='relation':
  mode=v['mode'];positions=[(220,160),(580,160),(940,160)];base=[(0,0),(0,1),(1,2)] if mode=='pairs' else [(0,0),(1,1),(2,2),(0,1),(1,0)] if mode=='properties' else [(0,1),(1,2)]
  active=min(len(base)-1,int(p*len(base)))
  for i,(a,b) in enumerate(base):
   x,y=positions[a];xx,yy=positions[b];col=ORANGE if i==active else BLUE
   if a==b:d.arc((x-30,y-95,x+30,y-25),10,350,fill=col,width=3);arrow((x+26,y-45),(x+16,y-24),col)
   else:offset=-12 if a<b else 15;arrow((x+(30 if a<b else -30),y+offset),(xx+(-30 if a<b else 30),yy+offset),col)
  if mode=='transitive':
   d.line((220,220,940,220),fill=GRID,width=2);arrow((220,220),(220+720*p,220),ORANGE);text(580,242,'待补捷径：(1,3)',25,ORANGE,'mt')
  for i,(x,y) in enumerate(positions):node(x,y,str(i+1))
  text(25,20,{'pairs':'R={(1,1),(1,2),(2,3)}','properties':'自环齐全；1与2双向：对称，但非反对称','transitive':'1→2与2→3，要求补上1→3'}[mode],25);bar()
 elif kind=='partition':
  groups=[[0,3],[1,4],[2,5]];active=min(2,int(3*p))
  for i,g in enumerate(groups):box(70+i*360,80,370+i*360,220,', '.join(map(str,g)),ORANGE if active==i else BLUE);text(220+i*360,240,'余数'+str(i),25,MUTED,'mt')
  text(30,15,'按除以3所得余数分组；不遗漏、不交叉',26);bar()
 elif kind=='hasse':
  pos={'1':(580,250),'2':(340,150),'3':(820,150),'6':(580,50)};es=[('1','2'),('1','3'),('2','6'),('3','6')];active=min(3,int(4*p))
  for i,(a,b) in enumerate(es):d.line((*pos[a],*pos[b]),fill=ORANGE if i==active else BLUE,width=4)
  for s,(x,y) in pos.items():node(x,y,s)
  text(20,35,'整除偏序',27,ORANGE);text(20,80,'2与3不可比',25);text(20,125,'最小元1；最大元6',25);bar('省略自环与传递边')
 elif kind=='mapping':
  full=v['mode']=='bijection';right=['a','b','c'] if full else ['a','b'];targets=[0,1,2] if full else [0,1,0];active=min(2,int(3*p))
  for i,j in enumerate(targets):arrow((250,60+i*90),(850,85+j*(75 if full else 120)),ORANGE if i==active else BLUE)
  for i in range(3):node(220,60+i*90,str(i+1))
  for j,s in enumerate(right):node(880,85+j*(75 if full else 120),s)
  text(70,8,'定义域A',23,MUTED);text(940,8,'陪域B',23,MUTED);text(410,265,'双射：不合并、不遗漏' if full else '函数且满射；不是单射',26,GREEN);bar()
 elif kind=='composition':
  for x,val in [(100,'3'),(580,'4'),(1060,'8')]:box(x-60,100,x+60,190,val)
  arrow((180,145),(490,145));arrow((660,145),(970,145));text(330,75,'f：加1',26);text(810,75,'g：乘2',26)
  if p<.5:pulse((180,145),(800,145))
  else:
   q=(p-.5)*2;x=660+310*q;d.ellipse((x-7,138,x+7,152),fill=ORANGE)
  text(35,235,'先f后g得到8；先g后f则得到7',28,ORANGE);bar('复合顺序按箭头检查')
 elif kind=='pigeon':
  for i in range(12):
   x=40+i*90;box(x,90,x+72,215,str(i+1)+'月');node(x+36,60,str(i+1),GREEN,r=19)
  x=80+min(1,p)*980;y=25+min(1,p)*118;node(x,y,'13',ORANGE,r=20)
  text(30,250,'13人 → 12个月：至少一月有2人',27);bar('橙色为第13名同学；不指定真实生日')
 elif kind=='choice':
  active=min(5,int(p*6));node(80,150,'选')
  for i in range(3):
   y=55+i*100;arrow((110,150),(420,y));node(450,y,str(i+1))
   for j in range(2):
    yy=y-25+j*50;idx=i*2+j;arrow((480,y),(900,yy),ORANGE if idx==active else BLUE);box(920,yy-20,1100,yy+20,str(i+1)+('a' if j==0 else 'b'),ORANGE if idx==active else BLUE)
  bar('第一步3种；每条分支再选2种')
 elif kind=='combination':
  perms=list(itertools.permutations('ABC'));active=min(5,int(p*6))
  for i,s in enumerate(perms):box(30+i*180,80,190+i*180,160,''.join(s),ORANGE if i==active else BLUE)
  text(35,215,'同一三人小组有6种内部顺序：60 ÷ 6 = 10',29,GREEN);bar('排列会区分这些顺序；组合不区分')
 elif kind=='sequence':
  vals=[3,5,7,9,11] if v['mode']=='linear' else [0,1,1,2,3,5,8];active=min(len(vals)-1,int(p*len(vals)))
  for i,val in enumerate(vals):
   x=85+i*150;box(x,100,x+115,180,str(val),ORANGE if i==active else BLUE);text(x+57,195,'第'+str(i+(1 if v['mode']=='linear' else 0))+'项',22,MUTED,'mt')
   if i:arrow((x-30,140),(x-4,140),GREEN)
  if v['mode']=='fib' and active>=2:
   text(60,35,f'{vals[active-2]} + {vals[active-1]} = {vals[active]}',31,ORANGE)
   x=85+(active-2)*150+57;xx=85+active*150+57;d.line((x,182,x,253,xx,253),fill=ORANGE,width=3);arrow((xx,253),(xx,184),ORANGE);text((x+xx)/2,266,'另一份输入来自前两项中的较早一项',21,MUTED,'mt')
  else:text(60,35,'从起点开始，依据规则生成下一项',27,ORANGE)
  bar('下标和初始条件一起保留')
 elif kind=='induction':
  n=8;active=min(n-1,int(p*n))
  for i in range(n):
   x=55+i*140;color=ORANGE if i<=active else GRID;box(x,85,x+90,220,'P('+str(i+1)+')',color)
   if i<n-1:arrow((x+94,150),(x+132,150),color)
  text(25,250,'起点成立 + 每步都能推进 → 覆盖全部目标下标',27);bar('示意有限几步；一般推进仍须证明')
 elif kind in ['graph','adjacency']:
  mode=v.get('mode','matrix');active=min(4,int(p*5));weighted=mode in ['weighted','mst'];route=[('A','B'),('B','C'),('C','D'),('D','A'),('A','C')]
  done=min(5,int(p*5)+1);visited=set(['A'])
  if mode=='bfs':visited={'A'} if p<.34 else {'A','B','C','D'}
  for i,(a,b) in enumerate(EDGES):
   if mode=='degrees' and i>=done:continue
   col=ORANGE if mode=='euler' and i<done or mode=='mst' and i<min(3,int(p*3)+1) or mode=='weighted' and i<3 else BLUE
   d.line((*VERTICES[a],*VERTICES[b]),fill=col,width=5 if col==ORANGE else 3)
   if weighted:
    x=(VERTICES[a][0]+VERTICES[b][0])/2;y=(VERTICES[a][1]+VERTICES[b][1])/2;d.rectangle((x-17,y-17,x+17,y+17),fill=BG);text(x,y,WEIGHTS[(a,b)],24,WHITE,'mm')
  for name,(x,y) in VERTICES.items():node(x,y,name,ORANGE if mode=='bfs' and name in visited else BLUE)
  if kind=='adjacency':
   names=list(VERTICES);grid=EDGES;start=650;step=78
   for i,a in enumerate(names):text(start-35,67+i*48,a,24,BLUE,'mm');text(start+i*step,20,a,24,BLUE,'mm')
   for i,a in enumerate(names):
    for j,b in enumerate(names):
     value=int((a,b) in EDGES or (b,a) in EDGES);text(start+j*step,67+i*48,value,26,ORANGE if (i*4+j)==min(15,int(p*16)) else WHITE,'mm')
  else:
   if mode=='degrees':
    deg={a:sum(a in e for e in EDGES[:done]) for a in VERTICES};text(650,65,'度数：'+', '.join(str(deg[a]) for a in VERTICES),28);text(650,115,f'度数和 {sum(deg.values())} = 2 × {done}',27,GREEN)
   elif mode=='euler':text(650,65,'A → B → C → D → A → C',26,ORANGE);text(650,120,'逐边走一次；起点A，终点C',26);text(650,175,'两个奇度点：A与C',26,GREEN)
   elif mode=='bfs':text(650,65,'从A出发：先找到A',27);text(650,120,'邻居B、C、D均可直接到达',26);text(650,175,'所有顶点可达：连通',26,GREEN)
   elif mode=='weighted':text(650,65,'直接 A—D：8',27);text(650,120,'A—B—C—D：1+2+3=6',27,ORANGE)
   elif mode=='mst':text(650,65,'依次选AB、BC、CD',27,ORANGE);text(650,120,'总权重 1+2+3 = 6',27,GREEN);text(650,175,'4顶点，3条边，覆盖全部顶点',25)
  # The moving marker traces only real graph edges; endpoint state persists.
  a,b=EDGES[active];pulse(VERTICES[a],VERTICES[b]);bar('有限简单无向图；交叉处不另设顶点')
 elif kind=='tree':
  pos={'A':(580,45),'B':(340,135),'C':(820,135),'D':(220,245),'E':(460,245)};es=[('A','B'),('A','C'),('B','D'),('B','E')];order=['A','B','D','E','C'];count=min(5,int(p*5)+1)
  for i,(a,b) in enumerate(es):
   if v['mode']=='basic' and i>=min(4,int(p*4)+1):continue
   d.line((*pos[a],*pos[b]),fill=BLUE,width=3)
  for a,(x,y) in pos.items():node(x,y,a,ORANGE if v['mode']=='preorder' and a in order[:count] else BLUE)
  text(10,15,'前序：A B D E C' if v['mode']=='preorder' else '目标：5个顶点，4条边，无回路',25);bar('孩子按左到右访问')
 elif kind in ['code_tree','huffman']:
  pos={'根':(580,40),'A':(340,145),'N':(820,145),'B':(710,255),'C':(930,255)}
  for a,b,label in [('根','A','0'),('根','N','1'),('N','B','0'),('N','C','1')]:
   d.line((*pos[a],*pos[b]),fill=BLUE,width=3);x=(pos[a][0]+pos[b][0])/2;y=(pos[a][1]+pos[b][1])/2;text(x,y,label,24,ORANGE,'mm')
  for s,(x,y) in pos.items():node(x,y,{'根':'8','N':'3','A':'A:5','B':'B:2','C':'C:1'}[s] if kind=='huffman' else s,r=30 if kind=='huffman' else 25)
  text(15,20,'B:2 + C:1 → 3，再与A:5合并' if kind=='huffman' else 'A:0；B:10；C:11',25,ORANGE)
  text(15,65,'带权路径长度：5×1+2×2+1×2=11' if kind=='huffman' else '01011 → A B C',23)
  pulse(pos['根'],pos['N'] if p<.5 else pos['A']);bar('字符放在叶子；内部节点不表示字符')
 elif kind=='cayley':
  start=300;step=100;active=min(3,int(p*4))
  for i in range(4):text(start+i*step,20,i,27,BLUE,'mt');text(start-70,76+i*50,i,27,BLUE,'mm')
  for i in range(4):
   for j in range(4):
    if i==active:d.rectangle((start+j*step-36,60+i*50,start+j*step+36,94+i*50),fill='#263547')
    text(start+j*step,76+i*50,(i+j)%4,27,ORANGE if i==active else WHITE,'mm')
  text(770,70,'先相加，再除以4取余',26);text(770,130,'例：3 * 2 = 1',26,GREEN);bar('每个结果仍在0、1、2、3中')
 else:raise ValueError(kind)
 return im
