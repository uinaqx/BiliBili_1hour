using System.Text.Json;
decimal[] amounts = { 12m, 8m };
string json = JsonSerializer.Serialize(amounts);
File.WriteAllText("summary.json", json);
decimal[] restored = JsonSerializer.Deserialize<decimal[]>(
    File.ReadAllText("summary.json")) ?? Array.Empty<decimal>();
Console.WriteLine(restored.Length);
Console.WriteLine($"{restored.Sum():F2}");
