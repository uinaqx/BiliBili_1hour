extension Int {
    func asCents() -> String {
        "\(self) 分"
    }
}
let amount = 250
print(amount.asCents())
