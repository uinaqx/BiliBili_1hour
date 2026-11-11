from author import chapter,page
c=chapter('异常、异步与模块')
page(c,'用异常传递失败原因','''function parseAmount(text) {
  const value = Number(text);
  if (!Number.isFinite(value)) throw new Error("金额格式有误");
  return value;
}
try {
  console.log(parseAmount("abc"));
} catch (error) {
  console.log(error.message);
}''','金额格式有误',['throw 抛出带有原因的错误','try 包围可能失败的操作','失败后进入对应 catch','error.message 读取错误说明'],
 '程序在运行过程中可能遇到无法完成的步骤，可以用异常把原因传到处理位置。这里先把文字转换成数字，转换失败时，throw抛出一个Error对象，里面写金额格式有误。调用处用try包住这次操作，遇到抛出的错误，就来到catch里面。error参数接收这个错误，我们读取它的message，让用户看到发生了什么。',
 '交入abc以后，程序在检查处抛出错误，try里面的显示没有取得正常返回值，转到catch显示金额格式有误。交入十二时，函数正常返回十二，就沿成功路线显示十二。返回null和抛出异常是两种常见的失败表达方式，具体项目按接口约定选择，并在调用处统一处理。这里先掌握成功继续、失败进入catch的基本路线。')
page(c,'定时回调与执行顺序','''console.log("开始");
setTimeout(() => {
  console.log("稍后记录");
}, 0);
console.log("结束当前步骤");''','开始\n结束当前步骤\n稍后记录',['当前脚本先继续执行','setTimeout 注册稍后执行的回调','0 表示定时等待阈值为 0','回调在当前执行结束后获得机会'],
 '现在观察一个稍后执行的操作。第一行先显示开始，接着setTimeout注册一个回调，里面准备显示稍后记录。最后一个参数是等待时间，单位毫秒，这里写零。注册好以后，当前脚本继续往下执行，所以先显示结束当前步骤。等当前这一轮执行完成，定时回调才获得执行机会，显示稍后记录。',
 '这段代码的结果是开始、结束当前步骤、稍后记录。等待零毫秒表达的是定时等待阈值，实际执行还要等当前任务完成。我们把这种把后续工作安排到未来的方式叫作异步。学习异步时先分清两件事：哪行现在就执行，哪段函数被登记起来等以后调用。右侧时间线把注册与回调分开放，帮助你沿执行顺序读代码。')
page(c,'Promise 保存未来的结果','''console.log("开始");
const task = Promise.resolve(12);
task.then((amount) => {
  console.log(amount);
});
console.log("当前步骤完成");''','开始\n当前步骤完成\n12',['Promise 表达一项异步结果','resolve 建立成功结果','then 注册成功后的处理函数','当前脚本完成后执行这里的回调'],
 'Promise可以先理解成一张记录异步结果的凭据。这一行通过resolve提供一个成功结果十二，得到task。随后调用then，把成功以后要执行的函数交进去。这个函数接收完成结果amount，并把它显示出来。使用Promise的工具通常会在任务完成时交付结果，调用者提前写好后续处理的步骤。',
 '即使这里的成功结果已经准备好，then里的回调也会安排到当前脚本完成以后运行。因此先显示开始，再显示当前步骤完成，最后显示十二。Promise的成功状态和失败状态，分别决定后面进入哪条处理路线。今天先学会沿着then接收成功结果，下一页再使用async和await，把这样的处理写成更接近普通顺序阅读的形式。')
page(c,'async 与 await 接收结果','''async function loadAmount() {
  const amount = await Promise.resolve(12);
  return amount + 8;
}
console.log("开始");
const total = await loadAmount();
console.log(total);''','开始\n20',['async 函数返回 Promise','await 接收完成后的成功结果','函数内先取得 12，再加 8','模块中的顶层 await 等待最终结果'],
 '把函数标为async以后，就能在里面使用await接收一个Promise完成后的结果。这次await取得十二，再加八，最后返回二十。async函数向外提供的仍然是Promise，所以调用处也使用await，取得最终的二十。我们把例子保存为模块文件，Node可以直接运行，浏览器里则使用带module类型的脚本。',
 'await会暂停所在异步函数的后续步骤，等结果就绪再继续。应用可以在等待期间处理其他已经安排的工作。成功时拿到结果继续计算，失败时可以用try和catch处理。真实网页经常await一个fetch请求，再await响应的json方法读取数据。配套综合项目把数据保存在本地，便于第一次练习时稳定复现全部交互。')
