let cents = [300, 1800, 500, 2300]
let large = cents.filter { amount in
    amount >= 1000
}
print(large)
