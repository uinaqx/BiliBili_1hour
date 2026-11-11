var ids = new List<int> { 1, 2, 3 };
int target = 2;
int removed = ids.RemoveAll(id => id == target);
Console.WriteLine(removed);
Console.WriteLine(string.Join(",", ids));
