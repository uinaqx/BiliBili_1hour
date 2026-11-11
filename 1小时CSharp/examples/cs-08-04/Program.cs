var amounts = new List<int> { 12, 5 };
var query = amounts.Where(value => value >= 8);
amounts.Add(20);
Console.WriteLine(string.Join(",", query));
var snapshot = query.ToList();
amounts.Add(30);
Console.WriteLine(string.Join(",", snapshot));
Console.WriteLine(string.Join(",", query));
