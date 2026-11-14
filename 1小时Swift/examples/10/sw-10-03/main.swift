var names = ["午餐", "地铁", "早餐"]
let number = 2
if (1...names.count).contains(number) {
    let removed = names.remove(at: number - 1)
    print("已删除 \(removed)")
}
print(names.joined(separator: "、"))
