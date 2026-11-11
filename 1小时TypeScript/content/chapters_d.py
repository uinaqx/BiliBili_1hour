from author import chapter,page
c=chapter('类与对象组织')
page(c,'把数据与方法组织成类','''class Wallet {
  balance: number;
  constructor(initial: number) {
    this.balance = initial;
  }
  add(amount: number): void {
    this.balance += amount;
  }
}
const wallet = new Wallet(10);
wallet.add(5);
console.log(wallet.balance);''','15',['class 定义一类对象的结构和操作','constructor 准备每个对象的初始数据','this 指向当前这一个对象','void 表示调用者主要使用操作效果'],
 '[1,2]如果希望把余额和修改余额的操作放在一起，可以定义Wallet类。balance保存这个对象的余额。[3,4]constructor是构造函数，创建对象时接收初始数字，并用this点balance把它保存到当前对象。this可以先理解成这一次正在处理的对象，让同一套方法能操作各个对象自己的数据。',
 '[6,7]add方法接收金额，加进当前余额。返回类型void表示这里主要使用方法产生的操作效果。[10]通过new创建钱包，起始余额十。[11]调用add增加五。[12]最后读取余额，得到十五。类把字段和相关操作集中组织起来，调用者通过对象来使用它。先跟踪一个对象的创建和一次方法调用，再扩展到多个对象，就容易看清它们各自保存的状态。')
page(c,'访问范围与读取入口','''class Wallet {
  private amount = 0;
  add(value: number): void { this.amount += value; }
  get balance(): number { return this.amount; }
}
const wallet = new Wallet();
wallet.add(12);
console.log(wallet.balance);''','12',['private 约束类外对字段的直接访问','方法在类内部维护 amount','get 提供一个属性式的读取入口','调用者通过公开能力操作对象'],
 '[1,2]这次把内部金额命名为amount，并标为private，类型检查会约束类外直接访问它的方式。[3]增加金额统一通过add完成，方法在类内部读取和更新amount。[4]get balance提供一个读取入口，外部用属性形式读取余额时，由这里返回内部数字。把写入和读取安排成明确入口，可以让对象的数据维护集中到类本身。',
 '[6]创建新钱包以后，amount从零开始。[7]调用add并交入十二，内部金额变成十二。[8]读取wallet点balance，得到十二。后面要增加金额检查或日志时，可以在方法中集中处理，而调用位置仍然按原入口使用。protected允许派生类在继承关系中使用相应成员，public则向使用者公开；先围绕实际需要的访问范围选择修饰符，类的职责会更清楚。')
page(c,'继承与 override','''class Report {
  title(): string { return "开销记录"; }
}
class MonthlyReport extends Report {
  override title(): string {
    return super.title() + "：本月";
  }
}
console.log(new MonthlyReport().title());''','开销记录：本月',['extends 建立派生关系','派生类可以补充或重写方法','override 标明对应基类已有方法','super 调用基类提供的实现'],
 '[1,2]Report先提供一个title方法，返回开销记录。[4]MonthlyReport通过extends继承它，再安排本月报表需要的行为。[5]override标明这里重写基类已经有的方法，工具会据此核对对应关系。继承适合让几种对象共享一部分能力，再在各自的位置补充差异，阅读时先找到基类提供了什么。',
 '[6]派生方法通过super调用基类的title，先得到开销记录，再接上本月这段文字。[9]创建MonthlyReport并调用title，最后显示开销记录冒号本月。继承把对象关系写进结构中；简单地复用几个独立计算步骤，也可以继续使用普通函数。先选择最容易表达当前关系的组织方式，再逐步补充类型和方法，避免为很小的需求安排过深的层级。')
page(c,'implements 核对一组共同能力','''interface Printable { print(): string; }
class Expense implements Printable {
  constructor(public name: string, public amount: number) {}
  print(): string { return `${this.name}：${this.amount}元`; }
}
const item: Printable = new Expense("午餐", 12);
console.log(item.print());''','午餐：12元',['接口描述需要提供的方法','implements 核对类是否满足约定','构造参数修饰符可同时声明属性','使用者可以面向共同接口调用'],
 '[1]Printable接口要求提供一个返回字符串的print方法。[2]Expense声明实现这个接口，检查工具就会核对它是否具备相应能力。[3]构造参数前面的public同时声明并初始化同名属性，这是一种参数属性简写。[4]print读取对象的名称和金额，整理为显示文字。接口描述的是约定，类提供具体的数据和实现。',
 '[6]我们按Printable类型使用新建的Expense对象，只围绕这份共同能力调用。[7]print返回午餐冒号十二元。以后其他类也能提供相同的方法，再交给同一组使用接口的代码。实现接口时还要在类本身写出合适的参数和字段类型，让具体实现也能得到清楚检查。把约定和实现分别定位，读多文件工程时会更容易找到各自的责任。')