page(c,'模块导出与导入','''// budget.mjs 中的完整内容
export function remaining(budget, spent) {
  return budget - spent;
}''','5',['export 把工具提供给其他模块','import 明确读取哪个模块的导出','相对路径从当前模块所在位置开始','例子保留 budget.mjs 与 main.mjs'],
 '当工具函数越来越多，可以把它们放到独立模块里。budget模块定义remaining函数，并在前面加export，表示把这个函数提供出去。主程序用import读取同目录budget模块导出的remaining，然后像普通函数一样调用。模块让我们沿着文件名和导出名找到代码来源，也方便把同一个计算工具交给不同页面使用。',
 '配套目录包含两个完整文件：budget模块保存定义，main模块负责导入和调用，交入三十和二十五，得到五。终端里运行main点mjs即可。浏览器加载模块时，把入口脚本标成module，并通过本地服务器打开项目。后面的完整网页会给出具体命令。先把最小的两个文件跑通，再增加更多模块，结构就能逐步扩展。',fixtures={'budget.mjs':'export function remaining(budget, spent) { return budget - spent; }\n'},kind='module')
page(c,'练习：当前执行与异步回调','''console.log("A");
Promise.resolve().then(() => console.log("B"));
console.log("C");''','A\nC\nB',['同步语句先显示 A','then 中的 B 等待当前脚本结束','接着同步显示 C','最后执行回调显示 B'],
 '这一页只有三行，请预测字母的显示顺序。第一行直接显示A，第二行把显示B放到Promise的then回调里，第三行直接显示C。先在纸上把同步语句和登记的回调分开，再按执行时机排队。你有四秒，想清楚这次回调什么时候获得机会，然后再对照下方的结果。',
 '正确顺序是A、C、B。A和C属于当前正在执行的脚本，按顺序先完成。then注册的回调随后执行，才显示B。做入门异步顺序题时，先走完当前同步路线，再处理已经就绪的Promise回调。涉及更多任务种类时，再根据对应队列规则继续分析。这里把最常见的第一步建立起来，读网页请求和按钮里的异步函数就有了基础。',kind='exercise')

c=chapter('综合项目与复盘')
page(c,'准备一份完整的开销记录','''const expenses = [
  {id: 1, name: "午餐", amount: 12},
  {id: 2, name: "交通", amount: 8}
];
const total = expenses.reduce((sum, item) => sum + item.amount, 0);
console.log(total);
console.log(expenses.map((item) => item.name).join(","));''','20\n午餐,交通',['数组保存多条记录','每条记录用对象组织字段','reduce 累加每条记录的 amount','map 提取名称形成新数组'],
 '最后把前面学过的内容连成一个小开销本。expenses数组保存两条记录，每条记录都有编号、名称和金额。编号帮助我们在删除和修改时定位同一条记录，名称用于页面显示，金额用于汇总。先把数据结构写清楚，再写处理过程，页面交互就能围绕同一份数据逐步展开。',
 'reduce每次取出一条item，把item点amount加进累计值，所以总额是二十。map取出每条记录的name，形成名称数组，再用join连接，显示午餐和交通。一个数组中放对象，再通过回调读取属性，组合起来就是许多实际列表页面的基础。你可以先在控制台验证这些纯数据处理，再把结果交给页面元素。')
page(c,'用函数生成需要显示的结果','''function summary(items, budget) {
  const total = items.reduce((sum, item) => sum + item.amount, 0);
  const left = budget - total;
  return {total, left, within: left >= 0};
}
const result = summary([{amount: 12}, {amount: 8}], 30);
console.log(JSON.stringify(result));''','{"total":20,"left":10,"within":true}',['summary 只接收数据并生成结果','总额 20，预算 30，余额 10','对象简写用变量名作为属性名','页面展示使用返回对象中的结果'],
 '把汇总过程封装成summary函数。它接收记录数组和预算，先算total，再算left，也就是剩余预算，最后返回一个对象，把这几个结果一起交出去。这里total和left写成属性简写，表示属性名和要保存的变量同名。within保存余额是否至少为零，用来表达当前开销是否还在预算内。',
 '例子交入十二和八两条记录，以及预算三十，返回总额二十、余额十、预算内为真。页面只需要调用这个函数，再读取结果对象，就能显示对应文字。这样做题和调试时，可以直接给函数准备不同输入，例如空记录、正好花完预算、超出预算，分别核对结果。把计算集中到一个位置，按钮和显示区域的代码也会更清楚。')
