"""Series layout with persistent code selection, output below code and real simulation diagrams."""
import functools,hashlib,json,math,pathlib,re
from PIL import Image,ImageDraw,ImageFont
import diagrams
ROOT=pathlib.Path(__file__).resolve().parents[1];BG='#09172a';PANEL='#10243a';TEXT='#eff5ff';MUTED='#9fb2ca';BLUE='#70cfff';ORANGE='#ffbd68';GREEN='#8fe0b2';GRID='#25435e';BY={}
@functools.lru_cache(48)
def font(size):return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',size)
@functools.lru_cache(8)
def mono(size):return ImageFont.truetype('C:/Windows/Fonts/consola.ttf',size)
def text(d,xy,s,size=30,color=TEXT,anchor='lt'):d.text(xy,str(s),font=font(size),fill=color,anchor=anchor)
def wrap(d,s,xy,width,size=30,line=43,color=TEXT):
 x,y=xy;row=''
 for ch in s:
  if font(size).getlength(row+ch)>width and row:text(d,(x,y),row,size,color);y+=line;row=''
  row+=ch
 if row:text(d,(x,y),row,size,color);y+=line
 return y
def init(t):
 global BY;BY={s['key']:s for s in t['scenes']}
def prepare_formulas(course):
 assert not any(r['math'] for c in course['chapters'] for s in c['scenes'] for r in s['rows'])
 (ROOT/'build/formula-review.json').write_text(json.dumps(dict(allPassed=True,formulas=0,reason='Verilog code and circuit diagrams; no TeX formula assets')),encoding='utf8')
def state(s,frame):
 begun=[u for u in s['units'] if u['begin']<=frame];u=begun[-1] if begun else s['units'][0];progress=0 if u.get('motions') else 1
 for m in u.get('motions',[]):
  if frame<m['begin']:break
  q=max(0,min(1,(frame-m['begin'])/(m['end']-m['begin'])));q=q*q*(3-2*q);progress=m['fromProgress']+(m['toProgress']-m['fromProgress'])*q
 return u['index'],progress
def diagram_box(s):return (1295,585,1845,895) if s.get('code') else (78,603,1243,913)
def cover():
 im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im);text(d,(86,67),'从电路出发 · 用仿真核对每一次变化',31,ORANGE);text(d,(80,140),'Verilog',112);text(d,(86,300),'一小时',100,ORANGE)
 text(d,(86,440),'零基础入门 · 代码、电路与波形一起看',32,MUTED)
 for i,title in enumerate(dict.fromkeys(s['chapter'] for s in BY.values())):
  x=90+i//5*910;y=540+i%5*80;d.ellipse((x,y+12,x+16,y+28),fill=ORANGE);text(d,(x+32,y),title,33)
 return im
TOKEN=re.compile(r'//.*|\b(?:module|endmodule|input|output|wire|reg|assign|always|begin|end|if|else|case|endcase|default|posedge|parameter|localparam|genvar|generate|endgenerate|for|function|endfunction|initial|task|endtask|integer)\b|\b\d+\x27[sS]?[bBoOdDhH][0-9a-fA-FxXzZ_]+|\b\d+\b|\$[a-zA-Z]+')
def code_line(d,xy,s):
 x,y=xy;cursor=0
 for match in TOKEN.finditer(s):
  ordinary=s[cursor:match.start()];d.text((x,y),ordinary,font=mono(34),fill=TEXT);x+=mono(34).getlength(ordinary)
  token=match.group();color=MUTED if token.startswith('//') else ORANGE if token[0].isdigit() else GREEN if token.startswith('$') else BLUE
  d.text((x,y),token,font=mono(34),fill=color);x+=mono(34).getlength(token);cursor=match.end()
 d.text((x,y),s[cursor:],font=mono(34),fill=TEXT)
def render(s,frame):
 index,progress=state(s,frame);p=s['parts'][index]
 if s['kind']=='overview':return cover()
 im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
 d.rectangle((0,0,1920,5),fill=GRID);d.rounded_rectangle((60,215,1260,925),18,fill=PANEL,outline=GRID,width=2);d.rounded_rectangle((1280,215,1860,925),18,fill=PANEL,outline=GRID,width=2)
 text(d,(64,36),f'Verilog · {s["chapterIndex"]:02}',25,ORANGE);text(d,(1850,40),'零基础大学生 · Verilog-2005',23,MUTED,'rt');text(d,(64,88),s['chapter'],46);text(d,(64,158),s['title'],29,BLUE)
 assert font(29).getlength(s['title'])<1180
 if s.get('code'):
  text(d,(92,231),s['codeFile'],21,MUTED)
  for i,line in enumerate(s['code'],1):
   y=270+(i-1)*39;assert mono(34).getlength(line)<=1080,('Code overflow',s['key'],i,len(line));assert y+37<=805,('Too many code rows',s['key'])
   if i in p['codeLines']:d.rounded_rectangle((80,y-4,1240,y+35),5,fill='#263547');d.rectangle((80,y-4,85,y+35),fill=ORANGE)
   d.text((94,y),f'{i:02}',font=mono(23),fill=MUTED);code_line(d,(145,y),line)
  d.line((90,816,1230,816),fill=GRID,width=2);text(d,(92,827),'仿真结果 / 检查',21,BLUE)
  outputs=s['output'] or ['代码对应的完整测试与仿真记录见工程文件']
  for j,out in enumerate(outputs[:2]):
   assert font(30).getlength(out)<=1100,('Output overflow',s['key']);text(d,(92,860+j*35),out,30,GREEN)
 else:
  for i,r in enumerate(s['rows'],1):
   if i>p['show']:continue
   height=118 if s.get('visual') else min(166,665//len(s['rows']));y=230+(i-1)*height
   if i in p['focus']:d.rounded_rectangle((78,y,1242,y+height-6),10,fill='#263547');d.rectangle((79,y+8,84,y+height-15),fill=ORANGE)
   text(d,(106,y+7),r['label'],24,ORANGE if i in p['focus'] else MUTED);end=wrap(d,r['text'],(112,y+42),1090,33,42);assert end<=y+height-4,(s['key'],'Row overflow')
 if s.get('visual'):
  x,y,xx,yy=diagram_box(s);im.paste(diagrams.render(dict(s['visual'],narrationPart=index),p['phase'],progress,(xx-x,yy-y)),(x,y))
 text(d,(1310,247),{'question':'暂停动手','answer':'答案依据'}.get(s['kind'],'讲解要点'),26,ORANGE);y=310
 for note in p['notes']:text(d,(1310,y),'•',28,ORANGE);y=wrap(d,note,(1342,y),480,29,42)+22
 assert y<(535 if s.get('code') and s.get('visual') else 790),('Notes overflow',s['key'],index)
 steps_y=548 if s.get('code') and s.get('visual') else 780;text(d,(1310,steps_y),f'本页步骤 {index+1} / {len(s["parts"])}',23,BLUE)
 text(d,(65,947),f'本章第 {s["sceneIndex"]} 页',19,MUTED)
 if s['kind']=='question':
  pause=s['leadFrames']+s['speechFrames']+s['sentenceTailFrames']
  if frame>=pause:
   count=max(1,math.ceil((s['durationFrames']-frame)/30));d.rounded_rectangle((1555,820,1838,905),12,fill='#183f50',outline=BLUE,width=2);text(d,(1696,862),f'思考 {count}',40,BLUE,'mm')
 return im
