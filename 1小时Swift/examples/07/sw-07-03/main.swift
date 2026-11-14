protocol Displayable {
    func label() -> String
}
extension Displayable {
    func label() -> String { "待填写" }
}
struct Draft: Displayable {}
let draft = Draft()
print(draft.label())
