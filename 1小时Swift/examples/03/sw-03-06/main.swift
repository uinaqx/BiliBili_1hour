var amounts = [10, 20]
amounts.append(5)
amounts[0] = 12
let removed = amounts.remove(at: 1)
print(removed, amounts.count)
print(amounts)
