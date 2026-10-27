"""Original mathematical diagrams, with explicit geometry and continuous authored progress."""
import functools,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
BG='#10243a';TEXT='#eff5ff';BLUE='#70cfff';ORANGE='#ffbd68';GREEN='#8fe0b2';RED='#ff929c';GRID='#33506a';MUTED='#a2b7cc'
@functools.lru_cache(32)
def font(size):return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size)
def txt(d,p,s,size=25,color=TEXT,anchor='lt'):d.text(tuple(p),str(s),font=font(size),fill=color,anchor=anchor)
def ln(d,a,b,color=BLUE,w=3):d.line([tuple(a),tuple(b)],fill=color,width=w)
def dot(d,p,color=ORANGE,r=6):d.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=color)
def arrow(d,a,b,color=ORANGE,w=4):
    a=np.array(a,float);b=np.array(b,float);v=b-a;length=np.linalg.norm(v)
    if length<2:return
    ln(d,a,b,color,w);v/=length;q=np.array([-v[1],v[0]]);d.polygon([tuple(b),tuple(b-12*v+6*q),tuple(b-12*v-6*q)],fill=color)
def path(d,points,color=BLUE,w=3):
    if len(points)>1:d.line([tuple(p) for p in points],fill=color,width=w)
def axes(d,origin=(160,265),scale=200,xmax=1.6,ymax=1.1):
    def p(x,y):return np.array([origin[0]+scale*x,origin[1]-scale*y])
    arrow(d,p(-.15,0),p(xmax,0),MUTED,2);arrow(d,p(0,-.1),p(0,ymax),MUTED,2);txt(d,p(xmax,0)+[6,0],'x',21);txt(d,p(0,ymax)+[0,-22],'y',21)
    return p
def proj(center=(360,215),scale=55):
    def p(x,y=None,z=None):
        a=np.asarray(x if y is None else [x,y,z],float);return np.array(center)+scale*np.array([.85*a[0]-.85*a[1],.34*a[0]+.34*a[1]-.85*a[2]])
    return p
def axes3(d,p,L=2):
    o=p([0,0,0])
    for i,label in enumerate(['x','y','z']):
        v=np.zeros(3);v[i]=L;arrow(d,o,p(v),MUTED,2);txt(d,p(v)+[6,-12],label,21)
def sphere(d,p,R=1,upper=False,color=GRID):
    for phi in np.linspace(.13,math.pi/2 if upper else math.pi-.13,8):path(d,[p([R*math.sin(phi)*math.cos(a),R*math.sin(phi)*math.sin(a),R*math.cos(phi)]) for a in np.linspace(0,2*math.pi,65)],color,2)
    for a in np.linspace(0,2*math.pi,12,endpoint=False):path(d,[p([R*math.sin(f)*math.cos(a),R*math.sin(f)*math.sin(a),R*math.cos(f)]) for f in np.linspace(0,math.pi/2 if upper else math.pi,45)],color,2)
def mesh(d,p,f):
    for fixed in np.linspace(-1,1,9):
        path(d,[p([u,fixed,f(u,fixed)]) for u in np.linspace(-1,1,35)],BLUE,2);path(d,[p([fixed,u,f(fixed,u)]) for u in np.linspace(-1,1,35)],BLUE,2)
def note(d,a,b=''):
    y=60
    for value,size,color in [(a,27,ORANGE),(b,24,MUTED)]:
        row=''
        for ch in value:
            if row and font(size).getlength(row+ch)>420:txt(d,(720,y),row,size,color);y+=38;row=''
            row+=ch
        if row:txt(d,(720,y),row,size,color);y+=52
    assert y<302,('Diagram note overflow',a,b)
def vectors(d,phase,t):
    p=proj((355,230),62);axes3(d,p,2.8);a=np.array([1,2,2]);arrow(d,p([0,0,0]),p(a*(t if phase=='first' else 1)),BLUE,5)
    if phase=='unit':arrow(d,p([0,0,0]),p(a*t/3),ORANGE,6);note(d,'单位向量长度：1','原向量长度：3')
    else:dot(d,p(a*t));note(d,'位移：(1, 2, 2)','蓝色向量从原点出发')
