"""Original OS teaching diagrams. Semantic phases are authored, motion persists at its endpoint."""
import functools,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import examples
BG='#10243a';TEXT='#eff5ff';BLUE='#70cfff';ORANGE='#ffbd68';GREEN='#8fe0b2';RED='#ff929c';GRID='#33506a';MUTED='#a2b7cc'
DATA=examples.all_examples();BOXES=[]
@functools.lru_cache(32)
def font(size):return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size)
def txt(d,xy,value,size=25,color=TEXT,anchor='lt'):d.text(tuple(xy),str(value),font=font(size),fill=color,anchor=anchor)
def wrap(d,value,xy,width=330,size=25,color=TEXT):
    x,y=xy;row=''
    for ch in str(value):
        if row and font(size).getlength(row+ch)>width:txt(d,(x,y),row,size,color);y+=36;row=''
        row+=ch
    if row:txt(d,(x,y),row,size,color);y+=36
    return y
def note(d,a,b=''):
    y=wrap(d,a,(805,52),330,25,ORANGE)+20
    if b:y=wrap(d,b,(805,y),330,23,MUTED)
    assert y<300,('Diagram annotation overflow',a,b)
def line(d,a,b,color=GRID,width=3):
    a=np.asarray(a,float);b=np.asarray(b,float);v=b-a;visible=[(0.,1.)]
    # Connections pass behind node interiors, keeping labels readable.
    for x,y,xx,yy in BOXES:
        enter,leave=0.,1.;hit=True
        for axis,low,high in [(0,x+2,xx-2),(1,y+2,yy-2)]:
            if abs(v[axis])<1e-9:
                if not low<=a[axis]<=high:hit=False;break
            else:
                p,q=sorted([(low-a[axis])/v[axis],(high-a[axis])/v[axis]]);enter=max(enter,p);leave=min(leave,q)
        if not hit or enter>=leave:continue
        pieces=[]
        for low,high in visible:
            if high<=enter or low>=leave:pieces.append((low,high));continue
            if low<enter:pieces.append((low,enter))
            if high>leave:pieces.append((leave,high))
        visible=pieces
    for low,high in visible:
        if high-low>1e-8:d.line([tuple(a+v*low),tuple(a+v*high)],fill=color,width=width)
def path(d,points,color=GRID,width=3):
    for a,b in zip(points,points[1:]):line(d,a,b,color,width)
def dot(d,p,color=ORANGE,r=6):d.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=color)
def arrow(d,a,b,color=GRID,width=3):
    a=np.array(a,float);b=np.array(b,float);v=b-a;n=np.linalg.norm(v)
    if n<2:return
    line(d,a,b,color,width);v/=n;q=np.array([-v[1],v[0]]);d.polygon([tuple(b),tuple(b-v*12+q*6),tuple(b-v*12-q*6)],fill=color)
def box(d,rect,label,color=BLUE,fill='#18374b',size=25):
    x,y,xx,yy=rect;BOXES.append(rect);d.rounded_rectangle(rect,10,fill=fill,outline=color,width=2)
    lines=str(label).split('\n');height=len(lines)*34
    for i,s in enumerate(lines):
        assert font(size).getlength(s)<xx-x-8,('Box text overflow',label,rect)
        txt(d,((x+xx)/2,(y+yy-height)/2+17+i*34),s,size,color,'mm')
def packet(d,points,t,color=ORANGE):
    lengths=[float(np.linalg.norm(np.array(b)-a)) for a,b in zip(points,points[1:])];amount=max(0,min(1,t))*sum(lengths);p=np.array(points[-1],float)
    for a,b,length in zip(points,points[1:],lengths):
        if amount<=length+1e-7:
            p=np.array(a)+(np.array(b)-a)*min(1,amount/max(length,1e-9));break
        amount-=length
    dot(d,p,color)
def flow(d,labels,phase,t):
    n=len(labels);w=min(205,690/n);gap=35;total=n*w+(n-1)*gap;x=(770-total)/2;y=120
    for i,label in enumerate(labels):
        left=x+i*(w+gap);box(d,(left,y,left+w,y+64),label,GREEN if i<phase else BLUE)
        if i<n-1:arrow(d,(left+w,y+32),(left+w+gap,y+32),GRID)
    points=[(x+w/2,y+32),(x+phase*(w+gap)+w/2,y+32)]
    packet(d,points,t)
