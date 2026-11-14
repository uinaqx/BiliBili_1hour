struct Box<T> {
    let value: T
}
let amount = Box(value: 900)
let name = Box(value: "电影票")
print(amount.value)
print(name.value)
