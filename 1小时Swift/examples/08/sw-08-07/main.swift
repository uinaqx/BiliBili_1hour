let cents = [300, 1800, 500, 2300]
let large = cents.filter { $0 >= 1000 }
let labels = large.map { "\($0) 分" }
let text = labels.joined(separator: "、")
print(text)
