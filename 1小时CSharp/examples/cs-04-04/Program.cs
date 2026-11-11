var expenses = new List<int> { 12, 8 };
expenses.Add(5);
expenses.Remove(8);
Console.WriteLine(expenses.Count);
Console.WriteLine(expenses[0]);
Console.WriteLine(string.Join(",", expenses));