page(c,'静态成员与类本身的工具','''class Expense {
  static currency = "CNY";
  constructor(public amount: number) {}
  static zero(): Expense { return new Expense(0); }
}
const item = Expense.zero();
console.log(Expense.currency);
console.log(item.amount);''','CNY\n0',['static 成员通过类本身访问','currency 表达这一类共享的信息','静态方法可以安排统一创建方式','普通 amount 属性属于具体对象'],
 '[1,2]有些信息适合放在类本身，例如这组开销统一使用的币种，可以声明为static成员。[3]amount则属于每个具体对象，在创建时分别接收数值。[4]静态zero方法安排一种常见的创建方式，直接返回金额为零的新对象。读静态和普通成员时，先确认调用位置是在类名后面，还是在具体对象后面。',
 '[6]Expense点zero通过类名调用，得到一条金额为零的记录。[7]Expense点currency读取共享的币种文字CNY。[8]item点amount读取这条具体记录的金额零。静态方法经常用于工厂入口或围绕这一类数据的工具，普通方法则处理某个对象自己的状态。把共享信息和实例状态分清，多个对象一起出现时也能判断每次读写影响哪一层。')
page(c,'练习：通过公开方法读取','''class Wallet {
  private amount = 12;
  read(): number { return this.amount; }
}
const wallet = new Wallet();
console.log(wallet.amount);''','12',['amount 是 private 字段','read 是公开的读取方法','原调用直接访问了内部字段','修正为 wallet.read()'],
 '[1,2]这道题的钱包把amount标成private，内部先保存十二。[3]同时提供一个read方法，返回内部金额。[5,6]创建钱包以后，最后一行直接读取wallet点amount。请判断类型检查会指出哪一行，以及可以怎样利用现有的公开入口取得金额。给自己四秒，把字段的访问约定和调用位置对应起来。',
 '[6]修正版改成调用wallet点read。[3]read在类内部访问amount，返回十二。[6]外层再显示这个结果。访问修饰符让对象向外提供的能力更清楚，调用者按照公开入口使用，就能和类内部的维护方式配合。看到访问类字段的报错时，先查类定义，再找已经提供的公开方法，而不是急着改动整组字段的声明。',kind='exercise',fixed='class Wallet {\n  private amount = 12;\n  read(): number { return this.amount; }\n}\nconst wallet = new Wallet();\nconsole.log(wallet.read());',diagnostic='TS2341')

c=chapter('类型工具与模块配置')
page(c,'枚举为一组状态命名','''enum Status {
  Pending = "pending",
  Paid = "paid"
}
const current: Status = Status.Paid;
console.log(current);''','paid',['enum 为一组成员提供命名入口','字符串枚举明确各成员的值','通过枚举名读取对应成员','普通枚举会生成运行时对象'],
 '[1,2,3]除了把状态写成字符串字面量联合，还可以使用枚举，为一组值提供统一命名入口。这里Status包含Pending和Paid两个成员，各自指定对应文字。代码通过Status点成员名取得值，编辑器也能提示这组候选项。先明确每个成员的实际值，再观察它怎样交给变量和函数使用。',
 '[5]current被声明为Status，接收Status点Paid。[6]运行时显示它对应的文字paid。普通枚举还会生成供运行时使用的对象，因此可以通过名字读取成员。字符串字面量联合侧重直接描述允许值，枚举则提供统一的成员入口；项目可以根据组织习惯选择。初学时先把示例中采用的这套方式保持一致，状态代码就比较容易查找。')
page(c,'keyof 与索引访问类型','''type Expense = {name: string; amount: number};
type Field = keyof Expense;
type Amount = Expense["amount"];
const field: Field = "amount";
const value: Amount = 12;
console.log(field, value);''','amount 12',['keyof 得到属性名称的联合','Field 允许 name 或 amount','索引访问类型取得某属性的类型','Amount 对应 number'],
 '[1,2]已经有Expense类型时，可以让工具从它推导新的类型。keyof Expense得到它的属性名范围，也就是name和amount组成的联合。[3]Expense方括号amount取得amount属性的类型，所以Amount对应number。这里处理的是类型之间的关系，帮助多个位置共用同一份字段说明，减少重复书写。',
 '[4]field只从允许的属性名里选择，这里保存amount。[5]value按Amount要求保存数字十二。[6]显示时得到amount和十二。以后调整Expense里的字段类型，依赖这些关系的代码也会跟着获得新的检查信息。读类型工具时，先把最外层名称还原为它引用的原始类型，再逐步看取了哪些属性或属性值，复杂表达式也能分层理解。')
