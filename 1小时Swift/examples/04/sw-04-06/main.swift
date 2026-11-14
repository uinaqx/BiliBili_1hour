func sum(_ values: [Int]) -> Int {
    var total = 0
    for value in values { total += value }
    return total
}
let amounts = [12, 8, 5]
let result = sum(amounts)
print(result)
