let cents = [300, 1800, 500]
let labels = cents.map { amount in
    "\(amount) 分"
}
for label in labels { print(label) }
