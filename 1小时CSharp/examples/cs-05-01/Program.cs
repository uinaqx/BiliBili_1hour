static int Remaining(int budget, int spent)
{
    return budget - spent;
}
int left = Remaining(30, 25);
Console.WriteLine(left);
