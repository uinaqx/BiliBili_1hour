var tags: Set<String> = ["餐饮", "交通", "餐饮"]
tags.insert("学习")
print(tags.count)
print(tags.contains("交通"))
let common = tags.intersection(["交通", "其他"])
print(common.sorted().joined(separator: "、"))
