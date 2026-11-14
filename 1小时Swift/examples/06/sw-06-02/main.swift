struct Wallet {
    var cents = 0
    mutating func add(_ amount: Int) {
        cents += amount
    }
}
var wallet = Wallet()
wallet.add(500)
print(wallet.cents)
