"""Modern dual-architecture frames; persistent authored selection and real CPU state."""
import functools,json,math,pathlib,re
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path(__file__).resolve().parents[1];BG='#09172a';PANEL='#10243a';TEXT='#eff5ff';MUTED='#9fb2ca';BLUE='#70cfff';ORANGE='#ffbd68';GREEN='#8fe0b2';GRID='#29465f'
@functools.lru_cache(32)
def font(n):return ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',n)
@functools.lru_cache(12)
def mono(n):return ImageFont.truetype('C:/Windows/Fonts/consola.ttf',n)
@functools.lru_cache(1)
def traces():return json.loads((ROOT/'build/execution-data.json').read_text(encoding='utf8'))
def display(s):
 s=re.sub('[⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]+',lambda m:'^('+m.group().translate(str.maketrans('⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻','0123456789+-'))+')',str(s))
 return re.sub('[₀₁₂₃₄₅₆₇₈₉]+',lambda m:'_'+m.group().translate(str.maketrans('₀₁₂₃₄₅₆₇₈₉','0123456789')),s)
def text(d,xy,s,n=30,c=TEXT,anchor='lt'):d.text(xy,display(s),font=font(n),fill=c,anchor=anchor)
def wrap(d,s,xy,width,n=28,step=38,c=TEXT):
 x,y=xy;units=[]
 for t in re.findall(r'0x[0-9a-fA-F]+|\d+(?:\.\d+)?(?:字节|KiB|MB|bit)?|[A-Za-z_][A-Za-z_0-9.]*|.',display(s).rstrip('。')):
  if t in '，。；：、）》】' and units:units[-1]+=t
  else:units.append(t)
 row=''
 for t in units:
  if row and font(n).getlength(row+t)>width:text(d,(x,y),row,n,c);y+=step;row=''
  assert font(n).getlength(t)<=width,t;row+=t
 if row:text(d,(x,y),row,n,c);y+=step
 return y
def current(s,f):
 p=next((p for p in reversed(s['parts']) if p['begin']<=f),s['parts'][0])
 if p.get('cues'):
  cue=next((x for x in reversed(p['cues']) if x['begin']<=f),p['cues'][0]);return dict(p,**{k:cue[k] for k in ['codeLines','stateIndex','motion']})
 return p
