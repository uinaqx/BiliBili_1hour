"""8086 execution views use actual snapshots; large concept panels state their conditions."""
import functools,math
from PIL import Image,ImageDraw,ImageFont
from sync_runtime import traces
BG='#10243a';WHITE='#eff5ff';MUTED='#9fb2ca';BLUE='#70cfff';ORANGE='#ffbd68';GREEN='#8fe0b2';GRID='#31516c';RED='#ff939c'
@functools.lru_cache(40)
def font(n):return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
@functools.lru_cache(20)
def mono(n):return ImageFont.truetype('C:/Windows/Fonts/consola.ttf',n)
def render(v,phase,p,size=(1165,310)):
    im=Image.new('RGB',size,BG);d=ImageDraw.Draw(im);w,h=size;p=max(0,min(1,float(p)));part=v.get('narrationPart',0);kind=v['kind'];small=w<700
    def text(x,y,s,n=24,c=WHITE,a='lt',code=False):d.text((x,y),str(s),font=mono(n) if code else font(n),fill=c,anchor=a)
    def line(points,c=BLUE,width=3):d.line(points,fill=c,width=width)
    def arrow(x,y,xx,yy,c=BLUE):
        line((x,y,xx,yy),c);angle=math.atan2(yy-y,xx-x);d.polygon([(xx,yy),(xx-12*math.cos(angle-.5),yy-12*math.sin(angle-.5)),(xx-12*math.cos(angle+.5),yy-12*math.sin(angle+.5))],fill=c)
    def box(x,y,ww,hh,label,c=BLUE,n=27):
        d.rounded_rectangle((x,y,x+ww,y+hh),9,fill='#19384d',outline=c,width=2);text(x+ww/2,y+hh/2,label,n,c,'mm')
    def title(s):text(10,6,s,22 if small else 24,ORANGE)
    def footer(s):text(w/2,289,s,17 if small else 21,MUTED,'mt')
    def step(n):return min(n-1,int(p*n))
    if kind=='execution':
        assert small;trace=traces()[v['trace']];index=v.get('stateIndex');assert isinstance(index,int) and 0<=index<len(trace['snapshots']),(v,index);state=trace['snapshots'][index];previous=trace['snapshots'][max(0,index-1)];regs=v['regs'];values=state['registers']
        text(10,6,'实际执行 · 本步完成状态',18,ORANGE);text(w-8,8,f'第{index}步',17,MUTED,'rt')
        instruction=state['instruction'] or 'initial state';assert mono(19).getlength(instruction)<w-22,instruction;text(10,31,instruction,19,BLUE,code=True)
        # Animation illustrates data flow; the actual state follows authored spoken cues.
        yy=57;arrow(15,yy,w-18,yy,GRID);xx=18+(w-43)*p;d.ellipse((xx-4,yy-4,xx+4,yy+4),fill=ORANGE)
        cols=3 if len(regs)>=5 else 2 if len(regs)>1 else 1;cw=(w-24)/cols;rows=math.ceil(len(regs)/cols)
        for i,name in enumerate(regs):
            x=10+(i%cols)*cw;y=65+(i//cols)*42;changed=values[name]!=previous['registers'][name];d.rounded_rectangle((x,y,x+cw-8,y+36),6,fill='#28483e' if changed else '#19384d',outline=ORANGE if changed else GRID,width=2)
            n=2 if len(name)==2 and name[1] in 'hl' else 4;label=f'{name.upper()}={values[name]:0{n}X}h';text(x+(cw-8)/2,y+18,label,24 if cols<=2 else 21,GREEN if changed else WHITE,'mm',True)
        y=68+rows*42
        if v.get('flags'):
            label='   '.join(f'{name.upper()}={state["flags"][name]}' for name in v['flags']);text(12,y,label,20,ORANGE);y+=24
        if v.get('memory'):
            memory=v['memory'];text(12,y,'内存字节（本例DS=SS，以下为段内偏移）',16,MUTED);y+=20;cw=(w-20)/len(memory)
            for i,offset in enumerate(memory):
                x=10+i*cw;value=state['memory'][f'{offset:04X}'];old=previous['memory'][f'{offset:04X}'];box(x,y,cw-4,32,f'{offset:04X}:{value:02X}',ORANGE if old!=value else BLUE,17 if len(memory)>4 else 20)
            y+=32
        elif state['instruction'].startswith(('push ','call ')) and state['writes']:
            write=state['writes'][-1];text(12,y,f'本步压入：{write["value"]:04X}h；SP={values["sp"]:04X}h',20,GREEN);y+=25
        elif state['instruction'].startswith('ret'):
            text(12,y,f'返回后IP={values["ip"]:04X}h；SP={values["sp"]:04X}h',20,GREEN);y+=25
        if state['output'] and not v.get('memory'):
            text(12,y,'服务记录输出：'+state['output'],21,GREEN);y+=25
        assert y<h-16,('Execution card overflow',v['trace'],index,y,h)
        text(w/2,h-16,'寄存器与内存数值按十六进制显示',14,MUTED,'mt')
    elif kind=='representation':
        title('同一8位位串，两种数值解释');at=step(8)
        for i in range(8):box(120+i*124,65,104,65,'1',ORANGE if i==at else BLUE,37)
        box(65,185,455,70,'无符号：128+127=255',BLUE,31);box(635,185,455,70,'有符号：−128+127=−1',GREEN,30);footer('FFh仍是同一组八个1；位宽与解释必须先约定')
    elif kind=='segment':
        title('8086实模式教学例：段值×16 + 偏移；本例不跨1MB边界');box(25,95,210,75,'1234h',BLUE,35);arrow(245,133,375,133);text(309,80,'×16',27,ORANGE,'mt');box(385,95,230,75,'12340h',GREEN,35);text(650,132,'+',39,ORANGE,'mm');box(700,95,190,75,'0010h',BLUE,35);arrow(905,133,973,133);box(985,95,170,75,'12350h',ORANGE,31)
        text(130,202,'段值',28,BLUE,'mt');text(500,202,'段基址',28,GREEN,'mt');text(795,202,'偏移',28,BLUE,'mt');text(1070,202,'物理地址',27,ORANGE,'mt');line((20,260,20+1120*p,260),ORANGE,4)
    elif kind=='address_modes':
        title('16位寻址有组合限制；同一偏移不等于同一物理地址');labels=[('BX+SI','DS','合法'),('BP+DI','SS','合法'),('AX','—','本模式不合法'),('BX+BP','—','本模式不合法')];at=step(4)
        for i,(a,b,c) in enumerate(labels):
            yy=53+i*48
            if i==at:d.rounded_rectangle((28,yy-2,552,yy+42),5,fill='#30404e')
            text(45,yy,a,26,BLUE);text(250,yy,b,26,GREEN);text(355,yy,c,25,WHITE if i<2 else RED)
        text(820,67,'教学给定：DS=1000h，SS=2000h',25,ORANGE,'mt');text(820,123,'DS:0200h → 10200h',29,BLUE,'mt');text(820,178,'SS:0200h → 20200h',29,GREEN,'mt');footer('合法地址还可加位移；使用段超越时另按明确指定的段处理')
    elif kind=='data_sizes':
        title('明确BYTE与WORD的访问范围 · 初始两字节CDh、ABh');items=[('mov byte [0200h],1',['01','AB'],'只改0200h'),('mov word [0200h],1',['01','00'],'修改0200h与0201h')]
        for i,(code,vals,note) in enumerate(items):
            x=30+i*590;text(x,60,code,30,BLUE,code=True)
            for j,val in enumerate(vals):box(x+85+j*180,118,150,65,val,ORANGE if j==0 or i else GRID,35);text(x+160+j*180,194,f'{0x200+j:04X}h',23,MUTED,'mt')
            text(x+260,240,note,26,GREEN,'mt')
        xx=45+1080*p;d.ellipse((xx-6,36,xx+6,48),fill=ORANGE)
    elif kind=='bit_logic':
        title('4位按位逻辑示意 · 对齐同一位置，再按规则计算');names=['AND','OR','XOR'];results=['1000','1110','0110'];at=0 if part==0 else step(3)
        for i in range(3):
            x=30+i*390;box(x,55,345,54,names[i],ORANGE if i==at else BLUE,31);text(x+172,143,'1010  与  1100',30,WHITE,'mm');text(x+172,215,'→ '+results[i],38,GREEN,'mm')
        footer('逻辑加乘与普通算术分开；NOT取反不更新条件标志')
    elif kind=='stack_contract':
        title('近CALL后的抽象栈布局 · 临时字必须先清理，RET才能取到真正返回IP');active=step(3)
        text(240,63,'正确路径',29,GREEN,'mt');box(70,112,340,58,'栈顶临时字 1234h',BLUE,28);box(70,182,340,58,'返回IP 0106h',GREEN,28);arrow(430,141,560,141,GREEN);text(670,116,'POP恢复临时值',28,GREEN,'mt');text(670,184,'RET再返回0106h',28,GREEN,'mt')
        text(980,63,'错误路径',29,RED,'mt');box(870,117,280,72,'RET误取1234h',RED,28);text(1010,221,'控制位置错误',29,RED,'mt');xx=65+1080*p;d.ellipse((xx-6,265,xx+6,277),fill=ORANGE)
    elif kind=='decimal_conversion':
        title('无符号123转十进制字符 · 反复除10；下图按抽象先后顺序，不是地址布局');at=step(3)
        for i,(a,q,r) in enumerate([(123,12,3),(12,1,2),(1,0,1)]):
            y=56+i*69;box(25,y,430,54,f'{a} ÷ 10 → 商{q}，余{r}',ORANGE if i==at else BLUE,28);arrow(465,y+26,565,y+26,GREEN)
        for i,value in enumerate([1,2,3]):box(595,55+i*69,170,54,str(value),GREEN if part else BLUE,32)
        text(680,267,'栈顶是最后压入的1',22,GREEN,'mt');arrow(780,142,865,142,GREEN);box(875,104,270,75,'输出：123',ORANGE,36);text(1010,218,'各位先加字符0',25,BLUE,'mt')
    elif kind=='debug_process':
        a=traces()['intro_add']['snapshots'][1];b=traces()['intro_add']['snapshots'][2];title('实际执行记录示例：输入、指令与写回分开核对')
        box(30,95,270,90,f'执行前 AX={a["registers"]["ax"]}',BLUE,34);arrow(310,140,435,140);box(445,95,280,90,'ADD AX,5',ORANGE,34);arrow(735,140,855,140);box(865,95,270,90,f'执行后 AX={b["registers"]["ax"]}',GREEN,34);text(580,235,'先找第一处偏差；IP指向后续位置，不等于本步没有执行',26,MUTED,'mt');xx=30+1105*p;d.ellipse((xx-6,61,xx+6,73),fill=ORANGE)
    elif kind=='error_stages':
        title('用发生阶段选排查方式 · 三类错误不混为一种');items=[('汇编阶段','MOV AX,BL','宽度不匹配，拒绝'),('指令执行','DIV 除数为0','CPU除法错误'),('结果检查','负数用无符号关系','执行成功，逻辑不符')];at=step(3)
        for i,(a,b,c) in enumerate(items):
            x=25+i*390;box(x,63,350,62,a,ORANGE if i==at else BLUE,32);text(x+175,164,b,27,WHITE,'mm');text(x+175,237,c,26,RED if i<2 else GREEN,'mm')
    else:raise ValueError(v)
    return im
