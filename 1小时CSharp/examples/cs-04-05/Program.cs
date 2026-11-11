var costs = new Dictionary<string, int>();
costs["午餐"] = 12;
costs["交通"] = 8;
if (costs.TryGetValue("午餐", out int amount))
    Console.WriteLine(amount);
Console.WriteLine(costs.ContainsKey("住宿"));
