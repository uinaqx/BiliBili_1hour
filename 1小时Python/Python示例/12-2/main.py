def within(spent, budget):
    return spent <= budget

expenses = [12, 8, 5]
budget = 30
total = sum(expenses)
print(f"total={total}")
if within(total, budget):
    print(f"remaining={budget - total}")
else:
    print("over")
