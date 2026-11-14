let line = readLine() ?? ""
if let cents = Int(line), cents > 0 {
    print("已录入 \(cents) 分")
} else {
    print("请输入正整数")
}