def layers(d,phase,t):
    for i,label in enumerate(['应用程序','操作系统','处理器 / 内存 / 设备']):box(d,(120,20+i*92,700,90+i*92),label)
    pts=[(740,55),(760,55),(760,240),(720,240)] if phase=='layers' else [(120,150),(65,150),(65,55),(120,55)]
    path(d,pts);packet(d,pts,t);note(d,'应用提出请求，系统协调资源','虚拟和共享都有管理规则')
def cpu_lanes(d,phase,t):
    colors=[BLUE,GREEN];txt(d,(40,8),'处理器执行时间 →',23,MUTED)
    if phase=='concurrent':
        txt(d,(35,110),'CPU',24);x=135
        for i in range(8):d.rectangle((x+i*75,82,x+(i+1)*75-3,150),fill='#1d4152',outline=colors[i%2]);txt(d,(x+i*75+36,116),'AB'[i%2],28,colors[i%2],'mm')
        cursor=x+600*t;line(d,(cursor,65),(cursor,170),ORANGE,4);note(d,'单处理机交替推进','A、B在一段时间内并发')
    else:
        for i in range(2):
            txt(d,(35,70+i*100),'CPU'+str(i),24);d.rectangle((150,55+i*100,730,120+i*100),fill='#1d4152',outline=colors[i]);txt(d,(420,87+i*100),'AB'[i],30,colors[i],'mm')
        line(d,(150+580*t,35),(150+580*t,240),ORANGE,4);note(d,'两个执行单元同时推进','同一时刻的并行')
def mode(d,phase,t):
    box(d,(70,60,310,145),'应用 · 用户态');box(d,(470,60,740,145),'内核服务',GREEN)
    pts=[(310,102),(470,102)] if phase=='user' else [(605,145),(605,235),(190,235),(190,145)]
    path(d,pts);packet(d,pts,t);txt(d,(350,55),'规定入口',23,ORANGE);note(d,'权限变化 ≠ 进程切换','可能始终为同一进程服务')
def kernel(d,phase,t):
    if phase=='interrupt':
        flow(d,['时钟 / 设备','处理器','内核处理'],2,t);note(d,'外部事件通知','保存现场，处理后再决定恢复谁')
    else:
        for i,label in enumerate(['较小内核核心','文件服务','设备服务']):box(d,(50+i*255,100,260+i*255,180),label,GREEN if i==0 else BLUE)
        pts=[(260,140),(305,140),(560,140)];path(d,pts);packet(d,pts,t);note(d,'服务边界由结构设计决定','微内核把部分服务放在核心之外')
def process_image(d,phase,t):
    box(d,(35,100,225,180),'磁盘程序');box(d,(365,25,630,135),'进程A\n代码 / 数据 / 栈');box(d,(365,175,630,285),'进程B\n代码 / 数据 / 栈')
    pts=[(225,140),(290,140),(290,80 if phase=='launch' else 230),(365,80 if phase=='launch' else 230)];path(d,pts);packet(d,pts,t)
    if phase=='pcb':box(d,(660,185,785,275),'PCB',ORANGE)
    note(d,'同一程序可以多次运行','进程有各自的运行状态和管理信息')
def process_states(d,phase,t):
    box(d,(35,75,235,145),'就绪');box(d,(385,75,585,145),'运行',GREEN);box(d,(385,230,585,295),'阻塞',ORANGE)
    for a,b in [((235,105),(385,105)),((385,125),(235,125)),((485,145),(485,230))]:arrow(d,a,b)
    pts=[(585,263),(710,263),(710,20),(135,20),(135,75)];path(d,pts)
    arrow(d,pts[-2],pts[-1])
    if phase=='ready_run':packet(d,[(385,125),(235,125)],t)
    else:packet(d,pts,t)
    note(d,'事件完成：阻塞 → 就绪','就绪只差处理器；阻塞还缺条件')
def threads(d,phase,t):
    box(d,(40,20,750,90),'进程共享：代码 / 全局数据 / 堆',GREEN)
    for i in range(3):box(d,(60+i*235,175,255+i*235,270),f'线程{i}\n寄存器 / 私有栈')
    k=min(2,int(t*3));pts=[(155+k*235,175),(155+k*235,90)];path(d,pts);packet(d,pts,t if phase=='shared' else 1-t/2);note(d,'共享地址空间，独立执行现场','共享变量仍需要同步保护')
