from author import chapter,page
c=chapter('联合类型与类型收窄')
page(c,'字面量类型列出允许的值','''type Status = "pending" | "paid";
function label(status: Status): string {
  return status === "paid" ? "已付款" : "待付款";
}
console.log(label("paid"));
console.log(label("pending"));''','已付款\n待付款',['字面量类型把范围缩小到具体值','联合类型列出几种允许状态','参数调用按允许值检查','条件表达式为状态选择显示文字'],
 '[1]付款状态通常只有几个固定选项。这里把pending和paid两个具体字符串连接起来，给这组允许值起名Status。它们表示待付款和已付款。这样的类型比任意字符串更贴近业务需要，编辑器能够直接提示可用选项，也能检查状态单词有没有拼错。先列出实际允许的情况，再写处理逻辑，规则会更清楚。',
 '[2,3]label接收Status，用严格相等检查是否为paid，为真就返回已付款，否则返回待付款。[5]交入paid，得到已付款。[6]交入pending，得到待付款。问号和冒号组成条件表达式，在两种结果之间选一个值。我们让状态范围和显示函数使用同一份约定，新增状态时，也能沿着类型和处理函数一起检查。')
page(c,'typeof 把联合类型分成两条路线','''function format(value: string | number): string {
  if (typeof value === "number") {
    return value.toFixed(1);
  }
  return value.toUpperCase();
}
console.log(format(12));
console.log(format("tea"));''','12.0\nTEA',['参数先允许 string 或 number','typeof 条件确认数字分支','数字分支可调用 toFixed','剩余字符串分支可调用 toUpperCase'],
 '[1]format准备同时接收文字和数字，所以参数写成两者的联合类型。[2]函数先通过typeof检查当前值是不是number。[3]进入这个分支以后，工具就把value按数字处理，可以调用toFixed，整理为一位小数。我们把根据条件缩小可能范围的过程叫作类型收窄，它让每条分支获得与实际情况对应的操作能力。',
 '[5]数字分支已经返回，来到下面这一行时，剩下的是字符串情况，因此可以调用转大写的方法。[7]交入十二，返回文字十二点零。[8]交入tea，返回大写TEA。这里运行时的条件判断和检查阶段的类型分析配合在一起。遇到联合类型，先列出可能有哪些值，再用清楚的判断把它们分开，往往就能顺着分支写出正确操作。')
page(c,'可选链与空值处理','''type User = {name: string; note?: string};
function noteLength(user: User | null): number {
  return user?.note?.length ?? 0;
}
console.log(noteLength({name: "小林", note: "午餐"}));
console.log(noteLength({name: "小林"}));
console.log(noteLength(null));''','2\n0\n0',['?. 在当前对象有值时继续读取','可选属性也可继续使用可选链','?? 为读取不到的情况提供默认值','本例统一返回数字长度'],
 '[1,2]用户可能还没有选中，所以参数允许User或null；用户对象本身也可能省略备注。[3]可选链把这两层情况连起来：user有值时读取note，note有值时再读取length，缺少其中一层时交出undefined。两个问号再把这种空结果整理为零。沿着对象到属性的路线逐层观察，就能读懂这一条表达式。',
 '[5]第一处调用提供两字备注午餐，得到长度二。[6]第二处没有备注，采用零。[7]第三处交入null，同样采用零。这样函数出口始终提供数字，调用者就能继续进行数值计算。需要对不同空状态给出不同提示时，也可以改写为几条if，分别返回说明。根据当前页面或接口的需求，选择清楚的处理路线即可。')
page(c,'用标签区分不同形状','''type Result =
  | {ok: true; amount: number}
  | {ok: false; message: string};
function show(result: Result): string {
  if (result.ok) return `${result.amount}元`;
  return result.message;
}
console.log(show({ok: true, amount: 12}));
console.log(show({ok: false, message: "请重新输入"}));''','12元\n请重新输入',['联合成员用 ok 字段区分','ok 为 true 时读取 amount','ok 为 false 时读取 message','相关字段随标签一起收窄'],
 '[1,2,3]如果成功结果和失败结果包含不同字段，可以让它们共享一个标签。这里ok为真时，记录amount；ok为假时，记录message。每一种情况都把标签和相关数据放在同一个对象里，这样类型能够表达它们之间的联系。读取结果时，先看标签，再沿对应的数据形状往下走。',
 '[4,5]show函数检查result点ok，进入成功路线就能读取金额，整理成十二元。[6]其余路线读取message，返回输入提示。[8,9]下面两次调用分别展示成功和失败。这种带标签的联合类型适合表单检查、网络请求和任务状态。后面增加加载中或空列表等状态时，也可以给它们各自安排清楚的标签和字段。')