page(c,'新增记录后刷新页面','''const items = [];
function addExpense(name, amount) {
  items.push({name, amount});
}
addExpense("午餐", 12);
addExpense("交通", 8);
console.log(items.length);
console.log(items.reduce((sum, item) => sum + item.amount, 0));''','2\n20',['添加函数把一条对象记录放进数组','两次添加后 length 为 2','汇总读取更新后的数组','完整网页中随后调用 render 刷新显示'],
 '新增操作先处理数据。addExpense接收名称和金额，用对象简写把两项组织成一条记录，再通过push放到数组末尾。调用两次以后，items里就有午餐十二元和交通八元，元素数量是二，总额是二十。先把新增后的数组核对清楚，再接上网页的显示步骤，就能逐层确认行为。',
 '完整配套项目里，表单提交时先读取名称和金额，调用检查函数，成功后新增记录，再调用render刷新列表和汇总。render会先整理当前总额，逐条创建列表元素，用textContent放入名称和金额，再加入页面。每次修改数据以后调用同一条刷新路线，页面显示就能跟着当前数据更新。项目中的三个文件已经放在配套目录，方便逐个打开对照。')
page(c,'把记录保存在浏览器里','''const items = [{name: "午餐", amount: 12}];
const saved = JSON.stringify(items);
const restored = JSON.parse(saved);
console.log(restored[0].name);
console.log(restored[0].amount);
// 网页中：localStorage.setItem("expenses", saved)
// 读取时：localStorage.getItem("expenses")''','午餐\n12',['浏览器 localStorage 用键保存文字','保存前把记录转换成 JSON 文字','读取后 parse 恢复记录数组','配套网页对损坏数据提供重置提示'],
 '为了刷新网页后继续看到记录，可以使用浏览器提供的localStorage。它按名称保存文字，所以先把items通过JSON转换成文字，再用setItem保存到expenses这个键。下次打开时，用getItem读取同一个键，再通过parse恢复数组。画面先把转换和恢复单独跑一遍，确认恢复后仍然能读出午餐和十二。',
 '完整项目把保存放在数据更新以后，把读取放在初始化阶段。读取时还会检查数组和金额字段，遇到格式损坏的数据，就显示重置提示，方便继续练习。localStorage属于当前浏览器站点的本地存储；同一项目保持相同的本地服务器地址，就能接着读取自己保存的记录。你可以添加两笔开销，再刷新页面，检查列表和总额是否一起恢复。')
page(c,'运行完整网页并检查三个场景','''// 在配套项目目录打开终端：
// python -m http.server 8000
// 浏览器打开：http://localhost:8000
// 文件：index.html、app.js、budget.js
console.log("添加 12 和 8：总额 20，余额 10");
console.log("删除第一笔：总额 8，余额 22");
console.log("刷新页面：恢复保存后的记录");''','添加 12 和 8：总额 20，余额 10\n删除第一笔：总额 8，余额 22\n刷新页面：恢复保存后的记录',['从完整项目目录启动本地服务器','依次添加午餐 12、交通 8','删除第一笔后总额为 8','刷新页面检查记录恢复'],
 '请打开配套的完整网页项目文件夹，在这个目录启动本地服务器，再用浏览器访问画面里的地址。页面有名称输入框、金额输入框、添加按钮、列表和总额区域。先添加午餐十二和交通八，检查总额二十、余额十；接着删除午餐，检查列表只剩交通，总额八、余额二十二。每个操作都沿着输入、数据更新、保存、刷新显示的路线执行。',
 '最后刷新页面，检查刚才保存的记录能否恢复。你还可以输入空名称、字母金额或负数，观察提示是否清楚。先测正常情况，再测输入边界，最后测试连续操作和刷新。这是一套很实用的自查顺序。配套项目里保留了独立的计算模块，页面代码按初始化、渲染、添加和删除组织，你可以从自己最熟悉的函数开始阅读，再逐步连接到完整流程。')
page(c,'练习与课程回顾','''const items = [{amount: 12}, {amount: 8}, {amount: 5}];
const selected = items.filter((item) => item.amount >= 8);
const total = selected.reduce((sum, item) => sum + item.amount, 0);
const message = total <= 30 ? "预算内" : "超出预算";
console.log(total, message);''','20 预算内',['筛选保留金额 12 和 8','汇总得到 20','条件表达式选择预算内','继续练习：添加分类与按名称搜索'],
 '最后一道题，把对象数组、筛选、汇总和条件表达式连起来。三笔金额是十二、八、五，先留下至少八元的记录，再计算这些记录的总额，最后判断是否在三十元预算内。请用四秒时间，在每一步旁边写出中间结果。阅读长一点的程序，仍然可以从这些已经熟悉的小操作开始，一步一步推到最后。',
 '筛选以后留下十二和八，总额二十，因此显示二十和预算内。今天我们从一行输出走到可以交互的小网页，学过变量、类型、运算、分支、循环、函数、数组、对象、字符串、事件、异步和模块。课后先运行全部例子，再把完整项目加上分类和按名称搜索。每次改一处，预测结果，再运行核对，你就能把这一小时里的语法变成真正会使用的工具。',kind='exercise')
