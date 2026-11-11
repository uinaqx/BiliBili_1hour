var amounts = new List<int> { 10, 20 };
amounts.Add(5);
amounts[0] = 12;
amounts.Remove(20);
int total = 0;
foreach (int amount in amounts) total += amount;
Console.WriteLine($"{amounts.Count} {total}");
