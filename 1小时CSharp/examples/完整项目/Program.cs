using System.Globalization;
using System.Text;
using ExpenseCourse;

Console.OutputEncoding = Encoding.UTF8;
Console.InputEncoding = Encoding.UTF8;
CultureInfo.CurrentCulture = CultureInfo.InvariantCulture;
string path = args.Length > 0 ? args[0] : "expenses.json";
var book = new ExpenseBook(path);
Console.WriteLine("C# 开销记录");
if (book.LoadMessage.Length > 0) Console.WriteLine(book.LoadMessage);
bool running = true;
while (running)
{
    Console.WriteLine("1 添加  2 查看  3 删除  0 保存退出");
    string? choice = Console.ReadLine();
    if (choice is null) choice = "0";
    switch (choice.Trim())
    {
        case "1":
            Console.WriteLine("名称：");
            string name = (Console.ReadLine() ?? "").Trim();
            if (name.Length == 0) { Console.WriteLine("请输入名称"); break; }
            Console.WriteLine("金额（例如 12.50）：");
            string amountText = Console.ReadLine() ?? "";
            if (!decimal.TryParse(amountText, NumberStyles.AllowLeadingSign | NumberStyles.AllowDecimalPoint
                | NumberStyles.AllowLeadingWhite | NumberStyles.AllowTrailingWhite,
                CultureInfo.InvariantCulture, out decimal amount) || amount < 0)
            { Console.WriteLine("金额请输入大于等于零的十进制数"); break; }
            try
            {
                var added = book.Add(name, amount);
                Console.WriteLine($"已添加 #{added.Id}");
                await Save();
            }
            catch (OverflowException) { Console.WriteLine("记录编号已达到上限，请先清理记录"); }
            break;
        case "2":
            foreach (var item in book.Items)
                Console.WriteLine($"#{item.Id} {item.Name} {item.Amount:F2}");
            Console.WriteLine($"共 {book.Items.Count} 笔，总额 {book.Total:F2} 元");
            break;
        case "3":
            Console.WriteLine("输入要删除的编号：");
            if (int.TryParse(Console.ReadLine(), out int id) && book.Remove(id))
            { Console.WriteLine("已删除"); await Save(); }
            else Console.WriteLine("未找到该编号");
            break;
        case "0":
            await Save();
            running = false;
            break;
        default:
            Console.WriteLine("请选择 0、1、2、3");
            break;
    }
}
async Task Save()
{
    try { await book.SaveAsync(); Console.WriteLine("已保存"); }
    catch (Exception error) when (error is IOException or UnauthorizedAccessException)
    { Console.WriteLine("保存失败：" + error.Message); }
}