def mapping(d,phase,t):
    for i in range(3):box(d,(45+i*245,30,245+i*245,95),'用户线程'+str(i))
    if phase=='many_one':
        box(d,(295,215,535,285),'一个内核调度实体',GREEN);pts=[(145,95),(145,150),(415,150),(415,215)];path(d,pts);packet(d,pts,t)
        for x in [390,635]:path(d,[(x,95),(x,150),(415,150)])
        note(d,'多对一','多个用户线程不能仅凭此映射在多核并行')
    else:
        for i in range(3):box(d,(45+i*245,215,245+i*245,285),'内核线程'+str(i),GREEN);arrow(d,(145+i*245,95),(145+i*245,215))
        packet(d,[(145,95),(145,215)],t);note(d,'一对一','内核分别调度，管理成本也会增加')
def schedule(d,phase,t):
    key='srtf' if phase=='first' else 'sjf' if phase in ['sjf','hrrn'] else 'rr' if phase=='rr' else 'fcfs';seq=DATA['rr'] if key=='rr' else DATA['schedules'][key];colors={'A':BLUE,'B':GREEN,'C':ORANGE};scale=70;x0=70;y=115
    txt(d,(50,15),key.upper()+' · 不计切换开销',24,ORANGE)
    for z in seq:
        a=x0+z['start']*scale;b=x0+z['end']*scale;box(d,(a,y,b-2,y+75),z['name'],colors[z['name']],size=25);txt(d,(a,y+86),z['start'],22,MUTED)
    txt(d,(x0+9*scale,y+86),9,22,MUTED);cursor=x0+9*scale*t;line(d,(cursor,86),(cursor,204),ORANGE,4)
    if phase=='hrrn':note(d,'时刻5：B响应比7/3，C为4','优先选择C，比较同一当前时刻')
    elif phase=='turnaround':note(d,'完成减到达','A：5；B：7；C：7')
    else:note(d,'按规则一步步更新时间线','到达时间和剩余时间都要检查')
def queues(d,phase,t):
    if phase=='mlfq':
        for i,(label,q) in enumerate([('高优先级',2),('中优先级',4),('低优先级',8)]):box(d,(80,10+i*95,700,82+i*95),label+' · 示例时间片'+str(q))
        packet(d,[(730,45),(760,45),(760,235),(700,235)],t);note(d,'迁移按给定规则','时间片和优先级不是越大越高的固定关系')
    else:
        box(d,(60,75,310,210),'CPU0\nA / B / C');box(d,(500,75,750,210),'CPU1\n空闲');packet(d,[(310,140),(500,140)],t);note(d,'负载均衡 ↔ 处理器亲和性','迁移可能改善负载，也可能损失缓存收益')
def race(d,phase,t):
    box(d,(280,95,505,175),'count = '+('1' if phase=='write' and t>.75 else '0'),ORANGE)
    box(d,(20,25,220,105),'A读到0');box(d,(20,205,220,285),'B读到0')
    if phase=='read':pts=[(505,135),(640,135),(640,245),(220,245)]
    else:pts=[(220,65),(280,65),(280,135),(505,135)]
    path(d,pts);packet(d,pts,t);note(d,'两次增加，可能只写回1','读、改、写的交错造成丢失更新')
def semaphore(d,phase,t):
    box(d,(40,80,245,170),'等待者A');box(d,(355,80,565,170),'许可 / mutex',GREEN);box(d,(650,80,790,170),'临界区')
    pts=[(245,125),(355,125),(565,125),(650,125)];path(d,pts);packet(d,pts,t);note(d,'P申请，V释放','操作原子；互斥初值通常为1')
    if phase=='lock':txt(d,(330,225),'A持有许可时，其他参与者等待',24,ORANGE,'mm')
def precedence(d,phase,t):
    labels=['A完成a','V(s)通知','B的P(s)','B执行b'];x=15;w=170
    for i,label in enumerate(labels):box(d,(x+i*200,100,x+i*200+w,185),label,GREEN if phase=='after' and i<3 else BLUE)
    pts=[(185,143),(215,143),(385,143),(415,143),(585,143),(615,143)];path(d,pts);packet(d,pts,t)
    note(d,'s初始为0','先完成条件，再通知；先等待，再执行')
