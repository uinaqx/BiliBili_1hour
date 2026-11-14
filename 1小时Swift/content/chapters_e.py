from author import chapter, page

c = chapter("错误处理与异步")
page(c,"把失败原因写成错误类型",'''enum InputError: Error {
    case invalid
}
func parse(_ text: String) throws -> Int {
    guard let n = Int(text) else {
        throw InputError.invalid
    }
    return n
}
print(try parse("120"))''',"120",["自定义错误类型遵守 Error","throws 说明函数调用可能抛出错误","throw 结束当前调用并交出错误"],
"""[1,2]处理输入时，有时我们希望把失败的原因一起交出去。这里定义一个枚举 InputError，并让它遵守 Swift 的 Error 协议。invalid 表示内容格式无效。如果以后还要区分金额过大，就可以再添一种情况。[4]函数签名里的 throws 表示这个函数有可能抛出错误。正常走完时，它返回一个整数。读这一行，你就能提前看出调用时需要处理哪种结果。""",
"""[5,6]先用 guard 解析文本。解析失败就执行 throw，把 invalid 交给调用方，并结束这次函数执行。[8,10]当前传进来一百二十，解析成功，return 交出整数一百二十，外层打印它。调用可能抛出错误的代码，写上 try。下一页我们用 do 和 catch 把异常路径接住，让程序在输入出错以后还能继续给提示。""")
page(c,"用 do 和 catch 接住错误",'''enum InputError: Error { case invalid }
func parse(_ text: String) throws -> Int {
    guard let n = Int(text) else { throw InputError.invalid }
    return n
}
do {
    let cents = try parse("abc")
    print(cents)
} catch {
    print("格式错误")
}''',"格式错误",["try 标出可能抛出错误的调用","出错时跳过 do 块后续代码","catch 分支打印提示"],
"""[1,2,3]这一次故意把字母送进解析函数。函数的规则和上一页一样，格式正确时返回整数，格式无效时抛出 InputError 的 invalid。[6,7]把可能出错的调用放进 do 的花括号里。执行到 try parse 时，字母解析失败，错误沿着这个调用回到外面。cents 的赋值还没有完成，接下来的成功输出也被跳过。""",
"""[9,10]流程来到 catch，输出格式错误。catch 可以通过更具体的匹配分别处理不同类型的错误。这里用一个通用分支，把所有收到的错误都转成这条提示。[7,8]把输入换成十二再试，函数会正常返回，do 里面继续打印十二。写带错误的程序时，最好跑一组成功输入和一组会抛错的输入，确认两条路都能得到清楚的反馈。""")
page(c,"用 try? 把失败转成空值",'''enum PriceError: Error { case invalid }
func amount(_ value: Int) throws -> Int {
    guard value >= 0 else { throw PriceError.invalid }
    return value
}
let ok = try? amount(500)
let bad = try? amount(-20)
print(ok ?? 0)
print(bad ?? 0)''',"500\n0",["try? 成功时得到装着结果的可选值","调用抛错时，try? 得到 nil","用 ?? 决定如何显示空值"],
"""[1,2,3]这个金额检查函数接收整数，只有非负数才通过。负数会抛出 PriceError。现在假设界面只要知道有结果还是没有结果，就可以用 try 后面加问号，把它接到可选值这条熟悉的路径上。[6]先传五百。函数正常返回，ok 得到装着五百的可选整数。这个写法把成功返回保留在可选值内部。""",
"""[7]再传负二十。函数抛出错误，try 问号把结果转成 nil。[8,9]后面两行分别用两个问号取值。第一项有五百，直接打印五百。第二项为空，备用值零被打印。需要根据具体错误给不同提示时，用 do 和 catch 分开处理。页面只要把有结果和没结果分开时，try 问号就很简洁。""")
page(c,"让收尾代码随作用域结束执行",'''func report() {
    defer { print("结束") }
    print("开始")
    print("生成报告")
}
report()''',"开始\n生成报告\n结束",["defer 注册一段离开作用域时执行的代码","普通语句继续按顺序执行","适合把配套的收尾放在相关操作旁边"],
"""[1]有一类代码总要放在最后做，比如给报告打印结束提示。Swift 提供 defer，可以把收尾动作写在相关代码旁边，再让程序离开当前作用域时执行它。[2]读到 defer 的这一行，程序先登记这段收尾，接着继续向下走。等会儿离开 report 函数的花括号，已经登记的代码就有机会执行。""",
"""[6,3,4]外面调用 report，进入函数以后，先打印开始，再打印生成报告。这两条普通语句按顺序执行。[5,2]走到函数末尾，执行登记好的收尾，于是最后打印结束。实际代码也常用 defer 做配套清理。读到一个 defer 时，可以先记下它负责什么，然后读完主要流程，最后再把收尾那一步接上。""")
page(c,"用 async 和 await 表示等待",'''func fetchTotal() async -> Int {
    try? await Task.sleep(nanoseconds: 100_000_000)
    return 2600
}
let total = await fetchTotal()
print(total)''',"2600",["async 表示这个函数可以挂起","await 标出可能暂停当前任务的位置","等待结束后继续取回总额"],
"""[1]读文件、访问网络或等待界面事件时，结果可能过一会儿才到。Swift 用 async 标记可以挂起的函数。我们先写一个很小的模拟函数，等一小段时间以后交回总额。[2]Task 点 sleep 在这里模拟等待。参数是纳秒，当前值等于十分之一秒。await 标出当前任务可能暂停的位置，之后它能在结果准备好时继续。""",
"""[3]等待过后返回两千六百。这一页固定返回一个值，方便观察调用顺序。[5,6]调用 async 函数时，也写 await。拿到返回值以后，才继续给 total 赋值，并在下一行打印两千六百。这是顺序等待的写法。程序从上到下依然很好读，同时把可能等待的位置明确标在代码里。""")
page(c,"用 async let 启动两项独立工作",'''func load(_ value: Int) async -> Int {
    try? await Task.sleep(nanoseconds: 50_000_000)
    return value
}
async let lunch = load(1800)
async let ticket = load(300)
let total = await lunch + ticket
print(total)''',"2100",["async let 启动子任务","lunch 和 ticket 可以重叠运行","计算总额时等待所需结果"],
"""[1,2,3]如果两项工作各自能完成，就可以先把它们都启动，再统一等结果。这页仍用短暂等待模拟加载金额，load 接收一个整数，等一下就把它返回。[5,6]两条 async let 分别启动午餐和车票这两项工作。午餐这项返回一千八百，车票这项返回三百。启动第二项时，第一项可以继续进行。""",
"""[7]算总额需要两个金额，这一行用 await 等所需的结果，然后执行加法。写两条 async let 的顺序说明从哪里启动它们，实际先完成哪项由运行时和任务耗时决定。[8]最后输出两千一百。选择写法时先看数据依赖。如果第二项需要第一项的返回值，就先等待第一项。如果两项互相独立，就可以像这样分别启动。""")
page(c,"练习：捕获错误后程序走到哪里",'''enum CheckError: Error { case negative }
func check(_ n: Int) throws {
    if n < 0 { throw CheckError.negative }
}
do {
    try check(-2)
    print("通过")
} catch {
    print("请重输")
}
print("继续")''',"请重输\n继续",["负数使 check 抛出 negative","do 里的成功提示被跳过","catch 结束后执行后面的 print"],
"""[1,2,3]这个函数检查参数是否为负数，遇到负数就抛出 negative。函数没有提供一个用来继续计算的返回值，调用方只关心这次检查走到了哪里。[5,6,7]题目传的是负二。请按行号追一下，先判断通过会不会打印，再判断最后一行的继续会不会打印。[8,9,11]这里有一个 catch，还有一个放在整个结构后面的 print。暂停几秒，把输出按顺序记下来。""",
"""[3,6]负二小于零，check 抛出错误。当前的 try 调用中断，do 里面的下一行被跳过。[8,9]错误被 catch 接住，第一行输出请重输。[11]catch 执行结束后，程序回到这个结构后面，第二行输出继续。这个模式可以用于带菜单的程序。一次录入有问题就提示一下，之后回到菜单，用户还有机会输入新的数据。""",kind="exercise")

