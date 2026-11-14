var cents = [300, 1200]
cents.append(500)
let removed = cents.remove(at: 0)
let total = cents.reduce(0, +)
print(removed)
print(total)