def buffer(d,phase,t):
    for i in range(3):box(d,(180+i*170,95,325+i*170,205),'产品' if phase=='produce' and i==0 and t>.65 else '空位',GREEN if phase=='produce' and i==0 else BLUE)
    box(d,(20,100,145,200),'生产者',ORANGE);packet(d,[(145,150),(180,150)],t)
    note(d,'放入1个：empty=2，full=1' if phase=='produce' and t>.65 else '容量3：初始empty=3，full=0','计数表示完成操作后的稳定状态')
def deadlock(d,phase,t):
    if phase=='wait':flow(d,['磁盘执行','完成通知','P回就绪'],2,t);note(d,'普通等待可能正常解除','不要把一切阻塞都叫死锁');return
    box(d,(70,25,250,105),'进程A');box(d,(490,205,670,285),'进程B');box(d,(490,25,670,105),'打印机');box(d,(70,205,250,285),'扫描仪')
    edges=[((490,65),(250,65),GREEN),((160,105),(160,205),BLUE),((250,245),(490,245),GREEN),((580,205),(580,105),BLUE)]
    for a,b,color in edges:arrow(d,a,b,color)
    pts=[(490,65),(250,65),(160,105),(160,205),(250,245),(490,245),(580,205),(580,105)];packet(d,pts,t);note(d,'A持打印机，B持扫描仪','绿色占有，蓝色请求；等待形成环')
def resource_graph(d,phase,t):
    if phase=='reduce':
        flow(d,['满足P1需求','P1完成释放','可用量增加'],2,t);note(d,'多实例不能只看有没有环','按当前可用量尝试消去可完成者');return
    box(d,(45,20,245,100),'进程P');box(d,(470,20,730,100),'资源R1',BLUE)
    box(d,(45,205,245,285),'进程Q');box(d,(470,205,730,285),'资源R2',GREEN)
    arrow(d,(245,60),(470,60),BLUE);arrow(d,(470,245),(245,245),GREEN);packet(d,[(245,60),(470,60)],t);txt(d,(330,15),'请求',22,BLUE);txt(d,(330,195),'分配',22,GREEN);note(d,'进程→资源：请求','资源→进程：已经分配；两个独立方向图例')
def banker(d,phase,t):
    for i,(a,m,n) in enumerate(zip([1,2,1],[6,5,3],[5,3,2])):box(d,(40+i*245,20,260+i*245,115),f'P{i}  已分配{a}\n最大{m} / 还需{n}')
    sequence=[(1,3,5)] if phase=='first' else [(0,5,6),(2,6,7)];at=min(len(sequence)-1,max(0,math.ceil(t*len(sequence)-1e-8)-1));p,before,after=sequence[at];local=min(1,t*len(sequence)-at);work=after if local>.8 else before
    box(d,(250,210,540,290),f'Work = {work}',GREEN);packet(d,[(150+p*245,115),(150+p*245,160),(395,160),(395,210)],local);note(d,f'P{p}完成，释放原分配量' if local>.8 else f'试推P{p}，还需{[5,3,2][p]}',f'{before}＋{after-before}＝{after}；不是加最大需求')
def address(d,phase,t):
    box(d,(30,105,240,180),'逻辑偏移 800');box(d,(330,65,555,215),'界限1200\n基址4000',GREEN);box(d,(635,105,790,180),'物理4800',ORANGE)
    pts=[(240,142),(330,142)] if phase=='logical' else [(555,142),(635,142)];path(d,pts);packet(d,pts,t);note(d,'先确认800＜1200','再算4000＋800；越界则不进入相加路径')
def holes(d,phase,t):
    holes=[100,500,200,300,600];chosen=[1,3,4]
    for row,(label,index) in enumerate(zip(['首次','最佳','最坏'],chosen)):
        y=20+row*92;txt(d,(12,y+25),label,22,MUTED)
        for i,size in enumerate(holes):
            x=88+i*138;box(d,(x,y,x+125,y+65),size,ORANGE if i==index else BLUE,size=24)
            if i==index:
                frac=212/size*(t if phase=='remainder' else .08);d.rectangle((x+3,y+50,x+3+round(119*frac),y+61),fill=GREEN)
        if phase=='remainder':txt(d,(90,y+68),f'{holes[index]} − 212 = {holes[index]-212}',20,GREEN)
    if phase=='fit':dot(d,(88+138*(4*t)+62,300),ORANGE)
    note(d,'每种算法独立比较同一次申请','申请212；初始空闲区完全相同')
