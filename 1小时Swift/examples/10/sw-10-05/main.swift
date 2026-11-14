import Foundation
let url = URL(fileURLWithPath: "swift-demo.txt")
let data = Data("2600".utf8)
try data.write(to: url, options: .atomic)
let saved = try Data(contentsOf: url)
print(String(decoding: saved, as: UTF8.self))
