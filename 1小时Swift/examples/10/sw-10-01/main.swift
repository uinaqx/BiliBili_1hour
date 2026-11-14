struct Expense {
    let name: String
    let cents: Int
}
var expenses: [Expense] = []
expenses.append(Expense(name: "午餐", cents: 1800))
expenses.append(Expense(name: "地铁", cents: 300))
for item in expenses {
    print("\(item.name) \(item.cents) 分")
}