def paging(d,phase,t):
    if phase=='fragment':
        for i in range(4):
            x=45+i*175;box(d,(x,90,x+145,220),'整页' if i<3 else '末页')
            d.rectangle((x+4,165,x+141,216),fill='#285d67')
            if i==3:d.rectangle((x+4+int(135*.4),165,x+141,216),fill='#5a3a3c')
        packet(d,[(670,240),(740,240)],t);note(d,'末页未装满：内部碎片','固定页框不等于完全没有空间开销');return
    for i,frame in enumerate([4,1,5]):
        y=25+i*90;box(d,(70,y,280,y+65),f'逻辑页 {i}');box(d,(520,y,740,y+65),f'物理页框 {frame}',GREEN);arrow(d,(280,y+32),(520,y+32))
    i=min(2,int(t*3));packet(d,[(280,57+i*90),(520,57+i*90)],min(1,t*3-i));note(d,'页号通过页表映射为页框号','不同逻辑页可以分散放置')
def page_lookup(d,phase,t):
    box(d,(30,100,220,180),'逻辑地址2500');box(d,(315,20,535,90),'页号2',BLUE);box(d,(315,210,535,285),'偏移452',GREEN);box(d,(610,20,790,90),'页表2→5',ORANGE);box(d,(610,210,790,285),'地址5572',GREEN)
    path(d,[(220,140),(265,140),(265,55),(315,55)]);path(d,[(265,140),(265,247),(315,247)])
    if phase=='split':packet(d,[(220,140),(265,140),(265,55),(315,55)],t)
    else:
        arrow(d,(535,55),(610,55));arrow(d,(700,90),(700,210));arrow(d,(535,247),(610,247));packet(d,[(535,55),(700,55),(700,210)],t)
    note(d,'2500＝2×1024＋452','换成页框5后：5×1024＋452＝5572')
def tlb(d,phase,t):
    box(d,(20,115,165,185),'页号');box(d,(280,25,485,100),'TLB · 10ns',GREEN);box(d,(280,210,485,290),'内存页表');box(d,(625,115,790,185),'目标数据\n内存100ns',ORANGE)
    if phase=='hit':pts=[(165,150),(225,150),(225,63),(485,63),(707,63),(707,115)];value=110
    else:pts=[(165,150),(225,150),(225,63),(380,63),(380,210),(485,250),(707,250),(707,185)];value=210
    path(d,pts);packet(d,pts,t);note(d,('命中110ns' if phase=='hit' else '快表未命中210ns'),'本模型一级页表、不缺页，查询串行')
def segments(d,phase,t):
    if phase=='segment':flow(d,['段号','查基址和段长','检查偏移','基址＋偏移'],3,t);note(d,'段基址4000，长度1200','偏移800合法→4800；1300越界')
    else:
        labels=['段号','本段页表','页号→页框','加页内偏移'];flow(d,labels,3,t);note(d,'段页式：先段后页','每层字段与表项各有含义')
def page_fault(d,phase,t):
    if phase=='fault':labels=['合法访问','页面未驻留','缺页异常']
    else:labels=['调入页面','更新映射','就绪后调度','重试指令']
    flow(d,labels,len(labels)-1,t);note(d,'缺页可能伴随外存等待','已修改的淘汰页还可能先写回')
def replacement(d,phase,t):
    if phase=='belady':
        for row,n in enumerate(['3','4']):
            seq=DATA['belady'][n];idx=min(len(seq)-1,int(t*(len(seq)-1)));x=seq[idx];txt(d,(40,15+row*145),f'{n}页框 FIFO · 当前缺页{x["faults"]}',24,ORANGE)
            for j,p in enumerate(x['frames']):box(d,(65+j*155,62+row*145,205+j*155,130+row*145),p,GREEN if p==x['page'] else BLUE)
            dot(d,(50+680*t,140+row*145))
        note(d,'相同12次访问序列','终点：3框缺9次，4框缺10次');return
    algorithm=phase if phase in ['fifo','lru','opt'] else 'fifo';states=DATA['replacements'][algorithm];idx=min(5,2+int(t*3+1e-7)) if phase=='fifo' else min(len(states)-1,int(t*(len(states)-1)));s=states[idx]
    txt(d,(35,5),algorithm.upper()+' · 初始3框全空',24,ORANGE)
    for i,p in enumerate(examples.REFS):
        x=35+i*55;d.rectangle((x,52,x+49,102),fill='#285365' if i==idx else BG,outline=GREEN if i<idx else GRID);txt(d,(x+24,77),p,23,TEXT,'mm')
    for i in range(3):box(d,(95+i*195,150,260+i*195,235),s['frames'][i] if i<len(s['frames']) else '空',GREEN if i<len(s['frames']) and s['frames'][i]==s['page'] else BLUE,size=32)
    cursor=35+55*(2+3*t if phase=='fifo' else (len(states)-1)*t)+24;line(d,(cursor,112),(cursor,132),ORANGE,4);txt(d,(70,255),'缺页' if s['fault'] else '命中',26,ORANGE);txt(d,(310,255),'累计缺页 '+str(s['faults']),26,GREEN);note(d,'先装入7、0、1，再处理2、0、3' if phase=='fifo' else '每次访问先判命中','初次装入也算缺页；帧内显示真实模拟状态')
