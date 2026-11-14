func fetchTotal() async -> Int {
    try? await Task.sleep(nanoseconds: 100_000_000)
    return 2600
}
let total = await fetchTotal()
print(total)
