var item = new Expense();
item.Name = "午餐";
item.Amount = 12;
Console.WriteLine($"{item.Name}：{item.Amount}");
class Expense
{
    public string Name = "";
    public int Amount;
}
