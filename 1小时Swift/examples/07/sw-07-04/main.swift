protocol Label {
    func text() -> String
}
struct Expense: Label {
    func text() -> String { "开销" }
}
struct Reminder: Label {
    func text() -> String { "提醒" }
}
let rows: [any Label] = [Expense(), Reminder()]
for row in rows { print(row.text()) }
