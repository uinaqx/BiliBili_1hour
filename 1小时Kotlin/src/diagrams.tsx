import React from 'react';
type Spec={title:string;rows:string[][];foot:string};
const specs:Record<string,Spec>={
 roadmap:{title:'从想法到操作步骤',rows:[['保存成绩'],['判断及格'],['计算平均分']],foot:'一次理解一个具体变化'},
 pipeline:{title:'文件 → 编译 → 运行',rows:[['Main.java'],['javac Main.java'],['java Main']],foot:'写法错误先在编译阶段修正'},
 hello:{title:'显示语句的作用',rows:[['"Hello, Java!"'],['System.out.println'],['Hello, Java!']],foot:'只显示引号里的文字'},
 variable:{title:'变量保存当前值',rows:[['score = 80'],['score = 85'],['当前读取：85']],foot:'赋值以后，跟踪新的值'},
 types:{title:'不同种类的数据',rows:[['int：3','double：82.5'],['boolean：true']],foot:'类型规定能保存什么值'},
 text:{title:'文字与单个字符',rows:[['String："Ana"'],["char：'A'"]],foot:'双引号与单引号用途不同'},
 constant:{title:'固定规则参与判断',rows:[['passLine：60'],['score：80'],['80 >= 60 → true']],foot:'final 变量赋值后不能重新赋值'},
 copy:{title:'先复制值，再各自修改',rows:[['a = 3','b = 8'],['a = b → a 为 8'],['b = 9 → a 仍为 8']],foot:'整数赋值复制当时的值'},
 calculate:{title:'先看括号与优先顺序',rows:[['12 × 3 → 36'],['(2 + 3) × 4'],['5 × 4 → 20']],foot:'括号把想先做的计算圈起来'},
 division:{title:'参与计算的类型很重要',rows:[['7 / 2 → 3'],['7.0 / 2 → 3.5'],['double r = 7 / 2 → 3.0']],foot:'先计算，再把结果保存进变量'},
 condition:{title:'比较得到真假',rows:[['score：80'],['score >= 60'],['结果：true']],foot:'== 比较，= 赋值'},
 update:{title:'逐步更新同一份值',rows:[['score：80'],['score += 5 → 85'],['score++ → 86']],foot:'每一步都从当前值继续'},
 concat:{title:'从左到右观察连接',rows:[['"sum=" + 3 + 5'],['"sum=3" + 5'],['"sum=35"']],foot:'加括号后先算 3 + 5，得到 8'},
 input:{title:'键盘输入进入变量',rows:[['输入：80'],['input.nextInt()'],['score：80']],foot:'先读取，再参与计算'},
 'input-line':{title:'读取一整行文字',rows:[['输入：Ana Lee'],['input.nextLine()'],['name："Ana Lee"']],foot:'本行中的空格也包含在内'},
 'input-lines':{title:'数值之后还有本行剩余',rows:[['80 ↵'],['nextLine() 读完本行'],['下一行：Ana Lee']],foot:'逐行跟踪输入的读取位置'},
 branch:{title:'根据判断选择路线',rows:[['score >= 60 ?'],['true：pass','false：retry']],foot:'只走当前条件对应的一条路'},
 levels:{title:'按顺序判断成绩',rows:[['先看 >= 90'],['不满足，再看 >= 60'],['80 → pass']],foot:'命中分支后不再向下尝试'},
 switch:{title:'按选择值进入分支',rows:[['choice：2'],['case 2：list'],['break：离开 switch']],foot:'default 处理其余选择'},
 for:{title:'重复前先检查条件',rows:[['i = 1'],['i <= 3 ? → 执行'],['i++ → 再检查']],foot:'条件不满足，循环结束'},
 sum:{title:'把每次的值加入总和',rows:[['total：0'],['+1 → 1；+2 → 3'],['+3 → 6']],foot:'累加结果保留到下一次'},
 while:{title:'先判断，再做一次',rows:[['n：3 → 2 → 1'],['每次显示后 n--'],['n = 0：结束']],foot:'循环要有走向结束的变化'},
 do:{title:'至少先做一次',rows:[['先显示文字：zero'],['再判断 n > 0'],['false → 结束']],foot:'n 为 0，条件不成立，仍先做了一次'},
 continue:{title:'跳过本次剩余操作',rows:[['1、2：显示'],['3：continue'],['4、5：继续显示']],foot:'continue 后进入下一轮检查'},
 array:{title:'数组位置从零开始',rows:[['位置 0','位置 1','位置 2'],['60','80 → 85','100']],foot:'scores[1] 访问第二项'},
 'array-length':{title:'长度不等于最后的位置',rows:[['长度：3'],['有效位置：0、1、2'],['最后位置：length - 1']],foot:'new int[3] 的元素初始值为 0'},
 'array-sum':{title:'循环逐项读取数组',rows:[['60 + 80 + 100'],['total：240'],['240 / 3.0 → 80.0']],foot:'i < length 保证位置有效'},
 string:{title:'本例使用英文字符',rows:[['位置：0、1、2'],['A','n','a'],['substring(1, 3) → na']],foot:'结尾位置 3 不包含在结果中'},
 'string-result':{title:'操作返回新的文字',rows:[['name："Ana"'],['toUpperCase() → "ANA"'],['name 仍为 "Ana"']],foot:'比较文字内容使用 equals'},
 method:{title:'给一段操作起名字',rows:[['greet()'],['执行方法里面的操作'],['返回调用位置继续']],foot:'重复调用，可以重复执行'},
 'method-add':{title:'输入两个数，返回一个数',rows:[['add(3, 5)'],['a：3；b：5'],['return 8']],foot:'实参与参数按位置对应'},
 'method-check':{title:'用结果表达一次判断',rows:[['isPassed(59) → false'],['isPassed(60) → true']],foot:'返回类型 boolean 表示真假'},
 scope:{title:'大括号划定使用范围',rows:[['{ int bonus = 5; }'],['范围结束'],['外面不能再用 bonus']],foot:'先声明，再在有效范围内使用'},
 'method-return':{title:'用返回值更新外面的变量',rows:[['score：80'],['addFive(score) → 85'],['score = 返回值']],foot:'方法参数接收传入值的副本'},
 class:{title:'类与实际建立的对象',rows:[['Student 类'],['new Student()'],['姓名 Ana；成绩 80']],foot:'字段保存数据，方法操作数据'},
 objects:{title:'两次 new，两份记录',rows:[['a → Ana：85'],['b → Bo：90']],foot:'修改 a 的记录，不会修改 b'},
 construct:{title:'建立时准备初始数据',rows:[['new Student(80)'],['构造方法接收 80'],['对象中的 score：80']],foot:'构造方法与类同名'},
 privacy:{title:'通过方法使用对象',rows:[['setScore(85)'],['对象内部 score：85'],['getScore() → 85']],foot:'private 字段由类内部管理'},
 references:{title:'第二次 new 建立独立记录',rows:[['a → 学生甲：80'],['b → 学生乙：90']],foot:'原题没有第二次 new：共享同一对象'},
 list:{title:'按先后顺序保存姓名',rows:[['0：Ana','1：Bo'],['size() → 2'],['get(0) → Ana']],foot:'add 可以继续在后面添加'},
 'list-update':{title:'修改已有位置',rows:[['80','90'],['set(0, 85)'],['85','90']],foot:'内容改变，数量仍然为 2'},
 map:{title:'姓名与成绩的对应关系',rows:[['Ana → 80'],['Bo → 90'],['get("Ana") → 80']],foot:'按键查值，不依靠排列位置'},
 'map-default':{title:'保存与查询分开考虑',rows:[['Ana：80 → 85'],['Cy：尚无记录'],['默认返回 0，未录入 Cy']],foot:'containsKey 判断是否存在'},
 'list-remove':{title:'删除后的位置变化',rows:[['0：Ana','1：Bo'],['删除 Ana → 0：Bo'],['再添加 → 0：Bo，1：Cy']],foot:'位置随当前排列变化'},
 exception:{title:'失败时转入处理路线',rows:[['parseInt("abc")'],['NumberFormatException'],['catch 提示 → continue']],foot:'失败后跳过 try 内剩余步骤'},
 validation:{title:'按约定检查成绩范围',rows:[['传入 120'],['超出 0～100 → throw'],['调用处 catch → bad score']],foot:'合格的参数可以正常返回'},
 'exception-routes':{title:'两条路线各自跟踪',rows:[['"abc"：A → C → D'],['"80"：A → B → D']],foot:'只进入实际发生的那条路线'},
 recap:{title:'从当前数据跟踪下一步',rows:[['保存什么？'],['修改谁？选择哪条路？'],['重复何时结束？']],foot:'每次解释一个具体变化'},
 final:{title:'小步骤连成统计程序',rows:[['数组：60、80、100'],['累加：240；平均：80.0'],['level(80.0) → pass']],foot:'自己改数据，预测以后再运行'}
};
export const DataDiagram:React.FC<{type:string;stage:number;sceneKey:string;progress:number;state?:unknown}>=({type,stage,sceneKey,progress})=>{
 let spec=specs[type]??specs.roadmap;
 if(sceneKey==='java-04-a')spec={title:'输入后再计算',rows:[['输入：80'],['score += 5'],['显示：85']],foot:'更换输入，按相同步骤处理'};
 if(sceneKey==='java-05-1')spec={title:'只有条件成立才显示 pass',rows:[['score >= 60 ?'],['true：pass；false：跳过'],['随后都显示 done']],foot:'done 在 if 的大括号之外'};
 if(sceneKey==='java-05-a')spec={title:'把相等的边界包含进来',rows:[['score：60'],['60 >= 60 → true'],['显示：pass']],foot:'原题 60 > 60 为假，会显示 retry'};
 if(sceneKey==='java-07-a')spec={title:'读取有效的最后一项',rows:[['先检查 length > 0'],['last = 3 - 1 = 2'],['scores[2] → 100']],foot:'不访问不存在的位置 3'};
 if(type==='roadmap'&&sceneKey.endsWith('-a')){
  const answers:Record<string,Spec>={
   'java-01-a':{title:'修正缺少的分号',rows:[['补上 println 后面的 ;'],['编译通过'],['运行显示 Hello, Java!']],foot:'编译通过后才开始运行'},
   'java-02-a':specs.copy,'java-03-a':specs.concat,
   'java-04-a':{title:'先读取，再修改',rows:[['输入 80'],['score += 5'],['显示 85']],foot:'输入 60 则显示 65'},
   'java-05-a':{title:'边界值也要包含',rows:[['score：60'],['60 >= 60 → true'],['显示 pass']],foot:'> 与 >= 的等号会改变边界'},
   'java-06-a':specs.sum,
   'java-07-a':{title:'使用有效的最后位置',rows:[['length：3'],['最后位置：3 - 1 = 2'],['读取 100']],foot:'先确认数组非空，再读取最后一项'}
  };spec=answers[sceneKey]??spec;
 }
 const rowY=[51,112,173];
 const units=(text:string)=>Array.from(text).reduce((n,c)=>n+(c.charCodeAt(0)>255?1:.56),0);
 const footLines:string[]=[];let foot='';for(const c of spec.foot){if(units(foot+c)>21){footLines.push(foot);foot='';}foot+=c;}if(foot)footLines.push(foot);
 return <svg viewBox={`0 0 390 ${footLines.length>1?286:270}`} width="100%" role="img" aria-label={spec.title} style={{display:'block',fontFamily:'Microsoft YaHei, sans-serif',overflow:'visible'}}>
  <text x="0" y="24" fontSize="22" fill="#80d4e7">{spec.title}</text>
  {spec.rows.map((row,i)=>{const gap=8,w=(390-gap*(row.length-1))/row.length,active=i<=stage;return <g key={i} opacity={active?1:.32}>
   {i>0&&<path d={`M195 ${rowY[i-1]+43} L195 ${rowY[i]-6} m-4 -4 l4 4 l4 -4`} fill="none" stroke="#80d4e7" strokeWidth="2"/>}
   {row.map((label,j)=><g key={j}><rect x={j*(w+gap)} y={rowY[i]} width={w} height="43" rx="8" fill={active?'#1b334b':'#15263b'} stroke={active?'#7bacc0':'#35516d'} strokeWidth="1.3"/><text x={j*(w+gap)+w/2} y={rowY[i]+28} fontSize={Math.min(row.length===3?19:22,(w-12)/units(label))} textAnchor="middle" fill={active?'#f0f3f7':'#96a9c0'}>{label}</text></g>)}
  </g>})}
  {footLines.map((line,i)=><text key={i} x="0" y={249+i*23} fontSize="18" fill="#a5dfb4">{line}</text>)}
 </svg>;
};
