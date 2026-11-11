var amounts = new List<int> { 12, 8, 5 };
var selected = amounts.Where(value => value >= 8);
var raised = selected.Select(value => value + 1);
Console.WriteLine(string.Join(",", raised));
