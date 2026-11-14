enum CheckError: Error { case negative }
func check(_ n: Int) throws {
    if n < 0 { throw CheckError.negative }
}
do {
    try check(-2)
    print("通过")
} catch {
    print("请重输")
}
print("继续")
