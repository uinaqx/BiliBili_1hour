from author import chapter,page
c=chapter('字符串与网页内容')
page(c,'模板字符串整理显示内容','''const name = "午餐";
const amount = 12;
const label = `${name}：${amount}元`;
console.log(label);''','午餐：12元',['反引号包围模板字符串','${...} 插入表达式的结果','文字与变量放在同一模板中','本例生成 午餐：12元'],
 '现在准备把记录显示得更清楚。模板字符串使用反引号包围，在需要插入数据的位置，写美元符号加一对大括号。这里先插入name的午餐，再写冒号，再插入amount的十二，最后接上元。运行以后，就得到午餐冒号十二元。模板让固定文字和变化数据出现在一条清楚的显示格式里。',
 '大括号中也可以放一个算式，例如金额乘二，会先算出结果，再放进文字。用键盘输入时，反引号通常在数字一左边，和普通的单引号双引号形状不同。平常保存固定文字时仍然可以用普通引号，组合多项变量时再选模板。你可以改动name和amount，观察同一个模板怎样为不同记录生成显示文字。')
page(c,'去空白、查找与切片','''const input = "  午餐  ";
const name = input.trim();
console.log(name);
console.log("JavaScript".includes("Script"));
console.log("hello".slice(0, 2));''','午餐\ntrue\nhe',['trim 返回去掉两端空白的文字','includes 检查是否包含某段内容','slice(0, 2) 取下标 0 到 2 之前','字符串方法通常返回新的文字或结果'],
 '用户输入名称时，前后可能带着空格。trim会返回去掉两端空白后的文字，所以name保存的是午餐。接着用includes检查JavaScript这段文字里是否含有Script，结果为真。字符串也有按位置读取和截取的工具，这些方法让我们能够先整理输入，再进行比较、搜索或显示。',
 'slice的两个位置描述截取区间，零到二表示从下标零开始，到下标二之前结束，所以hello取出h和e，显示he。这里的方法返回新结果，原来的字符串值保持原样。英文短词的位置很容易在纸上列出来，中文和表情涉及更复杂的字符表示；入门练习先用画面中这些清楚的样例掌握方法的输入和返回值。')
page(c,'split 与 join 的两个方向','''const text = "茶,面包,水果";
const items = text.split(",");
console.log(items.length);
console.log(items[1]);
console.log(items.join(" / "));''','3\n面包\n茶 / 面包 / 水果',['split 按分隔文字拆成数组','拆开后可按数组位置读取','join 用分隔文字连接各项','处理链路：文字 → 数组 → 文字'],
 '有时一段文字里包含几个项目，可以用split按指定分隔文字拆开。这里的逗号把茶、面包、水果分成三项，结果保存在items数组里。length取得三，下标一读取第二项面包。读到split以后，就把结果当作数组，继续使用前面学过的位置读取和逐项处理方法。',
 '最后一行用join把三项重新连接，中间放入空格、斜线、空格，形成更适合页面显示的一行文字。这条路线是文字变数组，再由数组变文字。每经过一个工具，先标注输出的数据类型，再决定下一步可以做什么。网页输入、列表整理和显示格式，常常就是由这些很小的数据转换步骤连接起来的。')
page(c,'选中网页中的元素','''<!doctype html>
<meta charset="UTF-8">
<p id="status">等待记录</p>
<script>
  const status = document.querySelector("#status");
  console.log(status.textContent);
</script>''','等待记录',['id 给页面元素一个可定位的名字','document 表示当前网页文档','querySelector 按选择器找到元素','#status 匹配 id 为 status 的元素'],
 '接下来让JavaScript读取网页内容。页面里有一个段落，id叫status，文字是等待记录。document可以先理解成当前网页提供给程序的入口，querySelector接收一个选择器，帮我们找到对应元素。井号status表示查找id为status的元素。找到以后，把这个元素保存在status变量里，就能继续读取它的属性。',
 'textContent保存这个元素的文字内容，因此控制台显示等待记录。网页上的标题、按钮和输入框，都可以通过这种方式找到。配套例子把script写在元素后面，浏览器先建立段落，再执行查找。后面也会看到使用模块脚本的组织方式。现在先建立一条清楚路线：用HTML放元素，用选择器找到它，再读取想要的内容。',kind='html',lines=[[1,2,3],[4,5,6,7]])
