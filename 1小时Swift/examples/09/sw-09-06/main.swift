func load(_ value: Int) async -> Int {
    try? await Task.sleep(nanoseconds: 50_000_000)
    return value
}
async let lunch = load(1800)
async let ticket = load(300)
let total = await lunch + ticket
print(total)
