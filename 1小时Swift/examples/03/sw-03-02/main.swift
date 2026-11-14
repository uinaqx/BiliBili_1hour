var items: [String] = []
items.append("午餐")
items.append("交通")
let removed = items.remove(at: 0)
print(removed)
print(items.joined(separator: "、"))