page(c,'把计算结果写回页面','''<!doctype html>
<meta charset="UTF-8">
<p id="total">总额：0元</p>
<script>
  const total = 12 + 8;
  const output = document.querySelector("#total");
  output.textContent = `总额：${total}元`;
  console.log(output.textContent);
</script>''','总额：20元',['先计算出数字 20','选中用于显示总额的段落','模板生成 总额：20元','赋值 textContent 更新页面文字'],
 '这次把十二加八得到的结果显示到页面上。先计算total，取得数字二十，再找到id为total的段落。模板字符串把二十整理成总额冒号二十元，最后赋给元素的textContent。赋值发生后，浏览器里的段落文字就从总额零元更新成总额二十元。右侧流程图依次保留计算、查找和更新三个步骤。',
 '这里可以把数据和显示分开看：total是程序里的数字，output是网页元素，textContent是元素上显示的文字。先把数字算对，再整理格式，再写进页面。以后更新学生成绩、购物车数量或搜索结果时，都能沿用这条路线。用textContent显示用户输入时，输入会作为文字呈现，适合作为我们这门入门课的默认显示方式。',kind='html',lines=[[4,5,6],[7,8,9]])
page(c,'练习：读取后再更新','''<!doctype html>
<meta charset="UTF-8">
<p id="message">你好</p>
<script>
  const p = document.querySelector("#message");
  const before = p.textContent;
  p.textContent = before + "，小林";
  console.log(p.textContent);
</script>''','你好，小林',['选择器找到原段落','before 读取原文字 你好','拼接得到 你好，小林','新文字写回同一个段落'],
 '请预测页面最后显示什么。程序先找到段落，再把当前文字保存给before，接着把before和逗号小林连接起来，交回段落的textContent。你可以把元素想成页面上的一个显示位置，把before想成从这个位置抄出来的一份文字。给你四秒，沿着读取、拼接、写回的顺序推到最后。',
 '读取时段落里是你好，所以before保存你好。连接逗号小林以后，得到你好，小林，页面和控制台都显示这段新文字。读取出来的字符串值和页面后来的文字更新各有自己的位置。做这种题时，明确什么时候读取，什么时候赋值，就能判断每个名字保存的具体内容。下一章加入按钮和输入框，让这些更新由用户的操作来触发。',kind='html',lines=[[3,4,5,6],[7,8,9]])

c=chapter('事件与用户输入')
page(c,'给按钮注册点击事件','''<!doctype html>
<meta charset="UTF-8">
<button id="add">记录一笔</button>
<p id="message">等待点击</p>
<script>
  const button = document.querySelector("#add");
  button.addEventListener("click", () => {
    document.querySelector("#message").textContent = "已记录";
  });
</script>''','点击后：已记录',['先找到按钮元素','addEventListener 注册事件处理函数','用户点击时执行回调','回调把段落更新为已记录'],
 '按钮要对点击做出反应，可以注册事件处理函数。先找到id为add的按钮，再调用它的addEventListener。第一个参数click指定点击事件，第二个参数是一个箭头函数，描述点击发生以后要执行的操作。页面打开时先完成注册，等用户真正点击按钮，浏览器再调用这个函数。',
 '回调里找到message段落，把文字更新成已记录。你可以先打开网页观察等待点击，再点一下按钮，看到文字改变。函数在这里表达未来某个时刻要做的事，事件就是触发这件事的入口。把注册阶段和执行阶段分开看，就能解释为什么页面刚打开时，回调里的更新还在等点击。',kind='html',lines=[[3,4,5,6,7],[8,9,10]])
page(c,'点击次数保存在程序状态里','''<!doctype html>
<meta charset="UTF-8">
<button id="add">增加</button><p id="count">0</p>
<script>
  let count = 0;
  document.querySelector("#add").addEventListener("click", () => {
    count += 1;
    document.querySelector("#count").textContent = String(count);
  });
</script>''','点击两次后：2',['count 保存累计点击次数','每次点击把数据增加 1','String 把数字整理成文字','更新数据后再刷新显示'],
 '如果每次点击都希望在原来基础上增加，就把count声明在事件函数外面，起始为零。点击发生时，回调读取当前count，加一，再写回count。随后调用String，把数字整理成文字，交给页面上的count段落。一次点击完成一次更新，接着等待下一次用户操作。',
 '第一次点击以后，数据从零变成一，页面显示一；第二次点击以后，从一变成二，页面显示二。count保存程序状态，页面文字呈现这个状态。把累计变量写在回调外面，几次点击就能延续同一份记录。你可以加入另一个减少按钮，再按相同思路更新数据和显示，观察多个操作怎样共同影响这一份状态。',kind='html',lines=[[3,4,5,6],[7,8,9,10]])
