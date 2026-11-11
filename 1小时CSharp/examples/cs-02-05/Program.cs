Console.WriteLine("请输入金额：");
string text = Console.ReadLine() ?? "";
if (int.TryParse(text, out int amount))
{
    Console.WriteLine(amount + 8);
}
else Console.WriteLine("请输入整数");
