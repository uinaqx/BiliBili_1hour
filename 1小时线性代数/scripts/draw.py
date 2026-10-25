"""Original mathematical diagrams. Every motion frame recomputes the displayed geometry."""
import functools,hashlib,io,itertools,json,math,pathlib,re
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path(__file__).resolve().parents[1]
BG='#09172a';PANEL='#10243a';TEXT='#eff5ff';MUTED='#9fb2ca';BLUE='#70cfff';ORANGE='#ffbd68';GREEN='#8fe0b2';RED='#ff929c';PURPLE='#c6abff';GRID='#25435e'
@functools.lru_cache(32)
def font(size,mathfont=False):return ImageFont.truetype('C:/Windows/Fonts/cambria.ttc' if mathfont else 'C:/Windows/Fonts/msyh.ttc',size)
def tx(d,p,text,size=32,color=TEXT,anchor='lt',mathfont=False):
    text=str(text).translate(str.maketrans({'₁':'1','₂':'2','₃':'3','ᵀ':'^T','⁻':'^-','¹':'1'}))
    d.text(tuple(map(float,p)),text,font=font(size,mathfont),fill=color,anchor=anchor)
def number(x):
    if isinstance(x,str):return x
    if abs(float(x))<.005:return '0'
    if abs(float(x)-round(float(x)))<1e-7:return str(int(round(float(x))))
    return f'{float(x):.2f}'.rstrip('0').rstrip('.')
def coords(a):return '('+', '.join(number(x) for x in a)+')'
def wrap(d,text,x,y,width,size=28,color=TEXT,line=41):
    row=''
    for ch in text:
        if font(size).getlength(row+ch)>width and row:tx(d,(x,y),row,size,color);y+=line;row=''
        row+=ch
    if row:tx(d,(x,y),row,size,color);y+=line
    return y
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
def line(d,a,b,color=BLUE,width=3):d.line([tuple(a),tuple(b)],fill=color,width=width)
def arrow(d,a,b,color=BLUE,width=5,label=None):
    a=np.array(a,float);b=np.array(b,float);delta=b-a;length=np.linalg.norm(delta)
    if length<2:
        d.ellipse((b[0]-4,b[1]-4,b[0]+4,b[1]+4),fill=color)
        if label:tx(d,b+[12,12],label+' → 0',25,color)
        return
    line(d,a,b,color,width);v=delta/length;perp=np.array([-v[1],v[0]])
    pts=[b,b-15*v+7*perp,b-15*v-7*perp];d.polygon([tuple(x) for x in pts],fill=color)
    if label:tx(d,b+np.array([10,-28]),label,29,color)
def dot(d,p,color=GREEN,r=7):d.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=color)
def graph(d,origin=(570,350),scale=85,lim=4):
    o=np.array(origin,float)
    def p(x):return o+np.array([float(x[0]),-float(x[1])])*scale
    for k in range(-lim,lim+1):
        line(d,p((k,-lim)),p((k,lim)),GRID,1);line(d,p((-lim,k)),p((lim,k)),GRID,1)
    arrow(d,p((-lim,0)),p((lim,0)),MUTED,2);arrow(d,p((0,-lim)),p((0,lim)),MUTED,2)
    tx(d,p((lim,0))+[3,10],'x',24,MUTED);tx(d,p((0,lim))+[10,0],'y',24,MUTED);tx(d,o+[10,10],'0',22,MUTED)
    if scale>=45:
        for k in range(-lim,lim+1):
            if k:tx(d,p((k,0))+[0,9],str(k),18,MUTED,'mt')
    return p
def matrix(d,A,center=(570,310),size=48,cell=88,row=76,colors=None,split=None,label=None):
    A=np.array(A,dtype=object);m,n=A.shape;x=center[0]-n*cell/2;y=center[1]-m*row/2
    if label:tx(d,(center[0],y-48),label,30,ORANGE,'mt')
    for i in range(m):
        for j in range(n):
            if colors and (i,j) in colors:d.rounded_rectangle((x+j*cell+2,y+i*row+2,x+(j+1)*cell-2,y+(i+1)*row-2),radius=7,fill=colors[i,j])
            tx(d,(x+(j+.5)*cell,y+(i+.5)*row),number(A[i,j]),size,TEXT,'mm',True)
    for xx,sgn in [(x-14,1),(x+n*cell+14,-1)]:
        d.line([(xx+sgn*12,y),(xx,y),(xx,y+m*row),(xx+sgn*12,y+m*row)],fill=MUTED,width=3)
    if split:line(d,(x+split*cell,y),(x+split*cell,y+m*row),ORANGE,3)
    return x,y,cell,row
