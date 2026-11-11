try
{
    Spend(-1);
}
catch (ArgumentOutOfRangeException)
{ Console.WriteLine("金额应大于等于零"); }
static void Spend(int amount)
{
    if (amount < 0) throw new ArgumentOutOfRangeException(nameof(amount));
    Console.WriteLine(amount);
}