def clock(d,phase,t):
    center=np.array([370,165]);positions=[center+np.array([math.cos(a),math.sin(a)])*108 for a in [-math.pi/2,math.pi/6,5*math.pi/6]]
    for i,pos in enumerate(positions):
        value=4 if phase=='replace' and i==1 and t>.65 else i+1;bit=0 if i==0 and (phase=='replace' or t>.65) else [1,0,1][i]
        if phase=='replace' and i==1 and t>.65:bit=1
        box(d,(pos[0]-70,pos[1]-40,pos[0]+70,pos[1]+40),f'页{value} / R={bit}',GREEN if i==1 and phase=='replace' else BLUE,size=21)
    angle=-math.pi/2+2*math.pi/3*(t if phase=='scan' else 1+t);q=center+95*np.array([math.cos(angle),math.sin(angle)]);arrow(d,center,q,ORANGE,4);note(d,'初始访问位：[1,0,1]','先清页1，再替换页2，指针前移')
def latency(d,phase,t):
    for i,(label,cost,color) in enumerate([('正常访问',100,BLUE),('缺页总耗时',8000000,ORANGE)]):
        y=45+i*115;txt(d,(30,y),label,24,color);d.rectangle((210,y+5,210+500*(.12 if i==0 else 1),y+52),outline=color,width=2)
        end=210+500*(.12 if i==0 else 1)*t;line(d,(210,y+30),(end,y+30),color,5);txt(d,(220,y+62),str(cost)+' ns',23,color)
    note(d,'代价示意采用压缩比例','缺页率0.001，平均8099.9ns；条宽不是线性比例')
def working_set(d,phase,t):
    if phase=='thrash':
        box(d,(55,80,270,210),'内存页框\n容量不足');box(d,(510,80,740,210),'外存页面')
        pts=[(270,115),(510,115),(510,175),(270,175)];path(d,pts);packet(d,pts,t);note(d,'刚换出，很快又要换回','工作集装不下，调页可能反复发生')
    else:
        box(d,(20,35,230,110),'父进程');box(d,(20,205,230,280),'子进程');box(d,(445,35,715,110),'原物理页 · 只读共享',GREEN,size=23);box(d,(445,205,715,280),'写入时的新副本',ORANGE,size=23)
        arrow(d,(230,72),(445,72));arrow(d,(230,242),(445,72));packet(d,[(580,110),(580,205)],t);note(d,'写时复制','逻辑保持隔离，写入才复制对应页')
def file_allocation(d,phase,t):
    blocks=[4,5,6,7] if phase=='contiguous' else [4,9,2,11]
    for i,b in enumerate(blocks):
        x=30+i*195;box(d,(x,110,x+160,190),'盘块'+str(b),GREEN if i<t*4 else BLUE)
        if i<3:arrow(d,(x+160,150),(x+195,150))
    packet(d,[(190,150),(615,150)],t)
    if phase=='fat':txt(d,(45,35),'FAT：4→9，9→2，2→11，11→结束',24,ORANGE)
    note(d,'连续盘块直接定位' if phase=='contiguous' else 'FAT集中存放下一块关系','图示文件有4个数据块；地址链不等于直接索引')
