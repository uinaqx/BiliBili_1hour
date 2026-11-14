func quantity(_ text: String) -> Int {
    guard let n = Int(text), n > 0 else {
        return 0
    }
    return n
}
print(quantity("8"))
print(quantity("-3"))
