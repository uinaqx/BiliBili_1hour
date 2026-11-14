import bisect,functools,pathlib,re
from PIL import Image,ImageDraw,ImageFont
from pygments import lex
from pygments.lexers import SqlLexer
from pygments.token import Token
from highlight_sync import selected_lines
BG='#091421';PANEL='#102237';TEXT='#eff5ff';MUTED='#99afc6';ORANGE='#ffbd68';BLUE='#70cfff';GREEN='#95d9b0'
# Original Rust 2 style: a warm translucent wash, a 3px orange left bar,
# and an orange active line number. No enclosing outline or blue selection box.
HIGHLIGHT_ORANGE='#ffba78'
HIGHLIGHT_BG=tuple(round(a*.085+b*.915) for a,b in zip((255,186,120),(16,34,55)))
@functools.lru_cache(64)
def font(n,code=False):return ImageFont.truetype('C:/Windows/Fonts/consola.ttf' if code else 'C:/Windows/Fonts/msyh.ttc',n)
def width(text,n,code=False):return sum(font(n,code and ord(c)<256).getlength(c) for c in text) if code else font(n).getlength(text)
def wrap(text,width,n,code=False):
    rows=[];row=''
    units=re.findall(r'\$\{[^}]+\}|[A-Za-z_$][A-Za-z0-9_$]*|[\s\S]',text)
    for ch in units:
        if ch=='\n':rows.append(row);row='';continue
        limit=width+40 if code and ch in ');,]}' else width
        if row and globals()['width'](row+ch,n,code)>limit:rows.append(row);row=''
        row+=ch
    if row:rows.append(row)
    return rows
def label(d,xy,text,n=28,color=TEXT,code=False):
    if not code:d.text(xy,text,font=font(n),fill=color);return
    x,y=xy
    for c in text:
        f=font(n,ord(c)<256);baseline=y+font(n,True).getmetrics()[0]+max(1,round(n*.18));d.text((x,baseline),c,font=f,fill=color,anchor='ls');x+=f.getlength(c)
