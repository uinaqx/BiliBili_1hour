def within(spent, budget=30):
    return spent <= budget

print(within(25))
print(within(35))
print(within(35, 40))