page(c,'类型断言与真正的数据转换','''const raw: unknown = "12";
const text = raw as string;
const amount = Number(text);
console.log(typeof text);
console.log(typeof amount);
console.log(amount + 8);''','string\nnumber\n20',['unknown 接收暂未确认的数据','as 提供检查阶段的类型信息','Number 在运行时进行数字转换','转换和断言各自承担不同步骤'],
 '[1]unknown表示我们暂时还没有确认这份数据的具体类型。本例在代码里已经知道它是文字十二。[2]通过as string，把这个已知信息提供给检查工具，后面text就按字符串来检查。类型断言适合你有明确依据、需要向工具补充说明的位置；项目中从外部取得未知数据时，可以先做实际检查再继续使用。',
 '[3]Number才负责运行时的转换，把文字十二整理成数字十二。[4]显示text的类型名称，仍然是string。[5]显示amount的类型名称，是number。[6]amount再加八得到二十。读代码时把这两个步骤分开标注：as说明后面怎样检查，Number实际计算一个新值。有这条清楚的路线，看到更长的类型断言表达式时也容易判断数据在哪里变化。')
page(c,'练习：根据类型选择格式','''function label(value: number | string): string {
  if (typeof value === "number") return value.toFixed(0);
  return value.trim();
}
console.log(label(12.6));
console.log(label("  午餐  "));''','13\n午餐',['number 分支整理为 0 位小数','string 分支去掉两端空白','12.6 显示为文字 13','第二次调用返回午餐'],
 '[1]这道题的参数允许数字或文字。[2]数字分支调用toFixed，并传入零，表示整理为零位小数。[3]文字分支调用trim，去掉两端空白。[5,6]请预测交入十二点六以及带两端空格的午餐时，各自返回什么。先确定每次进入哪条分支，再使用该分支对应的方法。给自己四秒，按两次调用分别推算。',
 '[5,2]十二点六进入数字分支，整理为零位小数，返回文字十三。[6,3]带空格的午餐进入文字分支，trim返回午餐。两次结果都是字符串，符合函数出口的说明。这个例子把联合类型、运行时判断和不同方法连起来。以后参数允许多种形状时，也按先确认情况、再调用对应操作的顺序组织，函数就会既清楚又容易检查。',kind='exercise')

c=chapter('函数类型与泛型')
page(c,'默认参数与可选参数','''function greet(name: string, prefix = "你好"): string {
  return `${prefix}，${name}`;
}
function note(text?: string): string {
  return text ?? "暂无备注";
}
console.log(greet("小林"));
console.log(note());''','你好，小林\n暂无备注',['默认参数提供常用起始值','可选参数使用 ? 标记','省略参数时要处理对应情况','返回类型保持明确'],
 '[1]greet接收姓名和前缀，前缀默认采用你好。只传姓名时，函数就能完成常见的问候；需要其他前缀时，再显式传进去。[2]模板把前缀和姓名连接成一段返回文字。默认值还能帮助工具推断参数类型，这里prefix从字符串默认值取得清楚的检查信息。',
 '[4,5]note的参数后面使用问号，表示调用时可以省略。函数里用默认文字处理undefined，让出口始终返回string。[7]调用greet并传入小林，得到你好，小林。[8]不提供备注时，得到暂无备注。设计函数入口时，先决定哪些数据必需、哪些有常用默认值、哪些可以缺省，再把这些安排写到参数中。')
page(c,'用函数类型描述回调','''type Transform = (value: number) => number;
function apply(value: number, action: Transform): number {
  return action(value);
}
const double: Transform = (value) => value * 2;
console.log(apply(6, double));''','12',['函数类型描述参数和返回值','Transform 接收数字并返回数字','apply 调用交入的操作','回调中的 value 可由上下文推断'],
 '[1]函数本身也有类型。Transform描述一种操作：接收数字，返回数字，箭头左边写参数，右边写返回类型。[2]apply除了接收一个值，还接收符合这份约定的action。[3]它把value交给action，再返回action完成后的结果。这样一个工具可以把固定的调用步骤和变化的处理方法组合起来。',
 '[5]double符合Transform要求，接收当前值并返回它的两倍。回调参数value能从上下文推断为数字。[6]把六和double交给apply，就得到十二。数组方法、事件函数和异步任务里，经常需要描述回调的入口与出口。把这份函数类型写清，交入的方法是否能按约定工作，就可以在检查阶段得到反馈。')
