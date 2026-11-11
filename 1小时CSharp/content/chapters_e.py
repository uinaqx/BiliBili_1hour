from author import chapter,page
c=chapter('异常、文件与异步')
page(c,'用 try 和 catch 处理异常','''try
{
    int amount = int.Parse("abc");
    Console.WriteLine(amount);
}
catch (FormatException)
{
    Console.WriteLine("请输入整数");
}''','请输入整数',['try 包住可能出现异常的操作','Parse 遇到无法解析的文字会抛出格式异常','catch 按异常类型接住对应失败','可预期的输入问题优先用 TryParse 表达分支'],
'[1,2,3]执行过程中有些操作会用异常报告失败。int点Parse尝试把abc解析成整数，遇到这份文字时抛出FormatException，也就是格式异常。把可能抛出异常的操作放进try，就能在附近安排处理。[4,5]异常抛出后，执行路线转向匹配的catch，因此本页的金额显示语句会被跳过，程序开始寻找对应的处理方法。',
'[6,7,8,9]catch写出准备接住的异常类型，这里显示请输入整数，随后继续执行结构后面的代码。请按抛出位置、匹配类型和处理动作三个步骤跟踪。面对日常输入，TryParse能把成功和失败直接写成分支；文件访问等操作则经常采用异常处理。根据操作本身提供的接口选择相应写法，就能把失败路线放到清楚的位置。')
page(c,'抛出异常与释放资源','''try
{
    Spend(-1);
}
catch (ArgumentOutOfRangeException)
{ Console.WriteLine("金额应大于等于零"); }
static void Spend(int amount)
{
    if (amount < 0) throw new ArgumentOutOfRangeException(nameof(amount));
    Console.WriteLine(amount);
}''','金额应大于等于零',['throw 把失败原因交给调用链上的处理位置','nameof 取得参数名称，方便错误定位','catch 处理对应类型的参数范围异常','finally 安排收尾，using 常用于自动释放可释放资源'],
'[7,8,9]自己的方法也可以用throw报告失败。Spend要求金额大于等于零，收到负数就抛出参数范围异常。nameof取得参数名称，帮助调用者定位是哪一项数据需要处理。[10,11]合法金额会继续执行后面的操作。这样方法把输入约定和检查放在一起，多个调用位置都能共用同一份规则，成功路径也保持直接。',
'[1,2,3,4,5,6]本页传入负一，异常交给外层catch，最后显示金额应大于等于零。异常处理还可以配合finally完成收尾。文件流等对象通常提供释放资源的约定，可以用using把使用范围包起来，离开范围时安排释放。下一页先用简短的文件工具方法完成保存和读取，等需要逐行处理大文件时，再学习更完整的流和资源管理写法。')
page(c,'把文字保存到文件','''string path = "note.txt";
File.WriteAllText(path, "午餐：12");
string text = File.ReadAllText(path);
Console.WriteLine(text);''','午餐：12',['WriteAllText 写入文字，已有文件会被覆盖','ReadAllText 读取文件内容并返回字符串','相对路径按程序当前工作目录解释','配套示例在独立目录运行，生成文件保留供检查'],
'[1]数据想保留到下次运行，可以写进文件。path保存文件名note点txt，这个相对路径按程序当前工作目录解释。[2]File点WriteAllText把午餐十二写到文件里，如果文件已经存在，会用本次内容覆盖。实际练习先使用专门的示例目录和明确文件名，这样每次运行都能清楚找到生成的数据，也方便观察内容发生了什么变化。',
'[3]ReadAllText读取文件的文字内容，交给text。[4]最后显示午餐十二。写入和读取组成了保存数据的最小过程。配套验证会在每个例子的独立运行目录执行，生成的文件可以直接打开检查。实际项目还可以使用完整路径，把保存位置安排在固定数据目录，并在读取时处理文件缺失或访问失败，让用户得到清楚的操作反馈。')
page(c,'用 JSON 保存结构化记录','''using System.Text.Json;
var amounts = new List<int> { 12, 8 };
string json = JsonSerializer.Serialize(amounts);
File.WriteAllText("amounts.json", json);
string saved = File.ReadAllText("amounts.json");
var restored = JsonSerializer.Deserialize<List<int>>(saved) ?? new List<int>();
Console.WriteLine(json);
Console.WriteLine(restored.Sum());''','[12,8]\n20',['Serialize 把数据整理成 JSON 文字','文件负责保存文字，数据格式由 JSON 表达','Deserialize 按指定类型读取回列表','实际项目读取后继续检查金额、名称等业务规则'],
'[1]JSON适合保存结构化数据，使用工具前引入System点Text点Json命名空间。[2,3]把十二和八的列表交给Serialize，得到方括号包住两个数字的JSON文字。[4]再把这份文字写进amounts点json文件。这里可以分成两层理解，JSON负责表达数据结构，文件负责把文字保存下来，它们分别完成格式转换和持久保存这两个步骤。',
'[5,6]重新读取文字，用Deserialize按整数列表解析回来。返回值可能为空，两个问号在这里提供空列表作为备用。[7,8]最后显示JSON文字和总额二十。完整记录也可以按同样方式序列化对象列表。读取以后再检查名称、金额和编号等业务规则，文件损坏时通过异常处理给出提示，恢复为可继续操作的状态，项目的数据路线就完整了。')
page(c,'用 async 和 await 等待文件结果','''string path = "async-note.txt";
await File.WriteAllTextAsync(path, "记录完成");
string text = await File.ReadAllTextAsync(path);
Console.WriteLine(text);
static async Task<int> LoadAmountAsync()
{
    await Task.Delay(10);
    return 12;
}
Console.WriteLine(await LoadAmountAsync());''','记录完成\n12',['异步操作返回 Task 或带结果的 Task<T>','await 等待本次操作完成后继续当前流程','async 让方法内部可以使用 await','等待期间把执行机会交回，适合文件与网络等 I/O'],
'[1,2,3,4]文件和网络操作经常需要等待。Async结尾的这些方法返回Task来表示一项异步工作，await等待本次结果准备好，再继续当前流程。先等待写入完成，再读取并显示文字，这样执行关系很清楚。异步等待期间可以把执行机会交回，让应用更方便地同时处理其他事情，界面程序和服务程序都经常使用这套写法。',
'[5,6,7,8,9]自己的异步方法在前面写async，返回Task加尖括号int，表示最终得到一个整数。方法先用Delay模拟短暂等待，再返回十二。[10]调用处await取得这份整数并显示。入门先沿着发起操作、等待结果、继续处理三个步骤阅读。课程采用顶层语句，入口也可以直接写await，配套项目已经设置好相应的语言版本。')
page(c,'练习：解析文件数据并统计','''File.WriteAllText("values.txt", "12,8,5");
string text = File.ReadAllText("values.txt");
int total = 0;
foreach (string part in text.Split(','))
{
    if (int.TryParse(part, out int amount)) total += amount;
}
Console.WriteLine(total);''','25',['Split 以逗号分开文字，取得三个片段','每个片段通过 TryParse 尝试转换','解析成功的数字参与累加','文件内容 12、8、5，合计输出 25'],
'[1,2]本章练习，把十二、八、五这段逗号分隔的文字写入文件，再读回来。[3,4]total从零开始，Split按逗号拆开文字，foreach逐项取得字符串片段。[5,6,7,8]每次用TryParse尝试转换，成功就累计。请预测最后显示的总额，再想一想如果文件中间多了一个abc片段，当前程序会怎样安排这一项的处理。',
'[4,6]三个合法片段分别转换成十二、八和五，total累计为二十五。[8]最终显示二十五。按照当前规则，abc解析失败时跳过这一项，继续处理后面的内容。如果业务需要逐项提示，也可以在失败分支记录行号或片段内容。先明确处理规则，再把读取、解析和统计连接起来，文件操作就能自然进入前面已经学会的数据处理流程。',kind='exercise')
c=chapter('综合项目与课程回顾')
page(c,'设计开销记录的数据结构','''var item = new Expense { Id = 1, Name = "午餐", Amount = 12m };
Console.WriteLine($"{item.Id} {item.Name} {item.Amount:F2}");
class Expense
{
    public int Id { get; set; }
    public string Name { get; set; } = "";
    public decimal Amount { get; set; }
}''','1 午餐 12.00',['Id 区分记录，Name 描述名称，Amount 保存金额','金额采用 decimal，输入输出使用同一约定','公开属性便于列表显示与 JSON 保存','先设计数据，再接上输入、统计和文件'],
'[3,4,5,6,7,8]最后把知识点连成一个开销管理程序。Expense保存编号、名称和金额。编号用来找到某条记录，名称用于展示，金额采用decimal完成十进制计算。把这三项设计清楚，后面的新增、删除、统计和保存就能围绕同一种记录格式连接。每增加一个功能，先确定它需要哪些字段，再决定相应的方法接收什么输入。',
'[1,2]这里创建编号一、午餐、十二元的记录，再读取三个属性显示出来，金额统一保留两位小数。配套完整项目使用控制台菜单，选添加、查看、删除或保存退出，就会调用对应的处理方法。本章先分几页看清关键步骤，再按README里的命令运行完整程序。跟着自己的输入观察数据怎样变化，就是把语法转成实际使用经验的过程。')
page(c,'把新增操作集中到方法','''var items = new List<Expense>();
Add("午餐", 12m);
Add("交通", 8m);
Console.WriteLine(items.Count);
void Add(string name, decimal amount)
{
    items.Add(new Expense { Name = name, Amount = amount });
}
class Expense
{
    public string Name { get; set; } = "";
    public decimal Amount { get; set; }
}''','2',['List<Expense> 保存多条记录对象','新增方法接收名称和金额，建立对应对象','局部方法可以使用外层同一作用范围的数据','完整项目先检查输入，再统一分配编号和保存'],
'[1]列表的元素类型改成Expense，每一项就能同时保存名称和金额。[5,6,7,8]新增方法接收两项输入，建立一个对象并添加到列表。本页用局部方法组织步骤，它可以使用外层作用范围中的items。项目变大以后，也可以把这些数据和操作放到专门的管理类里，先保持数据由哪一部分维护这条关系清楚即可。',
'[2,3]主流程调用两次，分别添加午餐十二和交通八。[4]当前列表Count是二。完整项目在进入新增操作前检查名称有内容、金额是大于等于零的有限十进制数，再分配独立编号。成功后统一保存并显示反馈。把新增规则集中在一处，按钮、菜单或其他输入方式都能连接到同样的处理步骤，后面扩展也更方便。')
page(c,'筛选记录并计算总额','''var items = new List<Expense>
{
    new Expense { Name = "午餐", Amount = 12m },
    new Expense { Name = "交通", Amount = 8m }
};
decimal total = items.Sum(item => item.Amount);
var names = items.Select(item => item.Name);
Console.WriteLine(string.Join("、", names));
Console.WriteLine($"总额：{total:F2}");
class Expense
{
    public string Name { get; set; } = "";
    public decimal Amount { get; set; }
}''','午餐、交通\n总额：20.00',['Sum 的选择器指出每条记录取哪个金额','Select 提取名称，再连接成展示文字','总额来自当前完整列表，更新后重新统计','金额显示格式统一，便于核对新增和删除结果'],
'[1,2,3,4,5]列表里现在有两条完整记录，午餐十二和交通八。循环里的当前元素从整数变成对象，但逐项处理的思路相同。[6]Sum的lambda取出每条记录的Amount，把金额相加，得到二十。[7]Select取出Name，形成准备显示的名称序列。先从当前元素读出目标字段，再交给统计或显示工具，步骤就很清楚。',
'[8,9]最后显示午餐、交通和总额二十点零零。数据变化以后，重新按当前列表统计，总额就会跟着更新。这里把名称展示和金额求和分开写，阅读时更容易看出每个结果从哪里来。如果要按名称筛选，可以先加Where条件再统计。原始数据、选择字段、形成结果，这条路线可以覆盖很多日常的数据展示任务。')
page(c,'用编号删除目标记录','''var ids = new List<int> { 1, 2, 3 };
int target = 2;
int removed = ids.RemoveAll(id => id == target);
Console.WriteLine(removed);
Console.WriteLine(string.Join(",", ids));''','1\n1,3',['编号作为记录身份，显示位置可以变化','RemoveAll 按条件移除所有匹配项并返回数量','本页只匹配编号 2，删除数量为 1','完整项目用相同方式比较 item.Id 与输入编号'],
'[1,2]删除记录时，使用独立编号会比较清楚。本页先用编号列表一、二、三单独观察删除步骤，target是准备删除的二。[3]RemoveAll接收一个判断方法，编号等于target时移除，并把实际移除数量返回。把条件读成找到编号二的记录，再看方法怎样处理匹配项，和前面的筛选逻辑就能互相对应。',
'[4,5]本次移除一项，列表剩下一和三。完整项目把条件写成item点Id等于输入编号，删除后重新统计并保存，再告诉用户是否找到了目标。编号描述记录身份，列表位置则随着排序和删除变化，所以菜单里展示编号能让用户选择得更明确。添加新记录时统一分配编号，也方便后续查找、更新和导出数据。')
page(c,'运行完整项目并检查结果','''using System.Text.Json;
decimal[] amounts = { 12m, 8m };
string json = JsonSerializer.Serialize(amounts);
File.WriteAllText("summary.json", json);
decimal[] restored = JsonSerializer.Deserialize<decimal[]>(
    File.ReadAllText("summary.json")) ?? Array.Empty<decimal>();
Console.WriteLine(restored.Length);
Console.WriteLine($"{restored.Sum():F2}");''','2\n20.00',['JSON 保存数据结构，文件把内容保留到下次运行','读取后检查记录字段，异常时给出恢复提示','完整项目包含新增、查看、删除和保存退出','检查首次运行、非法输入、刷新读取和损坏文件'],
'[1,2,3,4]保存数据时，把列表序列化成JSON，再写入固定文件。这里用金额数组演示保存步骤，完整项目保存的是Expense对象列表。[5,6]下次运行先读取文件，按相同数据类型解析回来，再检查编号、名称和金额是否满足规则。文件缺失就从空列表开始，读取失败时显示原因，并保留原文件便于检查，然后再开始新的操作。',
'[7,8]本页取回两笔金额，总额是二十点零零。完整项目请依次测试添加两条、删除一条、退出后重新打开，再尝试空名称、负数和无效菜单编号。README提供运行命令和文件位置，源码也可以直接打开阅读。每次只改变一个输入，观察菜单反馈、列表和保存文件，三者对应起来，就能确认程序的整条数据路线。')
page(c,'综合练习与下一步','''var amounts = new List<decimal> { 12m, 8m, 5m };
var selected = amounts.Where(value => value >= 8m).ToList();
decimal total = selected.Sum();
Console.WriteLine($"{selected.Count} 笔，合计 {total:F2} 元");''','2 笔，合计 20.00 元',['先建立 decimal 列表，再筛选并固定结果','12 和 8 满足条件，2 笔合计 20.00 元','输入、方法、对象、查询和文件连接成完整项目','下一步练习分类统计、修改记录和预算提示'],
'[1,2]最后一道综合练习，金额改用decimal，筛选大于等于八的记录，再用ToList保存本次结果。[3,4]求合计并显示数量和金额。请在脑中依次走过数据建立、条件筛选、结果保存和统计输出，预测这行文字会显示什么。你已经学过每个单独步骤，现在把它们按顺序连接，就是一个小型的数据处理过程。',
'[2,3,4]答案是两笔，合计二十点零零元，因为留下的是十二和八。回顾整门课，我们用变量保存值，用条件和循环安排执行，用方法组织步骤，用类和接口表达数据与能力，再用查询、异常和文件完成实际功能。接下来先亲手跑通配套项目，再增加分类统计、修改记录或预算提示。每做一个功能，就从输入一路跟踪到保存和显示，把学到的语法真正用起来。',kind='exercise')
