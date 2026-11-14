import Foundation

struct Expense: Codable {
    let name: String
    let cents: Int
}

func parseCents(_ text: String) -> Int? {
    guard let amount = Int(text), (1...1_000_000).contains(amount) else {
        return nil
    }
    return amount
}

func loadExpenses(from file: URL) throws -> [Expense] {
    guard FileManager.default.fileExists(atPath: file.path) else { return [] }
    let data = try Data(contentsOf: file)
    return try JSONDecoder().decode([Expense].self, from: data)
}

func saveExpenses(_ expenses: [Expense], to file: URL) throws {
    let encoder = JSONEncoder()
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    let data = try encoder.encode(expenses)
    try data.write(to: file, options: .atomic)
}

func showExpenses(_ expenses: [Expense]) {
    if expenses.isEmpty {
        print("暂无开销")
        return
    }
    for (index, expense) in expenses.enumerated() {
        print("\(index + 1). \(expense.name) \(expense.cents) 分")
    }
    let total = expenses.reduce(0) { sum, expense in sum + expense.cents }
    print("总额：\(total) 分")
}

func run() throws {
    let file = URL(fileURLWithPath: "expenses.json")
    var expenses = try loadExpenses(from: file)
    while true {
        print("1 添加  2 查看  3 删除  0 退出")
        guard let command = readLine() else { return }
        switch command {
        case "1":
            print("名称：")
            guard let text = readLine() else { return }
            let name = text.trimmingCharacters(in: .whitespacesAndNewlines)
            guard !name.isEmpty else {
                print("请输入名称")
                continue
            }

            print("金额（整数分）：")
            guard let text = readLine() else { return }
            guard let cents = parseCents(text) else {
                print("请输入 1 到 1000000 分的整数")
                continue
            }
            var updated = expenses
            updated.append(Expense(name: name, cents: cents))
            do {
                try saveExpenses(updated, to: file)
                expenses = updated
                print("已添加 \(name)")
            } catch {
                print("保存失败：\(error.localizedDescription)")
            }

        case "2":
            showExpenses(expenses)

        case "3":
            showExpenses(expenses)
            guard !expenses.isEmpty else { continue }
            print("输入要删除的编号：")
            guard let text = readLine() else { return }
            guard let number = Int(text), number > 0,
                  expenses.indices.contains(number - 1) else {
                print("编号无效")
                continue
            }
            var updated = expenses
            let removed = updated.remove(at: number - 1)
            do {
                try saveExpenses(updated, to: file)
                expenses = updated
                print("已删除 \(removed.name)")
            } catch {
                print("保存失败：\(error.localizedDescription)")
            }

        case "0":
            return

        default:
            print("请选择菜单编号")
        }
    }
}

do {
    try run()
} catch {
    print("读取 expenses.json 失败：\(error.localizedDescription)")
}
