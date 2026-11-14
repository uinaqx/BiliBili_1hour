enum PriceError: Error { case invalid }
func amount(_ value: Int) throws -> Int {
    guard value >= 0 else { throw PriceError.invalid }
    return value
}
let ok = try? amount(500)
let bad = try? amount(-20)
print(ok ?? 0)
print(bad ?? 0)
