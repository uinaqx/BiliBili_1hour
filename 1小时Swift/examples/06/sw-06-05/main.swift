enum Check {
    case accepted(Int)
    case rejected(String)
}
let result = Check.accepted(600)
switch result {
case .accepted(let cents):
    print("已录入 \(cents)")
case .rejected(let reason):
    print(reason)
}
