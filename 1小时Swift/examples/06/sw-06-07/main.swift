struct Expense {
    let cents: Int
    init(cents: Int) {
        self.cents = max(0, cents)
    }
}
let record = Expense(cents: -50)
print(record.cents)
