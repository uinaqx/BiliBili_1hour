from author import chapter,page
c=chapter('异步、异常与外部数据')
page(c,'等待稍后完成的结果','''async function loadAmount(): Promise<number> {
  return 20;
}
async function main(): Promise<void> {
  const amount = await loadAmount();
  console.log(amount);
}
main();''','20',['async 函数返回 Promise，类型参数表示最终结果','await 取得完成后的值，继续执行下一行','Promise<void> 表示完成后没有返回值','练习把立即返回替换为实际网络请求'],
'[1,2,3]实际项目经常等待网络或文件结果。我们先用一个很小的异步函数认识写法。在函数前加上 async，返回类型写成 Promise，尖括号里填 number，表示这项工作完成后会得到一个数字。函数体直接返回二十，运行时会把它包装成一个承诺稍后给出结果的对象。现在先记住这组固定搭配。',
'[4,5]主函数也写上 async，这样就能在函数内部使用 await。程序执行到第五行时，等待前面的工作完成，把得到的二十交给 amount。[6,7,8]接着输出二十。主函数的返回类型是 Promise 加 void，表示它完成后没有额外的返回值。等你把第一段替换成真正的请求，等待和读取结果的写法依然相同。')
page(c,'用异常传递失败原因','''function pay(amount: number): void {
  if (amount < 0) throw new Error("金额应大于等于零");
  console.log("支付", amount);
}
try {
  pay(-1);
} catch (error: unknown) {
  if (error instanceof Error) {
    console.log(error.message);
  }
}''','金额应大于等于零',['throw 抛出异常，当前执行流程转到 catch','try 包住可能抛出异常的调用','catch 的 unknown 值先检查，再读取属性','instanceof Error 后可以读取 message'],
'[1,2]支付函数接收一个数字。业务要求金额大于等于零，所以负数进入这一行时，用 throw 抛出一个 Error，把清晰的原因一起带出去。[3,4]合法金额会继续输出支付信息。这样函数可以把成功路径写在正常流程中，把失败原因交给调用它的地方统一处理。这个思路在请求失败和解析错误时也很常见。',
'[5,6]把调用放进 try，故意传入负一，看看失败路线。[7,8,9,10,11]抛出的值来到 catch。我们把它看作 unknown，也就是先保留具体类型，等检查后再使用。instanceof Error 确认它是错误对象，随后读取 message，控制台显示金额应大于等于零。实际页面也可以在这里把原因展示给用户。')
page(c,'先检查未知数据','''function readAmount(value: unknown): number {
  if (typeof value === "number") {
    return value;
  }
  return 0;
}
console.log(readAmount(12));
console.log(readAmount("12"));''','12\n0',['unknown 接收任意来源，使用前先判断类型','typeof 判断后，分支里的值收窄为 number','检查失败时返回默认值，结果类型保持一致','数字字符串需要明确选择转换策略'],
'[1]外部数据可能来自用户输入，也可能来自服务器。我们先用 unknown 接收，意思是现在还没有确认具体内容。这个函数的任务非常明确，最后交回一个数字。[2,3,4]如果 typeof 检查得到 number，就原样返回。检查表达式同时帮助我们和编译器看清当前分支里是什么数据，后面的操作也就有了依据。',
'[5,6]其他情况统一返回零，这就是本页约定的处理策略。[7,8]第一次传入数字十二，结果是十二。第二次传入文字十二，结果是零。观察两次调用，值的外观接近，类型却决定了不同路线。如果业务允许数字字符串，可以增加一个转换分支，再检查转换结果是否为有限数字。规则由函数清楚地表达出来。')
page(c,'验证 JSON 中的对象','''type Expense = { name: string; amount: number };
function isExpense(v: unknown): v is Expense {
  return typeof v === "object" && v !== null
    && "name" in v && typeof v.name === "string"
    && "amount" in v && typeof v.amount === "number";
}
const data: unknown = JSON.parse('{"name":"午餐","amount":12}');
if (isExpense(data)) {
  console.log(data.name, data.amount);
}''','午餐 12',['JSON.parse 的结果先交给 unknown 接收','依次检查对象、非空、属性存在和属性类型','v is Expense 把检查结论传给调用处','检查条件要覆盖后续代码依赖的字段'],
'[1,2]现在处理一条服务器传来的开销记录。我们写一个检查函数，参数是未知值，返回位置写 v is Expense。这种写法把函数的检查结论传给调用者。[3,4,5,6]函数依次检查它是非空对象，包含 name 和 amount，并且姓名是字符串，金额是数字。这里每一项都对应后续代码真正要使用的内容，读起来就是一份数据检查清单。',
'[7]JSON.parse 把字符串解析成运行时的值，我们先把结果放进 unknown。[8,9,10]通过检查函数以后，当前分支就能按 Expense 使用，输出午餐和十二。类型声明描述期望的数据结构，这段检查负责确认实际收到的内容。项目中可以把这样的函数集中保存，让网络请求、本地存储和表单导入共用同一套规则。')
page(c,'检查网页输入元素','''const input = document.querySelector("#amount");
if (input instanceof HTMLInputElement) {
  const amount = Number(input.value);
  if (Number.isFinite(amount)) {
    console.log(amount + 8);
  }
}''','20',['querySelector 可能返回元素或 null','instanceof 确认取得输入框后读取 value','表单 value 是字符串，用 Number 转换','有限数字检查通过后再参与计算'],
'[1]最后把类型检查放到网页里。按选择器查找元素，返回值可能是一个元素，也可能是空值。浏览器环境的类型声明已经记录了这些可能。[2]我们用 instanceof 确认它是一个输入框。进入分支之后，编译器就知道这个对象有 value 属性，也知道 value 读出来是一段文字。实际练习页面会预先填入十二。',
'[3,4]用 Number 把输入内容转成数字，再用 Number.isFinite 检查结果是否为有限数字。通过检查后参与运算，程序输出二十。[5,6,7]这几行串起了三个步骤，找到元素，检查种类，处理内容。网页里很多带空值的提示都能沿着这个顺序解决。下一章把对象、数组和这些检查方法连起来，完成开销统计小项目。',kind='dom',fixtures={'html':'<input id="amount" value="12">'})
page(c,'练习：处理异步查询','''type Result = { ok: true; amount: number }
  | { ok: false; message: string };
async function load(): Promise<Result> {
  return { ok: true, amount: 12 };
}
async function main(): Promise<void> {
  const result = await load();
  if (result.ok) console.log(result.amount + 8);
  else console.log(result.message);
}
main();''','20',['await 后得到 Result，随后按 ok 区分情况','成功分支读取 amount，失败分支读取 message','联合类型同时约定状态和状态对应的数据','输出二十，成功路径完成一次金额计算'],
'[1,2]这一题把前面几章连起来。Result 有两种情况，成功带金额，失败带说明。[3,4,5]查询函数暂时直接给出成功结果，金额十二。[6,7,8,9,10,11]主函数等待结果，再检查 ok。请先沿着实际返回的对象走一遍，判断执行哪一行，最终输出多少。先看清状态，再选择对应字段，整个过程和普通条件判断是一样的。',
'[7,8]答案是二十。await 取得成功对象，ok 为真，于是使用 amount 加八。[1,2,9]如果把查询结果改成失败对象，另一条分支会读取 message。状态和数据放在同一个联合类型里，编译器就能跟随状态判断，提醒我们选用正确的字段。这种返回结构很适合表达常见业务结果，抛出异常则适合交给外层统一处理的失败。',kind='exercise')
c=chapter('综合项目与课程回顾')
page(c,'用类型设计开销记录','''type Expense = {
  id: number;
  name: string;
  amount: number;
};
const items: Expense[] = [
  { id: 1, name: "午餐", amount: 12 },
  { id: 2, name: "交通", amount: 8 }
];
console.log(items.map(item => item.name).join("、"));''','午餐、交通',['记录用 id 区分身份，name 描述名称，amount 保存金额','Expense[] 约定每个数组元素的形状','map 提取名称，join 把名称连接成一段文字','先设计数据，再连接输入、统计和页面'],
'[1,2,3,4,5]最后做一个开销记录项目。我们先决定每条记录保存什么。id 用来区分记录，name 保存名称，amount 保存金额。把这三个字段写成 Expense，后面的新增、删除和统计都围绕这份约定展开。设计数据时，先想清楚页面要显示什么，以及操作时要用什么找到一条记录，通常就能确定主要字段。',
'[6,7,8,9]数组保存两条示例记录，午餐十二，交通八。每个元素都接受同一份类型检查，字段名和金额类型可以在编辑时及时确认。[10]最后提取名称并连接，输出午餐、交通。配套工程会把同样的记录画成网页列表，这一页先把数据形状看清楚。后续每一步都保持形状一致，程序就容易连接和维护。')
page(c,'把统计写成独立函数','''type Expense = { name: string; amount: number };
function total(items: readonly Expense[]): number {
  return items.reduce((sum, item) => sum + item.amount, 0);
}
const items: Expense[] = [
  { name: "午餐", amount: 12 },
  { name: "交通", amount: 8 }
];
console.log(total(items));
console.log(total([]));''','20\n0',['统计函数接收只读数组，返回金额总和','reduce 从零开始逐项累加 amount','空数组返回零，方便初始化页面','独立函数可在控制台和网页中共同使用'],
'[1,2]统计功能写成一个独立函数。参数是只读的开销数组，返回值是数字。这个约定告诉使用者，函数负责读取记录并计算结果。[3,4]reduce 从零开始，每读到一条记录，就把它的金额加进累计值。这几行只关心数据计算，页面按钮和输入框可以留给另外的代码处理，职责清楚后测试也更直接。',
'[5,6,7,8,9]先传入午餐十二和交通八，总额是二十。[10]再传入空数组，结果是零。第二个例子对应用户刚打开页面，还没有添加记录的状态。以后增加分类统计，也可以保留这个函数，再写一个筛选函数选出目标记录。先用小输入和空输入验证结果，再把函数接到页面上，是很省力的开发顺序。')
page(c,'通过函数集中更新记录','''type Expense = { id: number; amount: number };
let items: Expense[] = [];
function add(item: Expense): void {
  items = [...items, item];
}
function remove(id: number): void {
  items = items.filter(item => item.id !== id);
}
add({ id: 1, amount: 12 });
add({ id: 2, amount: 8 });
remove(1);
console.log(items.map(item => item.amount).join(","));''','8',['新增使用展开语法生成更新后的数组','删除使用 filter 保留其他 id 的记录','参数类型约定每种操作需要哪些信息','集中更新后统一保存并刷新页面'],
'[1,2,3,4,5]有了数据和统计，再处理新增和删除。新增函数接收一条完整记录，用展开语法保留已有元素，把新记录接到末尾，再更新 items。[6,7,8]删除函数只需要一个数字编号，用 filter 留下编号不同的记录。两种操作都生成新数组，页面刷新时读取当前的 items，就能看到最新状态。',
'[9,10,11]现在按顺序添加十二元和八元两条记录，再删除编号一。[12]数组里剩下编号二，所以输出八。请把代码中的编号和金额分开看，编号负责定位，金额负责计算。配套项目在更新完成后还会保存到本地存储，再重新绘制列表与总额。把这些步骤集中在更新函数附近，新增功能时更容易保持页面一致。')
page(c,'让外部输入经过检查','''function parseAmount(text: string): number | null {
  if (text.trim() === "") return null;
  const amount = Number(text);
  return Number.isFinite(amount) && amount >= 0
    ? amount : null;
}
console.log(parseAmount("12.5"));
console.log(parseAmount("abc"));
console.log(parseAmount(""));''','12.5\nnull\nnull',['先处理空白输入，再转换为数字','金额要求为有限数字且大于等于零','成功返回 number，失败返回 null','调用处检查 null 后继续新增记录'],
'[1,2]输入框读出来的是文字，我们用一个专门的函数检查金额。返回类型是数字或者空值，成功给出金额，失败给出 null。首先处理只有空白的输入，让用户补充金额。[3,4,5,6]接着转换成数字，检查结果有限且大于等于零，通过时返回金额，其他情况返回空值。每一步都对应页面上的具体规则。',
'[7,8,9]三次调用依次得到十二点五、空值、空值。调用者检查结果是否为 null，就知道接下来展示提示，还是添加一条记录。这种把解析和页面操作分开的写法很适合练习。你可以直接增加小测试，输入零、带空格的数字和负数，逐项确认规则，再放心地把函数连接到提交按钮。')
page(c,'检查完整网页项目','''type Expense = { id: number; name: string; amount: number };
const items: Expense[] = [
  { id: 1, name: "午餐", amount: 12 },
  { id: 2, name: "交通", amount: 8 }
];
const saved = JSON.stringify(items);
const restored: unknown = JSON.parse(saved);
console.log(Array.isArray(restored));
console.log(items.reduce((sum, item) => sum + item.amount, 0));''','true\n20',['JSON.stringify 保存数组，JSON.parse 取回运行时数据','本地存储读回后同样执行完整字段检查','网页工程包含新增、删除、统计和持久化','按首次打开、合法输入、错误输入、刷新顺序检查'],
'[1,2,3,4,5]配套网页工程已经把这些步骤连接起来。列表里的记录采用同一份 Expense 类型，提交表单时先检查名称和金额，成功后添加记录并更新总额。[6,7]保存时把数组转成 JSON 文字，读取时再解析回来。取回的数据依然经过数组和字段检查，这样页面使用的始终是确认过形状的记录。',
'[8,9]这一页的小例子显示解析结果确实是数组，总额是二十。完整项目的使用顺序是，先编译，再启动本地服务，打开页面测试。试着新增两条记录，删除一条，刷新页面看看剩下的数据。再输入空名称、负数和非数字，观察提示。README 里给出了具体命令和目录位置，所有示例也都可以单独运行。')
page(c,'综合练习与下一步','''type Item = { amount: number };
function sum<T extends Item>(items: readonly T[]): number {
  return items.reduce((n, item) => n + item.amount, 0);
}
const items = [
  { name: "午餐", amount: 12 },
  { name: "交通", amount: 8 }
];
console.log(sum(items));''','20',['泛型约束要求 amount，同时保留其他字段','输入、判断、函数和对象连接成完整处理过程','unknown 数据先检查，联合类型按条件收窄','练习路线：修改示例、阅读提示、编译运行、扩展项目'],
'[1,2,3,4]最后一道题，统计函数使用泛型，要求每个元素都有数字类型的 amount，参数又是只读数组。[5,6,7,8,9]实际记录多了 name 字段。请判断能否传入，最后输出多少。先从函数的要求出发，再看输入对象是否具备对应字段。前面学过的结构检查、泛型约束和数组累加，会在这里一起派上用场。',
'[2,3,9]可以传入，结果是二十。每个对象都具有需要的 amount，额外的名称继续保留在原记录中。回顾整门课，我们从变量开始，学会描述数组、对象和函数，用联合类型表达情况，用检查把数据收窄，再用泛型连接不同输入。接下来请先跑通配套项目，再亲手增加分类和预算提示。每增加一个功能，就练习一次从数据到类型再到运行结果的完整过程。',kind='exercise')
