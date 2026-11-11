"""Hand-authored phrase to source line and actual execution-state mapping.

Each entry is reviewed against its paragraph. Numeric registers do not advance
by paragraph percentage. Occurrences select real loop iterations explicitly.
"""
EXTRA={
'as-01-02':{0:[('先把三放进AX',[1])]},
'as-01-04':{0:[('先写AX为十六进制一二三四',[1])]},
'as-02-01':{0:[('把七放进AX',[1]),('再把AX复制到BX',[2])]},
'as-02-02':{0:[('因此读一个字得到一二三四',[2])]},
'as-02-03':{0:[('比如BX是零二零零，SI是四',[1,2]),('LEA可以把这种地址计算结果放到寄存器',[3])]},
'as-03-01':{0:[('先把十放进AX',[1]),('再减去十',[2])]},
'as-03-03':{1:[('现在先把低十六位全一加一',[6])]},
'as-03-04':{0:[('这里AL是二十',[1]),('BL是十五',[2]),('乘积三百',[3])]},
'as-03-05':{0:[('这里把一千放进AX',[1]),('除以BL中的三十',[2]),('商三十三放AL',[3])]},
'as-04-03':{0:[('比如AL为八一H',[1]),('用一去测试最低位',[2])]},
'as-04-04':{1:[('逻辑右移得到四零',[2])]},
'as-04-05':{0:[('八位八一H向右循环一位',[2])]},
'as-05-01':{1:[('执行沿着相等路径到达SAME',[6])]},
'as-06-01':{1:[('AX得到二',[3]),('第二轮AX成为四',[3],{'occurrence':2}),('CX减到一',[4],{'occurrence':2}),('第三轮AX成为六',[3],{'occurrence':3}),('CX减到零',[4],{'occurrence':3})]},
'as-06-03':{1:[('每次先把字节放进BL',[4]),('并把BH清零',[5]),('再用整个BX加到AX',[6]),('最后总和十五',[6],{'occurrence':3}),('SI到零二零三',[7],{'occurrence':3}),('CX为零',[8],{'occurrence':3})]},
'as-06-04':{1:[('现在让指针每轮前进二',[5]),('得到六百',[4],{'occurrence':3}),('最后SI停在零二零六',[5],{'occurrence':3}),('CX回到零',[6],{'occurrence':3})]},
'as-06-05':{1:[('完成后，目标区得到ABC三个字符',[5],{'occurrence':3}),('CX为零',[5],{'occurrence':4})]},
'as-07-01':{1:[('现在从SP等于零一零零开始',[1],{'stateIndex':3,'afterLine':None}),('压入AX中的一二三四',[4])]},
'as-07-02':{1:[('现在从AX等于四出发',[1],{'stateIndex':1,'afterLine':None})]},
'as-07-04':{0:[('调用者先压入一个字',[2]),('近CALL再压返回IP',[3]),('子程序又保存旧BP',[6]),('随后让BP对齐当前栈顶',[7])]},
'as-08-01':{1:[('就得到字符五',[2]),('减字符零得到相应数值',[4])]},
'as-08-03':{1:[('依次送出H和I',[3])]},
'as-09-02':{1:[('执行后AX取得一二三四',[1])]},
'as-10-02':{0:[('先从SI指向位置读一个字节到AL',[5]),('再清AH',[6]),('交给ADD',[7])],1:[('现在只追踪总和这条线',[7],{'stateIndex':4,'afterLine':None}),('第一项三让DX成为三',[7]),('第二项五让它成为八',[7],{'occurrence':2}),('第三项七让它成为十五',[7],{'occurrence':3})]},
'as-10-03':{0:[('最大值部分比较当前元素AL与候选BL',[8]),('当前元素小于等于候选，就跳过更新',[9]),('否则把AL复制给BL',[10])],1:[('现在让三、五、七依次与候选比较',[8],{'stateIndex':7,'afterLine':None}),('第一项三把候选从零改为三',[10]),('第二项五更大，候选改为五',[10],{'occurrence':2}),('第三项七更大，候选改为七',[10],{'occurrence':3}),('再用七、五、三测试',[9],{'afterLine':None}),('用五、五、五测试',[9],{'afterLine':None})]},
'as-10-04':{1:[('现在先让AX传入十五并调用输出',[1,2],{'completion':'call-return','afterLine':2}),('随后传入七再调用',[6,7],{'completion':'call-return','afterLine':7})]}}

def apply(chapters):
 for c in chapters:
  for s in c['scenes']:
   if not s.get('code'):continue
   if s['run']=='multiply':s['visual']['regs']=['ax','al','bl']
   if s['key']=='as-07-04':s['visual']['windows'][0][0]=0
   if s['key'] in ['as-05-02','as-05-03']:s['visual']['regs']=['al']
   if s['key']=='as-05-05':s['visual']['regs']=['bx']
   for i,p in enumerate(s['parts']):
    cues={}
    for m in p['moves']:cues[m['anchor']]=dict(anchor=m['anchor'],codeLines=p['codeLines'],afterLine=p['codeLines'][-1],occurrence=1)
    for h in p['highlights']:cues[h['anchor']]=dict(h,afterLine=h['codeLines'][-1],occurrence=1)
    for spec in EXTRA.get(s['key'],{}).get(i,[]):
     phrase,lines,*opts=spec;h=dict(anchor=phrase,codeLines=lines,afterLine=lines[-1],occurrence=1);h.update(opts[0] if opts else {});cues[phrase]=h
    p['highlights']=sorted(cues.values(),key=lambda h:p['text'].find(h['anchor']))
    for h in p['highlights']:assert p['text'].count(h['anchor'])==1,(s['key'],i,h['anchor'])
