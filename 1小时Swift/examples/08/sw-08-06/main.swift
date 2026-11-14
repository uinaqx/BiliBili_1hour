var threshold = 500
let passes = { (amount: Int) in
    amount >= threshold
}
print(passes(600))
threshold = 800
print(passes(600))
