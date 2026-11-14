enum InputError: Error { case invalid }
func parse(_ text: String) throws -> Int {
    guard let n = Int(text) else { throw InputError.invalid }
    return n
}
do {
    let cents = try parse("abc")
    print(cents)
} catch {
    print("格式错误")
}
