protocol Describable {
    func label() -> String
}
struct Expense: Describable {
    let name: String
    func label() -> String { "开销：\(name)" }
}
let expense = Expense(name: "早餐")
print(expense.label())
