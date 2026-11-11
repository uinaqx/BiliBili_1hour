int total = 0;
for (int i = 1; i <= 4; i++)
{
    if (i == 2) continue;
    total += i;
}
Console.WriteLine(total);
