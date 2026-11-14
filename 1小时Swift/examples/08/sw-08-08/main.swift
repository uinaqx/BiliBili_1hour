let cents = [100, 900, 500, 700]
let chosen = cents.filter { $0 >= 500 }
let total = chosen.reduce(0, +)
print(total)
