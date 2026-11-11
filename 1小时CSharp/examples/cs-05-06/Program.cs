static int Sum(List<int> values)
{
    int total = 0;
    foreach (int value in values) total += value;
    return total;
}
var amounts = new List<int> { 12, 8, 5 };
int result = Sum(amounts);
Console.WriteLine(result);
