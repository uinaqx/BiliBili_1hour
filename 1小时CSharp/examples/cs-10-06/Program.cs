var amounts = new List<decimal> { 12m, 8m, 5m };
var selected = amounts.Where(value => value >= 8m).ToList();
decimal total = selected.Sum();
Console.WriteLine($"{selected.Count} 笔，合计 {total:F2} 元");
