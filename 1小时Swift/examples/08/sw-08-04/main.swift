let cents = [1800, 300, 500]
let ordered = cents.sorted { a, b in
    a < b
}
print(ordered)
print(cents)
