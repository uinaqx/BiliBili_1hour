var items = new List<Expense>
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
}
