"""Original continuous diagrams. Each animation tick recomputes visible state."""
import functools,json,math,pathlib,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'content'))
from visuals import graph_for
BG='#09172a';PANEL='#10243a';TEXT='#eff5ff';MUTED='#9fb2ca';BLUE='#70cfff';ORANGE='#ffbd68';GREEN='#8fe0b2';RED='#ff929c';PURPLE='#c6abff';GRID='#25435e';COLORS=dict(blue=BLUE,orange=ORANGE,green=GREEN,red=RED,purple=PURPLE)
@functools.lru_cache(48)
def font(size,mono=False):return ImageFont.truetype('C:/Windows/Fonts/consola.ttf' if mono else 'C:/Windows/Fonts/msyh.ttc',size)
def tx(d,p,s,size=30,color=TEXT,anchor='lt',mono=False):d.text(tuple(map(float,p)),str(s),font=font(size,mono),fill=color,anchor=anchor)
def wrap(d,s,x,y,width,size=28,color=TEXT,line=40):
    row=''
    for ch in s:
        if font(size).getlength(row+ch)>width and row:tx(d,(x,y),row,size,color);row='';y+=line
        row+=ch
    if row:tx(d,(x,y),row,size,color);y+=line
    return y
def line(d,a,b,color=GRID,width=3):d.line([tuple(a),tuple(b)],fill=color,width=width)
def arrow(d,a,b,color=BLUE,width=4):
    a=np.array(a,float);b=np.array(b,float);delta=b-a;length=np.linalg.norm(delta)
    if length<2:return
    line(d,a,b,color,width);v=delta/length;q=np.array([-v[1],v[0]]);d.polygon([tuple(b),tuple(b-13*v+6*q),tuple(b-13*v-6*q)],fill=color)
def dot(d,p,color=ORANGE,r=9):d.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=color)
def box(d,b,label,color=BLUE,selected=False,size=30):
    x,y,w,h=b;d.rounded_rectangle((x,y,x+w,y+h),12,fill='#24364b' if selected else '#152d44',outline=color if selected else GRID,width=4 if selected else 2)
    rows=label.split('\n');yy=y+h/2-(len(rows)-1)*21
    for r in rows:
        assert font(size).getlength(r)<=w-14,('Node text overflow',r,w,size)
        tx(d,(x+w/2,yy),r,size,color if selected else TEXT,'mm');yy+=42
def poly(d,points,color=BLUE,width=4,head=True):
    for a,b in zip(points,points[1:]):line(d,a,b,color,width)
    if head:arrow(d,points[-2],points[-1],color,width)
def along(points,q):
    lens=[float(np.linalg.norm(np.array(b)-a)) for a,b in zip(points,points[1:])];target=max(0,min(1,q))*sum(lens)
    for a,b,length in zip(points,points[1:],lens):
        if target<=length:return np.array(a)+(np.array(b)-a)*(target/max(length,1e-9))
        target-=length
    return np.array(points[-1])
def edge_points(a,b):
    ac=np.array([a['x']+a['w']/2,a['y']+a['h']/2]);bc=np.array([b['x']+b['w']/2,b['y']+b['h']/2]);delta=bc-ac
    if abs(delta[0])>=abs(delta[1])*.8:
        sign=1 if delta[0]>0 else -1;start=ac+[sign*a['w']/2,0];end=bc-[sign*b['w']/2,0]
        if abs(delta[1])<15:return [start,end]
        mid=(start[0]+end[0])/2;return [start,[mid,start[1]],[mid,end[1]],end]
    sign=1 if delta[1]>0 else -1;start=ac+[0,sign*a['h']/2];end=bc-[0,sign*b['h']/2]
    if abs(delta[0])<15:return [start,end]
    mid=(start[1]+end[1])/2;return [start,[start[0],mid],[end[0],mid],end]