def file_index(d,phase,t):
    box(d,(15,95,205,195),'索引节点');box(d,(320,10,520,75),'直接数据块',GREEN);box(d,(320,115,520,180),'单级索引块');box(d,(320,225,520,295),'二级索引块');box(d,(610,115,790,180),'数据块',GREEN);box(d,(610,225,790,295),'下级索引')
    paths=[[(205,125),(265,125),(265,43),(320,43)],[(205,145),(320,145),(520,145),(610,145)],[(205,165),(265,165),(265,260),(320,260),(520,260),(610,260)]]
    for p in paths:path(d,p)
    selected=0 if phase=='direct' else min(2,1+int(t*2));packet(d,paths[selected],t if selected==0 else min(1,t*2-(selected-1)))
    note(d,'每索引块1024个地址项','直接12；单级1024；二级1024²个数据块')
def directory(d,phase,t):
    if phase=='directory':flow(d,['文件名','目录项','索引节点','数据块'],3,t);note(d,'名称、管理信息和内容分开','索引节点编号不等于文件内容')
    else:flow(d,['根 /','course','os','note'],3,t);note(d,'逐级解析路径','相对路径还要先确定当前工作目录')
def open_files(d,phase,t):
    if phase=='open':
        flow(d,['描述符3','打开状态','索引节点','数据块'],3,t);note(d,'当前位置属于打开状态','描述符是进程引用已打开文件的入口');return
    box(d,(20,20,230,90),'另行open两次');box(d,(330,20,520,90),'状态A · 偏移0');box(d,(590,20,785,90),'状态B · 偏移0')
    box(d,(20,205,240,275),'继承同一打开状态');box(d,(420,205,740,275),'共享偏移 '+str(100 if t>.8 else 0),GREEN)
    pts=[(240,240),(420,240)];path(d,pts);packet(d,pts,t);note(d,'同一文件，偏移关系仍要看引用','分别open可以独立；继承状态可以共享')
def disk_mechanics(d,phase,t):
    cx,cy,R=345,155,112
    for rr in [R,R*.75,R*.45]:d.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=GRID,width=3)
    if phase=='rotate':a=t*2*math.pi;dot(d,(cx+R*.75*math.cos(a),cy+R*.75*math.sin(a)));arrow(d,(cx,cy),(cx+R*.75,cy),BLUE,3)
    else:arrow(d,(cx+R+65,cy),(cx+R*(1-.55*t),cy),ORANGE,5)
    note(d,'旋转等待与寻道不同','7200转/分钟：周期8.33ms，平均等待约4.17ms')
def disk_schedule(d,phase,t):
    path_values=DATA['disks'][phase];n=len(path_values)-1;step=min(n-1,int(t*n));local=min(1,t*n-step)
    def p(v):return (65+690*v/199,75)
    line(d,p(0),p(199),MUTED,3)
    for i,value in enumerate(sorted(set([0,199,50,*examples.DISK]))):
        x,y=p(value);line(d,(x,y-7),(x,y+7),BLUE,2);txt(d,(x,y+18+(i%2)*24),value,19,MUTED,'mt')
    head=path_values[step]+(path_values[step+1]-path_values[step])*local;dot(d,p(head),ORANGE,9)
    txt(d,(40,145),phase.upper()+' 路径',24,ORANGE);label=' → '.join(str(v) for v in path_values);wrap(d,label,(40,192),730,24,TEXT)
    note(d,'起点50，磁道0—199，初始向上',f'总移动距离：{examples.distance(path_values)}；回跳和边界按规则计入')
def bitmap(d,phase,t):
    bits=[1,0,0,1,0,0,0,1,1,0,0,0,1,0,0,1];index=min(15,int(t*16));free=bits.index(0)
    if phase=='allocate' and t>.7:bits[free]=1
    for i,b in enumerate(bits):
        x=30+i%8*94;y=55+i//8*100;box(d,(x,y,x+80,y+68),b,GREEN if b else BLUE,size=30)
    x=30+index%8*94+40;y=45+index//8*100;dot(d,(x,y),ORANGE)
    note(d,'1已占，0空闲；这里只示意16位','1000位＝125字节；按4KiB盘块存需1块')
def io_layers(d,phase,t):
    labels=['应用 / 库','设备独立层','驱动','控制器'];x=[10,210,410,610]
    for left,label in zip(x,labels):box(d,(left,110,left+170,185),label)
    pts=[(180,148),(210,148),(380,148),(410,148),(580,148),(610,148)]
    if phase=='complete':pts=list(reversed(pts))
    path(d,pts);packet(d,pts,t);note(d,'请求向下，完成通知向上','驱动是软件；控制器是硬件部件')
