Func<int, int> doubleValue = value => value * 2;
Action<string> show = text => Console.WriteLine(text);
Console.WriteLine(doubleValue(6));
show("处理完成");