def graph(d,spec,phase,t):
    nodes={n['id']:n for n in spec['nodes']};paths=spec['paths'][phase];route=0 if t<=.5 else 1;q=min(1,t*2) if route==0 else (t-.5)*2
    completed=paths[:route];active=paths[route];marked=set();selected=set()
    for path in completed:
        marked.update(zip(path,path[1:]));selected.update(path)
    if phase=='schedule' and t>=.5:
        path=['start','b','join'];marked.update(zip(path,path[1:]));selected.update(path)
    leg=min(len(active)-2,int(q*(len(active)-1)));local=q*(len(active)-1)-leg
    selected.update(active[:leg+1]);marked.update(zip(active[:leg+1],active[1:leg+1]))
    if q>=.999:
        selected.update(active);marked.update(zip(active,active[1:]))
    for a,b in spec['edges']:
        points=edge_points(nodes[a],nodes[b]);color=GREEN if (a,b) in marked else GRID
        # Keep the final-response branch outside the tool node in this schematic.
        if a=='branch' and b=='done':
            aa=nodes[a];bb=nodes[b];points=[[aa['x']+aa['w'],aa['y']+aa['h']/2],[1145,aa['y']+aa['h']/2],[1145,bb['y']+bb['h']/2],[bb['x']+bb['w'],bb['y']+bb['h']/2]]
        poly(d,points,color,4 if (a,b) in marked else 2)
    for n in nodes.values():box(d,(n['x'],n['y'],n['w'],n['h']),n['label'],COLORS[n['color']],n['id'] in selected,size=27 if n['w']<220 else 29)
    a,b=active[leg:leg+2];points=edge_points(nodes[a],nodes[b]);poly(d,points,ORANGE,4);dot(d,along(points,local),RED if b=='deny' else ORANGE,10)
    if phase=='schedule' and route==0:
        branch=['start','b','join'];leg2=min(1,int(q*2));local2=q*2-leg2;dot(d,along(edge_points(nodes[branch[leg2]],nodes[branch[leg2+1]]),local2),BLUE,10)
    if q>=.999:
        n=nodes[active[-1]];box(d,(n['x'],n['y'],n['w'],n['h']),n['label'],COLORS[n['color']],True,size=27 if n['w']<220 else 29)
def sequence(d,phase,t):
    xs=[150,560,980]
    for x,label in zip(xs,['运行时','语言模型','工具执行器']):tx(d,(x,50),label,31,BLUE,'mt');line(d,(x,110),(x,630),GRID,3)
    labels=['任务与上下文','read_file / call-1','实际读取','结果 / call-1','包含结果的新上下文','run_tests / call-2','实际测试','结果 / call-2'] if phase=='round' else ['exit 1 / 错误位置','包含真实错误的新上下文','修正动作 / 请求等待']
    directions=[(0,1),(1,0),(0,2),(2,0),(0,1),(1,0),(0,2),(2,0)] if phase=='round' else [(2,0),(0,1),(1,0)]
    level=t*8 if phase=='round' else t*2 if t<=.5 else 1+(t-.5)*4
    for i,((a,b),label) in enumerate(zip(directions,labels)):
        y=150+i*(64 if phase=='round' else 155);color=GREEN if i<level else GRID;arrow(d,(xs[a],y),(xs[b],y),color,3);tx(d,((xs[a]+xs[b])/2,y-28),label,24 if phase=='round' else 27,TEXT if i<level else MUTED,'mt')
        if i<=level<i+1:dot(d,along([[xs[a],y],[xs[b],y]],level-i),ORANGE,10)
    if phase=='error':box(d,(215,575,730,70),'运行时按策略继续、等待或停止',ORANGE,t>=.99,30)
def contract(d,phase,t):
    box(d,(35,90,480,350),'',BLUE,t<.5 if phase=='schema' else t>.5);box(d,(630,90,490,350),'',ORANGE,t>=.5 if phase=='schema' else t<=.5)
    left=['工具定义','name: read_file','用途：读取指定文件','path: string','返回：内容或错误'] if phase=='schema' else ['原调用对象','tool: read_file','path: total.py','call_id: call-1']
    right=['调用对象','tool: read_file','path: total.py','call_id: call-1'] if phase=='schema' else ['工具结果','call_id: call-1','status: OK / ERROR','content: 实际返回内容']
    for x,rows in [(65,left),(660,right)]:
        for i,label in enumerate(rows):tx(d,(x,115+i*62),label,31 if i==0 else 29,BLUE if i==0 else TEXT,mono=i in [1,2] and 'path' in label)
    arrow(d,(525,260) if phase=='schema' else (620,260),(620,260) if phase=='schema' else (525,260),ORANGE,5);dot(d,(525+95*t if phase=='schema' else 620-95*t,260),ORANGE,10)
    y=510;box(d,(95,y,980,100),'参数结构校验 ≠ 操作授权 ≠ 业务成功',GREEN,t>=.5,32)
    tx(d,(580,650),'字段为通用教学简化，具体协议名称可能不同',24,MUTED,'mt')
