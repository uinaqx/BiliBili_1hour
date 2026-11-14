struct Ticket { var cents: Int }
class Counter { var cents = 0 }
let first = Counter()
let same = first
same.cents = 800
print(first.cents)
let original = Ticket(cents: 300)
var copy = original
copy.cents = 500
print(original.cents)