def formula_path(text):return ROOT/'build/formulas'/(hashlib.sha256(('alpha-v2'+text).encode()).hexdigest()+'.png')
def prepare_formulas(course):
    import matplotlib;matplotlib.use('Agg')
    from matplotlib import mathtext,font_manager,rcParams
    rcParams.update({'mathtext.fontset':'custom','mathtext.rm':'Microsoft YaHei','mathtext.it':'DejaVu Sans:italic','mathtext.bf':'DejaVu Sans:bold','mathtext.fallback':'stix'})
    folder=ROOT/'build/formulas';folder.mkdir(exist_ok=True);warnings=[];failures=[]
    formulas=sorted(set(f for c in course['chapters'] for s in c['scenes'] for p in s['parts'] for f in p['formulas']))
    for text in formulas:
        path=formula_path(text)
        if not path.exists():
            parsed=re.sub(r'\\(le|ge|ne)(?![A-Za-z])',lambda m:'\\'+dict(le='leq',ge='geq',ne='neq')[m[1]],text).replace(r'\iff',r'\Leftrightarrow')
            parsed=re.sub(r'\\frac([0-9])',r'\\frac{\1}',parsed);parsed=re.sub(r'\\sqrt([0-9])',r'\\sqrt{\1}',parsed)
            try:
                raster=mathtext.MathTextParser('agg').parse('$'+parsed+'$',prop=font_manager.FontProperties(size=24),dpi=144)
                alpha=np.asarray(raster.image,dtype=np.uint8);pixels=np.empty((*alpha.shape,4),dtype=np.uint8);pixels[:,:,:3]=[239,245,255];pixels[:,:,3]=alpha
            except ValueError as e:failures.append(dict(formula=text,error=str(e)));continue
            Image.fromarray(pixels).save(path)
        with Image.open(path) as im:
            scale=min(1,510/im.width,88/im.height)
            if scale<.65:warnings.append(dict(formula=text,width=im.width,height=im.height,scale=scale))
    (ROOT/'build/formula-review.json').write_text(json.dumps(dict(formulas=len(formulas),small=warnings),ensure_ascii=False,indent=2),encoding='utf8')
    print('FORMULAS_READY',len(formulas),'small',len(warnings),'failed',len(failures),flush=True)
    if failures:print(json.dumps(failures,ensure_ascii=False));raise RuntimeError('Review unsupported formula syntax')
@functools.lru_cache(12)
def base(key,index):
    s=BY[key];p=s['parts'][index];im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
    d.rounded_rectangle((60,215,1245,925),18,fill=PANEL,outline=GRID,width=2);d.rounded_rectangle((1280,215,1860,925),18,fill=PANEL,outline=GRID,width=2)
    tx(d,(64,36),f'线性代数 · {s["chapterIndex"]:02}',25,ORANGE);tx(d,(1850,40),'零基础大学生 · 动态可视化',23,MUTED,'rt')
    tx(d,(64,88),s['chapter'],46);tx(d,(64,158),s['title'],29,BLUE)
    tx(d,(1310,244),'独立思考' if s['kind']=='question' else '公式与观察',26,ORANGE)
    y=294
    for f in p['formulas']:
        with Image.open(formula_path(f)) as raw:
            img=raw.convert('RGBA');r=min(1,510/img.width,88/img.height);img=img.resize((round(img.width*r),round(img.height*r)),Image.Resampling.LANCZOS);im.paste(img,(1310,y),img);y+=img.height+19
    y=max(y+24,570)
    for note in p['notes']:
        tx(d,(1310,y+2),'•',26,ORANGE);y=wrap(d,note,1340,y,485,28)+16
    assert y<=925,('Side notes overflow',key,index,y)
    tx(d,(65,947),f'本章第 {s["sceneIndex"]} 页',19,MUTED)
    return im
def draw_vectors(d,v,t):
    u=np.array(v.get('u',[1,1]),float);b=np.array(v.get('v',[0,0]),float);phase=v.get('phase','static');target=np.array(v.get('target',[0,0]),float)
    limit=max(3.2,max(abs(np.r_[u,b,u+b,target]))*1.25)
    if 'coeff' in v:limit=max(limit,float(np.max(abs(v['coeff'][0]*u+v['coeff'][1]*b)))*1.2)
    if phase=='span':limit=max(limit,float(np.max(abs(u)+abs(b)))*1.65)
    scale=min(135,300/limit);p=graph(d,scale=scale,lim=min(8,math.ceil(limit)))
    if phase=='rotate':
        a=np.array(v['start'],float);angle=(1-t)*math.atan2(a[1],a[0])+t*math.atan2(u[1],u[0]);u=np.linalg.norm(u)*np.array([math.cos(angle),math.sin(angle)])
    if phase=='scale':
        if v.get('factor')==-1:
            factors=[1,2,-1,0];x=t*3;i=min(2,int(x));k=factors[i]+(factors[i+1]-factors[i])*(x-i)
        else:k=1+(v.get('factor',2)-1)*t
        arrow(d,p([0,0]),p(u),GRID,3);u=k*u;tx(d,(40,30),'数乘系数 = '+number(k),31,ORANGE)
    if phase=='span':
        cross=np.linalg.det(np.stack([u,b],axis=1));c1=1.35*math.cos(t*math.tau);c2=1.35*math.sin(t*math.tau)
        if abs(cross)<1e-8:
            direction=u/np.linalg.norm(u);line(d,p(-limit*direction),p(limit*direction),GREEN,8)
        else:d.rectangle((140,100,1000,600),outline='#3e785e',width=3)
        arrow(d,p([0,0]),p(c1*u+c2*b),GREEN,5,'组合')
        tx(d,(40,30),f'系数：{number(c1)}，{number(c2)}',31,GREEN)
    elif phase=='combine':
        c=v.get('coeff',[1,1]);arrow(d,p([0,0]),p(t*(c[0]*u+c[1]*b)),GREEN,6,'组合结果')
    elif phase=='cancel':
        arrow(d,p([0,0]),p(-2*t*u),BLUE,6);arrow(d,p(-2*t*u),p(-2*t*u+t*b),ORANGE,6);dot(d,p([0,0]),GREEN)
    if phase=='add':
        a=min(1,t/.6)*u;arrow(d,p([0,0]),p(u),BLUE,5,'u');arrow(d,p(a),p(a+b),ORANGE,5,'v')
        if t>.6:arrow(d,p([0,0]),p((t-.6)/.4*(u+b)),GREEN,6,'u + v')
    else:
        arrow(d,p([0,0]),p(u),BLUE,5,'u')
        if np.linalg.norm(b):arrow(d,p([0,0]),p(b),ORANGE,5,'v')
    if 'target' in v:dot(d,p(target),PURPLE,9);tx(d,p(target)+[12,10],'目标 '+coords(target),27,PURPLE)
    tx(d,(40,640),'蓝色 u = '+coords(u),28,BLUE)
