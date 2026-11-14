import Foundation
struct Expense: Codable {
    let name: String
    let cents: Int
}
let rows = [Expense(name: "午餐", cents: 1800)]
let data = try JSONEncoder().encode(rows)
let copy = try JSONDecoder().decode([Expense].self, from: data)
print(copy.count, copy[0].cents)
