var first = new Expense { Amount = 12 };
var second = first;
second.Amount = 20;
Console.WriteLine(first.Amount);
Console.WriteLine(ReferenceEquals(first, second));
class Expense
{
    public int Amount { get; set; }
}
