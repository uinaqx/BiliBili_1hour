using System.Text.Json;
var amounts = new List<int> { 12, 8 };
string json = JsonSerializer.Serialize(amounts);
File.WriteAllText("amounts.json", json);
string saved = File.ReadAllText("amounts.json");
var restored = JsonSerializer.Deserialize<List<int>>(saved) ?? new List<int>();
Console.WriteLine(json);
Console.WriteLine(restored.Sum());