def cross(d,phase,t):
    p=proj((360,215),62);axes3(d,p,2.6);a=np.array([1,0,0]);b=np.array([0,2,0]);c=np.array([0,0,3]);zero=np.zeros(3)
    d.polygon([tuple(p(q)) for q in [zero,a,a+b,b]],fill='#224a59');arrow(d,p(zero),p(a),BLUE);arrow(d,p(zero),p(b),GREEN)
    if phase=='area':arrow(d,p(zero),p([0,0,2*t]),ORANGE,5);note(d,'平行四边形面积：2','橙色：a × b')
    else:
        for q in [zero,a,b,a+b]:ln(d,p(q),p(q+c*t),ORANGE)
        for q,q2 in [(zero,a),(a,a+b),(a+b,b),(b,zero)]:ln(d,p(q+c*t),p(q2+c*t),ORANGE)
        note(d,'底面积2 × 高3','体积：6')
def quadrics(d,phase,t):
    if phase=='sphere':
        p=proj((270,175),48);sphere(d,p,2);dot(d,p([2*math.cos(t*2*math.pi),2*math.sin(t*2*math.pi),0]));txt(d,(190,270),'球：半径2',23)
        p=proj((845,225),52)
        for z in [0,1,2.4]:path(d,[p([math.cos(a),math.sin(a),z]) for a in np.linspace(0,2*math.pi,65)],BLUE)
        for a in np.linspace(0,2*math.pi,10):ln(d,p([math.cos(a),math.sin(a),0]),p([math.cos(a),math.sin(a),2.4]),GRID,2)
        dot(d,p([1,0,2.4*t]));txt(d,(760,270),'柱：z方向延伸',23)
    else:
        for center,f,label in [((270,155),lambda x,y:.8*(x*x+y*y),'平方和：碗形'),((845,155),lambda x,y:.7*(x*x-y*y),'平方差：马鞍形')]:
            p=proj(center,70);mesh(d,p,f);u=-1+2*t;dot(d,p([u,0,f(u,0)]));txt(d,(center[0]-110,270),label,24)
def domain(d,phase,t):
    cx,cy,R=330,155,118;d.ellipse((cx-R,cy-R,cx+R,cy+R),fill='#193345',outline=BLUE,width=3)
    pts=[(cx,cy)]+[(cx+R*math.cos(a),cy-R*math.sin(a)) for a in np.linspace(-3*math.pi/4,math.pi/4,70)];d.polygon(pts,fill='#2a5c60')
    ln(d,(cx-R*1.05,cy+R*1.05),(cx+R*1.05,cy-R*1.05),RED,3);a=-3*math.pi/4+math.pi*t;dot(d,(cx+R*math.cos(a),cy-R*math.sin(a)),ORANGE)
    if phase=='boundary':dot(d,(cx+(2*t-1)*R*.7,cy-(2*t-1)*R*.7),RED,7)
    note(d,'圆盘与开半平面的交集','蓝圆周可取；红斜线不取')
def paths(d,phase,t):
    p=axes(d,(225,255),190,1.65,1.1);value=.95-.9*t
    if phase=='axis':ln(d,p(0,0),p(1.25,0),BLUE,5);dot(d,p(value,0));note(d,'沿y=0：函数值0','靠近同一个原点')
    else:ln(d,p(0,0),p(1,1),ORANGE,5);dot(d,p(value,value));note(d,'沿y=x：函数值1/2','两条路径结果不同')
def chain(d,phase,t):
    boxes=[(35,115,180,70,'t'),(360,30,260,70,'x=t'),(360,220,260,70,'y=t²'),(900,115,230,70,'z=x²+y²')]
    for x,y,w,h,label in boxes:d.rounded_rectangle((x,y,x+w,y+h),12,fill='#1d3a50',outline=BLUE,width=3);txt(d,(x+w/2,y+h/2),label,30,TEXT,'mm')
    lines=[[(215,150),(290,150),(290,65),(360,65)],[(215,150),(290,150),(290,255),(360,255)],[(620,65),(760,65),(760,150),(900,150)],[(620,255),(760,255),(760,150),(900,150)]]
    for i,pts in enumerate(lines):path(d,pts,GREEN if i<2 and (phase=='merge' or t>=.999) or phase=='merge' and t>=.999 else GRID,3)
    for j in range(2):
        pts=lines[j if phase=='branches' else j+2];lens=[np.linalg.norm(np.array(b)-a) for a,b in zip(pts,pts[1:])];q=t*sum(lens)
        point=np.array(pts[-1])
        for a,b,L in zip(pts,pts[1:],lens):
            if q<=L+1e-6:point=np.array(a)+(np.array(b)-a)*min(1,q/max(L,1));break
            q-=L
        dot(d,point,ORANGE if j==0 else GREEN)