page(c,'泛型保留输入与输出的联系','''function identity<T>(value: T): T {
  return value;
}
const amount = identity(12);
const name = identity("午餐");
console.log(amount + 8);
console.log(name.toUpperCase());''','20\n午餐',['T 是本次调用使用的类型参数','参数与返回值使用同一个 T','每次调用分别确定对应类型','返回后继续获得正确的操作提示'],
 '[1]如果一个函数的处理步骤适用于多种类型，又希望保留输入和输出之间的联系，可以使用泛型。尖括号里的T是类型参数，这次调用决定T是什么；参数value和返回值都写T，表达同一种类型沿调用过程传递。[2]identity直接返回交入的值，步骤很简单，适合先观察类型怎样变化。',
 '[4]交入数字十二时，这次调用的结果按数字处理。[5]交入文字午餐时，另一次调用的结果按字符串处理。[6]因此amount可以加八得到二十。[7]name可以使用字符串方法。泛型让一份实现服务于不同类型，同时保留具体调用中的信息。先从这种一进一出的对应关系理解，再学习约束和多个参数之间的联系。')
page(c,'给泛型添加需要的能力','''function size<T extends {length: number}>(value: T): number {
  return value.length;
}
console.log(size("hello"));
console.log(size([12, 8, 5]));''','5\n3',['extends 在这里约束类型参数','传入值需要具备数字 length','函数只使用声明过的能力','文字与数组都能满足这项要求'],
 '[1]一个泛型函数需要读取length，就把这项能力写进约束。T extends后面说明传入类型需要带有数字length属性。[2]函数体依据这份要求读取长度并返回。约束把实现真正需要的内容交代清楚，让函数既能接受不同类型，又有足够的信息完成当前操作。',
 '[4]字符串hello拥有长度属性，所以返回五。[5]三项数字数组同样拥有长度属性，所以返回三。这里关注的是共同能力，而不是先把所有允许的具体类型列成清单。编写泛型时，先问实现究竟要对参数做什么，再给出相应约束，通常比一开始就安排复杂的类型表达式更容易得到清楚的接口。')
page(c,'keyof 约束可以读取的属性名','''function get<T, K extends keyof T>(item: T, key: K): T[K] {
  return item[key];
}
const expense = {name: "午餐", amount: 12};
console.log(get(expense, "name"));
console.log(get(expense, "amount") + 8);''','午餐\n20',['keyof T 取得 T 的属性名范围','K 必须属于这组属性名','T[K] 表示对应属性的值类型','返回类型随所选属性变化'],
 '[1]这一页把对象和属性名联系起来。T描述对象类型，keyof T取得它有哪些属性名，K再从这些名字里选一个。返回类型T方括号K，表示选中属性的值类型。[2]函数体按照key读取对象中的值。读这条声明时，先看对象是谁，再看允许选择哪些字段，最后看所选字段会带出什么类型。',
 '[4]expense同时包含文字名称和数字金额。[5]选择name时，调用结果按字符串处理，显示午餐。[6]选择amount时，结果按数字处理，继续加八得到二十。检查工具还会约束传入的属性名称，帮助发现拼写错误。这个例子展示泛型怎样让两个参数和返回值共同保持一条具体关系，后面的类型工具也会沿用这种按字段推导的思路。')
page(c,'练习：保持容器中的元素类型','''function wrap<T>(value: T): {value: T} {
  return {value};
}
const box = wrap(12);
console.log(box.value + 8);''','20',['wrap 返回一个带 value 的对象','value 的类型与传入值对应','本次交入数字 12','读取后继续做数字运算'],
 '[1]wrap把一个值放进带value属性的对象中，参数和属性都使用同一个类型参数T。[2]返回时用属性简写组织对象。[4,5]这次交入十二，再读取box点value加八。请判断box里的value应按什么类型处理，以及最后显示多少。给自己四秒，先在本次调用里确定T，再把它代回返回对象的说明。',
 '[4]本次交入数字十二，所以box里的value按数字处理。[5]读出十二再加八，得到二十。换成文字调用时，返回对象会保留文字类型。泛型的关键是让类型信息沿着你写出的对应关系传递，调用者取得结果后仍能继续使用准确的能力。后续面对更大的响应对象，也可以先找到这种最简单的类型联系，再逐层组合。',kind='exercise')