def draw_transform(d,v,t,det=False,inverse=False):
    A=np.array(v.get('A',[[2,1],[0,1]]),float);phase=v.get('phase','')
    if phase=='compare':
        for k,(mat,label) in enumerate([(A,'先错切，再拉伸'),(np.array(v['B'],float),'先拉伸，再错切')]):
            T=np.eye(2)+(mat-np.eye(2))*t;render_grid(d,T,origin=(280+590*k,370),scale=55,lim=3);tx(d,(280+590*k,55),label,31,ORANGE,'mt')
        return
    T=np.eye(2)+(A-np.eye(2))*t
    if 'point' in v:T=A
    if phase=='swap':T=A@np.array([[1-t,t],[t,1-t]])
    if phase=='rowswap':T=np.array([[1-t,t],[t,1-t]])@A
    if phase=='scale':T=A*(1+(v.get('factor',2)-1)*t)
    if phase=='rowscale':T=np.diag([1+min(t*2,1),1+max(t*2-1,0)])@A
    if phase=='rowadd':T=np.array([[1,0],[v.get('factor',2)*t,1]])@A
    if phase=='question':T=A
    if inverse:
        if t<=.45:T=np.eye(2)+(A-np.eye(2))*t/.45
        else:T=(np.eye(2)+(np.linalg.inv(A)-np.eye(2))*(t-.45)/.55)@A
    # Use one camera scale for the whole operation. Grid lines may leave the
    # viewport, but the two column arrows and the area polygon must stay in it.
    endpoint=A.copy()
    if phase=='rowadd':endpoint=np.array([[1,0],[v.get('factor',2),1]])@A
    if phase=='scale':endpoint=A*v.get('factor',2)
    if phase=='rowscale':endpoint=2*A
    bounds=[np.eye(2),A,endpoint]
    points=np.concatenate([m.T for m in bounds])
    if det:points=np.concatenate([points,np.array([m@np.ones(2) for m in bounds])])
    if 'point' in v:points=np.concatenate([points,[A@np.array(v['point'])]])
    scale=min(83,220/max(1,float(np.max(abs(points[:,1])))),460/max(1,float(np.max(abs(points[:,0])))))
    render_grid(d,T,scale=scale,lim=3,area=det)
    matrix(d,A,center=(190,92),size=32,cell=55,row=48,label='目标 A')
    if inverse:matrix(d,np.linalg.inv(A),center=(920,92),size=32,cell=65,row=48,label='撤销 A⁻¹')
    if det and phase!='question':tx(d,(570,636),'当前带符号面积倍率 = '+number(np.linalg.det(T)),32,GREEN,'mt')
    if 'point' in v:
        p=lambda x:np.array([570,370])+np.array([x[0],-x[1]])*scale
        x=np.array(v['point'])*t;arrow(d,p([0,0]),p(T@x),GREEN,6,'A x')
def render_grid(d,T,origin=(570,370),scale=83,lim=3,area=False):
    o=np.array(origin,float)
    def p(x):return o+np.array([x[0],-x[1]])*scale
    for k in range(-lim,lim+1):
        for a,b in [([k,-lim],[k,lim]),([-lim,k],[lim,k])]:line(d,p(np.array(a)),p(np.array(b)),'#1b344a',1);line(d,p(T@np.array(a)),p(T@np.array(b)),GRID,2)
    if area:
        pts=[p(T@np.array(x)) for x in [[0,0],[1,0],[1,1],[0,1]]];d.polygon([tuple(x) for x in pts],fill='#285b67' if np.linalg.det(T)>=0 else '#653a4c');d.line([tuple(x) for x in pts+[pts[0]]],fill=GREEN,width=3)
    arrow(d,p(np.array([-lim,0])),p(np.array([lim,0])),MUTED,2);arrow(d,p(np.array([0,-lim])),p(np.array([0,lim])),MUTED,2)
    arrow(d,p(np.array([0,0])),p(T[:,0]),BLUE,5,'第一列');arrow(d,p(np.array([0,0])),p(T[:,1]),ORANGE,5,'第二列')
