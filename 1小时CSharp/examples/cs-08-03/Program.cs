int[] amounts = { 12, 8, 5 };
var sorted = amounts.OrderBy(value => value);
Console.WriteLine(string.Join(",", sorted));
Console.WriteLine(amounts.Sum());
Console.WriteLine(amounts.Max());
