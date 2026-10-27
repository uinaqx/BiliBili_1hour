"""Exam-oriented formula boards with authored, persistent steps and no subtitles."""
import functools,hashlib,json,math,pathlib,re,warnings
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import diagrams
ROOT=pathlib.Path(__file__).resolve().parents[1]
BG='#09172a';PANEL='#10243a';TEXT='#eff5ff';MUTED='#9fb2ca';BLUE='#70cfff';ORANGE='#ffbd68';GREEN='#8fe0b2';GRID='#25435e'
@functools.lru_cache(32)
def font(size):return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size)
def text(d,xy,s,size=30,color=TEXT,anchor='lt'):d.text(xy,str(s),font=font(size),fill=color,anchor=anchor)
def wrap(d,s,xy,width,size=30,line=43,color=TEXT):
    x,y=xy;row=''
    for ch in s:
        if font(size).getlength(row+ch)>width and row:text(d,(x,y),row,size,color);y+=line;row=''
        row+=ch
    if row:text(d,(x,y),row,size,color);y+=line
    return y
def normalized(s):
    # MathText needs explicit arguments, including nested frac numerators.
    def atom(at):
        while at<len(s) and s[at].isspace():at+=1
        if at>=len(s):raise ValueError('Missing TeX argument')
        if s[at]=='{':
            begin=at;depth=0
            for j in range(at,len(s)):
                if s[j]=='{':depth+=1
                elif s[j]=='}':
                    depth-=1
                    if depth==0:return s[begin:j+1],j+1
            raise ValueError('Unbalanced TeX braces')
        if s[at]=='\\':
            found=re.match(r'\\[A-Za-z]+',s[at:]);end=at+len(found[0]) if found else at+2;return '{'+s[at:end]+'}',end
        return '{'+s[at]+'}',at+1
    for command,count in [('mathbf',1),('mathbb',1),('frac',2),('sqrt',1)]:
        result='';at=0;needle='\\'+command
        while at<len(s):
            if s.startswith(needle,at) and (at+len(needle)==len(s) or not s[at+len(needle)].isalpha()):
                result+=needle;at+=len(needle)
                for _ in range(count):value,at=atom(at);result+=value
            else:result+=s[at];at+=1
        s=result
    s=re.sub(r'\\(le|ge|ne)(?![A-Za-z])',lambda m:'\\'+dict(le='leq',ge='geq',ne='neq')[m[1]],s)
    s=re.sub(r'\\mathbb\s+([A-Za-z])',r'\\mathbb{\1}',s)
    s=re.sub(r'\\frac(?!\{)(\\[A-Za-z]+|[A-Za-z0-9])',r'\\frac{\1}',s)
    s=re.sub(r'\\frac\{([^{}]*)\}(?!\{)(\\[A-Za-z]+|[A-Za-z0-9])',r'\\frac{\1}{\2}',s)
    s=re.sub(r'\\sqrt(?!\{)([A-Za-z0-9])',r'\\sqrt{\1}',s)
    return s