def dma(d,phase,t):
    box(d,(20,30,230,115),'CPU');box(d,(20,210,230,290),'设备');box(d,(330,210,545,290),'控制器');box(d,(625,210,790,290),'内存',GREEN)
    if phase=='poll':pts=[(125,115),(125,210),(125,115)];path(d,pts);packet(d,pts,t);note(d,'轮询反复检查设备','处理器仍在执行检查循环')
    else:
        path(d,[(230,73),(435,73),(435,210)],BLUE);txt(d,(285,35),'CPU先配置',23,BLUE);pts=[(230,250),(330,250),(545,250),(625,250)];path(d,pts);packet(d,pts,t);note(d,'数据在设备与内存间传送','初始化、完成或异常处理仍可能需要CPU')
def buffer_pipeline(d,phase,t):
    rows=[('设备',82),('复制/处理',195)];scale=21;x=130
    for label,y in rows:txt(d,(10,y+20),label,22,MUTED);line(d,(x,y+66),(x+630,y+66),GRID,2)
    for k in range(3):
        start=k*(12 if phase=='single' else 10);end=start+10
        if end<=30:
            a=x+start*scale;b=x+end*scale;box(d,(a,82,b-2,142),'读入',BLUE,size=22)
        copy=start+10
        if copy+2<=30:d.rectangle((x+copy*scale,195,x+(copy+2)*scale-2,255),fill='#47634d');txt(d,(x+(copy+1)*scale,225),'复',20,GREEN,'mm')
        if copy+2<30:
            a=x+(copy+2)*scale;b=x+min(30,copy+8)*scale;box(d,(a,195,b-2,255),'处理',ORANGE,size=22)
    cursor=x+630*t;line(d,(cursor,55),(cursor,270),ORANGE,4);note(d,'单缓冲稳定周期12' if phase=='single' else '双缓冲稳定周期10','T=10，M=2，C=6；时间线为该简化模型')
def spooling(d,phase,t):
    for i,name in enumerate(['作业A','作业B','作业C']):box(d,(20,15+i*95,205,85+i*95),name)
    box(d,(350,70,565,230),'磁盘排队区',GREEN);box(d,(650,95,790,195),'打印机',ORANGE)
    pts=[(205,50),(265,50),(265,150),(350,150)] if phase=='spool' else [(565,150),(650,150)]
    path(d,pts);packet(d,pts,t);note(d,'多个作业可提交，设备依次执行','假脱机不改变一台打印机的物理能力')
def read_path(d,phase,t):
    labels=['read请求','文件与缓存','设备等待','就绪并调度']
    for i,label in enumerate(labels):box(d,(5+i*200,115,190+i*200,195),label,size=23)
    pts=[(190,155),(205,155),(390,155),(405,155),(590,155),(605,155)]
    path(d,pts);packet(d,pts,t);note(d,'缓存未命中的常见简化读取链' if phase=='read' else '设备完成后，先具备继续条件','没有把所有read都等同于一次磁盘访问')
def render(visual,phase,t):
    BOXES.clear();im=Image.new('RGB',(1165,310),BG);d=ImageDraw.Draw(im);kind=visual['kind'];t=max(0,min(1,t))
    functions={'layers':layers,'cpu_lanes':cpu_lanes,'mode_switch':mode,'kernel_structure':kernel,'process_image':process_image,'process_states':process_states,'threads':threads,'thread_mapping':mapping,'schedule':schedule,'queues':queues,'race':race,'semaphore':semaphore,'precedence':precedence,'buffer':buffer,'deadlock':deadlock,'resource_graph':resource_graph,'banker':banker,'address':address,'holes':holes,'paging':paging,'page_lookup':page_lookup,'tlb':tlb,'segments':segments,'page_fault':page_fault,'replacement':replacement,'clock':clock,'latency':latency,'working_set':working_set,'file_allocation':file_allocation,'file_index':file_index,'directory':directory,'open_files':open_files,'disk_mechanics':disk_mechanics,'disk_schedule':disk_schedule,'disk_scan':disk_schedule,'disk_cycle':disk_schedule,'bitmap':bitmap,'io_layers':io_layers,'dma':dma,'buffer_pipeline':buffer_pipeline,'spooling':spooling,'read_path':read_path}
    assert kind in functions,('Unimplemented authored diagram',kind);functions[kind](d,phase,t);return im