def window(d,phase,t):
    labels=['用户目标','项目文件','历史日志','工具目录','工作笔记']
    for i,label in enumerate(labels):box(d,(40,80+i*105,300,80),label,PURPLE,i in [0,1,3],29)
    d.rounded_rectangle((600,80,1115,600),18,outline=ORANGE,width=4);tx(d,(857,95),'本轮上下文窗口',31,ORANGE,'mt')
    for i,label in enumerate(['必要约束','当前目标','可用工具','相关文件与最新错误']):
        x=640+(1-min(1,t*2))*(-190) if i<2 else 640+(1-max(0,(t-.5)*2))*(-190)
        y=180+i*90;box(d,(x,y,430,70),label,BLUE,True,27)
    tx(d,(600,625),'窗口容量与注意力都需要管理',27,GREEN)
    for i in range(2):
        q=min(1,t*2) if i==0 else max(0,(t-.5)*2);dot(d,along([[350,210+i*210],[470,210+i*210],[470,215+i*175],[620,215+i*175]],q),ORANGE)
def compact(d,phase,t):
    for i in range(9):
        x=30+min(1,t*2)*270;y=50+i*65+(280-(50+i*65))*min(1,t*2);w=280-100*min(1,t*2)
        d.rounded_rectangle((x,y,x+w,y+42),7,fill='#304259',outline=GRID,width=2)
    box(d,(410,180,310,285),'工作摘要\n目标 / 结果\n待办 / 引用',PURPLE,t>=.45,31)
    box(d,(860,180,250,285),'新窗口\n摘要 + 当前任务',ORANGE,t>=.95,29)
    arrow(d,(725,325),(850,325),BLUE);dot(d,(725+125*max(0,(t-.5)*2),325),ORANGE)
    tx(d,(580,605),'压缩有信息损失：关键结论必须能找回证据',28,GREEN,'mt')
def injection(d,phase,t):
    box(d,(30,80,320,130),'外部网页\n“改发外部地址”',RED,t<.5,29);box(d,(435,80,300,130),'读取内容\n保留来源',BLUE,t>=.3,29);box(d,(850,80,270,130),'模型上下文',PURPLE,t>=.48,29)
    box(d,(30,440,320,130),'用户目标与授权',GREEN,True,29);box(d,(435,440,300,130),'执行策略检查',ORANGE,t>=.5,29);box(d,(850,440,270,130),'拒绝并记录',GREEN,phase=='contain' and t>=.9,29)
    arrow(d,(350,145),(425,145),RED);arrow(d,(735,145),(840,145),BLUE);arrow(d,(350,505),(425,505),GREEN);arrow(d,(735,505),(840,505),GREEN)
    points=[[585,215],[585,430]];poly(d,points,RED,3)
    if t<=.5:dot(d,(350+75*t*2,145),RED)
    else:dot(d,along(points,(t-.5)*2),RED)
    if t>=.95 or phase=='contain':
        line(d,(555,320),(615,380),RED,7);line(d,(615,320),(555,380),RED,7)
    if phase=='contain':dot(d,(740+100*max(0,(t-.5)*2),505),GREEN)
    tx(d,(580,620),'数据通道不能自动升级为授权控制通道',29,ORANGE,'mt')
def retry(d,phase,t):
    if phase=='classify':
        labels=[('参数错误','返回可修正原因'),('权限拒绝','拒绝或等待授权'),('测试失败','反馈并修复'),('暂时网络故障','有限重试')]
        for i,(a,b) in enumerate(labels):
            x=10+i*287;box(d,(x,95,270,105),a,RED,t<.5,29);arrow(d,(x+135,210),(x+135,340),GREEN if i==3 and t>=.5 else GRID);box(d,(x,350,270,125),b,GREEN,i==3 and t>=.5,27)
        q=max(0,(t-.5)*2);tx(d,(580,565),'示意：有上限的重试与等待',31,ORANGE,'mt')
        if t<=.5:dot(d,(145+861*t*2,265),ORANGE,10)
        else:dot(d,(1006,210+130*q),ORANGE,10)
        for i in range(3):dot(d,(450+i*125,625),GREEN if q>=(i+1)/3 else GRID,18)
    else:
        for i,label in enumerate(['发送请求','服务可能已执行','回执丢失','状态未知']):box(d,(15+i*287,100,270,115),label,RED if i>=2 else BLUE,t*2>=i/3,28)
        for i in range(3):arrow(d,(285+i*287,155),(300+i*287,155),RED if i==2 else BLUE)
        if t<=.5:line(d,(145,250),(1015,250),GRID,3);dot(d,(145+870*t*2,250),ORANGE,10)
        box(d,(70,375,320,135),'逻辑操作 op-17\n稳定幂等标识',ORANGE,t>=.5,29);box(d,(480,375,320,135),'服务端查重\n返回既有结果',GREEN,t>=.75,29);box(d,(885,375,230,135),'实际副作用\n仍为 1 次',GREEN,t>=.95,29)
        arrow(d,(400,440),(470,440),BLUE);arrow(d,(810,440),(875,440),GREEN);dot(d,(400+475*max(0,(t-.5)*2),440),ORANGE)
        tx(d,(580,625),'关联请求的编号，不会自动提供所有服务的幂等性',27,MUTED,'mt')