c = chapter("综合项目与课程回顾")
page(c,"把一笔开销装进数组",'''struct Expense {
    let name: String
    let cents: Int
}
var expenses: [Expense] = []
expenses.append(Expense(name: "午餐", cents: 1800))
expenses.append(Expense(name: "地铁", cents: 300))
for item in expenses {
    print("\(item.name) \(item.cents) 分")
}''',"午餐 1800 分\n地铁 300 分",["Expense 保存名称和整数分","用可变数组按录入顺序保存","循环逐笔生成列表文字"],
"""[1,2,3]现在来做课程最后的开销记录项目。程序负责四件事，录入、展示、删除和保存。先确定一笔开销长什么样。Expense 里面有一个名称和一个整数金额，金额单位是分。这里一千八百代表十八元。每次录入都创建一条结构相同的记录，后面展示和计算会用到这两个属性。[5]数组初始为空，明确写出每个元素是 Expense。""",
"""[6,7]用 append 先放进午餐，再放进地铁。数组里的顺序和录入的顺序一致。[8,9]用 for 每次取出一个 Expense，再读它的名称和金额。打印时把两项插进字符串。看到的两行输出是午餐一千八百分、地铁三百分。完整项目会在这一段之外添加菜单和输入校验。你也可以先手动加一条记录，看看列表如何随数组内容变化。""")
page(c,"用函数检查金额并计算总额",'''func parseCents(_ text: String) -> Int? {
    guard let n = Int(text), (1...1_000_000).contains(n) else {
        return nil
    }
    return n
}
let cents = ["1800", "abc", "300"].compactMap(parseCents)
print(cents.reduce(0, +))''',"2100",["函数只接收 1 到 1000000 分","compactMap 收集成功解析的值","完整交互版会对无效输入单独提示"],
"""[1,2,3]添加一笔开销时，项目把金额检查交给单独的函数。先解析整数，再检查它在一到一百万分之间。contains 接收一个数字，判断这个范围里有没有它。检查不通过时返回 nil，通过则把金额交回调用处。这里的上限让练习程序有一个明确的数据范围。[7]示例用三个字符串演示批量解析。""",
"""[7]compactMap 和 map 一样逐项调用函数，并把成功取出的值收集起来。第一个文本变成一千八百，第二个解析失败，第三个变成三百，所以数组保留两个有效整数。在完整项目里，用户一次录入一笔，遇到无效金额会直接得到提示。[8]reduce 从零开始对两项相加，最后打印两千一百。""")
page(c,"先检查编号，再删除一笔",'''var names = ["午餐", "地铁", "早餐"]
let number = 2
if (1...names.count).contains(number) {
    let removed = names.remove(at: number - 1)
    print("已删除 \(removed)")
}
print(names.joined(separator: "、"))''',"已删除 地铁\n午餐、早餐",["菜单显示从 1 开始的编号","访问数组时将编号减 1","完整项目用 indices 检查空数组和越界"],
"""[1,2]界面上给三条记录显示一、二、三。现在用户想删掉编号二的地铁。用户看到的编号从一开始，数组下标从零开始，所以中间要做一次转换。[3]本页的数组已知有三项，先检查编号是否在一到三之间。完整项目会用数组的 indices 处理可能为空的列表，并在转换下标前检查编号为正。""",
"""[4,5]二通过检查，减一得到下标一。remove 会取出并删除这一项，所以打印已删除地铁。删除后，后面的元素会向前移动。[7]最后用顿号连接剩下的名称，显示午餐、早餐。做带编号的列表时，可以让用户每次删除前先看一遍当前列表，因为删除之后的位置会改变。""")
page(c,"把记录变成 JSON 再读回来",'''import Foundation
struct Expense: Codable {
    let name: String
    let cents: Int
}
let rows = [Expense(name: "午餐", cents: 1800)]
let data = try JSONEncoder().encode(rows)
let copy = try JSONDecoder().decode([Expense].self, from: data)
print(copy.count, copy[0].cents)''',"1 1800",["Codable 让本例的字段可编码与解码","JSONEncoder 把记录编码为 Data","JSONDecoder 按目标类型恢复数组"],
"""[1,2,3,4]让记录关掉程序后还能找回来，先选一种能写进文件的表示。这里用常见的 JSON。Foundation 提供了编码和解码的工具。给 Expense 声明 Codable，这里的名称和整数金额都能自动跟随结构体转换。[6,7]先准备一条午餐记录，再用 JSONEncoder 把整个数组变成 Data。Data 是待保存的一组字节。""",
"""[8]再从这组字节读回数据。decode 的第一个参数告诉它，目标是一个 Expense 数组。这里展示在内存中来回转换，方便只验证数据结构。[9]读回后打印数组个数和第一条金额，得到一和一千八百。完整项目把编码和解码包在错误处理里。写文件时使用编码好的 Data，下一次启动时读取文件字节，再恢复成数组。""")
page(c,"将数据写进文件",'''import Foundation
let url = URL(fileURLWithPath: "swift-demo.txt")
let data = Data("2600".utf8)
try data.write(to: url, options: .atomic)
let saved = try Data(contentsOf: url)
print(String(decoding: saved, as: UTF8.self))''',"2600",["相对路径指向当前运行目录下的文件","Data.write 保存字节，Data(contentsOf:) 读回","项目存的是 JSON，此处用 2600 演示读写"],
"""[1,2]这一页把文件读写单独跑一遍。文件名叫 swift 连字符 demo 点 txt。运行时以当前目录为起点找这个文件，因此在终端的哪个目录运行，文件就出现在对应的位置。[3,4]先把文字两千六百转成 UTF 八字节，再写入指定路径。atomic 选项让写入通过替换文件来完成。完整项目对 JSON 数据也用同一种写入方式。""",
"""[5,6]现在重新读取文件字节，并按 UTF 八还原成文字，屏幕输出两千六百。文件和程序中的值是两件可以分别验证的东西。运行完成以后，你还可以在目录里打开生成的文件，核对里面的内容。实际项目在启动时读 JSON，只有成功保存以后才更新当前列表。读取或写入出问题时，会显示错误反馈。""")
page(c,"练习：求当前列表总额",'''var cents = [300, 1200]
cents.append(500)
let removed = cents.remove(at: 0)
let total = cents.reduce(0, +)
print(removed)
print(total)''',"300\n1700",["append 把 500 加到末尾","remove(at: 0) 删除并返回 300","最后两项为 1200 和 500"],
"""[1,2]做一道收尾练习。初始有三百和一千二百，再添加五百。接着删除位置零上的第一项。把数组写在纸上，每执行一行，就在下一行写出现在还剩哪些数据。[3,4]removed 保存删掉的金额，total 用当前数组重新求和。这是两个不同的结果。[5,6]题目会先打印删除金额，再打印当前总额。给自己几秒钟，先预测这两行输出。""",
"""[2,3]添加以后，数组按顺序是三百、一千二百、五百。位置零是三百，remove 返回三百并把它从数组移走。[4]现在剩一千二百和五百，从零开始累计，得到一千七百。[5,6]所以第一行输出三百，第二行输出一千七百。完整程序也按这样的顺序做，先更新当前列表，再按更新后的列表计算总额。保存后重新打开，仍然可以验证这两项金额。""",kind="exercise")
page(c,"运行完整项目并复盘",'''// 在完整项目目录的终端运行：swift main.swift
// 1 添加  2 查看  3 删除  0 退出
let actions = ["录入开销", "查看列表", "删除记录", "保存文件"]
for (index, action) in actions.enumerated() {
    print("\(index + 1). \(action)")
}''',"1. 录入开销\n2. 查看列表\n3. 删除记录\n4. 保存文件",["完整项目位于 examples/完整项目/main.swift","保存成功后再替换内存里的记录","练习目标：添加两笔、删除一笔、重开验证"],
"""[1,2]打开工程里的完整项目目录，在终端运行 swift main 点 swift，就可以看到交互菜单。先选一录入午餐一千八百分，再选一录入车票三百分。选二查看，核对列表和总额两千一百。然后选三，根据屏幕当前编号删除第一笔。退出，再运行一次。文件会在程序启动时被读取，列表里应该只剩车票。[3]这页的短例子单独列出了项目的四项工作。""",
"""[4,5]最后回顾一下从哪里开始写代码。先用变量和类型表示数据，用判断和循环安排顺序，用函数提取重复步骤。金额可能解析失败时，用可选值表达结果。数据多起来后，用结构体和集合组织，再用错误处理和文件读写完成保存。课后可以给每笔记录加一个分类字段，先把分类打印出来，再做按分类合计。每加完一个小功能，就用几条真实输入运行一遍。""")
