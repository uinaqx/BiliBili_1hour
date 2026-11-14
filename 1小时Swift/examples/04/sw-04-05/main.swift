func fee(for amount: Int) -> Int {
    if amount <= 0 { return 0 }
    if amount >= 30 { return 0 }
    return 5
}
print(fee(for: 12))
print(fee(for: 40))