def draw_matrix(d,v,t):
    A=v.get('A',[[1,0],[0,1]]);B=v.get('B');op=v.get('operation','');a=np.array(A,dtype=object)
    if op=='add':
        a=np.array(A,float);b=np.array(B,float);n=a.size;idx=min(n-1,int(t*n));ij=np.unravel_index(idx,a.shape);colors={ij:'#45613e'}
        matrix(d,a,(190,320),38,65,68,colors,label='A');matrix(d,b,(570,320),38,65,68,colors,label='B');matrix(d,a+b,(950,320),38,65,68,colors,label='A+B');tx(d,(375,320),'+',52,ORANGE,'mm');tx(d,(760,320),'=',52,ORANGE,'mm');return
    if op in ['symmetry','similarity','congruence','dimensions'] and B is not None:
        matrix(d,A,(300,330),42,77,70,label='S' if op=='symmetry' else 'A');matrix(d,B,(850,330),42,77,70,label='K' if op=='symmetry' else 'B')
        tx(d,(575,330),'与' if op=='symmetry' else '→' if op in ['similarity','congruence'] else '和',46,ORANGE,'mm');return
    if op=='adjugate':
        a=np.array(A,float);adj=np.linalg.det(a)*np.linalg.inv(a);values=a.copy()
        if t<=1/3:values[0,0]=a[0,0]+(a[1,1]-a[0,0])*t*3;values[1,1]=a[1,1]+(a[0,0]-a[1,1])*t*3
        elif t<=2/3:values=adj.copy();q=(t-1/3)*3;values[0,1]=a[0,1]*(1-2*q);values[1,0]=a[1,0]*(1-2*q)
        else:values=adj/(1+(np.linalg.det(a)-1)*(t-2/3)*3)
        matrix(d,A,(270,330),50,label='A');matrix(d,values,(850,330),50,label='整理后');tx(d,(570,330),'→',56,ORANGE,'mm');return
    if op=='power':
        n=1+min(2,int(t*3));a=np.array(A,float);result=np.linalg.matrix_power(a,n) if n<3 else a@a+2*a+np.eye(len(a));matrix(d,A,(270,330),48,label='A');matrix(d,result,(850,330),48,label=f'A 的 {n} 次幂' if n<3 else 'p(A)');return
    colors={}
    if op=='blocks':
        palette=['#234d69','#655036','#3d5750','#4e3c66']
        for i in range(a.shape[0]):
            for j in range(a.shape[1]):colors[i,j]=palette[(i//2)*2+j//2]
    elif op=='characteristic':A=[[str(x)+'−λ' if i==j else x for j,x in enumerate(row)] for i,row in enumerate(A)];colors={(i,i):'#4e4e39' for i in range(len(A))}
    elif op=='quadratic':colors={(0,1):'#6a4b31',(1,0):'#6a4b31'}
    elif v.get('highlight')=='diagonal':colors={(i,i):'#425f4b' for i in range(min(a.shape))}
    elif isinstance(v.get('highlight'),list):colors={tuple(v['highlight']):'#6a4b31'}
    matrix(d,A,(570,330),size=43 if a.shape[0]>=3 else 56,cell=100,row=86,colors=colors,label='矩阵 A')
    if op=='vandermonde':tx(d,(570,570),'行参数：1，2，4',33,ORANGE,'mt')
    if 'vector' in v:tx(d,(570,580),'v = '+str(tuple(v['vector'])),35,BLUE,'mt')
def draw_multiply(d,v,t):
    A=np.array(v['A'],float);B=np.array(v['B'],float);C=A@B;n=C.size;idx=min(n-1,int(t*n));i,j=np.unravel_index(idx,C.shape)
    matrix(d,A,(220,290),34,65,65,{(i,k):'#315874' for k in range(A.shape[1])},label='左矩阵：取一行')
    matrix(d,B,(660,290),34,65,65,{(k,j):'#70522f' for k in range(B.shape[0])},label='右矩阵：取一列')
    values=np.array([number(x) if k<=idx else '?' for k,x in enumerate(C.flat)],object).reshape(C.shape)
    matrix(d,values,(1020,290),34,59,65,{(i,j):'#416344'},label='乘积');tx(d,(440,290),'×',46,ORANGE,'mm');tx(d,(850,290),'=',46,ORANGE,'mm')
    expr=' + '.join(number(a)+' × '+number(b) for a,b in zip(A[i,:],B[:,j]))+' = '+number(C[i,j]);tx(d,(570,535),expr,34,GREEN,'mt')
def draw_transpose(d,v,t):
    A=np.array(v['A']);m,n=A.shape;matrix(d,[['' for _ in range(n)] for _ in range(m)],(270,330),cell=90,row=83,label='A');matrix(d,[['' for _ in range(m)] for _ in range(n)],(850,330),cell=90,row=83,label='Aᵀ')
    for i in range(m):
        for j in range(n):
            start=np.array([270+(j-(n-1)/2)*90,330+(i-(m-1)/2)*83]);end=np.array([850+(i-(m-1)/2)*90,330+(j-(n-1)/2)*83]);at=start+(end-start)*t;tx(d,at,str(A[i,j]),47,BLUE if i==0 else ORANGE,'mm',True)
    tx(d,(570,550),'原来的第 i 行，成为第 i 列',31,MUTED,'mt')
def draw_permutation(d,v,t):
    values=v['values'];positions=[300,570,840]
    if 'matrix' in v:
        perms=list(itertools.permutations(range(3)));k=min(5,int(t*6));perm=perms[k];values=[x+1 for x in perm]
    top=80 if 'matrix' in v else 160
    for x,value in zip(positions,values):d.rounded_rectangle((x-75,top,x+75,top+120),14,fill='#274461');tx(d,(x,top+60),value,64,TEXT,'mm')
    pairs=[(i,j) for i in range(3) for j in range(i+1,3) if values[i]>values[j]];count=len(pairs) if 'matrix' in v else min(len(pairs),int(t*len(pairs)+1e-6))
    for k,(i,j) in enumerate(pairs[:count]):
        y=235+k*38 if 'matrix' in v else 315+k*55
        line(d,(positions[i],y),(positions[j],y),ORANGE,4);tx(d,(570,y+8),f'{values[i]} 在 {values[j]} 前面',27 if 'matrix' in v else 29,ORANGE,'mt')
    if 'matrix' in v:
        A=np.array(v['matrix']);perms=list(itertools.permutations(range(3)));k=min(5,int(t*6));perm=perms[k];inv=sum(perm[i]>perm[j] for i in range(3) for j in range(i+1,3));value=(-1)**inv*np.prod([A[i,perm[i]] for i in range(3)])
        matrix(d,A,(570,470),38,85,61,{(i,perm[i]):'#6b5535' for i in range(3)})
        total=sum((-1)**sum(q[i]>q[j] for i in range(3) for j in range(i+1,3))*np.prod([A[i,q[i]] for i in range(3)]) for q in perms[:k+1])
        tx(d,(570,595),f'本次选列 {tuple(x+1 for x in perm)}，本项 {value}',27,GREEN,'mt');tx(d,(570,638),f'已完成各项的代数和 = {total}',28,ORANGE,'mt')
    else:tx(d,(570,590),f'逆序数：{count}；完整逆序数：{len(pairs)}',33,GREEN,'mt')
def draw_cofactor(d,v,t):
    A=np.array(v['A']);i,j=v['cell'];colors={}
    for r in range(3):
        for c in range(3):
            if r==i or c==j:colors[r,c]='#5d3f47' if t>.05 else '#304a62'
    matrix(d,A,(340,320),48,95,83,colors,label='删去选中元素的行与列')
    minor=np.delete(np.delete(A,i,axis=0),j,axis=1);matrix(d,minor,(900,320),48,85,80,label='留下的余子式')
    if t>.5:line(d,(200,320+(i-1)*83),(480,320+(i-1)*83),RED,3);line(d,(340+(j-1)*95,195),(340+(j-1)*95,445),RED,3)
    tx(d,(570,565),f'位置符号：(−1)^({i+1}+{j+1}) = {(-1)**(i+j)}',30,ORANGE,'mt')
def draw_elimination(d,v,t):
    states=[np.array(x,float) for x in v['states']];q=min(t*(len(states)-1),len(states)-1);i=min(len(states)-2,int(q));f=q-i;A=states[i]*(1-f)+states[i+1]*f
    changed=[r for r in range(A.shape[0]) if not np.allclose(states[i][r],states[i+1][r])];colors={(r,c):'#3a564e' for r in changed for c in range(A.shape[1])}
    matrix(d,A,(570,335),45 if A.shape[1]<4 else 40,100,90,colors,split=v.get('split'))
    label=v['labels'][min(len(states)-1,math.ceil(q))];tx(d,(570,70),label,33,ORANGE,'mt');tx(d,(570,600),'同一行的所有位置一起变化',30,MUTED,'mt')
def draw_rank(d,v,t):
    A=np.array(v['A'],float);phase=v.get('phase','')
    if phase in ['minor','leading']:
        order=1 if t<.7 else min(A.shape);rows=tuple(range(order));cols=tuple(range(order))
        if phase=='minor':
            candidates=[(rs,cs) for rs in itertools.combinations(range(A.shape[0]),order) for cs in itertools.combinations(range(A.shape[1]),order) if abs(np.linalg.det(A[np.ix_(rs,cs)]))>1e-8]
            if candidates:rows,cols=candidates[0]
        colors={(i,j):'#466548' for i in rows for j in cols};matrix(d,A,(570,330),55,110,95,colors)
        value=np.linalg.det(A[np.ix_(rows,cols)]);tx(d,(570,580),f'{order} 阶'+('左上' if phase=='leading' else '所选')+'子式 = '+number(value),32,GREEN,'mt');return
    if phase=='canonical':
        rank=np.linalg.matrix_rank(A);R=np.zeros_like(A);R[:rank,:rank]=np.eye(rank);matrix(d,A,(280,330),42,75,73,label='原矩阵');matrix(d,R,(880,330),42,75,73,label='等价标准形');tx(d,(580,330),'→',52,ORANGE,'mm');return
    lim=max(3.2,np.max(abs(A))*1.3);p=graph(d,origin=(370,380),scale=min(95,250/lim),lim=math.ceil(lim))
    for i in range(A.shape[1]):
        u=A[:2,i];color=[BLUE,ORANGE,GREEN][i%3]
        if phase=='pivots' and i not in v.get('pivots',[]):color=GRID
        arrow(d,p([0,0]),p(u),color,5,'a'+str(i+1))
    colors={(i,j):'#315b70' for i in range(A.shape[0]) for j in v.get('pivots',[])};matrix(d,A,(925,320),37,69,70,colors,label='原矩阵的列')
    if phase!='question':tx(d,(570,620),'独立方向数 r = '+str(np.linalg.matrix_rank(A)),34,GREEN,'mt')
def draw_equations(d,v,t):
    mode=v.get('mode','cases')
    iscases=mode=='cases'
    if iscases:mode='unique' if t<=1/3+1e-6 else 'parallel' if t<=2/3+1e-6 else 'coincident'
    p=graph(d,origin=(570,370),scale=85,lim=4);xs=np.linspace(-4,4,90)
    m,b=(1,-1) if mode=='unique' else (-1,1) if mode=='parallel' else (-1,3)
    if iscases and 1/3<t<2/3:q=(t-1/3)*3;m=1-2*q;b=-1+2*q
    if iscases and 2/3<t<1:b=1+2*(t-2/3)*3
    paths=[[(x,3-x) for x in xs],[(x,m*x+b) for x in xs]]
    for k,path in enumerate(paths):d.line([tuple(p(x)) for x in path],fill=[BLUE,ORANGE][k],width=5 if k==0 else 3)
    label={'unique':'两条直线相交：唯一解','parallel':'平行且不重合：无解','coincident':'两条直线重合：无穷多解'}[mode]
    if iscases and 1/3<t<2/3:label='改变第二条直线，观察交点位置'
    if iscases and 2/3<t<1:label='平行直线逐渐移向重合位置'
    tx(d,(570,50),label,33,GREEN,'mt')
    if mode=='unique':dot(d,p([2,1]),GREEN,9);tx(d,p([2,1])+[12,12],'(2,1)',30,GREEN)
    if mode=='coincident' and (not iscases or t>=1):
        for x in [-.4,1,2.4]:dot(d,p([x,3-x]),GREEN)
def draw_nullspace(d,v,t):
    if v.get('mode')=='homogeneous':
        p=graph(d);direction=np.array([1,-1]);line(d,p(-3*direction),p(3*direction),GREEN,5);arrow(d,p([0,0]),p((t*4-2)*direction),BLUE,6);tx(d,(570,50),'齐次解直线经过原点',33,GREEN,'mt');return
    if v.get('mode')=='homogeneous-criterion':
        p=graph(d);dot(d,p([0,0]),ORANGE,9)
        label='齐次方程组 Ax = 0：原点始终是解'
        if 0<t<=.5:label='方阵 det A ≠ 0：只有零解'
        if t>.5:
            k=(t-.5)*2;direction=np.array([1,-1.]);line(d,p(-2.5*k*direction),p(2.5*k*direction),GREEN,5);dot(d,p(k*direction),ORANGE,9);label='方阵 det A = 0：存在非零齐次解'
        tx(d,(570,50),label,32,GREEN,'mt');return
    h=np.array(v['direction'],float);part=np.array(v['particular'],float)
    def p(a):return np.array([570,350])+np.array([a[0]-.65*a[1],.32*a[0]+.3*a[1]-a[2]])*70
    origin=p([0,0,0])
    for i,lab in enumerate('xyz'):
        axis=np.eye(3)[i]*2.5;arrow(d,origin,p(axis),MUTED,2,lab)
    offset=part*t if v.get('phase')=='translate' else part
    line(d,p(-2*h),p(2*h),GRID,4);line(d,p(offset-2*h),p(offset+2*h),GREEN,5)
    coeff=2*math.sin(t*math.tau);value=offset+coeff*h;dot(d,p(value),ORANGE,9);arrow(d,origin,p(offset),PURPLE,4,'特解' if np.linalg.norm(part) else None)
    tx(d,(570,40),'三维坐标的投影示意',29,MUTED,'mt');tx(d,(570,610),'参数 t = '+number(coeff)+'；解 = '+coords(value),30,GREEN,'mt')
def draw_eigen(d,v,t):
    A=np.array(v['A'],float);phase=v.get('phase','');T=np.eye(2)+(A-np.eye(2))*t
    if phase=='powers':T=A+(A@A-A)*t
    maxlength=12 if phase=='powers' else 4.5;p=graph(d,scale=480/maxlength,lim=4)
    if phase=='defective':vectors=[np.array([1,0]),np.array([0,1]),np.array([1,1])]
    else:vectors=[np.array([1,1])/np.sqrt(2),np.array([1,-1])/np.sqrt(2),np.array([1,.2]),np.array([.2,1])]
    for i,u in enumerate(vectors):
        color=[BLUE,ORANGE,GREEN,PURPLE][i%4];arrow(d,p([0,0]),p(u),GRID,3);arrow(d,p([0,0]),p(T@u),color,5)
    if phase=='defective':tx(d,(570,60),'只有水平方向提供独立特征向量',30,ORANGE,'mt')
    else:tx(d,(570,60),'两条对角线是特征方向',32,ORANGE,'mt')
def draw_basis(d,v,t):
    phase=v.get('phase','');p=graph(d,scale=125,lim=3);u=np.array([1,1.]);w=np.array([1,-1.]);factor=1+(1/np.sqrt(2)-1)*t if phase=='normalize' else 1/np.sqrt(2)
    arrow(d,p(-2*u),p(2*u),BLUE,3);arrow(d,p(-2*w),p(2*w),ORANGE,3)
    arrow(d,p([0,0]),p(factor*u),BLUE,6,'q₁');arrow(d,p([0,0]),p(factor*w),ORANGE,6,'q₂')
    if phase in ['change','diagonal']:
        x=np.array([2.,1.]);a=np.dot(x,u/np.sqrt(2));b=np.dot(x,w/np.sqrt(2));tail=t*a*u/np.sqrt(2);arrow(d,p([0,0]),p(tail),BLUE,5);arrow(d,p(tail),p(tail+t*b*w/np.sqrt(2)),ORANGE,5);dot(d,p(x),GREEN,9)
    tx(d,(570,625),'新基方向固定；观察坐标分量的组合',29,MUTED,'mt')
def draw_projection(d,v,t):
    u=np.array(v['u'],float);v0=np.array(v['v'],float);proj=np.dot(v0,u)/np.dot(u,u)*u;p=graph(d,scale=180,lim=2)
    phase=v.get('phase','');w=v0-t*proj if phase in ['gram','residual'] else v0
    arrow(d,p([0,0]),p(u),BLUE,6,'u');arrow(d,p([0,0]),p(v0),ORANGE,6,'v')
    if phase=='orthogonal':tx(d,(570,60),'内积 = '+number(np.dot(u,v0)),34,GREEN,'mt');return
    if phase=='project':arrow(d,p([0,0]),p(t*proj),GREEN,6,'投影');line(d,p(proj),p(v0),MUTED,2)
    else:arrow(d,p([0,0]),p(w),GREEN,6,'剩余');tx(d,(570,60),'u 与当前剩余的内积 = '+number(np.dot(u,w)),31,GREEN,'mt')
def contours(A):
    values,Q=np.linalg.eigh(A);paths=[]
    if values[0]>1e-8 or values[1]<-1e-8:
        a=np.linspace(0,math.tau,160)
        for c in [1,2,4]:paths.append((np.stack([np.cos(a)*np.sqrt(c/abs(values[0])),np.sin(a)*np.sqrt(c/abs(values[1]))],axis=1)@Q.T,BLUE))
    elif values[0]<-1e-8 and values[1]>1e-8:
        a=np.linspace(-1.5,1.5,120)
        for c in [1,2]:
            for sign in [-1,1]:
                paths.append((np.stack([np.sinh(a)*np.sqrt(c/-values[0]),sign*np.cosh(a)*np.sqrt(c/values[1])],axis=1)@Q.T,GREEN))
                paths.append((np.stack([sign*np.cosh(a)*np.sqrt(c/-values[0]),np.sinh(a)*np.sqrt(c/values[1])],axis=1)@Q.T,RED))
    return paths
def draw_quadratic(d,v,t):
    A=np.array(v.get('A',[[2,1],[1,2]]),float);phase=v.get('phase','');p=graph(d,scale=125,lim=3)
    paths=contours(A)
    S=np.diag([1+(np.sqrt(3)-1)*t,1]) if phase=='normalize' else np.eye(2)
    if phase=='standard':A=np.diag([3.,1.]);paths=contours(A)
    for path,color in paths:d.line([tuple(p(S@x)) for x in path],fill=color,width=3)
    if phase=='rotate':
        angle=t*math.pi/4;Q=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]]);new=Q.T@A@Q
        for i,col in enumerate([BLUE,ORANGE]):arrow(d,p(-2.5*Q[:,i]),p(2.5*Q[:,i]),col,4,['u','v'][i])
        tx(d,(570,60),'新坐标交叉项系数 = '+number(2*new[0,1]),32,GREEN,'mt')
    else:tx(d,(570,60),'同一高度的点组成等高线',32,ORANGE,'mt')
    if phase=='standard':
        a=t*math.tau;point=np.array([np.cos(a)*np.sqrt(4/3),2*np.sin(a)]);dot(d,p(point),ORANGE,9);tx(d,(570,620),'3u² + v² = 4',33,GREEN,'mt')
