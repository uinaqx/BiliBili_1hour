func echo<T>(_ value: T) -> T {
    return value
}
let amount = echo(600)
let name = echo("车票")
print(amount)
print(name)
