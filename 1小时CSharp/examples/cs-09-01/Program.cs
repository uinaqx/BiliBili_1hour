try
{
    int amount = int.Parse("abc");
    Console.WriteLine(amount);
}
catch (FormatException)
{
    Console.WriteLine("请输入整数");
}