def tangent(d,phase,t):
    p=proj((345,205),30);sphere(d,p,3);M=np.array([1,2,2]);n=M/3;u=np.array([2,-1,0])/math.sqrt(5);v=np.cross(n,u)
    corners=[M+a*u+b*v for a,b in [(-1,-1),(-1,1),(1,1),(1,-1)]];d.polygon([tuple(p(q)) for q in corners],fill='#325d66');path(d,[p(q) for q in corners+[corners[0]]],GREEN,3)
    arrow(d,p(M),p(M+n*(2*t if phase=='normal' else 2)),ORANGE,5);dot(d,p(M+n*(-.7+2*t)))
    note(d,'法向：(1, 2, 2)','切平面与法线在指定点相交')
def gradient(d,phase,t):
    p=axes(d,(190,255),110,3.5,1.8);M=np.array([1,1]);angle=math.atan2(4,3) if phase=='given' else math.atan2(4,3)+(math.atan2(4,2)-math.atan2(4,3))*t
    q=M+np.array([math.cos(angle),math.sin(angle)])*(1.4*t if phase=='given' else 1.4);arrow(d,p(*M),p(*q),ORANGE,5);dot(d,p(*M),GREEN)
    note(d,'先单位化，再与梯度点乘','橙色：选定的单位方向')
def extrema(d,kind,phase,t):
    p=proj((360,175),93);saddle=kind=='degenerate' and phase=='saddle';quartic=kind=='degenerate';f=(lambda x,y:.5*(x**4-y**4)) if saddle else (lambda x,y:.55*(x**4+y**4)) if quartic else (lambda x,y:.55*(x*x+y*y));mesh(d,p,f)
    u=-1+2*t;dot(d,p([u,0,f(u,0)]),ORANGE);dot(d,p([0,u,f(0,u)]),GREEN)
    note(d,'鞍点：附近有增有减' if saddle else '最低点：比较附近函数值','图示高度相对候选点；具体坐标见上式')
def disk_extreme(d,phase,t):
    p=axes(d,(350,165),110,1.5,1.3);pts=[p(math.cos(a),math.sin(a)) for a in np.linspace(0,2*math.pi,80)];d.polygon([tuple(q) for q in pts],fill='#1d3d50');path(d,pts+[pts[0]],BLUE)
    a=2*math.pi*t if phase=='disk' else -math.pi/2+3*math.pi*t/4;q=np.array([math.cos(a),math.sin(a)]);dot(d,p(*q));arrow(d,p(0,0),p(1.15/math.sqrt(2),1.15/math.sqrt(2)),GREEN)
    note(d,'边界上：x+y='+f'{sum(q):.3f}','最大值√2；最低点取相反方向')
def region(d,kind,phase,t):
    rectangle=kind=='rectangle';p=axes(d,(180,265),100 if rectangle else 210,2.8 if rectangle else 1.8,2.2 if rectangle else 1.1)
    points=[(0,0),(1,0),(1,2),(0,2)] if rectangle else [(0,0),(1,0),(1,1)] if kind=='swap' else [(0,0),(1,0),(0,1)]
    d.polygon([tuple(p(*q)) for q in points],fill='#214e5c');path(d,[p(*q) for q in points+[points[0]]],BLUE)
    v=.03+.94*t
    if rectangle:a,b=p(v,0),p(v,2)
    elif kind=='swap' and phase=='horizontal':a,b=p(v,v),p(1,v)
    elif kind=='swap':a,b=p(v,0),p(v,v)
    else:a,b=p(v,0),p(v,1-v)
    ln(d,a,b,ORANGE,5);dot(d,(a+b)/2,GREEN)
    note(d,'先固定外层变量，读内层范围','同一区域可用不同方向的切片')
def polar(d,phase,t):
    center=np.array([330,155]);R=122;d.ellipse((208,33,452,277),fill='#173c4f',outline=BLUE,width=3)
    angle=2*math.pi*t if phase=='sector' else math.pi/4;radius=R if phase=='sector' else R*t
    pts=[center]+[center+R*np.array([math.cos(a),-math.sin(a)]) for a in np.linspace(0,angle,65)];d.polygon([tuple(q) for q in pts],fill='#265963');end=center+radius*np.array([math.cos(angle),-math.sin(angle)]);arrow(d,center,end,ORANGE);dot(d,end)
    note(d,'面积元：r dr dθ','方位角扫区域，半径走上下界')
