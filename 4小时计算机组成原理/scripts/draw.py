"""Readable source-based lesson frames, fixed page summaries and authored focus."""
import bisect,functools,pathlib,re
from PIL import Image,ImageDraw,ImageFont,ImageOps
ROOT=pathlib.Path(__file__).resolve().parents[1]
BG='#09172a';PANEL='#10243a';TEXT='#eff5ff';MUTED='#9fb2ca';ORANGE='#ffbd68';BLUE='#70cfff';GREEN='#8fe0b2';GRID='#29455e'
@functools.lru_cache(32)
def font(n):return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
def display(s):
 table=str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁽⁾','0123456789+-()')
 s=re.sub('[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁽⁾]+',lambda m:'^('+m.group().translate(table)+')',str(s))
 return re.sub('[₀₁₂₃₄₅₆₇₈₉]+',lambda m:'_('+m.group().translate(str.maketrans('₀₁₂₃₄₅₆₇₈₉','0123456789'))+')',s)
def text(d,xy,s,size=30,color=TEXT,anchor='lt'):d.text(xy,display(s),font=font(size),fill=color,anchor=anchor)
def wrap(d,s,xy,width,size=30,line=41,color=TEXT):
 x,y=xy;row=''
 units=[]
 for token in re.findall(r'0[xX][0-9A-Fa-f]+|[0-9A-Fa-f]+[Hh]\b|\d+(?:\.\d+)?(?:KiB|MiB|GiB|GB|MB|B|bit|ns|ms|GHz|MHz|Hz|%)?|[A-Za-z_][A-Za-z_0-9.]*|.',display(s).rstrip('。')):
  if token in '，。；：、！？）》】' and units:units[-1]+=token
  else:units.append(token)
 for ch in units:
  if row and font(size).getlength(row+ch)>width:text(d,(x,y),row,size,color);y+=line;row=''
  if font(size).getlength(ch)>width:raise ValueError('Overlong unbreakable display token')
  row+=ch
 if row:text(d,(x,y),row,size,color);y+=line
 return y
def render(s,frame):
 i=max(0,bisect.bisect_right(s['beatFrames'],frame)-1);b=s['beats'][i]
 im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
 text(d,(55,30),s['chapter'],38);text(d,(1860,40),'计算机组成原理 · 课件精讲',25,MUTED,'rt')
 text(d,(58,109),s['title'],31,BLUE);assert font(31).getlength(s['title'])<1735,('Title overflow',s['id'])
 d.rounded_rectangle((45,175,1430,1005),18,fill=PANEL,outline=GRID,width=2)
 d.rounded_rectangle((1450,175,1875,1005),18,fill=PANEL,outline=GRID,width=2)
 if b.get('board'):
  rows=b['board'];assert 1<=len(rows)<=4
  height=min(192,760//len(rows))
  for j,r in enumerate(rows):
   y=205+j*height;d.rounded_rectangle((70,y,1405,y+height-14),12,fill='#182e46',outline=GRID,width=1)
   text(d,(95,y+14),r['label'],26,ORANGE)
   end=wrap(d,r['text'],(100,y+56),1275,35,44)
   assert end<y+height-13,('Board overflow',s['id'],i,j,end,y+height)
 else:
  path=ROOT/'public/slides'/(b['page']+'.jpg')
  with Image.open(path) as original:
   original=original.convert('RGB');ow,oh=original.size;crop=b.get('crop') or [0,0,1,1]
   box=(round(crop[0]*ow),round(crop[1]*oh),round(crop[2]*ow),round(crop[3]*oh));original=original.crop(box)
   image=ImageOps.contain(original,(1355,800),Image.Resampling.LANCZOS);x=60+(1355-image.width)//2;y=190+(800-image.height)//2;im.paste(image,(x,y))
   if b.get('focus'):
    f=b['focus'];coords=(x+(f[0]*ow-box[0])*image.width/original.width,y+(f[1]*oh-box[1])*image.height/original.height,x+(f[2]*ow-box[0])*image.width/original.width,y+(f[3]*oh-box[1])*image.height/original.height)
    d=ImageDraw.Draw(im);d.rounded_rectangle(coords,5,outline=ORANGE,width=4)
 text(d,(1480,205),'例题总结' if s['kind']=='worked' else '本页总结',28,ORANGE);y=270
 for note in s['points']:
  text(d,(1475,y),'•',27,ORANGE);y=wrap(d,note,(1504,y),342,26,36)+22
 assert y<975,('Summary overflow',s['id'],y)
 text(d,(58,1025),f'讲解 {i+1} / {len(s["beats"])}',20,MUTED)
 return im
