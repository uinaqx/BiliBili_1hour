int spent = 25;
int budget = 30;
bool withinBudget = spent <= budget;
bool positive = spent > 0;
Console.WriteLine(withinBudget && positive);
Console.WriteLine(spent == budget);
Console.WriteLine(!withinBudget);
