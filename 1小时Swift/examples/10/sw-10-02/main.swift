func parseCents(_ text: String) -> Int? {
    guard let n = Int(text), (1...1_000_000).contains(n) else {
        return nil
    }
    return n
}
let cents = ["1800", "abc", "300"].compactMap(parseCents)
print(cents.reduce(0, +))
