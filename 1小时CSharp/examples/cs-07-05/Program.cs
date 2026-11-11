string? note = null;
Console.WriteLine(note?.Length ?? 0);
object data = 12;
if (data is int amount)
    Console.WriteLine(amount + 8);
