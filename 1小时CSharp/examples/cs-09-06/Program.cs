File.WriteAllText("values.txt", "12,8,5");
string text = File.ReadAllText("values.txt");
int total = 0;
foreach (string part in text.Split(','))
{
    if (int.TryParse(part, out int amount)) total += amount;
}
Console.WriteLine(total);
