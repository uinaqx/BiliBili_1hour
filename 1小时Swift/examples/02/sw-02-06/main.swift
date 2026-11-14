var total = 0
for i in 1...4 {
    if i == 2 { continue }
    total += i
}
print(total)