page(c,'typeof 从已有值取得类型','''const defaults = {currency: "CNY", limit: 30};
type Settings = typeof defaults;
const personal: Settings = {currency: "USD", limit: 50};
console.log(personal.currency);
console.log(personal.limit);''','USD\n50',['类型位置的 typeof 引用已有值的类型','Settings 描述 currency 与 limit','新的配置对象保持相同字段结构','与运行时 typeof 的用途分开阅读'],
 '[1]默认配置已经写成对象，currency保存文字，limit保存数字。[2]类型位置的typeof可以读取这个对象的类型信息，起名为Settings。[3]再声明personal时，按照同一套字段结构提供币种和限额。这样配置值和对应的类型说明可以保持联系，避免分别书写后逐渐出现差异。',
 '[4]personal保存新的币种USD。[5]限额改为五十。类型位置的typeof用于形成类型说明；放在运行语句中的typeof则取得类型名称文字。阅读时先看它出现在type声明里，还是普通表达式里，就能判断当前在做哪一层工作。此处默认对象的属性推断为string和number，因此新对象可以使用同类的其他文字和数字。')
page(c,'Pick 与 Partial 复用已有结构','''type Expense = {name: string; amount: number; note: string};
type Brief = Pick<Expense, "name" | "amount">;
type Update = Partial<Expense>;
const brief: Brief = {name: "午餐", amount: 12};
const update: Update = {amount: 15};
console.log(brief.name);
console.log(update.amount);''','午餐\n15',['Pick 选取已有类型中的部分属性','Partial 把各属性整理为可选','摘要对象只保留需要的字段','更新对象只提供本次准备修改的内容'],
 '[1]同一种记录会出现在完整详情、列表摘要和局部更新中，可以从原类型派生所需结构。[2]Pick从Expense里选出name和amount，形成摘要类型Brief。[3]Partial把Expense的各属性整理为可选，形成更新类型Update。先确定使用场景需要哪些字段、哪些可以省略，再选择对应的类型工具，关系就很具体。',
 '[4]brief提供名称和金额，适合列表显示。[5]update只提供这次准备修改的金额十五。[6,7]读取时分别显示午餐和十五。常见工具里，Omit按属性名排除字段，Readonly提供只读视图，Record按键类型安排对应值。它们都在复用已有的结构信息。入门先掌握选字段和设为可选这两种需求，再根据项目遇到的情况逐步扩展。')
page(c,'导出类型与导出函数','''// budget.ts
export type Expense = {amount: number};
export function total(items: Expense[]): number {
  return items.reduce((sum, item) => sum + item.amount, 0);
}
// main.ts
import {total} from "./budget.js";
import type {Expense} from "./budget.js";
const items: Expense[] = [{amount: 12}, {amount: 8}];
console.log(total(items));''','20',['export 提供类型与运行时工具','import type 标明只用于类型检查的导入','普通 import 取得运行时函数','两个完整文件都在配套目录中'],
 '[2]当代码增多，可以把类型和相关函数放到独立模块。budget文件先导出Expense类型。[3,4]total函数按这份类型接收记录数组，累计金额再返回数字。模块让使用者按需要导入工具，也方便回到定义位置查找实现。类型说明和实际操作围绕同一份数据组织，阅读时能够互相对照。',
 '[7]主文件普通导入total，因为运行时需要调用这个函数。[8]再用import type导入Expense，说明它用于类型检查。[9,10]建立两条记录并求总额，得到二十。路径中的点斜线从当前文件所在目录开始，编译器会处理相应的TypeScript来源。配套目录保留budget和main两个完整文件，用给出的配置编译，再运行生成的主文件即可。',kind='module')
page(c,'练习：在严格检查下处理空值','''// tsconfig.json 中启用 strict: true
function length(text: string | null): number {
  return text.length;
}
console.log(length(null));''','0',['strict 打开一组严格类型检查','text 可能为 null 时要安排处理','先判断空值，再读取 length','修正版对空值返回 0'],
 '[1]项目的tsconfig保存共同的检查和生成选项，strict用于打开一组严格检查。[2,3]这里函数允许接收字符串或null，却直接读取text点length。请判断检查工具会提示哪种可能情况，以及怎样给这条路线安排一个明确的返回结果。[5]当前调用交入null，你可以从输入开始跟踪，先找出读取发生以前缺少的步骤。',
 '[3]修正版先检查text是否为null，空值时直接返回零，有文字时再读取长度。[5]本次调用因此显示零。配套项目还使用noEmitOnError，让检查失败时先修正再生成，target选择生成代码版本，module安排模块输出方式。刚开始先用课程提供的固定配置，把注意力放在错误位置和处理路线，再逐项理解配置怎样影响自己的项目。',kind='exercise',fixed='// tsconfig.json 中启用 strict: true\nfunction length(text: string | null): number {\n  return text === null ? 0 : text.length;\n}\nconsole.log(length(null));',diagnostic='TS18047')
