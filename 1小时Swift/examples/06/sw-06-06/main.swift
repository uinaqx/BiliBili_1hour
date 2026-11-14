struct Item { var cents: Int }
let first = Item(cents: 500)
var second = first
second.cents += 200
print(first.cents, second.cents)
