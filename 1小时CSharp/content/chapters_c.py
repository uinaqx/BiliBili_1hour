from author import chapter,page
c=chapter('方法、参数与泛型')
page(c,'把计算步骤写成方法','''static int Remaining(int budget, int spent)
{
    return budget - spent;
}
int left = Remaining(30, 25);
Console.WriteLine(left);''','5',['方法用名称组织一组可复用步骤','参数说明调用时需要哪些输入','返回类型 int 说明最后交回整数','return 把结果交回调用位置，再继续后续语句'],
'[1]同一段计算要多次使用时，可以把步骤写成方法。Remaining表示计算剩余金额，括号里的两个参数分别是预算和已花金额，前面的int说明返回一个整数。这里先使用static写一个独立计算步骤，后面学习类时再把方法组织到对象里。[2,3,4]方法体执行相减，return把计算结果交回调用的位置。',
'[5]调用时写方法名和实际数据，三十交给budget，二十五交给spent。方法计算出五，再把它交给外面的left。[6]随后显示五。可以把方法想成一个输入和输出明确的小工具，先看它需要什么，再看它交回什么。以后统计总额、检查金额和生成文字，都可以分别写成方法，让主流程更像按顺序连接这些小工具。')
page(c,'返回值、默认参数与命名参数','''static void Show(string name, int amount = 12)
{
    Console.WriteLine($"{name}：{amount}");
}
Show("午餐");
Show(amount: 8, name: "交通");''','午餐：12\n交通：8',['void 表示方法执行后没有返回值','默认参数在调用者省略该项时提供值','命名参数按名称说明传入数据的用途','方法参数只在该方法的作用范围中使用'],
'[1,2,3,4]有的方法主要完成动作，例如显示记录，返回类型就写void。这里Show接收名称和金额，金额参数提供默认值十二，方法体把两项组织成文字显示出来。参数名在方法内部承担局部名称的作用，每次调用都使用本次交入的数据。把输入和动作放在一起看，就能理解它为什么需要这些参数。',
'[5]第一次只交入午餐，金额采用默认值十二，所以显示午餐十二。[6]第二次按参数名写出金额八和名称交通，最后显示交通八。命名参数能让某些调用更清楚，尤其是多个参数类型相同时。需要把结果交给后续计算，就选择具体返回类型，需要完成显示或更新动作，就可以使用void，让每个方法的用途保持明确。')
page(c,'跟踪参数与作用范围','''static void Change(int value)
{
    value = 99;
    Console.WriteLine(value);
}
int amount = 12;
Change(amount);
Console.WriteLine(amount);''','99\n12',['普通 int 参数接收调用时数值的一份副本','value 属于方法内部，amount 属于外部主流程','修改 value 后，外面的 amount 继续保存 12','希望交出新值时，可以设计一个返回 int 的方法'],
'[1,2,3,4,5]方法里面的value是本次调用的局部参数。执行到第三行时，把它改成九十九，然后显示这份局部值。[6,7]外面的amount先保存十二，普通整数参数传递时把数值的一份副本交给value。你可以画两个分别写着十二的小格子，一个叫amount，一个叫value，进入方法后修改的是后面那个格子。',
'[8]所以方法里面先显示九十九，回到主流程再显示amount，仍然是十二。跟踪参数时，先确认当前正在执行哪个方法，再区分各自的局部名字。需要根据旧金额算出新金额时，可以让方法返回一个整数，再由调用者决定保存到哪里。后面学习对象引用时，还会观察多个名字共同找到同一个对象的情况，届时再对照这份数值副本理解。')
page(c,'重载为不同输入提供做法','''Console.WriteLine(Formatter.Label(12));
Console.WriteLine(Formatter.Label("午餐"));
static class Formatter
{
    public static string Label(int value) => $"金额：{value}";
    public static string Label(string value) => $"名称：{value}";
}''','金额：12\n名称：午餐',['同名方法可通过不同参数列表形成重载','编译器根据调用处的参数选择匹配版本','=> 在本页用来简写单个表达式的方法体','Formatter 暂时作为相关显示方法的组织位置'],
'[3,4]一个功能有不同类型的输入，可以提供同名方法的不同版本，这叫重载。这里用Formatter集中组织显示工具，public static先看作让外部直接使用这组方法的写法。[5]接收整数的Label返回金额文字。[6]接收字符串的Label返回名称文字。箭头把只有一个表达式的方法体写得更短，表达式的结果就是返回值。',
'[1]第一次交入整数十二，编译工具选择整数版本，显示金额十二。[2]第二次交入文字午餐，选择字符串版本，显示名称午餐。判断调用哪个重载时，重点看参数的数量、类型和排列。方法名相同可以表达相近用途，各版本的输入约定则把具体处理区分开。下一章会正式认识class，再把这些组织方式放进完整的类和对象关系中理解。')
page(c,'用泛型保留输入输出的类型','''static T Echo<T>(T value)
{
    return value;
}
int amount = Echo(12);
string name = Echo("午餐");
Console.WriteLine(amount + 8);
Console.WriteLine(name.ToUpper());''','20\n午餐',['T 是本次调用使用的类型参数','参数和返回值使用同一个 T，保留两者关系','编译器可根据实参推断本次 T 的类型','List<int> 等容器也用泛型约定元素种类'],
'[1,2,3,4]如果同样的步骤可以处理不同类型，就能把具体类型留成一个参数。Echo的尖括号里写T，参数类型和返回类型也写T，意思是本次传入哪种类型，就按同一种类型交回。这种带类型参数的写法叫泛型。这里直接返回输入，步骤非常简单，正好用来观察输入和输出之间的对应关系。',
'[5,7]传入十二时，本次T确定为int，返回整数十二，接着加八显示二十。[6,8]传入午餐时，本次T确定为string，返回文字，随后可以调用字符串操作。前面见过的List加尖括号，也是用类型参数说明容器保存什么。泛型先掌握这条主线，让一套做法适应多种类型，同时把调用之间的类型关系保留下来。')
page(c,'练习：方法调用与求和','''static int Sum(List<int> values)
{
    int total = 0;
    foreach (int value in values) total += value;
    return total;
}
var amounts = new List<int> { 12, 8, 5 };
int result = Sum(amounts);
Console.WriteLine(result);''','25',['方法参数接收本次准备统计的列表','局部 total 从零开始逐项累加','return 将 25 交给外面的 result','可改变输入列表，再复用同一个方法'],
'[1,2,3,4,5,6]本章练习，把列表求和包装成Sum方法。参数values接收一组整数，局部total从零开始，foreach逐项累计，最后返回结果。[7,8,9]主流程准备十二、八、五，交给方法，再显示result。请先跟踪调用进入方法时发生什么，再跟踪return以后程序回到哪里，判断最后的输出。',
'[3,4,5]累计过程是零变成十二，再变成二十，最后成为二十五，return交回二十五。[8,9]调用位置用result接住它，显示二十五。想计算另一组数据，只要准备另一份列表再次调用。这样把变化的输入放到参数里，把稳定的处理保留在方法体中，程序就能自然复用。下一章再把每条记录的名称和金额放在一起，建立自己的数据类型。',kind='exercise')
c=chapter('类、对象与属性')
page(c,'用类描述一条记录','''var item = new Expense();
item.Name = "午餐";
item.Amount = 12;
Console.WriteLine($"{item.Name}：{item.Amount}");
class Expense
{
    public string Name = "";
    public int Amount;
}''','午餐：12',['class 描述一类对象保存哪些数据','new 创建一个具体对象，变量保存它的引用','本页 Name 与 Amount 是公开字段','点号访问该对象的字段，再按需要显示'],
'[5,6,7,8,9]一条开销同时有名称和金额，可以用class把它们组织起来。Expense描述这类对象的结构，Name保存文字，Amount保存整数，public让类外面的代码可以访问这些字段。你可以把类看作记录格式，把对象看作按这个格式建立的一份具体记录。后面增加分类和日期时，也可以继续围绕这份记录整理字段。',
'[1]new Expense创建一个对象，item保存找到这个对象的引用。[2,3]通过点号设置名称午餐和金额十二。[4]再读取同一对象的两个字段，显示午餐十二。先看类定义有哪些成员，再看对象创建以后怎样填写和读取，关系就很清楚。本页先用字段直接展示数据，下一页认识属性，为读取和修改提供更清楚的公开入口。')
page(c,'属性提供读取和设置入口','''var item = new Expense();
item.Name = "午餐";
item.Amount = 12;
Console.WriteLine(item.Amount);
class Expense
{
    public string Name { get; set; } = "";
    public int Amount { get; set; }
}''','12',['属性把读取和设置约定放在成员声明中','get 提供读取入口，set 提供赋值入口','自动属性由编译器安排保存数据的位置','属性名采用大写开头，局部变量常用小写开头'],
'[5,6,7,8,9]属性把对象成员的读取和设置入口写在一起。get表示允许读取，set表示允许设置。这种简短写法叫自动属性，编译器会安排实际保存数据的位置。Name初值是空字符串，Amount采用整数的默认值零。先理解公开的属性是怎样被外部使用的，再逐步学习在入口里加入检查或计算，学习顺序会更自然。',
'[1,2,3]创建对象以后，使用方式依然是通过点号给Name和Amount赋值。[4]随后读取金额，显示十二。你会在很多C sharp项目里看到属性名大写开头，局部变量小写开头，这是常见命名习惯，方便区分类的成员和临时数据。属性还可以只公开读取，把修改集中交给类自己的方法，这正是下一页要观察的组织方式。')
page(c,'构造函数建立可用的对象','''var wallet = new Wallet(30);
wallet.Spend(12);
Console.WriteLine(wallet.Balance);
class Wallet
{
    public int Balance { get; private set; }
    public Wallet(int balance) { Balance = balance; }
    public void Spend(int amount) { Balance -= amount; }
}''','18',['构造函数与类同名，创建对象时负责初始化','private set 把属性设置限制在类内部','公开 Spend 方法表达一次业务操作','30 初始化余额，消费 12 后读取到 18'],
'[4,5,6]Wallet表示钱包，余额属性公开读取，把设置入口留在类内部。[7]与类同名的Wallet方法是构造函数，new创建对象时会执行它，把传入的初始余额保存好。[8]Spend表示消费，接收金额并减少余额。把数据和围绕数据的操作组织在一起，外面的代码就能按业务动作使用这个对象。',
'[1]创建钱包时传入三十，构造函数把Balance初始化为三十。[2]调用Spend交入十二，余额更新为十八。[3]读取并显示余额，结果是十八。private表示只在类内部访问，public表示向外提供入口。实际业务还可以在Spend里检查金额和余额，保证每次消费都经过同一份处理。读对象程序时，沿着创建、调用、读取这三个阶段跟踪状态。')
page(c,'引用让多个名字找到同一对象','''var first = new Expense { Amount = 12 };
var second = first;
second.Amount = 20;
Console.WriteLine(first.Amount);
Console.WriteLine(ReferenceEquals(first, second));
class Expense
{
    public int Amount { get; set; }
}''','20\nTrue',['类变量保存对象引用，赋值会复制这份引用','first 与 second 找到同一个 Expense 对象','通过 second 修改后，从 first 也读到 20','ReferenceEquals 判断是否引用同一个对象'],
'[1]这一页先创建金额十二的对象，让first保存它的引用。[2]把first赋给second，复制的是找到对象的这份引用。可以画一个记录方框，再画first和second两个名字，各自用箭头指向同一个方框。和前面整数参数的数值副本相比，这次两个名字共同找到了一份对象数据，观察方式也就跟着改变。',
'[3,4]通过second把Amount改成二十，再从first读取，同样得到二十，因为读取的是同一个对象。[5]ReferenceEquals进一步确认两个引用找到同一个对象，结果为真。要建立另一份独立记录，就再次使用new，并按需要复制字段。学习引用时，先数清楚一共创建了几个对象，再看每个名字指向哪里，很多更新行为都能由这张关系图解释。')
page(c,'结构体与枚举表达小型数据','''var first = new Point { X = 1 };
var second = first;
second.X = 9;
Console.WriteLine(first.X);
Console.WriteLine(PayStatus.Paid);
struct Point { public int X { get; set; } }
enum PayStatus { Pending, Paid }''','1\nPaid',['struct 定义值类型，本页赋值复制 X 的值','更新 second 后，first.X 仍然是 1','enum 为一组具名选项提供共同类型','类、结构体和枚举按数据用途选择'],
'[6]struct定义结构体，它是一种值类型。这里Point只有一个整数属性X，用来观察复制行为。[1,2]first的X为一，把first赋给second，会复制这份结构体值。[3,4]随后修改second的X为九，从first读取依然得到一。请与上一页的类对象对照，一页是两个引用找到同一对象，这一页是两个各自保存数值的小记录。',
'[7]enum定义枚举，给有限的一组情况起清楚的名字。PayStatus包含待付款和已付款两种选项。[5]显示Paid会得到这个枚举成员的名称。状态数据使用具名选项，条件判断就能直接围绕业务含义来写。入门先掌握类、结构体和枚举分别适合什么，再根据需要学习更详细的复制规则、约束和表现形式，跟着实际例子逐步扩展即可。')
page(c,'练习：通过公开方法修改属性','''var wallet = new Wallet();
wallet.Balance = 12;
Console.WriteLine(wallet.Balance);
class Wallet
{
    public int Balance { get; private set; }
    public void Add(int value) { Balance += value; }
}''','12',['Balance 公开读取，设置入口为 private','类外通过公开 Add 方法执行增加操作','修正版将直接赋值改为 wallet.Add(12)','修改路径集中在类中，后续方便统一加入检查'],
'[1,2]本章练习，新建钱包以后，直接把Balance设置为十二。[4,5,6]但属性的设置入口写着private，请根据访问范围判断编译工具会在哪里给出提示。[7]类已经提供Add方法，可以接收一个整数增加余额。请想一想，调用者希望完成增加金额这个动作，怎样使用现成的公开入口把程序改通。',
'[2]修正版把直接设置改成调用wallet点Add，传入十二。方法在类内部执行，所以能够通过设置入口更新Balance。[3]最后公开读取余额，显示十二。把修改动作集中到方法里，随后就可以在同一处加入金额检查、操作记录或通知。调用代码按清楚的动作使用对象，类内部负责维护数据，这就是封装在本页例子中的具体作用。',kind='exercise',fixed='var wallet = new Wallet();\nwallet.Add(12);\nConsole.WriteLine(wallet.Balance);\nclass Wallet\n{\n    public int Balance { get; private set; }\n    public void Add(int value) { Balance += value; }\n}',diagnostic='CS0272')
