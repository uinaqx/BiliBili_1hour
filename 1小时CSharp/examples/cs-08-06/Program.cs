int[] amounts = { 12, 8, 5 };
var selected = amounts.Where(value => value >= 8).ToList();
Console.WriteLine(selected.Count);
Console.WriteLine(selected.Sum());