def render(s,f):
    im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im);idx=max(0,bisect.bisect_right(s.get('partFrames',[0]),f)-1);part=s['parts'][idx]
    thinking=next((x for x in s.get('thinkFrames',[]) if x['start']<=f<x['end']),None)
    label(d,(60,24),s['chapter'],32,ORANGE);label(d,(1515,28),'SQL · 零基础',26,MUTED)
    cover=s['kind']=='cover' and idx==0
    label(d,(60,80),s['title'],44);label(d,(62,146),'课程知识点' if cover else ('课堂练习' if s['parts'][0].get('think') else '代码与运行结果'),25,MUTED)
    if cover:
        d.text((95,190),'SQL',font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',200),fill=TEXT)
        d.text((100,405),'一小时',font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',100),fill=ORANGE)
        topics=['数据库与基础查询','条件筛选与空值','排序、分页与表达式','聚合统计与分组','多表连接','子查询与公用表表达式','建表与约束','数据增删改查','事务与索引','窗口函数与综合报表']
        for i,t in enumerate(topics):
            x=100+(i//5)*880;y=575+(i%5)*72;label(d,(x,y),'●',25,ORANGE);label(d,(x+42,y-2),t,34)
        return im
    code=s.get('answerCode') if idx and s.get('answerCode') else s['code']
    selected=selected_lines(s,f);visual=[]
    for i,line in enumerate(code.splitlines(),1):
        rows=wrap(line,1190,34,True) or ['']
        visual.extend((i,j,row) for j,row in enumerate(rows))
    assert len(visual)<=16,(s['key'],'code rows',len(visual))
    line_height=40
    code_bottom=max(668,247+(len(visual)-1)*line_height+48)
    output_top=code_bottom+16
    assert output_top+186<=974,(s['key'],'code and output overflow')
    d.rounded_rectangle((50,200,1375,code_bottom),18,fill=PANEL,outline='#29445c',width=2)
    label(d,(75,211),s['filename'],23,MUTED,True)
    # Paint every selection background before glyphs, so a later row cannot
    # cover the previous row's Chinese descenders.
    for k,(i,j,row) in enumerate(visual):
        y=247+k*line_height
        if i in selected:
            d.rectangle((62,y,1362,y+line_height-1),fill=HIGHLIGHT_BG)
            d.rectangle((62,y,64,y+line_height-1),fill=HIGHLIGHT_ORANGE)
    for k,(i,j,row) in enumerate(visual):
        y=247+k*line_height
        if j==0:label(d,(74,y+3),str(i),24,HIGHLIGHT_ORANGE if i in selected else '#6e829e',True)
        x=122
        for typ,value in lex(row,SqlLexer()):
            value=value.rstrip('\n')
            color=GREEN if typ in Token.Literal.String else ORANGE if typ in Token.Literal.Number else BLUE if typ in Token.Keyword or typ in Token.Name.Builtin else MUTED if typ in Token.Comment else TEXT
            label(d,(x,y),value,34,color,True);x+=width(value,34,True)
    d.rounded_rectangle((50,output_top,1375,output_top+186),15,fill='#0c1d2d',outline='#29445c',width=2)
    label(d,(76,output_top+10),'运行结果',24,BLUE)
    output=s['output'].replace('\\n','\n') if part.get('showOutput') else '跟随代码执行，稍后对照结果'
    if thinking:output='思考：'+str(max(1,(thinking['end']-f+29)//30))+' 秒'
    table=s.get('outputTable') if part.get('showOutput') and not thinking else None
    if table:
        columns=table[0]
        rows=table[1:]
        if len(rows)>3:
            row_bands=[rows[:3],rows[3:]]
        else:
            row_bands=[rows]
        band_width=1220//len(row_bands)
        for band,items in enumerate(row_bands):
            x0=76+band*band_width
            preferred=[max(width(str(row[j]),27,True) for row in [columns,*items])+24
                       for j in range(len(columns))]
            available=band_width-16
            scale=min(1,available/sum(preferred))
            cells=[int(v*scale)+(available-int(sum(preferred)*scale))//len(columns) for v in preferred]
            positions=[x0+sum(cells[:j]) for j in range(len(cells))]
            for j,col in enumerate(columns):
                size=next(n for n in range(27,12,-1) if width(col,n,True)<cells[j]-8)
                label(d,(positions[j],output_top+40),col,size,BLUE,True)
            d.line((x0,output_top+79,x0+band_width-20,output_top+79),fill='#29445c')
            for i,row in enumerate(items):
                for j,value in enumerate(row):
                    size=next(n for n in range(31,12,-1) if width(value,n,True)<cells[j]-8)
                    label(d,(positions[j],output_top+81+i*32),value,size,GREEN,True)
    else:
        for i,line in enumerate(wrap(output,1220,31)):
            label(d,(76,output_top+52+i*32),line,31,GREEN if part.get('showOutput') else MUTED)
    label(d,(1430,208),'本页总结',29,BLUE);y=269
    notes=['先预测程序的结果','逐行跟踪当前值和执行路线','思考结束后查看答案与原因'] if s['parts'][0].get('think') and idx==0 else s['notes']
    for note in notes:
        label(d,(1425,y),'●',18,ORANGE)
        for row in wrap(note,394,26):label(d,(1455,y-3),row,26);y+=36
        y+=16
    assert y<=691,(s['key'],'summary overlaps flow',y)
    label(d,(1430,690),'处理步骤',27,ORANGE)
    flows={
        '01':['找到来源表','决定要显示的列','执行查询并核对'],
        '02':['逐行读取条件用到的值','判断条件是否成立','保留满足条件的行'],
        '03':['为每行计算结果值','按指定键排序','选择要看的行数'],
        '04':['按条件筛选原始记录','按指定字段分组并汇总','筛选和排序汇总结果'],
        '05':['确定左表和右表','按 ON 条件匹配记录','选择要展示的字段'],
        '06':['先整理中间查询','给结果一个可读的名字','完成外层筛选或统计'],
        '07':['确定字段及数据类型','声明主键和业务约束','用数据检查约束'],
        '08':['确认要写入的数据','用条件定位修改目标','查询写入后的结果'],
        '09':['验证修改范围','提交或回滚事务','查看结果或查询计划'],
        '10':['先按需求整理基础数据','按分区计算和排序','核对报表与边界记录']}
    flow=flows[s['key'].split('-')[1]]
    for j,t in enumerate(flow):
        yy=744+j*71;d.rounded_rectangle((1425,yy,1865,yy+49),9,fill='#19354b',outline='#41647e')
        label(d,(1450,yy+7),t,26,TEXT if idx or j==0 else MUTED)
        if j<2:label(d,(1628,yy+46),'↓',22,BLUE)
    return im