def draw_surface(d,v,t):
    A=np.array(v['A'],float);angle=.5+(t-.5)*.5;ca,sa=math.cos(angle),math.sin(angle);zscale=.38/max(1,np.max(abs(np.linalg.eigvalsh(A))))
    def project(x,y,z):return np.array([570+(x*ca-y*sa)*135,350+(x*sa+y*ca)*55-z*zscale*80])
    o=project(0,0,0)
    for p,label in [(project(2.3,0,0),'x'),(project(0,2.3,0),'y'),(project(0,0,2.4/zscale),'f')]:arrow(d,o,p,MUTED,2,label)
    samples=np.linspace(-1.5,1.5,35)
    for fixed in np.linspace(-1.5,1.5,13):
        for swap in [False,True]:
            xs=np.full_like(samples,fixed) if swap else samples;ys=samples if swap else np.full_like(samples,fixed);z=A[0,0]*xs**2+2*A[0,1]*xs*ys+A[1,1]*ys**2
            d.line([tuple(project(x,y,f)) for x,y,f in zip(xs,ys,z)],fill=BLUE if np.mean(z)>=0 else RED,width=2)
    theta=t*math.tau;x,y=1.15*math.cos(theta),1.15*math.sin(theta);z=float(np.array([x,y])@A@np.array([x,y]));dot(d,project(x,y,z),GREEN if z>=-1e-8 else RED,9);line(d,project(x,y,0),project(x,y,z),ORANGE,3)
    tx(d,(570,35),'z = xᵀ A x：点的位置决定高度',31,ORANGE,'mt');tx(d,(570,630),'当前点的高度 = '+number(z),33,GREEN if z>=0 else RED,'mt')