def solid(d,kind,phase,t):
    p=proj((350,220),70)
    if kind=='box3':
        corners=[np.array([a,b,c]) for a in [0,1] for b in [0,2] for c in [0,3]]
        for i,a in enumerate(corners):
            for b in corners[i+1:]:
                if np.count_nonzero(a-b)==1:ln(d,p(a),p(b),BLUE,2)
        z=3*t;pts=[p(q) for q in [[0,0,z],[1,0,z],[1,2,z],[0,2,z],[0,0,z]]];path(d,pts,ORANGE,4);note(d,'长方体：1 × 2 × 3','橙色：当前水平切片')
    elif kind=='tetra3':
        p=proj((350,220),140);corners=[np.array(q,float) for q in [[0,0,0],[1,0,0],[0,1,0],[0,0,1]]]
        for i,a in enumerate(corners):
            for b in corners[i+1:]:ln(d,p(a),p(b),BLUE,2)
        z=t;pts=[p(q) for q in [[0,0,z],[1-z,0,z],[0,1-z,z],[0,0,z]]];path(d,pts,ORANGE,4);note(d,'四面体的水平截面逐渐缩小','x+y+z≤1，三个坐标均非负')
    elif kind=='cylinder3':
        for z in [0,2]:path(d,[p([math.cos(a),math.sin(a),z]) for a in np.linspace(0,2*math.pi,65)],BLUE)
        for a in np.linspace(0,2*math.pi,12):ln(d,p([math.cos(a),math.sin(a),0]),p([math.cos(a),math.sin(a),2]),GRID,2)
        z=2*t if phase=='height' else 0;angle=2*math.pi*t if phase=='base' else math.pi/3;dot(d,p([math.cos(angle),math.sin(angle),z]));note(d,'圆盘底面 + 高度','柱坐标体积元额外乘r')
    else:
        p=proj((350,165),56);sphere(d,p,2);phi=math.pi*t if phase=='angle' else math.pi/3;R=2 if phase=='angle' else 2*t;q=[R*math.sin(phi),0,R*math.cos(phi)];arrow(d,p([0,0,0]),p(q),ORANGE,4);dot(d,p(q));note(d,'极角从正z轴量起','完整球：极角0～π，方位角0～2π')
def curve(d,kind,phase,t):
    p=axes(d,(345,165),112,1.5,1.3);end=math.pi if kind=='semicircle' else 2*math.pi;angles=np.linspace(0,end,121);path(d,[p(math.cos(a),math.sin(a)) for a in angles],GRID,3)
    a=end*t;path(d,[p(math.cos(a),math.sin(a)) for a in np.linspace(0,a,100)],BLUE,4);q=p(math.cos(a),math.sin(a));dot(d,q);arrow(d,q,q+np.array([-math.sin(a),-math.cos(a)])*38,ORANGE,3)
    note(d,'弧长元ds：方向反转不变' if kind=='semicircle' else '逆时针：参数t递增','第一类看弧长；第二类看坐标微分')
def green(d,phase,t):
    p=axes(d,(345,165),112,1.5,1.3);pts=[p(math.cos(a),math.sin(a)) for a in np.linspace(0,2*math.pi,121)];d.polygon([tuple(q) for q in pts],fill='#1a3f4f');path(d,pts,BLUE,4)
    if phase=='boundary':a=2*math.pi*t;q=p(math.cos(a),math.sin(a));dot(d,q);arrow(d,q,q+np.array([-math.sin(a),-math.cos(a)])*35,ORANGE)
    else:x=-.98+1.96*t;y=math.sqrt(max(0,1-x*x));ln(d,p(x,-y),p(x,y),ORANGE,5)
    note(d,'边界方向：区域始终在左侧','外边界逆时针，内孔边界顺时针')
def surface(d,kind,phase,t):
    p=proj((370,240),112);axes3(d,p,1.4);corners=[np.array([x,y,x+y]) for x,y in [(0,0),(1,0),(1,1),(0,1)]];d.polygon([tuple(p(q)) for q in corners],fill='#234c57');path(d,[p(q) for q in corners+[corners[0]]],BLUE,3)
    for v in np.linspace(0,1,7):ln(d,p([v,0,v]),p([v,1,v+1]),GRID,2);ln(d,p([0,v,v]),p([1,v,v+1]),GRID,2)
    M=np.array([.5,.5,1]);base=np.array([.5,.5,0]);ln(d,p(base),p(M),MUTED,2)
    if kind=='surface_patch':dot(d,p(base+(M-base)*t));note(d,'曲面面积：√3','投影面积：1')
    else:
        arrow(d,p(M),p(M+np.array([-1,-1,1])*(t if phase=='up' else 1)*.55),ORANGE,4);arrow(d,p(M),p(M+np.array([0,0,.8])),BLUE,4)
        if phase=='flux':dot(d,p(M+np.array([0,0,.8*t])),BLUE)
        note(d,'橙色：上侧法向','蓝色：竖直向量场')
