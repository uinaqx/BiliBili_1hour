func add(_ value: Int, to total: inout Int) {
    total += value
}
var spent = 12
add(8, to: &spent)
print(spent)