def draw_cramer(d,v,t):
    A=np.array(v['A'],float);b=np.array(v['b'],float);index=0 if t<.5 else 1;q=t*2 if index==0 else (t-.5)*2;M=A.copy();M[:,index]=(1-q)*A[:,index]+q*b;D=np.linalg.det(A);Dj=np.linalg.det(M)
    matrix(d,A,(270,320),46,90,80,label='系数矩阵 A');matrix(d,M,(850,320),46,90,80,{(i,index):'#5b5937' for i in range(2)},label=f'第 {index+1} 列换成 b')
    tx(d,(570,320),'→',54,ORANGE,'mm')
    if q>.98:tx(d,(570,560),f'D = {number(D)}，D{index+1} = {number(Dj)}，未知数 = {number(Dj/D)}',32,GREEN,'mt')
    else:tx(d,(570,560),'正在把常数列 b 放入指定列',31,ORANGE,'mt')
def cover(im,scene,part):
    d=ImageDraw.Draw(im);d.rectangle((0,0,1920,1080),fill=BG)
    tx(d,(88,74),'从方向、变换到方程与曲面',31,ORANGE);tx(d,(80,150),'线性代数',108);tx(d,(88,300),'一小时',99,ORANGE)
    topics=['向量与线性组合','矩阵与线性变换','行列式与面积变化','初等变换与逆矩阵','线性相关与矩阵的秩','线性方程组与解的结构','特征值与相似对角化','内积与正交变换','二次型与坐标变换','正定判断与综合回顾']
    for i,n in enumerate(topics):
        x=90+(i//5)*910;y=555+i%5*78;dot(d,(x,y+20),ORANGE,9);tx(d,(x+30,y),n,35)
def concept_map(d):
    labels=['向量组合','矩阵变换','行列式','秩','方程组','特征值','正交化','二次型','合同与惯性','正定判据']
    boxes=[]
    for i,l in enumerate(labels):
        row=i//2;col=i%2 if row%2==0 else 1-i%2;x=65+col*560;y=45+row*125;boxes.append((x,y));d.rounded_rectangle((x,y,x+440,y+82),12,outline=BLUE,width=2,fill='#1b3650');tx(d,(x+220,y+41),l,31,TEXT,'mm')
    for (x,y),(xx,yy) in zip(boxes,boxes[1:]):
        if yy==y:
            if xx>x:arrow(d,(x+450,y+41),(xx-10,yy+41),ORANGE,3)
            else:arrow(d,(x-10,y+41),(xx+450,yy+41),ORANGE,3)
        else:arrow(d,(x+220,y+90),(xx+220,yy-8),ORANGE,3)
HANDLERS={'vectors':draw_vectors,'transform':draw_transform,'matrix':draw_matrix,'multiply':draw_multiply,'transpose':draw_transpose,'permutation':draw_permutation,'cofactor':draw_cofactor,'elimination':draw_elimination,'rank':draw_rank,'equations':draw_equations,'nullspace':draw_nullspace,'eigen':draw_eigen,'basis':draw_basis,'projection':draw_projection,'quadratic':draw_quadratic,'surface':draw_surface,'cramer':draw_cramer}
BY={}
def init(timeline):
    global BY;BY={s['key']:s for s in timeline['scenes']};base.cache_clear()
def state(s,frame):
    ready=[x for x in s['units'] if x['begin']<=frame];u=ready[-1] if ready else s['units'][0];progress=0 if u['motions'] else 1
    for m in u['motions']:
        if frame<m['begin']:break
        q=smooth((frame-m['begin'])/(m['end']-m['begin']));progress=m['fromProgress']+(m['toProgress']-m['fromProgress'])*q
    return u['index'],progress
def render(s,frame):
    index,t=state(s,frame);p=s['parts'][index];v=p['visual'];im=base(s['key'],index).copy()
    if v['kind']=='cover':cover(im,s,index)
    else:
        canvas=Image.new('RGB',(1165,690),PANEL);d=ImageDraw.Draw(canvas)
        if v['kind']=='det':draw_transform(d,v,t,det=True)
        elif v['kind']=='inverse':draw_transform(d,v,t,inverse=True)
        elif v['kind']=='map':concept_map(d)
        else:HANDLERS[v['kind']](d,v,t)
        im.paste(canvas,(70,225))
    d=ImageDraw.Draw(im);d.rectangle((0,0,1920,5),fill=GRID)
    if s['kind']=='question':
        pause=s['leadFrames']+s['speechFrames']+s['sentenceTailFrames']
        if frame>=pause:
            count=max(1,math.ceil((s['durationFrames']-frame)/30));d.rounded_rectangle((1555,820,1838,905),12,fill='#183f50',outline=BLUE,width=2);tx(d,(1696,862),f'思考 {count}',40,BLUE,'mm')
    return im