def formula_path(s):return ROOT/'build/formulas'/(hashlib.sha256(('stix-formula-v1'+s).encode()).hexdigest()+'.png')
def prepare_formulas(course):
    import matplotlib;matplotlib.use('Agg')
    from matplotlib import mathtext,font_manager,rcParams
    rcParams.update({'mathtext.fontset':'stix'})
    folder=ROOT/'build/formulas';folder.mkdir(exist_ok=True);small=[];fail=[];items=[]
    caps={}
    for c in course['chapters']:
        for page in c['scenes']:
            cap=69 if page.get('visual') else min(166,665//len(page['rows']))-52
            for row in page['rows']:
                if row['math']:caps[row['math']]=min(caps.get(row['math'],cap),cap)
    for value in sorted(caps):
        path=formula_path(value)
        if not path.exists():
            try:
                with warnings.catch_warnings(record=True) as caught:
                    raster=mathtext.MathTextParser('agg').parse('$'+normalized(value)+'$',prop=font_manager.FontProperties(size=26),dpi=144)
                    assert not any('Glyph' in str(w.message) for w in caught),value
                alpha=np.asarray(raster.image,dtype=np.uint8);a=np.empty((*alpha.shape,4),dtype=np.uint8);a[:,:,:3]=[239,245,255];a[:,:,3]=alpha;Image.fromarray(a).save(path)
            except Exception as exc:fail.append(dict(formula=value,error=str(exc)));continue
        with Image.open(path) as im:
            scale=min(1,1090/im.width,caps[value]/im.height);items.append(dict(formula=value,width=im.width,height=im.height,availableHeight=caps[value],scale=scale))
            if scale<.69:small.append(items[-1])
    report=dict(allPassed=not fail and not small,formulas=len(items),small=small,failures=fail,items=items)
    (ROOT/'build/formula-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    print('FORMULAS_READY',len(items),'too-small',len(small),'failed',len(fail),flush=True)
    if fail or small:raise RuntimeError(json.dumps(dict(failures=fail,small=small),ensure_ascii=False))
@functools.lru_cache(320)
def formula(s):
    with Image.open(formula_path(s)) as im:
        im=im.convert('RGBA');scale=min(1,1090/im.width);return im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.LANCZOS)
BY={}
def init(t):
    global BY;BY={s['key']:s for s in t['scenes']}
def state(s,frame):
    begun=[u for u in s['units'] if u['begin']<=frame];u=begun[-1] if begun else s['units'][0];progress=0 if u.get('motions') else 1
    for m in u.get('motions',[]):
        if frame<m['begin']:break
        q=max(0,min(1,(frame-m['begin'])/(m['end']-m['begin'])));q=q*q*(3-2*q);progress=m['fromProgress']+(m['toProgress']-m['fromProgress'])*q
    return u['index'],progress
def cover(s):
    im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
    text(d,(88,70),'零基础入门 · 概念、算法与解题步骤',31,ORANGE)
    text(d,(80,145),'408 操作系统',104);text(d,(88,305),'一小时',100,ORANGE)
    topics=[c for c in dict.fromkeys(x['chapter'] for x in BY.values())]
    for i,title in enumerate(topics):
        x=90+(i//5)*910;y=555+(i%5)*77;d.ellipse((x,y+13,x+16,y+29),fill=ORANGE);text(d,(x+32,y),title,34)
    return im
def render(s,frame):
    index,progress=state(s,frame);p=s['parts'][index]
    if s['kind']=='overview':return cover(s)
    im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
    d.rectangle((0,0,1920,5),fill=GRID);d.rounded_rectangle((60,215,1260,925),18,fill=PANEL,outline=GRID,width=2);d.rounded_rectangle((1280,215,1860,925),18,fill=PANEL,outline=GRID,width=2)
    text(d,(64,36),f'408 操作系统 · {s["chapterIndex"]:02}',25,ORANGE);text(d,(1850,40),'零基础大学生 · 408基础考点',23,MUTED,'rt')
    text(d,(64,88),s['chapter'],46);text(d,(64,158),s['title'],29,BLUE)
    assert font(29).getlength(s['title'])<1180,('Title overflow',s['key'])
    for i,r in enumerate(s['rows'],1):
        if i>p['show']:continue
        height=118 if s.get('visual') else min(166,665//len(s['rows']));y=230+(i-1)*height;selected=i in p['focus']
        if selected:d.rounded_rectangle((78,y,1242,y+height-6),10,fill='#263547');d.rectangle((79,y+8,84,y+height-15),fill=ORANGE)
        assert font(24).getlength(r['label'])<1110,('Label overflow',s['key'],i)
        text(d,(106,y+7),r['label'],24,ORANGE if selected else MUTED)
        if r['math']:
            img=formula(r['math'])
            limit=69 if s.get('visual') else height-52
            if img.height>limit:
                scale=limit/img.height;img=img.resize((round(img.width*scale),limit),Image.Resampling.LANCZOS)
            im.paste(img,(112,y+39 if s.get('visual') else y+42),img)
        else:
            end=wrap(d,r['text'],(112,y+42),1090,size=31 if s.get('visual') else 33,line=38 if s.get('visual') else 41);assert end<=y+height-4,('Plain row overflow',s['key'],i)
    if s.get('visual'):im.paste(diagrams.render(s['visual'],p['phase'],progress),(78,603))
    text(d,(1310,247),'暂停动手' if s['kind']=='question' else '条件与得分检查',26,ORANGE)
    y=310
    for note in p['notes']:
        text(d,(1310,y),'•',28,ORANGE);y=wrap(d,note,(1342,y),480,29,43)+24
    assert y<790,('Notes overflow',s['key'],index,y)
    text(d,(1310,745),'本页步骤',23,BLUE);text(d,(1310,788),f'{index+1} / {len(s["parts"])}',31,TEXT)
    text(d,(65,947),f'本章第 {s["sceneIndex"]} 页',19,MUTED)
    if s['kind']=='question':
        pause=s['leadFrames']+s['speechFrames']+s['sentenceTailFrames']
        if frame>=pause:
            count=max(1,math.ceil((s['durationFrames']-frame)/30));d.rounded_rectangle((1555,820,1838,905),12,fill='#183f50',outline=BLUE,width=2);text(d,(1696,862),f'思考 {count}',40,BLUE,'mm')
    return im