def checkpoint(d,phase,t):
    labels=['已确认步骤','执行操作','记录完成','继续下一步']
    for i,label in enumerate(labels):
        selected=(i<=1 and t*2>=i/2) if phase=='save' else (i<=1 or t>.85)
        box(d,(10+i*287,85,270,100),label,BLUE,selected,28)
    box(d,(160,410,330,145),'持久检查点\n状态 / 待办 / 结果',PURPLE,t>=.25,29);box(d,(790,410,330,145),'外部实际状态\n副作用是否已发生？',ORANGE,phase=='reconcile',29)
    arrow(d,(430,200),(325,400),PURPLE)
    line(d,(700,45),(700,615),RED,5);tx(d,(700,30),'可能在这里中断',27,RED,'mt')
    if phase=='save':
        q=min(1,t*2);dot(d,along([[430,200],[430,300],[325,300],[325,400]],q),PURPLE)
        if t>=.5:
            box(d,(465,255,230,95),'恢复的运行状态',GREEN,True,27)
            points=[[490,485],[580,485],[580,355]];poly(d,points,GREEN,4);dot(d,along(points,(t-.5)*2),GREEN,10);tx(d,(580,595),'新进程：从已保存状态恢复',29,GREEN,'mt')
    else:
        q=min(1,t*2);dot(d,(780-270*q,485),ORANGE);arrow(d,(780,485),(505,485),ORANGE)
        if t>=.5:
            box(d,(405,255,370,100),'核对 → 去重 / 事务 / 补偿',GREEN,True,28)
            points=[[590,255],[590,220],[730,220],[730,190]];poly(d,points,GREEN,3);dot(d,along(points,(t-.5)*2),GREEN,10)
    tx(d,(580,650),'检查点与现实副作用之间存在需要处理的缝隙',27,MUTED,'mt')
def cancel(d,phase,t):
    box(d,(45,90,460,210),'本次运行\n轮数 / 时间 / 资源预算',BLUE,t<.95,31);box(d,(700,90,390,210),'停止条件\n阈值 / 取消信号',RED,t>=.95,31)
    d.rounded_rectangle((75,340,1095,385),12,fill='#26364a');d.rounded_rectangle((75,340,75+max(3,1020*t),385),12,fill=ORANGE)
    for i,label in enumerate(['正常完成','预算停止','用户取消']):box(d,(55+i*380,465,330,115),label,GREEN if i==0 else RED,t>=.95 and i==1,31)
    tx(d,(580,630),'预算为教学示意，不是产品默认值；取消不自动撤销提交',26,MUTED,'mt')
def case(d,phase,t):
    box(d,(25,75,720,265),'',BLUE,True);tx(d,(55,100),'total.py',28,BLUE)
    example=demo_data();source=example['initial'] if phase=='first' and t<=.65 else example['firstPatch']
    if phase=='repair' and t>.65:source=example['final']
    code=source.splitlines()[1].strip();tx(d,(55,170),source.splitlines()[0],35,TEXT,mono=True);tx(d,(90,230),code,35,ORANGE,mono=True)
    q=t*2 if t<=.5 else (t-.5)*2;d.rounded_rectangle((55,307,55+max(3,650*q),315),3,fill=ORANGE)
    box(d,(815,75,305,265),'输入：'+'、'.join(str(x) for x in example['input'])+'\n预期：'+str(example['expected']),PURPLE,True,32)
    labels=['读取原函数','提交第一版补丁','测试：等待执行'] if phase=='first' else ['测试失败：得到10','提交正确补丁','同一测试通过：30']
    for i,label in enumerate(labels):
        y=400+i*77;selected=(phase=='first' and (i==0 or i==1 and t>.65)) or (phase=='repair' and t>=i*.45)
        box(d,(90,y,990,64),label,RED if phase=='repair' and i==0 else GREEN,selected,29)
    tx(d,(580,650),'模型输出预设；文件修改和测试真实运行',27,MUTED,'mt')