def closed_surface(d,kind,phase,t):
    p=proj((345,175),112);sphere(d,p,1,upper=kind in ['cap_disk','stokes']);a=2*math.pi*t
    if kind=='stokes':
        circle=[p([math.cos(q),math.sin(q),0]) for q in np.linspace(0,2*math.pi,81)];d.polygon([tuple(q) for q in circle],fill='#234c57');path(d,circle,BLUE,3);q=p([math.cos(a),math.sin(a),0]);dot(d,q);arrow(d,p([0,0,0]),p([0,0,.8]),ORANGE,4);note(d,'上侧法向配逆时针边界','同一边界可选择平圆盘计算')
    elif kind=='cap_disk':
        circle=[p([math.cos(q),math.sin(q),0]) for q in np.linspace(0,2*math.pi,81)];d.polygon([tuple(q) for q in circle],fill='#234c57');path(d,circle,ORANGE,3);arrow(d,p([0,0,0]),p([0,0,-(.4+.5*t)]),ORANGE,5);arrow(d,p([.6,0,.8]),p([.6,0,1.4]),BLUE,4);note(d,'补面外法向：向下','原面 = 闭合整体 − 补面')
    else:
        for phi in [math.pi/4,math.pi/2,3*math.pi/4]:
            angle=a if phase=='outward' else math.pi/3;q=np.array([math.sin(phi)*math.cos(angle),math.sin(phi)*math.sin(angle),math.cos(phi)]);arrow(d,p(q),p(q*1.55),ORANGE,3)
        if phase=='volume':
            z=-.97+1.94*t;R=math.sqrt(max(0,1-z*z));path(d,[p([R*math.cos(q),R*math.sin(q),z]) for q in np.linspace(0,2*math.pi,65)],GREEN,4);dot(d,p([0,0,z]),GREEN)
        note(d,'闭合曲面采用外法向','散度在内部体积上积分')
def partial_sums(d,phase,t):
    for center,label,values,color in [(85,'等比部分和',np.cumsum([.5**n for n in range(1,26)]),BLUE),(645,'调和部分和',np.cumsum([1/n for n in range(1,26)]),ORANGE)]:
        txt(d,(center,5),label,25,color);pts=[np.array([center+15+i*17,270-48*v]) for i,v in enumerate(values)];path(d,pts,GRID,2)
        progress=1 if center==85 and phase=='harmonic' else 0 if center==645 and phase=='partial' else t
        N=1+23*progress;last=min(23,int(N));path(d,pts[:last+1],color,3);dot(d,pts[last]+(pts[last+1]-pts[last])*(N-last),color);txt(d,(center+180,285),'N →',20,MUTED)
def alternating(d,phase,t):
    N=1+int(24*t) if phase=='alternate' else 5+int(95*t);values=np.cumsum([(-1)**(n-1)/n for n in range(1,N+1)]);scale=190
    ln(d,(80,80),(1100,80),GRID,1);ln(d,(80,260-math.log(2)*scale),(1100,260-math.log(2)*scale),GREEN,2)
    pts=[(90+i*min(35,930/max(N,1)),260-v*scale) for i,v in enumerate(values)];path(d,pts,BLUE,3);dot(d,pts[-1]);txt(d,(780,20),'N = '+str(N),28,ORANGE)
    if phase=='error':
        err=1/(N+1);yy=260-values[-1]*scale;d.rectangle((75,yy-err*scale,1100,yy+err*scale),outline=ORANGE,width=2);txt(d,(775,65),'误差 ≤ 1/'+str(N+1),26,ORANGE)
