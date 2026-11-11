Console.WriteLine(Formatter.Label(12));
Console.WriteLine(Formatter.Label("午餐"));
static class Formatter
{
    public static string Label(int value) => $"金额：{value}";
    public static string Label(string value) => $"名称：{value}";
}