def trace(d,phase,t):
    if phase in ['ledger','accept']:
        rows=[('call-1','读取文件','v0'),('call-2','第一版补丁','v1'),('call-3','测试失败：10','v1'),('call-4','正确补丁','v2'),('call-5','测试通过：30','v2')]
        tx(d,(55,45),'调用标识       外部事件与结果               文件版本',28,BLUE)
        limit=3 if phase=='ledger' else min(5,3+int(t*2.99))
        for i,(key,label,version) in enumerate(rows):
            y=105+i*92;color=RED if i==2 else GREEN
            box(d,(45,y,1070,75),'',color,i<limit,28);tx(d,(70,y+20),key,29,TEXT if i<limit else MUTED,mono=True);tx(d,(290,y+20),label if i<limit else '尚待确认',29,TEXT if i<limit else MUTED);tx(d,(990,y+20),version if i<limit else '?',29,PURPLE,mono=True)
        if phase=='accept' and t>=.95:tx(d,(580,615),'应用验收：测试通过 + 对应产物可核查',31,GREEN,'mt')
        dot(d,(65+1030*(t*5%1 if t<1 else 1),135+min(4,int(t*5))*92),ORANGE,8)
    else:
        spans=[('模型调用',.05,.25),('读取工具',.25,.37),('模型调用',.37,.59),('测试工具',.59,.88)]
        for i,(label,a,b) in enumerate(spans):
            y=90+i*115;tx(d,(20,y+10),label,30,BLUE);line(d,(260,y+30),(1115,y+30),GRID,2);end=260+855*(a+(b-a)*min(1,t*2))
            d.rounded_rectangle((260+855*a,y,end,y+60),8,fill=RED if phase=='inspect' and i==3 else '#367a9e')
        if t>=.5:box(d,(160,575,880,70),'关联标识 → 参数 → 原始结果 → 后续恢复动作',ORANGE,True,28)
        if t>=.5:dot(d,(180+830*(t-.5)*2,610),ORANGE,9)
        tx(d,(580,660),'时间条为教学比例，不表示厂商实测性能',24,MUTED,'mt')
def evaluate(d,phase,t):
    labels=['正常任务','错误参数','权限拒绝','超时与重复提交','中断后恢复'];heads=['输入场景','预期状态','副作用核查']
    for j,label in enumerate(heads):tx(d,(45+j*380,60),label,31,BLUE)
    for i,label in enumerate(labels):
        y=135+i*91;box(d,(25,y,340,70),label,BLUE,True,28)
        visible=i==0 or t>=.5 and max(0,(t-.5)*2)>=(i-1)/4
        for j,value in enumerate(['按策略继续 / 拒绝','与预期一致']):box(d,(405+j*380,y,340,70),value if visible else '待验证',GREEN,visible,26)
    dot(d,(390,170+min(1,t)*364),ORANGE,10)
    tx(d,(580,640),'回答质量只是一个维度；运行状态与产物也必须验收',27,ORANGE,'mt')
CODE=['state = load_checkpoint()','while within_budget(state):','    context = select_context(state)','    reply = model(context, tools)','    if reply.tool_calls:','        calls = validate_and_authorize(reply)','        results = execute(calls)','        append_and_checkpoint(state, results)','    elif application_accepts(reply, state):','        return completed(reply)','    else: return waiting_or_stopped(state)','return stopped(state)']
def code(d,phase,t):
    selected=range(0,4) if phase=='loop' and t<.5 else range(4,8) if phase=='loop' else range(8,12) if t<.5 else [5,6,7,8]
    for i,value in enumerate(CODE):
        y=70+i*44
        if i in selected:d.rounded_rectangle((15,y-2,1140,y+41),5,fill='#29374a');d.rectangle((16,y,21,y+38),fill=ORANGE)
        tx(d,(32,y+3),value,33,ORANGE if i in selected else TEXT,mono=True)
    indices=list(selected);q=t*2 if t<=.5 else (t-.5)*2;dot(d,(8,90+(indices[0]+q*(indices[-1]-indices[0]))*44),ORANGE,7)
    tx(d,(580,650),'控制流伪代码；生产实现还需异常、流式事件与资源管理',25,MUTED,'mt')
