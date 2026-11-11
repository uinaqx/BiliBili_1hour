static T Echo<T>(T value)
{
    return value;
}
int amount = Echo(12);
string name = Echo("午餐");
Console.WriteLine(amount + 8);
Console.WriteLine(name.ToUpper());
