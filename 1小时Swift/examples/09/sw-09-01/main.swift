enum InputError: Error {
    case invalid
}
func parse(_ text: String) throws -> Int {
    guard let n = Int(text) else {
        throw InputError.invalid
    }
    return n
}
print(try parse("120"))