def summary(d,phase,t):
    box(d,(420,245,320,130),'运行时\n组织与约束',ORANGE,True,34);box(d,(420,45,320,100),'语言模型',BLUE,True,33)
    labels=['工具执行','权限检查','状态管理','恢复策略','验收证据'];positions=[(30,150),(30,460),(420,490),(850,460),(850,150)]
    for i,(x,y) in enumerate(positions):
        show=phase=='answer' and t>=(i/5);label=labels[i] if show else '?';b=dict(x=x,y=y,w=270,h=105);a=dict(x=420,y=245,w=320,h=130);poly(d,edge_points(a,b),GREEN if show else GRID,3);box(d,(x,y,270,105),label,GREEN,show,32)
    arrow(d,(580,150),(580,235),BLUE);dot(d,(580,150+85*t),ORANGE)
    tx(d,(580,650),'模型提出动作；运行时组织执行；证据支持验收',28,BLUE,'mt')
HANDLERS=dict(sequence=sequence,contract=contract,window=window,compact=compact,injection=injection,retry=retry,checkpoint=checkpoint,cancel=cancel,case=case,trace=trace,eval=evaluate,code=code,summary=summary)
BY={}
@functools.lru_cache(1)
def demo_data():return json.loads((ROOT/'build/demo-execution.json').read_text(encoding='utf8'))
def init(timeline):
    global BY;BY={s['key']:s for s in timeline['scenes']};base.cache_clear();demo_data.cache_clear()
def prepare_formulas(course):return None
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def state(s,frame):
    begun=[u for u in s['units'] if u['begin']<=frame];u=begun[-1] if begun else s['units'][0];p=0
    for m in u['motions']:
        if frame<m['begin']:break
        q=smooth((frame-m['begin'])/(m['end']-m['begin']));p=m['fromProgress']+(m['toProgress']-m['fromProgress'])*q
    return u['index'],p
@functools.lru_cache(48)
def base(key,index):
    s=BY[key];p=s['parts'][index];im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
    d.rounded_rectangle((60,215,1245,925),18,fill=PANEL,outline=GRID,width=2);d.rounded_rectangle((1280,215,1860,925),18,fill=PANEL,outline=GRID,width=2)
    tx(d,(64,36),f'Agent Harness · {s["chapterIndex"]:02}',25,ORANGE);tx(d,(1850,40),'15分钟底层原理 · 原创动态示意',23,MUTED,'rt');tx(d,(64,88),s['chapter'],46);tx(d,(64,158),s['title'],29,BLUE)
    tx(d,(1310,245),'当前机制',27,ORANGE);y=310
    for note in p['notes']:
        tx(d,(1310,y),'•',28,ORANGE);y=wrap(d,note,1342,y,480,29)+26
    assert y<750,('Sidebar overflow',key,index,y)
    tx(d,(1310,735),'图中状态与数值为教学示意',23,MUTED);tx(d,(1310,777),'不表示隐藏推理或厂商性能',23,MUTED);tx(d,(65,947),f'本章第 {s["sceneIndex"]} 页',19,MUTED)
    return im
def cover():
    im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im);tx(d,(85,70),'模型、工具、上下文与控制循环',31,ORANGE);tx(d,(76,150),'Agent Harness',122);tx(d,(85,320),'15分钟 · 底层原理',83,ORANGE)
    topics=list(dict.fromkeys(s['chapter'] for s in BY.values()))
    for i,label in enumerate(topics):x=90+i//5*910;y=555+i%5*76;dot(d,(x,y+20),ORANGE,8);tx(d,(x+30,y),label,34)
    return im
def render(s,frame):
    index,t=state(s,frame);p=s['parts'][index];v=p['visual']
    if v['kind']=='cover':return cover()
    im=base(s['key'],index).copy();canvas=Image.new('RGB',(1165,690),PANEL);d=ImageDraw.Draw(canvas);spec=graph_for(v['kind'],v['phase'])
    if spec:graph(d,spec,v['phase'],t)
    else:HANDLERS[v['kind']](d,v['phase'],t)
    im.paste(canvas,(70,225));d=ImageDraw.Draw(im)
    for interval in s.get('thinkIntervals',[]):
        if interval['begin']<=frame<interval['end']:
            count=math.ceil((interval['end']-frame)/30);question=p['visual'].get('question','先预测，再看后面的状态')
            d.rounded_rectangle((1305,820,1835,905),12,fill='#183f50',outline=BLUE,width=2);tx(d,(1330,840),'思考 '+str(count),31,BLUE);wrap(d,question,1435,838,370,22,line=29)
    return im
