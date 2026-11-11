"""Narration-driven digital circuit illustrations. Unscaled models are explicitly labeled.

Actual VCD views are delegated to rtl_diagrams; all other pictures are teaching models.
"""
import functools,math
from PIL import Image,ImageDraw,ImageFont
import rtl_diagrams
BG='#10243a';WHITE='#eff5ff';MUTED='#9fb2ca';BLUE='#70cfff';ORANGE='#ffbd68';GREEN='#8fe0b2';GRID='#31516c';RED='#ff939c'
@functools.lru_cache(40)
def font(n):return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)

def render(v,phase,p,size=(1165,310)):
    if v['kind']=='wave':return rtl_diagrams.render(v,phase,p,size)
    im=Image.new('RGB',size,BG);d=ImageDraw.Draw(im);w,h=size;p=max(0,min(1,p));part=v.get('narrationPart',0);kind=v['kind'];mode=v.get('mode');step=lambda n:min(n-1,int(p*n))
    def text(x,y,s,n=24,c=WHITE,a='lt'):d.text((x,y),str(s),font=font(n),fill=c,anchor=a)
    def line(points,c=BLUE,width=3):d.line(points,fill=c,width=width)
    def arrow(x,y,xx,yy,c=BLUE):
        line((x,y,xx,yy),c);ang=math.atan2(yy-y,xx-x);d.polygon([(xx,yy),(xx-12*math.cos(ang-.5),yy-12*math.sin(ang-.5)),(xx-12*math.cos(ang+.5),yy-12*math.sin(ang+.5))],fill=c)
    def box(x,y,ww,hh,s,c=BLUE,n=24):
        d.rounded_rectangle((x,y,x+ww,y+hh),9,fill='#19384d',outline=c,width=2);text(x+ww/2,y+hh/2,s,n,c,'mm')
    def title(s):text(12,6,s,23,ORANGE)
    def footer(s):text(w/2,288,s,21,MUTED,'mt')
    def table(headers,rows,at=0,x=20,y=48,cw=None,rh=36,fs=23):
        cw=cw or [110]*len(headers)
        for j,hd in enumerate(headers):text(x+sum(cw[:j])+cw[j]/2,y,hd,fs,BLUE,'mt')
        yy=y+rh
        for i,row in enumerate(rows):
            if i==at:d.rounded_rectangle((x-4,yy-1,x+sum(cw)+4,yy+rh-2),5,fill='#30404e')
            for j,val in enumerate(row):text(x+sum(cw[:j])+cw[j]/2,yy+2,val,fs,ORANGE if i==at else WHITE,'mt')
            yy+=rh
    def bits(value,x,y,count=4,active=-1):
        for j in range(count):
            b=(value>>(count-j-1))&1;box(x+j*90,y,75,60,b,ORANGE if j==active else GREEN if b else GRID,33)
    def wave(label,events,y,color=GREEN,left=175,right=1110,amp=14,cursor=True):
        text(10,y,label,23,WHITE,'lm');points=[]
        for i,(at,val) in enumerate(events):
            xx=left+(right-left)*at;yy=y+amp*(1-2*val)
            if points:points.append((xx,points[-1][1]))
            points.append((xx,yy))
        points.append((right,points[-1][1]));line(points,color,3)
        if cursor:line((left+(right-left)*p,y-24,left+(right-left)*p,y+24),ORANGE,2)
    if kind=='levels':
        title('正逻辑示意：允许电压范围映射为0与1；未指定具体器件门限')
        left,right=160,1110;top,bottom=70,230
        d.rectangle((left,top,right,top+43),fill='#18443e');d.rectangle((left,bottom-43,right,bottom),fill='#193a52')
        text(20,83,'高电平 → 1',23,GREEN);text(20,205,'低电平 → 0',23,BLUE)
        line((left,top,left,bottom,right,bottom),GRID,2)
        pts=[]
        for i in range(301):
            t=i/300;val=1 if .2<=t<.48 or .67<=t<.87 else 0
            # Finite slopes illustrate continuous voltage; plateau values encode the bit.
            for edge,sgn in [(.2,1),(.48,-1),(.67,1),(.87,-1)]:
                if abs(t-edge)<.018:val=(t-(edge-.018))/.036 if sgn==1 else 1-(t-(edge-.018))/.036
            pts.append((left+(right-left)*t,bottom-18-val*(bottom-top-36)))
        line(pts,GREEN,4);xx=left+(right-left)*p;line((xx,top-5,xx,bottom+10),ORANGE,3);footer('时间 →　真实电压连续变化；逻辑状态按器件规定判断')
    elif kind=='bits':
        title('1101的位权展开 · 无符号解释');n=v['value'];active=3-step(4)
        for j in range(4):
            bit=(n>>(3-j))&1;x=170+j*230;box(x,63,175,65,bit,ORANGE if j==active else BLUE,38);text(x+88,145,f'位权 {2**(3-j)}',26,MUTED,'mt');text(x+88,195,f'{bit} × {2**(3-j)}',30,GREEN,'mt')
        footer('8 + 4 + 0 + 1 = 13　　位号从右侧最低位开始')
    elif kind=='binary_add':
        if part==0:
            title('十六进制按每4个二进制位分组；A=10，5=5')
            for i,b in enumerate('10100101'):box(100+i*125,78,105,65,b,ORANGE if i<4 else GREEN,35)
            text(340,190,'1010 → A',36,ORANGE,'mt');text(840,190,'0101 → 5',36,GREEN,'mt');footer('1010 0101（二进制）= A5（十六进制）');return im
        title('位宽与进位 · 4位无符号示例');text(60,75,'1111 + 0001',40);arrow(400,108,560,108)
        value='10000';active=4-step(5)
        for i,b in enumerate(value):box(600+i*98,70,82,75,b,ORANGE if i==active else GREEN,37)
        text(641,179,'进位',26,ORANGE,'mt');text(890,179,'保留的低4位：0000',27,GREEN,'mt');footer('完整结果16需要5位；仅保留4位会丢弃最高进位')
    elif kind=='gray':
        if part==0:
            title('8421 BCD码：把每一位十进制数字分别编码；不是直接把25转为二进制')
            for i,b in enumerate('00100101'):box(100+i*125,78,105,65,b,ORANGE if i<4 else GREEN,35)
            text(340,190,'十进制数字2 → 0010',31,ORANGE,'mt');text(840,190,'十进制数字5 → 0101',31,GREEN,'mt');footer('25的BCD码：0010 0101');return im
        title('两位格雷码：相邻编码只有一个二进制位变化');codes=['00','01','11','10'];at=step(4)
        for i,s in enumerate(codes):
            x=45+i*287;box(x,100,215,85,s,ORANGE if at==i else BLUE,40)
            if i<3:arrow(x+220,142,x+280,142,GREEN)
        footer('00 → 01 → 11 → 10；末尾10与开头00也只差1位')
    elif kind=='gates':
        if mode=='derived' and part==0:
            title('与非门示意：先做与，再在输出取反；输出的小圆圈表示取反')
            text(30,93,'A=1',32);text(30,174,'B=1',32);line((125,116,300,116));line((125,198,300,198));box(300,80,260,150,'与门',BLUE,37)
            d.ellipse((560,142,590,172),outline=ORANGE,width=4);arrow(590,157,850,157,GREEN);text(1010,157,'Y=0',43,ORANGE,'mm');text(690,210,'输出取反',27,ORANGE,'mt');footer('先得到AB=1，再取反得0；控制端圆圈还需结合位置解释');return im
        names=['与','或','非'] if mode=='basic' else ['与非','或非','异或','同或'];pair=step(4);a,b=pair//2,pair%2
        title(f'真值表逐行核对　当前输入 A={a}，B={b}');rows=[]
        for aa in range(2):
            for bb in range(2):rows.append([aa,bb,*([aa&bb,aa|bb,1-aa] if mode=='basic' else [1-(aa&bb),1-(aa|bb),aa^bb,1-(aa^bb)])])
        table(['A','B',*names],rows,pair,x=32,y=52,cw=[75,75]+[125]*len(names),rh=40)
        x=830;text(x,90,'本行输出',26,BLUE)
        for j,n in enumerate(names):text(x,132+j*35,f'{n}：{rows[pair][j+2]}',25,GREEN)
        footer('逻辑加号表示或；非门只使用A；不把逻辑或当算术加法')
    elif kind=='circuit':
        a,b,c=[int(x) for x in f'{step(8):03b}'];x=a&b;f=x|c;title('沿电路逐级求值：X=AB，再求F=X+C')
        text(25,75,f'A={a}',30);text(25,140,f'B={b}',30);text(25,222,f'C={c}',30)
        line((110,97,270,97));line((110,162,270,162));box(270,76,190,105,'与门',BLUE,31);arrow(460,128,750,128,GREEN);text(580,78,f'X={x}',30,GREEN,'mt')
        line((110,242,650,242,650,185,750,185));box(750,105,180,105,'或门',BLUE,31);arrow(930,158,1055,158,GREEN);text(1120,158,f'F={f}',31,ORANGE,'rm')
    elif kind=='thresholds':
        title('输入门限区间与保证输出 · 位置只作示意，不代替数据手册');x0,x1=170,1070
        for y,label in [(100,'输入'),(208,'输出')]:text(25,y,label,27,BLUE,'lm');arrow(x0,y,x1,y,GRID)
        d.rectangle((x0,77,x0+220,123),fill='#21516a');d.rectangle((x0+580,77,x1,123),fill='#215848');d.rectangle((x0+220,77,x0+580,123),fill='#4c3f3d')
        for x,s in [(x0+220,'VIL,max'),(x0+580,'VIH,min')]:line((x,65,x,135),WHITE,2);text(x,143,s,23,WHITE,'mt')
        text(x0+400,99,'不保证0或1',23,ORANGE,'mm');text(x0+108,99,'逻辑0',24,WHITE,'mm');text(x0+720,99,'逻辑1',24,WHITE,'mm')
        low=x0+140;high=x0+680
        for x,s in [(low,'VOL,max'),(high,'VOH,min')]:d.ellipse((x-6,202,x+6,214),fill=GREEN);text(x,234,s,23,GREEN,'mt')
        xx=x0+(x1-x0)*p;d.ellipse((xx-6,46,xx+6,58),fill=ORANGE);footer('VOL,max ≤ VIL,max　且　VOH,min ≥ VIH,min；还要检查电流等条件')
    elif kind=='delay':
        title('传播延迟示意 · 不按真实时间比例绘制')
        wave('输入',[(0,0),(.27,1),(.64,0)],95,BLUE);wave('输出',[(0,0),(.35,1),(.72,0)],200)
        arrow(175+935*.27,145,175+935*.35,145,ORANGE);text(650,250,'Z：高阻态，既不是逻辑0，也不是逻辑1',25,ORANGE,'mt')
    elif kind=='demorgan':
        title('德摩根定律：两侧表达式逐行相等');at=step(4);rows=[]
        for a in range(2):
            for b in range(2):rows.append([a,b,1-(a&b),(1-a)|(1-b)] if part==0 else [a,b,1-(a|b),(1-a)&(1-b)])
        table(['A','B','左侧结果','右侧结果'],rows,at,x=60,y=51,cw=[100,100,200,200],rh=40)
        box(800,105,290,75,'四行全部一致',GREEN,29);footer('与、或互换；每个输入取反；原来的整体取反被展开')
    elif kind=='kmap':
        wrap=mode=='wrap';ones={0,2,4,6} if wrap else {1,3,6,7};order=[[0,1,3,2],[4,5,7,6]]
        title('三变量卡诺图 · BC按00、01、11、10排列，首尾相邻');x,y=185,89;cw,rh=155,68
        text(105,62,'A / BC',24,BLUE)
        for j,col in enumerate(['00','01','11','10']):text(x+(j+.5)*cw,55,col,25,BLUE,'mt')
        filled=min(4,int(p*4)+1) if part==0 and not wrap else 4;visible=set(sorted(ones)[:filled])
        for i in range(2):
            text(125,y+(i+.5)*rh,i,27,BLUE,'mm')
            for j,m in enumerate(order[i]):
                rect=(x+j*cw,y+i*rh,x+(j+1)*cw,y+(i+1)*rh);d.rectangle(rect,outline=GRID,width=2);text(rect[0]+12,rect[1]+8,f'm{m}',18,MUTED);text((rect[0]+rect[2])/2,rect[1]+38,1 if m in visible else 0,30,GREEN if m in visible else MUTED,'mm')
        if wrap:
            # Two visible edge strips form one four-cell group on the wrapped map.
            for j in [0,3]:d.rounded_rectangle((x+j*cw+5,y+5,x+(j+1)*cw-5,y+2*rh-5),12,outline=ORANGE,width=4)
            text(900,115,'首尾四格合为一组',25,ORANGE,'mt');text(900,165,"保留 C'",31,GREEN,'mt')
        elif part==1:
            for i,jj,c in [(0,(1,2),ORANGE),(1,(2,3),GREEN)]:
                if p>i*.5:d.rounded_rectangle((x+jj[0]*cw+5,y+i*rh+5,x+(jj[1]+1)*cw-5,y+(i+1)*rh-5),12,outline=c,width=4)
            if p>0:text(960,105,"上组 A'C",28,ORANGE,'mt')
            if p>.5:text(960,160,'下组 AB',28,GREEN,'mt')
        line((x,y+2*rh+21,x+4*cw*p,y+2*rh+21),ORANGE,4);footer('每组为2的幂个方格；消去组内变化的变量，保留不变的变量')
    elif kind in ['truth','majority']:
        majority=kind=='majority';at=step(8);rows=[]
        for n in range(8):
            a,b,c=map(int,f'{n:03b}');rows.append([a,b,c,int(a+b+c>=2) if majority else a&b,(a&b)|(c)] if not majority else [a,b,c,int(a+b+c>=2)])
        table(['A','B','C','F'] if majority else ['A','B','C','X=AB','F=X+C'],rows,at,x=24,y=43,cw=[90,90,90,140]+([] if majority else [160]),rh=27,fs=22)
        a,b,c=map(int,f'{at:03b}');title('多数表决器：至少两票通过' if majority else '三输入真值表：所有8种组合都要覆盖')
        for j,(name,value) in enumerate(zip('ABC',[a,b,c])):box(720+j*140,72,100,64,f'{name}={value}',GREEN if value else GRID,26)
        text(900,182,f'F = {int(a+b+c>=2) if majority else (a&b)|c}',42,ORANGE,'mm');footer('当前行高亮对应当前输入；输出1表示通过' if majority else 'C为1时F必为1；C为0时F由AB决定')
    elif kind=='adder':
        if mode=='half' or part==0:
            full=mode=='full';count=8 if full else 4;at=step(count);rows=[]
            for n in range(count):
                vals=list(map(int,f'{n:0{3 if full else 2}b}'));total=sum(vals);rows.append([*vals,total%2,total//2])
            title('全加器：三个输入之和 = 2×进位 + 和位' if full else '半加器：完整结果拆成进位与和位')
            table(['A','B',*(['Cin'] if full else []),'S','Cout'],rows,at,x=35,y=44,cw=[95]*len(rows[0]),rh=27 if full else 42,fs=23)
            total=sum(rows[at][:-2]);text(840,92,f'完整结果 {total:02b}',36,ORANGE,'mt');text(840,164,f'C={total//2}　S={total%2}',31,GREEN,'mt');footer('S只表示最低位；进位是独立输出')
        else:
            title('串行进位示意：1111 + 0001 = 1 0000；不按实际延迟比例')
            at=step(4)
            for i in range(4):
                x=55+i*278;active=i<=at;box(x,103,205,78,f'第{i}位全加器',ORANGE if i==at else BLUE,24);text(x+102,62,f'A{i}=1　B{i}={1 if i==0 else 0}',23,MUTED,'mt');text(x+102,201,'S=0' if active else '等待进位',27,GREEN if active else MUTED,'mt')
                if i<3:arrow(x+209,141,x+274,141,GREEN if active else GRID)
            footer('从最低位向最高位传进位；最高位之外还产生Cout=1')
    elif kind=='hazard':
        title('B=C=1，A由0变1 · 仅演示一种路径延迟导致的静态1冒险')
        wave('A',[(0,0),(.4,1)],75,BLUE);wave('理想稳态F',[(0,1)],133);wave('延迟示意F',[(0,1),(.43,0),(.55,1)],191,RED)
        wave('加入BC后',[(0,1)],249,GREEN if part else GRID);footer('单输入变化模型；示意脉冲宽度不代表实际器件时间')
    elif kind=='mux':
        s=step(2);title(f'二选一：D0=0，D1=1；当前选择S={s}')
        for j in range(2):
            yy=90+j*115;box(25,yy-30,165,62,f'D{j}={j}',GREEN if j==s else GRID,31);arrow(200,yy,460,yy,ORANGE if j==s else GRID)
        xx=200+260*p;yy=90+s*115;d.ellipse((xx-7,yy-7,xx+7,yy+7),fill=GREEN)
        d.polygon([(460,47),(680,98),(680,209),(460,257)],outline=BLUE,width=3);text(565,151,'MUX',34,WHITE,'mm');arrow(680,151,985,151,GREEN);box(990,113,145,76,f'Y={s}',ORANGE,34);text(560,265,f'S={s}',29,ORANGE,'mt')
    elif kind=='decoder':
        n=2 if part==0 else step(4);title('2到4译码器 · 本页输出高有效，无额外使能限制');box(20,112,200,77,f'AB={n:02b}',BLUE,33);arrow(225,150,415,150);box(420,64,240,178,'译码器',BLUE,36)
        for i in range(4):
            yy=65+i*61;arrow(665,yy,920,yy,GREEN if i==n else GRID);text(940,yy,f'Y{i}={int(i==n)}',28,ORANGE if i==n else MUTED,'lm')
    elif kind=='encoder':
        states=[(0,1,0,1),(0,0,0,0),(0,0,0,1),(0,1,0,1)] if part else [(0,0,0,0),(0,0,0,1),(0,1,0,1),(1,1,0,1)];vals=states[step(4)];valid=any(vals);code=next((3-i for i,b in enumerate(vals) if b),0)
        title('优先级D3 > D2 > D1 > D0；V单独报告是否有有效输入')
        for i,b in enumerate(vals):text(35,65+i*51,f'D{3-i}={b}',28,GREEN if b else MUTED);arrow(155,85+i*51,360,85+i*51,GREEN if b else GRID)
        box(365,60,260,215,'优先编码器',BLUE,32);arrow(630,159,825,159);text(855,101,f'编码={code:02b}',35,ORANGE);text(855,183,f'V={int(valid)}',35,GREEN);footer('全0输入与仅D0有效：编号都可为00，但V分别是0与1')
    elif kind=='sevenseg':
        title('数字2的段位图 · 只约定亮灭，不代表引脚号或实际驱动极性');segments={'a':(260,65,420,65),'b':(435,80,435,153),'c':(435,177,435,250),'d':(260,264,420,264),'e':(245,177,245,250),'f':(245,80,245,153),'g':(260,164,420,164)};on=['a','b','g','e','d'];shown=set(on[:min(5,int(p*5)+1)]) if part==0 else set(on)
        for name,(x,y,xx,yy) in segments.items():
            line((x,y,xx,yy),GREEN if name in shown else GRID,13);text((x+xx)/2+(30 if x==xx and x>300 else -35 if x==xx else 0),(y+yy)/2+(-20 if x!=xx else 0),name,24,ORANGE,'mm')
        text(670,85,'点亮：a、b、d、e、g',30,GREEN);text(670,152,'熄灭：c、f',30,MUTED);text(670,219,'位序与有效电平需另行约定',25,ORANGE)
    elif kind=='sr':
        title('交叉耦合或非门SR锁存器 · S、R高电平有效');rows=[['0','0','保持旧Q'],['1','0','置1'],['0','1','置0'],['1','1','禁止组合']];at=step(4)
        table(['S','R','状态'],rows,at,x=32,y=51,cw=[90,90,270],rh=43)
        text(770,101,rows[at][2],39,RED if at==3 else GREEN,'mt');text(770,176,'11时Q与反相输出不再互补' if at==3 else '下一状态连同当前状态分析',24,RED if at==3 else MUTED,'mt');footer('禁止组合解除后的结果不能按正常保持、置位、清零规则保证')
    elif kind=='jk_t':
        title('从已知Q=0出发 · T=0保持，T=1翻转；每个箭头表示一个有效边沿');commands=[0,1,1,0,1];states=[0]
        for t in commands:states.append(states[-1]^t)
        at=step(6)
        for i,q in enumerate(states):
            x=20+i*193;box(x,121,135,74,f'Q={q}',ORANGE if i==at else BLUE,31)
            if i<5:arrow(x+140,158,x+188,158,GREEN);text(x+164,87,f'T={commands[i]}',23,GREEN,'mm')
        footer('JK：00保持、01清零、10置1、11翻转；同一边沿只更新一次')
    elif kind=='setup_hold':
        title('建立与保持窗口 · 示意宽度，无具体器件时间值');edge=640;left=360;right=850
        if part==1:
            d.rectangle((left,52,edge,237),fill='#284549');d.rectangle((edge,52,right,237),fill='#3d3c43')
        wave('时钟',[(0,0),((edge-175)/935,1),(.85,0)],109,BLUE,cursor=False)
        wave('数据D',[(0,0),(.12,1),(.85,0)],203,GREEN,cursor=False);line((edge,44,edge,251),ORANGE,3)
        text(edge,258,'采样边沿',25,ORANGE,'mt');text((left+edge)/2,56,'建立：边沿前',24,BLUE,'mt');text((right+edge)/2,56,'保持：边沿后',24,RED,'mt');xx=175+935*p;d.ellipse((xx-7,35,xx+7,49),fill=ORANGE)
    elif kind=='state_block':
        title('同步时序电路 · 一次有效边沿，把旧状态更新成下一状态')
        box(255,90,290,110,'组合逻辑',BLUE,35);box(755,90,230,110,'状态寄存器',BLUE,31);arrow(32,118,250,118);text(75,69,'输入X',26,BLUE);arrow(550,143,750,143);text(650,85,'下一状态D',25,GREEN,'mt');arrow(985,143,1125,143);text(1080,85,'当前Q',25,ORANGE,'mt')
        line((1060,150,1060,248,160,248,160,176),GREEN);arrow(160,176,250,176,GREEN);text(595,253,'反馈：以当前状态参与本轮计算',24,GREEN,'mt');arrow(870,51,870,84,ORANGE);text(870,18,'时钟',24,ORANGE,'mt');xx=1060-900*p;d.ellipse((xx-6,242,xx+6,254),fill=ORANGE)
    elif kind=='fsm':
        title('模3状态机 · 理想同步功能模型，11在下一有效边沿回到00')
        if part==0:
            table(['当前状态','下一状态'],[['00','01'],['01','10'],['10','00'],['11','00']],step(4),x=100,y=49,cw=[250,250],rh=43)
            text(900,108,'00 → 01 → 10 → 00',30,GREEN,'mt');text(900,181,'11安排回到00',26,ORANGE,'mt');return im
        states=['00','01','10'];at=[0,1,2,0][step(4)]
        for i,s in enumerate(states):
            x=165+i*395;d.ellipse((x-76,68,x+76,220),fill='#294b56' if i==at else BG,outline=ORANGE if i==at else BLUE,width=4);text(x,144,s,41,WHITE,'mm')
            if i<2:arrow(x+84,145,x+307,145,GREEN)
        line((955,225,955,264,165,264,165,229),BLUE);text(560,268,'下一拍返回00',22,BLUE,'mt');box(37,25,180,40,'非法态11 → 00',MUTED,20)
    elif kind=='state_table':
        at=1 if part==1 else step(4);rows=[['00','01','0','1'],['01','10','1','0'],['10','00','0','0'],['11','00','0','0']];title('先固定旧Q，再同时计算两位D；边沿后统一写入')
        table(['旧Q1Q0','新Q1Q0','D1','D0'],rows,at,x=30,y=50,cw=[180,180,90,90],rh=43)
        text(865,100,f'旧 {rows[at][0]} → 新 {rows[at][1]}',36,ORANGE,'mt');text(865,170,'D1、D0使用同一组旧状态',25,GREEN,'mt')
        if part==1:arrow(690,231,1090,231,GREEN);xx=690+400*p;d.ellipse((xx-7,224,xx+7,238),fill=ORANGE);text(890,248,'组合计算 → 等待边沿统一写入',22,BLUE,'mt')
        footer('11 → 00是主动设计的非法状态恢复行为')
    elif kind=='moore_mealy':
        title('状态固定为“运行” · 仅改变异常输入，比较两种输出关系')
        wave('异常输入X',[(0,0),(.27,1),(.7,0)],85,BLUE);wave('Moore忙碌',[(0,1)],162,GREEN);wave('Mealy报警',[(0,0),(.27,1),(.7,0)],238,ORANGE);footer('忙碌=运行状态；报警=运行状态且异常输入；理想功能关系')
    elif kind=='timing_budget':
        title('简化建立时间预算 · 忽略时钟偏斜和额外裕量');dur=[2,5,1];labels=['时钟到Q：2ns','组合逻辑：5ns','建立：1ns'];x=55
        for i,n in enumerate(dur):ww=n*125;d.rectangle((x,105,x+ww,190),fill=['#235a65','#305364','#68503b'][i],outline=BLUE,width=2);text(x+ww/2,147,labels[i],23,WHITE,'mm');x+=ww
        xx=55+1000*p;line((xx,78,xx,214),ORANGE,3);text(550,233,'2 + 5 + 1 = 8ns　→　理想上限125MHz',29,GREEN,'mt');footer('还要单独检查保持时间；真实设计需加入时钟偏斜与裕量')
    elif kind=='count':
        decade=mode=='decade';seq=[7,8,9,0,1] if decade else [0,1,2,3,0];at=step(len(seq));n=seq[at];title('十进制同步计数：到9后下一拍回0' if decade else '两位同步二进制加1计数：四个状态循环')
        bits(n,60,97,4 if decade else 2);text(590,109,f'当前十进制：{n}',37,ORANGE)
        for i,s in enumerate(seq):box(500+i*125,206,105,47,f'{s:04b}' if decade else f'{s:02b}',ORANGE if i==at else GRID,24)
        footer('理想同步功能模型 · 所有寄存器使用同一有效时钟边沿')
    elif kind=='ripple':
        title('脉动传播示意：01 → 暂态00 → 稳态10；不按实际器件时间比例')
        wave('Q0低位',[(0,1),(.35,0)],96,BLUE);wave('Q1高位',[(0,0),(.57,1)],177,GREEN)
        states=['01','00','10'];n=0 if p<.35 else 1 if p<.57 else 2;box(730,232,360,47,f'当前位型：{states[n]}',ORANGE,26);text(250,245,'多位输出不是同时稳定',27,RED)
    elif kind=='shift':
        title('四位移位寄存器 · 初态0000；每个有效边沿只移一位');seq=[0,1,2,5];inputs=[1,0,1];at=step(4);bits(seq[at],350,104)
        text(965,132,f'下一拍D={inputs[at]}' if at<3 else '已输入1、0、1',27,ORANGE,'mm');arrow(820,136,710,136)
        for j in range(3):arrow(350+(j+1)*90-3,136,350+j*90+76,136,GREEN)
        text(165,130,f'第{at}拍后',30,BLUE,'mm');footer('0000 → 0001 → 0010 → 0101；新状态=旧Q2Q1Q0与本拍输入D')
    elif kind=='ring':
        title('四位环形计数 · 初始化为0001，单个1循环移动');seq=[1,2,4,8,1];at=step(5);bits(seq[at],370,98)
        line((370,173,370,226,705,226),GREEN);arrow(705,226,705,173,GREEN);text(540,240,'最高位回接最低位',26,GREEN,'mt');text(85,110,'初态0001',27,BLUE);text(865,110,'0000会自锁',27,RED);footer('该4状态环形计数需4位；不要与最少二进制编码位数混淆')
    elif kind in ['memory','rom','ram']:
        rom=kind=='rom';ram=kind=='ram';at=step(8) if rom else step(4);addresses=list(range(8)) if rom else [0,1,2,1023];vals=[int(bin(n).count('1')>=2) for n in range(8)] if rom else [12,37,81,9]
        if ram and p>=.5:vals[2]=165
        title('ROM示例：ABC作地址，查表实现三人多数表决' if rom else 'RAM示意：只改写所选地址，其他单元保持' if ram else '1024×8存储器 · 1024个地址，每个地址8位')
        if ram:at=2
        rows=[[f'{a:03b}' if rom else str(a),str(val) if rom else f'{val:08b}'] for a,val in zip(addresses,vals)]
        table(['地址ABC' if rom else '地址','读出F' if rom else '数据'],rows,at,x=50,y=45,cw=[180,250],rh=27 if rom else 43,fs=23)
        text(790,95,f'地址 {rows[at][0]}',31,BLUE,'mt');text(790,150,f'数据 {rows[at][1]}',33,ORANGE,'mt')
        if ram:text(790,218,'写入地址2：01010001 → 10100101',23,GREEN,'mt')
        footer('8行查找表与组合逻辑真值表一一对应' if rom else '仅画部分地址；中间地址省略，容量仍为1024×8')
        line((500,258,500+610*p,258),ORANGE,3)
    elif kind=='expansion':
        bit=part==0;title('位扩展：两片1024×4 → 1024×8' if bit else '字扩展：两片1024×8 → 2048×8')
        for i in range(2):
            x=320+i*465;box(x,93,320,105,'1024×4' if bit else f'1024×8 区{i}',ORANGE if not bit and step(2)==i else BLUE,32)
            text(x+160,224,('低4位' if i==0 else '高4位') if bit else ('地址0～1023' if i==0 else '地址1024～2047'),26,GREEN,'mt')
        text(65,110,'低10位地址',25,BLUE);line((225,133,290,133,290,70,1060,70,1060,88));arrow(480,70,480,88)
        footer('同地址同时选中，两片分别连接数据高、低半部' if bit else '第11位地址选择芯片区；共用数据总线要避免输出争用')
        xx=320+785*p;d.ellipse((xx-7,54,xx+7,68),fill=ORANGE)
    elif kind=='schmitt':
        title('非反相施密特功能示意 · 阈值位置仅供教学，不代表器件参数');x0,x1=180,1110;top,bot=62,228;lo,hi=bot-55,top+48
        for yy,s in [(hi,'上阈值'),(lo,'下阈值')]:line((x0,yy,x1,yy),GRID,2);text(25,yy,s,22,BLUE,'lm')
        pts=[(x0,bot),(x0+(x1-x0)*.5,top),(x1,bot)];line(pts,BLUE,4);up=(bot-hi)/(bot-top)*.5;down=.5+(lo-top)/(bot-top)*.5
        wave('输出',[(0,0),(up,1),(down,0)],259,GREEN,left=x0,right=x1,amp=10);xx=x0+(x1-x0)*p;line((xx,44,xx,278),ORANGE,2)
        text(670,37,'上升跨上阈值才置1；下降跨下阈值才置0',22,ORANGE,'mt')
    elif kind=='pulse':
        title('单稳态与振荡 · 理想功能示意，不包含具体器件时间公式')
        wave('一次触发',[(0,0),(.15,1),(.19,0)],77,BLUE);wave('单稳输出',[(0,0),(.15,1),(.49,0)],150,GREEN)
        events=[(0,0)]+[(i/10,int(i%2==1)) for i in range(1,10)];wave('连续振荡',events,232,ORANGE);footer('单次脉冲与连续周期波形分开；能否重复触发要看具体型号')
    elif kind=='dac':
        title('理想3位单极性DAC · Vref=8V，Vout=8D/8；步长1V');n=5 if part==0 else 7 if p==0 else step(8);x0,x1=125,1100;y0,y1=250,75;cw=(x1-x0)/8
        line((x0,y1,x0,y0,x1+25,y0),GRID,2);points=[]
        for k in range(8):
            xx=x0+cw*k;yy=y0-(y0-y1)*k/7;points.extend([(xx,yy),(xx+cw,yy)]);text(xx+cw/2,y0+10,str(k),21,MUTED,'mt')
            if k==n:d.ellipse((xx+cw/2-8,yy-8,xx+cw/2+8,yy+8),fill=ORANGE)
        line(points,GREEN,3);text(20,65,'7V',22,BLUE);text(20,230,'0V',22,BLUE);text(565,49,f'数字码 {n:03b} → {n}V',30,ORANGE,'mt');footer('横轴为依次保持的输入码，未按真实时间比例；最大码输出7V')
    elif kind=='adc':
        title('向下分箱教学模型 · 输入0≤Vin<8V；每1V对应一个3位码');n=5 if part==1 and p==0 else step(8);x0=70;cw=131
        for k in range(8):
            xx=x0+k*cw;d.rectangle((xx,100,xx+cw,178),fill='#395646' if k==n else '#19384d',outline=ORANGE if k==n else GRID,width=3);text(xx+cw/2,139,f'{k:03b}',30,ORANGE if k==n else WHITE,'mm');text(xx,197,f'{k}V',23,MUTED,'mt')
        text(x0+8*cw,197,'8V',23,MUTED,'mt');xx=x0+cw*(n+.5);arrow(xx,62,xx,94,ORANGE);text(580,241,f'区间 [{n},{n+1})V → 码{n:03b}；用下端点重建',28,GREEN,'mt');footer('本页不是四舍五入ADC模型；区间上边界归下一档，8V不在给定输入范围内')
    else:raise ValueError(f'Unknown digital diagram: {v}')
    return im