def interval(d,phase,t):
    def p(x):return (180+140*(x+2),165)
    arrow(d,p(-2),p(4.7),MUTED,2);ln(d,p(-1),p(3),BLUE,8)
    for x in [-1,1,3]:ln(d,(p(x)[0],155),(p(x)[0],175),TEXT,2);txt(d,(p(x)[0],198),str(x),26,TEXT,'mt')
    if phase=='radius':dot(d,p(1+2*t));ln(d,p(1),p(1+2*t),ORANGE,4);txt(d,(490,55),'中心1，半径2',28,ORANGE)
    else:
        for x,closed in [(-1,t>=.35),(3,False)]:
            q=p(x);d.ellipse((q[0]-10,q[1]-10,q[0]+10,q[1]+10),fill=GREEN if closed else BG,outline=GREEN if closed else RED,width=3)
        dot(d,(p(-1)[0]+(p(3)[0]-p(-1)[0])*t,235),ORANGE);txt(d,(430,50),'端点必须分别代回原级数',28,ORANGE)
def taylor(d,phase,t):
    if phase=='taylor':
        def p(x,y):return (330+150*x,270-40*y)
        xs=np.linspace(-1.25,1.25,200);path(d,[p(x,math.exp(x*x)) for x in xs],GRID,4);N=1+int(4*t);ys=[sum(x**(2*k)/math.factorial(k) for k in range(N+1)) for x in xs];path(d,[p(x,y) for x,y in zip(xs,ys)],BLUE,3);v=-1.2+2.4*t;dot(d,p(v,sum(v**(2*k)/math.factorial(k) for k in range(N+1))));note(d,'e的x²次方：偶次幂展开','蓝色：有限阶多项式；灰色：原函数')
    else:
        def f(x):return (math.expm1(x)-x)/(x*x)
        def p(x,y):return (150+x*550,260-(y-.25)*370)
        xs=np.linspace(.001,1.25,180);path(d,[p(x,f(x)) for x in xs],BLUE,3);ln(d,p(0,.5),p(1.25,.5),GREEN,2);v=1.2*(1-t)+.001;dot(d,p(v,f(v)));txt(d,(825,90),'x → 0',29,ORANGE);txt(d,(825,145),'极限 1/2',29,GREEN)
def fourier(d,phase,t):
    def p(x,y):return (580+150*x,155-35*y)
    for shift in [-2*math.pi,0,2*math.pi]:path(d,[p(-math.pi+shift,-math.pi),p(math.pi+shift,math.pi)],GRID,3)
    xs=np.linspace(-math.pi,math.pi,450);N=1+int(11*t) if phase=='fourier' else 18;ys=np.zeros_like(xs)
    for n in range(1,N+1):ys+=2*(-1)**(n+1)*np.sin(n*xs)/n
    path(d,[p(x,y) for x,y in zip(xs,ys)],BLUE,3);v=-math.pi+2*math.pi*t;value=sum(2*(-1)**(n+1)*math.sin(n*v)/n for n in range(1,N+1));dot(d,p(v,value));txt(d,(70,8),'部分和：'+str(N)+'项',25,ORANGE)
    if phase=='jump':dot(d,p(math.pi,0),GREEN,8);txt(d,(785,270),'跳跃点的和：0',24,GREEN)
def render(spec,phase,t):
    t=max(0,min(1,t));im=Image.new('RGB',(1165,310),BG);d=ImageDraw.Draw(im);kind=spec['kind']
    if kind=='vectors3':vectors(d,phase,t)
    elif kind=='cross3':cross(d,phase,t)
    elif kind=='quadrics':quadrics(d,phase,t)
    elif kind=='domain':domain(d,phase,t)
    elif kind=='paths':paths(d,phase,t)
    elif kind=='chain':chain(d,phase,t)
    elif kind=='tangent3':tangent(d,phase,t)
    elif kind=='gradient':gradient(d,phase,t)
    elif kind in ['extrema','degenerate']:extrema(d,kind,phase,t)
    elif kind=='disk_extreme':disk_extreme(d,phase,t)
    elif kind in ['rectangle','triangle','swap']:region(d,kind,phase,t)
    elif kind=='polar':polar(d,phase,t)
    elif kind in ['box3','tetra3','cylinder3','sphere3']:solid(d,kind,phase,t)
    elif kind in ['semicircle','circle_orientation']:curve(d,kind,phase,t)
    elif kind=='green':green(d,phase,t)
    elif kind in ['surface_patch','surface_flux']:surface(d,kind,phase,t)
    elif kind in ['gauss','cap_disk','stokes']:closed_surface(d,kind,phase,t)
    elif kind=='partial_sums':partial_sums(d,phase,t)
    elif kind=='alternating':alternating(d,phase,t)
    elif kind=='interval':interval(d,phase,t)
    elif kind=='taylor':taylor(d,phase,t)
    elif kind=='fourier':fourier(d,phase,t)
    else:raise ValueError(kind)
    return im
