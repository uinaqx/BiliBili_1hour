let cents = [300, 1800, 500]
let total = cents.reduce(0) { sum, amount in
    sum + amount
}
print(total)
