static void Show(string name, int amount = 12)
{
    Console.WriteLine($"{name}：{amount}");
}
Show("午餐");
Show(amount: 8, name: "交通");
