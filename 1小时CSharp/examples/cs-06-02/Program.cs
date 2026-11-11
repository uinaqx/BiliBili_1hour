var item = new Expense();
item.Name = "午餐";
item.Amount = 12;
Console.WriteLine(item.Amount);
class Expense
{
    public string Name { get; set; } = "";
    public int Amount { get; set; }
}
