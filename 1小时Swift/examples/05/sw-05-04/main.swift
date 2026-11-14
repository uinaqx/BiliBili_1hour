let nickname: String? = "小林"
let missing: String? = nil
let size = nickname?.count
print(size ?? 0)
print(missing?.count ?? 0)
