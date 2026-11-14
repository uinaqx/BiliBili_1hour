func parseCents(_ text: String) -> Int? {
    guard let cents = Int(text), cents >= 0 else {
        return nil
    }
    return cents
}
print(parseCents("0") ?? -1)
print(parseCents("abc") ?? -1)
