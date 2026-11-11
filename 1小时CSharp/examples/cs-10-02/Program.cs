var items = new List<Expense>();
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
}
