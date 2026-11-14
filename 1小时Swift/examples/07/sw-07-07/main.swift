func smaller<T: Comparable>(_ a: T, _ b: T) -> T {
    if a < b { return a }
    return b
}
print(smaller(12, 8))
print(smaller("B", "A"))