page(c,'读取输入框里的金额','''<!doctype html>
<meta charset="UTF-8">
<input id="amount" value="12">
<button id="add">记录</button><p id="message"></p>
<script>
  document.querySelector("#add").addEventListener("click", () => {
    const raw = document.querySelector("#amount").value;
    const amount = Number(raw);
    document.querySelector("#message").textContent = `${amount + 8}元`;
  });
</script>''','输入 12，点击后：20元',['value 读取输入框中的文字','Number 把金额文字转为数字','每次点击重新读取当前输入','计算后用模板更新页面'],
 '输入框让用户提供数据。画面中value先写十二，打开页面时，框里就带着这段文字。点击记录以后，程序读取输入框的value，得到当前输入内容，再通过Number转换成数字。这里每次点击都会重新读取，所以用户把框里改成十五以后，下一次处理取得的就是十五。',
 '接着把转换后的金额加八，用模板整理为带元的文字，更新message。输入十二时显示二十元。完整的数据路线是输入框文字、数字金额、计算结果、显示文字。把这几个阶段分别保存到清楚的名字里，后面加入检查也方便。下一页先验证输入是否合适，合适时再更新累计结果，让用户能得到明确的反馈。',kind='html',lines=[[3,4,5,6,7],[8,9,10,11]])
page(c,'先验证输入再记录','''function readAmount(raw) {
  if (raw.trim() === "") return null;
  const amount = Number(raw);
  if (!Number.isFinite(amount) || amount < 0) return null;
  return amount;
}
console.log(readAmount("12"));
console.log(readAmount("abc"));
console.log(readAmount(""));''','12\nnull\nnull',['先检查去空白后是否为空','Number.isFinite 检查有限数值','金额还需满足非负条件','成功返回数字，失败返回 null'],
 '输入检查可以先写成独立函数。第一步去掉两端空白，检查是否为空，空输入就返回null。第二步转换成数字，再检查是否为有限数值，以及是否小于零。满足我们的记录要求时，最后返回这个金额。这样调用者就能根据结果，选择显示输入提示，或者继续记录这笔开销。',
 '交入文字十二，返回数字十二；交入abc，转换结果没有通过有限数值检查，返回null；交入空文字，在第一步就返回null。检查顺序按输入整理、类型转换和业务条件展开，理由很清楚。页面的点击函数可以调用readAmount，再把成功和失败两条路线写出来。把规则集中在一个函数里，也方便独立运行这些样例，逐个检查边界。')
page(c,'表单提交与默认操作','''<!doctype html>
<meta charset="UTF-8">
<form id="form">
  <input id="name" value="午餐"><button>添加</button>
</form>
<p id="message"></p>
<script>
  document.querySelector("#form").addEventListener("submit", (event) => {
    event.preventDefault();
    const name = document.querySelector("#name").value.trim();
    document.querySelector("#message").textContent = `收到：${name}`;
  });
</script>''','提交后：收到：午餐',['form 把输入与提交组织在一起','submit 可以由按钮或回车触发','preventDefault 阻止本次默认提交行为','由回调负责读取并更新页面'],
 '输入框和添加按钮经常放在form表单里。表单提交时会触发submit事件，用户点按钮或者在输入框里按回车，都可以走到这条处理路线。回调的event参数提供本次事件的信息，我们调用preventDefault，阻止这次表单原有的默认提交行为，接下来由自己的代码整理数据并更新页面。',
 '这里读取name输入框，去掉两端空白，再显示收到冒号午餐。页面仍然留在当前操作位置，用户可以继续输入下一项。事件函数既能使用前面定义的变量，也能调用独立的数据处理函数。实际组织时，把表单读取和页面展示放在事件层，把金额计算和条件检查放进小函数，整个流程就能沿着清楚的职责连接起来。',kind='html',lines=[[3,4,5,8,9],[10,11,12,13]])
page(c,'练习：两次点击如何累加','''let total = 0;
function add(raw) {
  total += Number(raw);
  return total;
}
console.log(add("12"));
console.log(add("8"));''','12\n20',['total 位于函数外，保存累计状态','每次调用先把输入文字转为数字','第一次返回 12','第二次在 12 的基础上得到 20'],
 '为了更容易检查点击逻辑，我们先把它简化成两次函数调用。total在外层从零开始，add每次接收一段金额文字，转成数字，加进total，再返回当前累计。先调用文字十二，再调用文字八，请预测两次输出。给自己四秒，看清第二次调用开始以前，外层total已经保存了什么。',
 '第一次把零加十二，返回十二。第二次读取的是已经更新后的十二，再加八得到二十，所以两次输出依次是十二和二十。函数之外的状态会延续到后面的调用。把这条更新放进点击回调，就能得到刚才网页上的累计效果。也可以增加检查函数，在金额合适时才调用add，把数据规则和交互步骤组合起来。',kind='exercise')
