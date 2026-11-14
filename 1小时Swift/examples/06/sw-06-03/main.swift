struct Expense {
    let name: String
    let cents: Int
    var summary: String {
        "\(name) \(cents) 分"
    }
}
let ticket = Expense(name: "地铁", cents: 300)
print(ticket.summary)