def cover(s):
 im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im);text(d,(85,65),'从同一个任务出发 · 读懂两套64位指令',32,ORANGE);text(d,(78,145),'现代汇编',112);text(d,(85,300),'x86-64 × AArch64',77,ORANGE)
 chapters=['现代汇编与两套64位架构','寄存器、位宽与数据表示','内存访问与地址计算','算术运算、位操作与条件码','比较、选择与循环','数组、字符串与数据布局','函数参数、调用与返回','寄存器保护、栈对齐与Windows','机器码、调试与系统接口','双架构综合实践与回顾']
 for i,label in enumerate(chapters):
  x=88+(i//5)*910;y=498+(i%5)*84;d.ellipse((x,y+13,x+16,y+29),fill=ORANGE);text(d,(x+34,y),label,31)
 text(d,(85,990),'完整画面版 · 待匹配新版讲稿的配音' if not s.get('audio') else '同一个任务 · 两套架构 · 实际指令执行',25,MUTED);return im
TOKEN=re.compile(r';.*|//.*|\b(?:mov|movz|movk|movzx|movsx|lea|add|adds|sub|subs|cmp|test|xor|and|or|shl|shr|sar|lsl|lsr|asr|mul|imul|div|idiv|sdiv|udiv|msub|cqo|jmp|jge|jz|jnz|je|seta|setl|cmova|csel|cset|cbz|ldr|str|ldrb|ldrsb|stp|ldp|push|pop|call|bl|ret|inc|dec|adr|nop)\b|\bb(?:\.\w+)?\b|0x[0-9a-fA-F]+|#?-?\d+|\b(?:r(?:ax|bx|cx|dx|si|di|bp|sp|ip|[89]|1[0-5])|e(?:ax|bx|cx|dx)|al|cl|dl|[xw](?:[0-9]|[12][0-9]|30)|xzr|sp)\b',re.I)
def code_line(d,x,y,s):
 at=0
 for m in TOKEN.finditer(s):
  d.text((x,y),s[at:m.start()],font=mono(34),fill=TEXT);x+=mono(34).getlength(s[at:m.start()]);t=m.group();color=MUTED if t.startswith((';','//')) else ORANGE if t[0].isdigit() or t[0] in '#-' else BLUE;d.text((x,y),t,font=mono(34),fill=color);x+=mono(34).getlength(t);at=m.end()
 d.text((x,y),s[at:],font=mono(34),fill=TEXT)
def cpu(d,s,p,f):
 st=traces()[s['run']]['snapshots'][p['stateIndex']];x=1300;y=670;w=540
 text(d,(x+8,y+4),'实际执行 · 本步完成后的状态',19,ORANGE);text(d,(x+w-5,y+7),f'第{st["step"]}步',18,MUTED,'rt')
 inst=st['instruction'];d.text((x+8,y+34),inst,font=mono(20),fill=BLUE)
 m=p['motion'];progress=max(0,min(1,(f-m['begin'])/(m['end']-m['begin']))) if m else 1;yy=y+64;d.line((x+10,yy,x+w-10,yy),fill=GRID,width=3);xx=x+12+(w-26)*progress;d.ellipse((xx-4,yy-4,xx+4,yy+4),fill=ORANGE)
 regs=s['regs'];assert len(regs)<=4
 for i,name in enumerate(regs):
  xx=x+8+(i%2)*267;yy=y+82+(i//2)*62;d.rounded_rectangle((xx,yy,xx+255,yy+55),6,fill='#19364b',outline=GRID,width=1);text(d,(xx+10,yy+4),name.upper(),18,MUTED);value='0x'+format(st['registers'][name],'X');assert mono(21).getlength(value)<236;d.text((xx+10,yy+27),value,font=mono(21),fill=GREEN)
 flags='  '.join(k.upper()+'='+str(v) for k,v in st['flags'].items())
 if s['arch']=='x64' and st['instruction'].startswith(('div ','idiv ')):flags='CF/ZF/SF/OF：本指令未定义'
 text(d,(x+10,y+212),flags,20,ORANGE)
def concepts(d,s,p):
 if s['diagram']=='borrow':
  boxes=[('同一个比较','1 − 2'),('x86-64','CF = 1：需要借位'),('AArch64','C = 0：需要借位')]
 elif s['diagram']=='arguments':boxes=[('System V AMD64','RDI RSI RDX RCX R8 R9'),('AAPCS64','X0 X1 X2 X3 X4 X5 X6 X7'),('Windows x64','RCX RDX R8 R9')]
 elif s['diagram']=='syscalls':boxes=[('Linux x86-64','RAX=1 → SYSCALL → write'),('Linux AArch64','X8=64 → SVC #0 → write'),('平台接口','按目标OS准备调用号和参数')]
 elif s['diagram']=='stack':boxes=[('System V AMD64','CALL前对齐 → 栈中返回地址'),('AAPCS64','SP对齐 → X30保存接续位置'),('Windows x64','对齐 + 32字节影子空间')]
 elif s['diagram']=='statistics':boxes=[('读取','uint32_t：3、5、7'),('运算','累计总和；更新无符号最大值'),('结果','总和15；最大值7')]
 else:
  labels={'layers':[('指令集','寄存器、指令与编码'),('ABI','参数、返回值与保护责任'),('操作系统','进程、内存与系统服务')],'tools':[('汇编','源码 → 机器码/目标文件'),('链接','符号 → 程序布局'),('调试','当前指令 → 寄存器与内存')],'debug':[('汇编阶段','语法、位宽与操作数组合'),('执行阶段','地址、映射与当前输入'),('结果阶段','数值解释、路径与边界')],'tests':[('入口','长度0与空数组'),('路径','相等、下降与候选保持'),('位宽','大数与64位累计')]}
  boxes=labels.get(s['diagram'],[('运行背景','架构、ABI与OS'),('数据与控制','输入 → 指令 → 状态'),('功能核对','结果、边界与保持项')])
 for i,(a,b) in enumerate(boxes):
  yy=320+i*150;d.rounded_rectangle((112,yy,1208,yy+116),12,fill='#19364b',outline=GRID,width=2);text(d,(142,yy+13),a,27,ORANGE);end=wrap(d,b,(145,yy+56),1015,34,43);assert end<yy+115
def render(s,f):
 p=current(s,f)
 if s['key']=='ma-01-01':
  im=cover(s);caption(im,s,f);return im
 im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im);d.rounded_rectangle((60,215,1260,925),18,fill=PANEL,outline=GRID,width=2);d.rounded_rectangle((1280,215,1860,925),18,fill=PANEL,outline=GRID,width=2)
 text(d,(64,35),'现代汇编 · '+s['chapterKey'],25,ORANGE);text(d,(64,88),s['chapter'],43);text(d,(64,157),s['title'],29,BLUE);text(d,(1850,40),'x86-64 · AArch64',25,MUTED,'rt')
 assert font(43).getlength(s['chapter'])<1640
 if s['code']:
  arch='x86-64 · NASM · '+('Windows x64' if s['run'].startswith('x_win') else 'System V AMD64') if s['arch']=='x64' else 'AArch64 · A64 · AAPCS64'
  text(d,(92,231),arch,21,MUTED)
  for i,line in enumerate(s['code'],1):
   yy=270+(i-1)*39;assert yy+37<=805 and mono(34).getlength(line)<1080,(s['key'],i,line)
   if i in p['codeLines']:d.rounded_rectangle((80,yy-4,1240,yy+35),5,fill='#26374b');d.rectangle((80,yy-4,85,yy+35),fill=ORANGE)
   d.text((94,yy),f'{i:02}',font=mono(23),fill=MUTED);code_line(d,145,yy,line)
  d.line((90,816,1230,816),fill=GRID,width=2);text(d,(92,828),'完整运行后的检查',21,BLUE)
  final=traces()[s['run']]['snapshots'][-1];from examples import CASES
  results=[]
  for name in CASES[s['run']]['expected']:
   value={**final['registers'],**final['flags']}[name];value=value-(1<<64) if value>=1<<63 else value;results.append(name.upper()+'='+str(value))
  if not results:results=['取得标签地址；按实际指令长度定位']
  line='；'.join(results);n=29 if font(29).getlength(line)<1110 else 24;assert font(n).getlength(line)<1110,(s['key'],line);text(d,(92,865),line,n,GREEN)
  cpu(d,s,p,f)
 elif s['kind'] in ['question','answer']:
  text(d,(108,251),'独立判断' if s['kind']=='question' else '结果与原因',28,ORANGE)
  for i,item in enumerate(s['points']):
   yy=325+i*130;d.rounded_rectangle((95,yy-5,1225,yy+110),9,fill='#19364b');end=wrap(d,item,(125,yy+17),1060,34,46);assert end<yy+110,(s['key'],i)
 else:concepts(d,s,p)
 text(d,(1310,247),'解题提示' if s['kind']=='question' else '答案总结' if s['kind']=='answer' else '本页总结',26,ORANGE);yy=300
 for item in s['points']:
  text(d,(1307,yy),'•',26,ORANGE);yy=wrap(d,item,(1340,yy),480,27,37)+14
 assert yy<(656 if s['code'] else 820),('Summary overflow',s['key'],yy)
 text(d,(65,947),'完整画面版 · 待新配音' if not s.get('audio') else '现代汇编 · NASM / A64 · 代码与实际执行状态',20,MUTED)
 if s['thinkStart'] is not None and f>=s['thinkStart']:
  remaining=max(1,math.ceil((s['durationFrames']-f)/30));d.rounded_rectangle((1560,825,1838,904),10,fill='#193f50',outline=BLUE,width=2);text(d,(1699,864),'思考 '+str(remaining),37,BLUE,'mm')
 caption(im,s,f);return im

def caption(im,s,f):
 if not s.get('subtitles'):return
 cap=next((c for c in s.get('captions',[]) if c['begin']<=f<c['end']),None)
 if cap is None:return
 d=ImageDraw.Draw(im);label=display(cap['text']);n=34
 while n>26 and font(n).getlength(label)>1720:n-=1
 assert font(n).getlength(label)<=1720,(s['key'],'Caption overflow',label)
 width=font(n).getlength(label)+70;d.rounded_rectangle((960-width/2,994,960+width/2,1068),12,fill='#07101d');text(d,(960,1030),label,n,TEXT,'mm')
