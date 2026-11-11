var item = new Expense { Id = 1, Name = "午餐", Amount = 12m };
Console.WriteLine($"{item.Id} {item.Name} {item.Amount:F2}");
class Expense
{
    public int Id { get; set; }
    public string Name { get; set; } = "";
    public decimal Amount { get; set; }
}
