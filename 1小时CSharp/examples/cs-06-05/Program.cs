var first = new Point { X = 1 };
var second = first;
second.X = 9;
Console.WriteLine(first.X);
Console.WriteLine(PayStatus.Paid);
struct Point { public int X { get; set; } }
enum PayStatus { Pending, Paid }
