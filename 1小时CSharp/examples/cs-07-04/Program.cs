IPrintable item = new Expense("午餐");
item.Print();
interface IPrintable
{
    void Print();
}
class Expense : IPrintable
{
    private string name;
    public Expense(string value) { name = value; }
    public void Print() => Console.WriteLine(name);
}
