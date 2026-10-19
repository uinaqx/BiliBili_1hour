import React from 'react';
type Spec={title:string;rows:string[][];foot:string};
const specs:Record<string,Spec>={
 roadmap:{title:'一个能够完成的小任务',rows:[['记录：12、8、5'],['总额：25'],['预算：30；余额：5']],foot:'一次观察一个具体变化'},
 learning:{title:'怎样把看懂变成会写',rows:[['只修改一笔数据'],['先预测新的结果'],['运行，再解释原因']],foot:'练习文件提供完整代码'},
 hello:{title:'把括号里的文字显示出来',rows:[['"Hello, Python!"'],['print(...)'],['Hello, Python!']],foot:'括号和引号分别配对'},
 pipeline:{title:'保存文件，再运行',rows:[['main.py'],['python main.py'],['Hello, Python!']],foot:'命令、代码、结果要分清'},
 variable:{title:'跟踪名字当前对应的值',rows:[['budget：30'],['budget = 40'],['再次读取：40']],foot:'赋值后，从新的当前值继续'},
 types:{title:'不同种类的数据',rows:[['int：30','float：8.5'],['str："tea"','bool：False']],foot:'看起来相似，不一定是同一种数据'},
 'number-text':{title:'先分清数字与文字',rows:[['12 + 8 → 20'],['"12" + "8" → "128"'],['print("spent", 20) → spent 20']],foot:'print 多项内容默认用空格分隔'},
 update:{title:'先计算，再保存新结果',rows:[['spent：12'],['12 + 8 → 20'],['再加 5 → 25']],foot:'+= 在这里把结果交回原名字'},
 rebind:{title:'只给 a 重新赋值',rows:[['a：12','b：12'],['a = 20'],['a：20','b：12']],foot:'b 没有再次被赋值'},
 calculate:{title:'把中间计算说明白',rows:[['12 × 2 → 24'],['total：24'],['30 - 24 → 余额 6']],foot:'括号可以指定先算哪一部分'},
 division:{title:'三种运算分别观察',rows:[['7 / 2 → 3.5'],['7 // 2 → 3；7 % 2 → 1'],['-7 // 2 → -4']],foot:'// 是向下取整，** 是乘方'},
 input:{title:'从输入到显示',rows:[['输入：Ana'],['name："Ana"'],['显示：Hello Ana']],foot:'input 先读到一行字符串'},
 convert:{title:'转换发生在哪一步',rows:[['text："12"'],['int(text) → 12'],['12 + 8 → 20']],foot:'不是所有文字都能转换成整数'},
 format:{title:'把结果填进说明文字',rows:[['spent：20；budget：30'],['f"spent={spent}"'],['spent=20；remaining=10']],foot:'f 字符串的大括号放入计算结果'},
 'input-types':{title:'同一输入，两种操作',rows:[['input() → "12"'],['文字连接 → "128"'],['转成整数再相加 → 20']],foot:'先判断当前数据是什么类型'},
 comparison:{title:'比较的结果是真或假',rows:[['spent：25；budget：30'],['>：False；==：False'],['非负并且不超预算：True']],foot:'and 同时满足；or 至少满足一个'},
 branch:{title:'这次选择超预算路线',rows:[['35 > 30 → True'],['显示 over，跳过 else'],['结构外继续显示 done']],foot:'缩进标明每条操作属于哪里'},
 levels:{title:'先检查负数，再比较预算',rows:[['spent：-5'],['-5 < 0 → True'],['显示 invalid']],foot:'选中后不再尝试本组其他分支'},
 boundary:{title:'把相等的边界包含进来',rows:[['spent：30；budget：30'],['30 <= 30 → True'],['显示 within']],foot:'原题 30 < 30 为假，会显示 over'},
 for:{title:'范围包含开始，不包含结束',rows:[['range(1, 4)'],['依次得到：1、2、3'],['4 不包含，循环结束']],foot:'每轮执行同一组缩进内的步骤'},
 sum:{title:'总和逐步累加',rows:[['total：0'],['加 1 → 1；加 2 → 3'],['加 3 → 6']],foot:'初始化在循环外，只做一次'},
 while:{title:'先判断，再重复一轮',rows:[['remaining：3 → 2 → 1'],['每轮显示后减少 1'],['变成 0，条件为 False']],foot:'明确什么变化能让循环结束'},
 break:{title:'在显示 4 之前离开循环',rows:[['1、2、3：显示'],['4：break'],['当前循环结束']],foot:'break 结束当前这一层循环'},
 continue:{title:'跳过本轮，再准备下一轮',rows:[['1、2：显示'],['3：continue'],['4、5：继续显示']],foot:'不是结束整个循环'},
 list:{title:'位置与数量分别看',rows:[['0：12','1：8','2：5'],['expenses[-1] → 5'],['len(expenses) → 3']],foot:'数量 3，不代表位置 3 存在'},
 'list-update':{title:'按操作跟踪当前内容',rows:[['位置 1：8 → 10'],['追加 6：暂时有 4 项'],['pop 取出 6：剩 3 项']],foot:'最终列表为 [12, 10, 5]'},
 slice:{title:'读取一段连续内容',rows:[['原列表：[12, 8, 5, 10]'],['[1:3] → [8, 5]'],['[:2] → [12, 8]']],foot:'读取切片，原列表内容不变'},
 'list-sum':{title:'逐项累加与直接求和',rows:[['12 + 8 + 5'],['循环结果：25'],['sum(expenses) → 25']],foot:'先理解过程，再使用现成工具'},
 alias:{title:'一份共享，另一份独立',rows:[['a、b → [12, 8]'],['c → [12, 8, 5]']],foot:'本例 copy 创建独立的一层列表'},
 'list-last':{title:'先确认有内容，再读取',rows:[['len(expenses) > 0'],['expenses[-1]'],['最后一笔：5']],foot:'空列表没有可读取的最后一项'},
 string:{title:'本页按英文字符练习',rows:[['0：P','1：y','…','5：n'],['word[-1] → n'],['word[0:2] → Py']],foot:'Python 共 6 个字符位置'},
 'string-clean':{title:'处理后得到新字符串',rows:[['text：" Tea "'],['strip() → "Tea"'],['lower() → "tea"']],foot:'text 原来的两端空格仍然保留'},
 'split-join':{title:'拆开与连接的两个方向',rows:[['"tea,bread,tea"'],['拆成 3 项字符串列表'],['"tea | bread | tea"']],foot:'split 拆开，join 重新连接'},
 'string-result':{title:'接住返回的大写结果',rows:[['text："tea"'],['upper() → 新结果 "TEA"'],['upper_text："TEA"']],foot:'原题没有接住，text 仍为小写'},
 dict:{title:'商品名与价格的对应关系',rows:[['tea → 8','bread → 12'],['prices["tea"] → 8'],['当前有 2 个键']],foot:'按键查询，不是按位置编号查找'},
 'dict-update':{title:'新增、修改和删除不同',rows:[['tea：8 → 10'],['新增 milk；删除 bread'],['剩余：tea、milk']],foot:'当前价格为 10、6，共 2 项'},
 'dict-missing':{title:'查询 cake：当前没有记录',rows:[['"cake" in prices → False'],['get("cake") → None'],['get("cake", 0) → 0']],foot:'备用值并不表示录入了真实价格'},
 containers:{title:'先按用途认识容器',rows:[['tuple：(3, 5)，按位置读取'],['set：tea、bread，去重后 2 项'],['空集合 set() → 数量 0']],foot:'集合不要依赖显示的排列顺序'},
 'dict-answer':{title:'先改旧值，再添新键',rows:[['tea：8 → 10'],['bread：12'],['数量：2；tea：10']],foot:'同一键不自动保留多次价格历史'},
 function:{title:'定义步骤，调用时执行',rows:[['show_title()'],['执行 print("Budget")'],['回到调用处继续']],foot:'本页调用两次，所以显示两次'},
 'function-add':{title:'输入、计算、返回',rows:[['add(12, 8)'],['left：12；right：8'],['返回 20 → total']],foot:'return 返回，print 向屏幕显示'},
 default:{title:'实际参数决定采用的预算',rows:[['within(25) → True'],['within(35) → False'],['within(35, 40) → True']],foot:'省略预算时才采用默认值 30'},
 scope:{title:'看名字所在的使用范围',rows:[['函数外 fee：99'],['函数内 fee：2 → 返回 14'],['函数外 fee 仍然为 99']],foot:'相同名字不表示同一个局部位置'},
 'function-return':{title:'调用处明确保存结果',rows:[['spent：12'],['add_fee(spent) → 14'],['spent = 返回值 → 14']],foot:'原题没有保存，外面仍然是 12'},
 module:{title:'从模块里找到需要的工具',rows:[['math.sqrt(9) → 3.0'],['math.ceil(12.3) → 13'],['导入 sqrt 后：sqrt(16) → 4.0']],foot:'math 是 Python 自带的标准库'},
 'own-module':{title:'两个文件各自负责一件事',rows:[['budget_tools.py：定义'],['main.py：导入并调用'],['within(25, 30) → True']],foot:'本例把两个文件放在同一目录'},
 'file-write':{title:'写入一份简单的记录',rows:[['w：覆盖原有内容'],['文件保存两行：12、8'],['离开 with，文件关闭']],foot:'expenses.txt 位于练习工作目录'},
 'file-read':{title:'文字逐行变成参与计算的数',rows:[['文件两行："12"、"8"'],['strip → int → 加入总和'],['total：20']],foot:'r 读取已经存在的文件'},
 'file-append':{title:'追加保留原来的记录',rows:[['初始：12，然后换行'],['a：追加 8 和换行'],['最终两行：12、8']],foot:'原题用 w，旧内容被覆盖，只剩 8'},
 exception:{title:'转换失败时改变路线',rows:[['输入："abc"'],['int 转换失败 → ValueError'],['except 提示，然后显示 done']],foot:'try 内剩下的正常显示被跳过'},
 validation:{title:'不能按约定处理就报告失败',rows:[['传入金额：-5'],['raise ValueError'],['显示 negative amount']],foot:'普通预算比较仍可使用 if'},
 'exception-routes':{title:'两种输入，两条路线',rows:[['"abc"：A → C → D'],['"12"：A → B → D']],foot:'只经过这次实际满足的路线'},
 recap:{title:'逐步回答几个具体问题',rows:[['现在是什么数据？'],['下一条操作改变了谁？'],['返回值有没有被使用？']],foot:'每次只跟踪一个可以解释的变化'},
 final:{title:'把基础连成开销小助手',rows:[['12 + 8 + 5 → 总额 25'],['within(25, 30) → True'],['余额：30 - 25 = 5']],foot:'改一笔数据，再预测新的结果'}
};
export const DataDiagram:React.FC<{type:string;stage:number;sceneKey:string;progress:number}>=({type,stage})=>{
 const spec=specs[type]??specs.roadmap;const rowY=[51,112,173];
 const units=(text:string)=>Array.from(text).reduce((n,c)=>n+(c.charCodeAt(0)>255?1:.56),0);
 const footLines:string[]=[];let foot='';for(const c of spec.foot){if(units(foot+c)>21){footLines.push(foot);foot='';}foot+=c;}if(foot)footLines.push(foot);
 return <svg viewBox={`0 0 390 ${footLines.length>1?286:270}`} width="100%" role="img" aria-label={spec.title} style={{display:'block',fontFamily:'Microsoft YaHei, sans-serif',overflow:'visible'}}>
  <text x="0" y="24" fontSize="22" fill="#80d4e7">{spec.title}</text>
  {spec.rows.map((row,i)=>{const gap=8,w=(390-gap*(row.length-1))/row.length,active=i<=stage;return <g key={i} opacity={active?1:.32}>
   {i>0&&<path d={`M195 ${rowY[i-1]+43} L195 ${rowY[i]-6} m-4 -4 l4 4 l4 -4`} fill="none" stroke="#80d4e7" strokeWidth="2"/>}
   {row.map((label,j)=><g key={j}><rect x={j*(w+gap)} y={rowY[i]} width={w} height="43" rx="8" fill={active?'#1b334b':'#15263b'} stroke={active?'#7bacc0':'#35516d'} strokeWidth="1.3"/><text x={j*(w+gap)+w/2} y={rowY[i]+28} fontSize={Math.min(row.length>2?19:22,(w-12)/units(label))} textAnchor="middle" fill={active?'#f0f3f7':'#96a9c0'}>{label}</text></g>)}
  </g>})}
  {footLines.map((line,i)=><text key={i} x="0" y={249+i*23} fontSize="18" fill="#a5dfb4">{line}</text>)}
 </svg>;
};
