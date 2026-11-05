total = 0
with open("expenses.txt", "r", encoding="utf-8") as file:
    for line in file:
        amount = int(line.strip())
        total += amount
print(total)
