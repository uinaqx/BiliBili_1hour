from author import chapter,page
c=chapter('继承、接口与多态')
page(c,'继承已有类型的成员','''var student = new Student { Name = "小林", Score = 80 };
Console.WriteLine($"{student.Name} {student.Score}");
class Person
{
    public string Name { get; set; } = "";
}
class Student : Person
{
    public int Score { get; set; }
}''','小林 80',['冒号在类声明中表示继承基类','Student 继承 Person，并增加 Score','派生类对象可使用继承来的公开成员','共有数据放到基类，专有数据放到派生类'],
'[3,4,5,6]如果几类对象有共同信息，可以把共有部分放到一个基类。Person保存姓名属性。[7,8,9,10]Student后面写冒号Person，表示学生继承人员这份结构，再增加成绩Score。这样学生同时具备姓名和成绩，后续另外一种人员类型也可以从共有部分扩展。先从数据之间的关系出发，继承就有了具体用途。',
'[1]创建学生时，用花括号一次设置姓名小林和成绩八十，这叫对象初始化器。[2]随后读取两项内容，显示小林和八十。读取Name时，使用的是从Person继承来的成员，读取Score时，使用Student自己声明的成员。设计类型时，可以先找出稳定的共有部分，再决定怎样扩展；当几个对象需要共同参与一种操作时，还可以通过接口描述操作要求。')
page(c,'虚方法根据实际对象选择实现','''Animal pet = new Cat();
pet.Speak();
class Animal
{
    public virtual void Speak() => Console.WriteLine("动物发声");
}
class Cat : Animal
{
    public override void Speak() => Console.WriteLine("喵");
}''','喵',['virtual 允许派生类提供自己的实现','override 明确重写基类的虚方法','Animal 变量可以引用 Cat 对象','虚方法调用根据实际对象类型选择实现'],
'[3,4,5,6]基类Animal提供Speak方法，virtual表示派生类可以给出自己的实现。[7,8,9,10]Cat继承Animal，用override写出猫的发声方法，显示喵。请把virtual和override配成一组记忆，基类开放这项操作的变化位置，派生类在对应位置写出自己的做法。代码读起来就像同一个动作有不同对象版本。',
'[1]外面把一只猫交给Animal类型的变量pet，变量负责按动物的共同约定使用对象。[2]调用虚方法Speak时，运行时根据实际对象是一只猫，选择Cat提供的实现，最后显示喵。这种同一调用根据实际对象表现出不同做法的方式叫多态。实际项目里，形状求面积、不同渠道发通知，都可以用共同操作连接各自的实现。')
page(c,'抽象类约定需要完成的方法','''Shape shape = new Square(3);
Console.WriteLine(shape.Area());
abstract class Shape
{
    public abstract int Area();
}
class Square : Shape
{
    private int side;
    public Square(int value) { side = value; }
    public override int Area() => side * side;
}''','9',['abstract class 描述有待具体化的共同类型','抽象方法只声明操作约定，由派生类实现','Square 的构造函数保存边长','通过 Shape 调用 Area，执行正方形的实现'],
'[3,4,5,6]Shape表示形状，写成abstract class。抽象方法Area只声明返回一个整数，具体面积怎样计算留给具体形状来完成。[7,8,9,10,11,12]Square表示正方形，构造函数保存边长，重写Area返回边长乘边长。这里把共同的面积操作和正方形的计算公式分开组织，使用者就能统一提出求面积的请求。',
'[1,2]创建边长三的正方形，通过Shape变量调用Area，得到九。抽象类适合表达共同基础，并把部分操作留给派生类补齐。学习时先看基类要求哪些方法，再看具体类怎样实现这些方法，最后跟踪对象创建和调用路线。这样从声明到实现再到结果连起来，就能理解抽象类型在这段程序中承担的角色。')
page(c,'接口约定对象能提供的操作','''IPrintable item = new Expense("午餐");
item.Print();
interface IPrintable
{
    void Print();
}
class Expense : IPrintable
{
    private string name;
    public Expense(string value) { name = value; }
    public void Print() => Console.WriteLine(name);
}''','午餐',['interface 描述调用者可以依赖的操作','实现接口的类提供相应方法','接口变量统一使用具体对象的能力','IPrintable 命名中的 I 是常见接口命名习惯'],
'[3,4,5,6]接口把一组操作要求起一个名字。IPrintable要求提供Print方法，可以读成具备打印或显示能力的对象。[7,8,9,10,11,12]Expense在类声明里列出这个接口，并提供公开的Print实现，把自己的名称显示出来。接口名称常用大写I开头，方便在项目中识别。你可以先围绕方法约定理解接口，再学习更丰富的成员形式。',
'[1,2]调用者用IPrintable接收一条开销记录，然后只需要调用Print，实际显示午餐。以后另外一个类型也实现同样接口，就能通过相同入口参与这项操作。基类适合组织共同基础，接口适合描述调用者依赖的能力。项目里先问当前代码真正需要对象做什么，再把这份需要写成接口，依赖关系通常会更清楚。')
page(c,'空值与模式匹配','''string? note = null;
Console.WriteLine(note?.Length ?? 0);
object data = 12;
if (data is int amount)
    Console.WriteLine(amount + 8);''','0\n20',['string? 说明变量允许保存 null','?. 在对象存在时继续读取成员','?? 为 null 的结果提供备用值','is int amount 检查类型并在分支中提供整数变量'],
'[1]有些数据可能暂时没有内容，例如记录备注，可以用string后面加问号表示允许空值，null就是这种空值。[2]问号点号表示对象存在时再读取Length，两个问号为得到的空值提供备用的零。所以这一行显示零。把可能缺失的数据写进类型约定，再在使用处选择默认值或条件分支，代码就能把两种情况表达完整。',
'[3]object可以接收各种值，这里保存整数十二。[4]is int amount检查当前数据是否是整数，匹配成功时，把可用的整数交给分支里的amount。[5]随后加八显示二十。这种一边检查一边取得匹配结果的写法属于模式匹配。和前面TryParse配合out类似，先确认情况，再使用确认后的数据，程序的每一步都有明确依据。')
page(c,'练习：接口调用选择哪份实现','''IMessage message = new Welcome();
message.Show();
interface IMessage { void Show(); }
class Welcome : IMessage
{
    public void Show() => Console.WriteLine("欢迎学习");
}''','欢迎学习',['message 按 IMessage 的约定使用对象','实际创建的是 Welcome，提供 Show 实现','调用 Show 时执行对象对应的实现','先看接口约定，再看 new 创建了哪个具体类型'],
'[1]这一题创建Welcome对象，交给IMessage类型的变量。[3]接口只要求Show这个操作。[4,5,6,7]Welcome提供具体实现，显示欢迎学习。[2]请判断从message调用Show时，程序会执行哪里，最终显示什么。先把变量的类型和实际创建的对象分别写下来，再用箭头连接两者，沿着方法调用找到实际实现。',
'[2,6]最终显示欢迎学习，因为message引用的对象是Welcome，它的Show方法负责完成这次调用。接口让调用者依赖共同约定，具体类把约定落成实际动作。学到这里，可以把对象程序分成三层阅读，数据和能力如何声明，对象怎样创建并初始化，最后哪些方法真正被调用。顺着这三层跟踪，继承、接口和多态就能放到同一段程序里理解。',kind='exercise')
c=chapter('委托与集合查询')
page(c,'把一段做法作为参数传递','''Func<int, int> doubleValue = value => value * 2;
Action<string> show = text => Console.WriteLine(text);
Console.WriteLine(doubleValue(6));
show("处理完成");''','12\n处理完成',['Func<int,int> 接收 int 并返回 int','Action<string> 接收文字并执行动作','lambda 箭头左边是参数，右边是处理表达式','委托变量保存可以调用的做法，便于传递行为'],
'[1]除了传递数字和文字，程序也能传递一段做法。Func的两个int分别说明输入整数，返回整数。箭头左边的value是输入，右边把它乘二，这种简短的方法表达式叫lambda。变量doubleValue保存这份可调用的做法。[2]Action接收字符串并完成显示动作，适合只执行操作的情况，这些类型都是常用委托。',
'[3]像调用方法一样，给doubleValue传入六，得到十二，再显示。[4]给show传入处理完成，就会执行显示动作。先看委托约定接收什么、交回什么，再看lambda写了怎样的处理，就能把两部分配起来。下一页筛选集合时，我们会把判断条件写成lambda交给筛选工具，让它对每个元素应用同一份规则。')
page(c,'Where 筛选，Select 转换','''var amounts = new List<int> { 12, 8, 5 };
var selected = amounts.Where(value => value >= 8);
var raised = selected.Select(value => value + 1);
Console.WriteLine(string.Join(",", raised));''','13,9',['Where 根据返回 bool 的条件保留元素','Select 把每个元素转换成新的结果','本页先保留 12、8，再分别加一','这些集合查询工具属于 LINQ，先按步骤读即可'],
'[1]继续处理十二、八、五这组三笔金额。[2]Where接收一个判断方法，对每一项检查是否大于等于八，通过的保留下来，因此得到十二和八这条结果序列。[3]Select再把每一项加一，形成十三和九。把两步先后写开，就像先筛选符合条件的记录，再整理准备显示的数据，处理路线很直观。',
'[4]Join实际遍历结果并连接显示，最后看到十三和九。这组查询工具叫LINQ，它把常见的筛选、转换和统计整理成一致的调用形式。刚开始先分别写出每一步，确认输入和输出，再按需要连接调用。lambda里的value代表当前元素，判断或转换的规则由右边表达式决定，和前面循环里一轮处理一项的思路相通。')
page(c,'排序与常用统计','''int[] amounts = { 12, 8, 5 };
var sorted = amounts.OrderBy(value => value);
Console.WriteLine(string.Join(",", sorted));
Console.WriteLine(amounts.Sum());
Console.WriteLine(amounts.Max());''','5,8,12\n25\n12',['OrderBy 根据选择出的键生成升序结果','本页直接用金额本身作为排序键','Sum 求和，Max 取最大值','原数组仍按原顺序保存，排序结果单独遍历'],
'[1,2]OrderBy负责排序，lambda选择排序依据，也叫键。这里直接选金额本身，所以得到按金额从小到大的结果序列。[3]遍历显示时，看到五、八、十二。换成记录对象以后，也可以选择记录的金额作为键，让整条记录按金额排列。先问按什么排序，再把对应值放进lambda，规则就能准确表达。',
'[4]Sum求出总额二十五。[5]Max取得最大值十二。统计方法完成的是一类常见遍历操作，使用前先确认输入数据和所需结果。这里排序结果单独保存，原数组仍然保持十二、八、五的原有顺序。需要把结果固定到新列表时，可以再调用ToList；下一页就观察查询什么时候读取原始数据，以及固定结果以后有什么变化。')
page(c,'查询执行与 ToList 快照','''var amounts = new List<int> { 12, 5 };
var query = amounts.Where(value => value >= 8);
amounts.Add(20);
Console.WriteLine(string.Join(",", query));
var snapshot = query.ToList();
amounts.Add(30);
Console.WriteLine(string.Join(",", snapshot));
Console.WriteLine(string.Join(",", query));''','12,20\n12,20\n12,20,30',['Where 保存查询规则，遍历时读取数据源','首次遍历已经能看到后来加入的 20','ToList 当场执行查询，把结果保存成列表','再次遍历 query 时，会读取包含 30 的当前数据源'],
'[1,2]这一页观察时间顺序。amounts最初是十二和五，Where保存大于等于八的筛选规则。[3,4]随后添加二十，再遍历query，当前数据源已经有二十，所以显示十二和二十。对这样的查询，建立规则和实际遍历发生在不同位置。读程序时，把哪一行开始真正取得结果标出来，后续变化就容易跟踪。',
'[5]ToList会当场执行查询，把当前结果保存成一个新列表，得到十二和二十。[6,7]之后往原列表添加三十，snapshot保留先前取得的那两项。[8]再次遍历query，就会读取当前数据源，显示十二、二十、三十。需要保留某一时刻的结果，就把值取出来保存，需要按当前数据重新查询，就在相应位置再次遍历这份规则。')
page(c,'用事件连接通知与处理','''var alarm = new Alarm();
alarm.Triggered += () => Console.WriteLine("预算提醒");
alarm.Raise();
class Alarm
{
    public event Action? Triggered;
    public void Raise() => Triggered?.Invoke();
}''','预算提醒',['event 向外提供订阅通知的入口','+= 把处理方法加入订阅，-= 取消订阅','发布者在类内部触发事件，订阅者执行对应操作','?.Invoke 在存在处理方法时进行调用'],
'[4,5,6]当某件事发生后，需要通知其他部分，可以使用事件。Alarm声明一个Action类型的事件Triggered，订阅者提供收到通知后要执行的方法。[7]Raise在类内部触发它，问号点Invoke表示存在订阅方法时进行调用。可以把发布者理解成发出提醒的地方，把订阅者理解成接到提醒后采取行动的地方，双方通过事件连接。',
'[1,2]外部创建Alarm，用加等号加入一段lambda，收到通知后显示预算提醒。[3]随后调用Raise，订阅的方法被执行，最终显示预算提醒。按钮点击、状态更新和记录变化都可以用类似方式组织通知。订阅通常配合减等号取消，按对象使用周期管理。入门先看清订阅发生在哪里、触发发生在哪里，再跟踪被调用的处理方法，路线就很明确。')
page(c,'练习：筛选后的数量与合计','''int[] amounts = { 12, 8, 5 };
var selected = amounts.Where(value => value >= 8).ToList();
Console.WriteLine(selected.Count);
Console.WriteLine(selected.Sum());''','2\n20',['Where 保留满足金额条件的元素','ToList 得到本次查询的具体结果列表','筛选后剩下 12 和 8，数量为 2','Sum 对筛选后的列表求和，得到 20'],
'[1,2]本章练习，从十二、八、五里保留大于等于八的金额，再使用ToList保存结果。[3,4]随后分别显示数量和合计。请先写出筛选后到底有哪些元素，再计算Count和Sum。调用链可以从左到右拆开看，原数组交给Where，筛选规则产生结果，ToList把结果保留下来，后面的统计都围绕这份新列表完成。',
'[2]满足条件的是十二和八，五被筛掉。[3]列表有两项，所以先显示二。[4]两项相加等于二十，所以再显示二十。到这里你已经能把多种方法连成一个处理过程，先按规则选数据，再根据目标做转换、排序或统计。练习时可以每次只改变一个条件，先预测结果再运行，逐步熟悉每个工具具体读入什么、交出什么。',kind='exercise')
