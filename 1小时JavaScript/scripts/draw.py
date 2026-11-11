import bisect,functools,pathlib,re
from PIL import Image,ImageDraw,ImageFont
from pygments import lex
from pygments.lexers import JavascriptLexer,HtmlLexer
from pygments.token import Token
from highlight_sync import selected_lines
BG='#091421';PANEL='#102237';TEXT='#eff5ff';MUTED='#99afc6';ORANGE='#ffbd68';BLUE='#70cfff';GREEN='#95d9b0'
@functools.lru_cache(64)
def font(n,code=False):return ImageFont.truetype('C:/Windows/Fonts/consola.ttf' if code else 'C:/Windows/Fonts/msyh.ttc',n)
def width(text,n,code=False):return sum(font(n,code and ord(c)<256).getlength(c) for c in text) if code else font(n).getlength(text)
def wrap(text,width,n,code=False):
    rows=[];row=''
    units=re.findall(r'\$\{[^}]+\}|[A-Za-z_$][A-Za-z0-9_$]*|.',text) if code else list(text)
    for ch in units:
        if ch=='\n':rows.append(row);row='';continue
        if row and globals()['width'](row+ch,n,code)>width:rows.append(row);row=''
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
    label(d,(60,24),s['chapter'],32,ORANGE);label(d,(1515,28),'JavaScript · 零基础',26,MUTED)
    label(d,(60,80),s['title'],44);label(d,(62,146),'课程知识点' if s['kind']=='cover' else ('课堂练习' if s['parts'][0].get('think') else '代码与运行结果'),25,MUTED)
    if s['kind']=='cover':
        d.text((95,210),'JavaScript',font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',156),fill=TEXT)
        d.text((100,405),'一小时',font=ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc',100),fill=ORANGE)
        topics=['变量与数据类型','运算符与表达式','条件判断与循环','函数与作用域','数组与数据处理','对象与数据交换','字符串与网页内容','事件与用户输入','异常、异步与模块','综合项目与复盘']
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
    code_bottom=max(813,247+(len(visual)-1)*line_height+48)
    output_top=code_bottom+16
    assert output_top+143<=1056,(s['key'],'code and output overflow')
    d.rounded_rectangle((50,200,1375,code_bottom),18,fill=PANEL,outline='#29445c',width=2)
    label(d,(75,211),s['filename'],23,MUTED,True)
    # Paint every selection background before glyphs, so a later row cannot
    # cover the previous row's Chinese descenders.
    for k,(i,j,row) in enumerate(visual):
        y=247+k*line_height
        if i in selected:
            d.rounded_rectangle((62,y-1,1362,y+line_height-2),5,fill='#24415a',outline=ORANGE,width=1)
    for k,(i,j,row) in enumerate(visual):
        y=247+k*line_height
        if j==0:label(d,(74,y+3),str(i),24,MUTED,True)
        x=122
        for typ,value in lex(row,HtmlLexer() if s['kind']=='html' else JavascriptLexer()):
            value=value.rstrip('\n')
            color=GREEN if typ in Token.Literal.String else ORANGE if typ in Token.Literal.Number else BLUE if typ in Token.Keyword or typ in Token.Name.Builtin else MUTED if typ in Token.Comment else TEXT
            label(d,(x,y),value,34,color,True);x+=width(value,34,True)
    d.rounded_rectangle((50,output_top,1375,output_top+143),15,fill='#0c1d2d',outline='#29445c',width=2)
    label(d,(76,output_top+10),'运行结果' if s['key']!='js-10-05' else '操作检查清单',24,BLUE)
    output=s['output'].replace('\\n','\n') if part.get('showOutput') else '跟随代码执行，稍后对照结果'
    if thinking:output='思考：'+str(max(1,(thinking['end']-f+29)//30))+' 秒'
    rows=[]
    for line in output.splitlines():rows.extend(wrap(line,1220,31))
    # For six short arithmetic outputs use two columns, keeping font size stable.
    if len(rows)>3:
        assert len(rows)<=6,(s['key'],'output rows')
        for j,row in enumerate(rows):label(d,(77+(j//3)*625,output_top+46+(j%3)*30),row,30,GREEN)
    else:
        for j,row in enumerate(rows):label(d,(77,output_top+48+j*29),row,31,GREEN if part.get('showOutput') else MUTED)
    label(d,(1430,208),'本页总结',29,BLUE);y=269
    notes=['先预测程序的结果','逐行跟踪当前值和执行路线','思考结束后查看答案与原因'] if s['parts'][0].get('think') and idx==0 else s['notes']
    for note in notes:
        label(d,(1425,y),'●',18,ORANGE)
        for row in wrap(note,386,27):label(d,(1455,y-3),row,27);y+=39
        y+=21
    label(d,(1430,690),'处理步骤',27,ORANGE)
    flows={
      '01':['编辑代码','执行程序','查看控制台'],
      '02':['确认数据类型','完成转换或运算','得到数值、文字或真假'],
      '03':['读取当前值','检查条件','执行分支或下一轮'],
      '04':['传入参数','执行函数体','返回调用位置'],
      '05':['读取当前元素','回调处理当前项','累计或生成新数组'],
      '06':['按属性名取得数据','沿引用关系更新','保存或转换记录'],
      '07':['准备文字与选择器','读取或生成文字','写入页面元素'],
      '08':['用户提交或点击','检查并更新数据','刷新页面显示'],
      '09':['执行当前步骤','等待或接收后续结果','处理成功结果或错误'],
      '10':['输入与检查','更新并保存记录','刷新列表与总额']}
    flow=flows[s['key'].split('-')[1]]
    for j,t in enumerate(flow):
        yy=744+j*71;d.rounded_rectangle((1425,yy,1865,yy+49),9,fill='#19354b',outline='#41647e')
        label(d,(1450,yy+7),t,26,TEXT if idx or j==0 else MUTED)
        if j<2:label(d,(1628,yy+46),'↓',22,BLUE)
    return im
