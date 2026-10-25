// ============================================================================
// 第 41 题 · strings4 —— 一眼分清 String 和 &str
// ----------------------------------------------------------------------------
// 题目类型：compile（把代码改到能编译通过就算过关）
// 课件位置：第 3 章 · 3.1 字符串与切片（String / &str 的区别与相互转换）
// 难度：★★★☆☆
// 前置知识：strings1~3（String、&str、to_string、trim、replace）
// ============================================================================
//
// 【题目要求】
// 下面有 10 个值，有的是 String，有的是 &str。
// 请给每一行选择正确的函数：
//     string_slice(arg: &str)   —— 接收“借用文本”
//     string(arg: String)       —— 接收“拥有所有权的文本”
// 把占位符换成函数名，全部选对就能编译通过。
//
// 原题代码（未完成，仅供对照）：
//     fn string_slice(arg: &str) { println!("{}", arg); }
//     fn string(arg: String) { println!("{}", arg); }
//
//     fn main() {
//         ???("blue");
//         ???("red".to_string());
//         ???(String::from("hi"));
//         ???("rust is fun!".to_owned());
//         ???("nice weather".into());
//         ???(format!("Interpolation {}", "Station"));
//         ???(&String::from("abc")[0..1]);
//         ???("  hello there ".trim());
//         ???("Happy Monday!".to_string().replace("Mon", "Tues"));
//         ???("mY sHiFt KeY iS sTiCkY".to_lowercase());
//     }
//
// 【解题思路】
// 判断方法只有一条：**看这个表达式最终产生的是 String 还是 &str。**
//   - 只要出现了“把文本复制/新建成堆数据”的方法（to_string、to_owned、format!、
//     replace、to_lowercase、String::from），结果就是 String → 用 string。
//   - 只要是“指向已有文本的一段视图”（字面量、trim、对字符串切片再取 &），
//     结果就是 &str → 用 string_slice。
// 逐个判断：
//   1. "blue"                                → 字面量，&str
//   2. "red".to_string()                     → String
//   3. String::from("hi")                    → String
//   4. "rust is fun!".to_owned()             → String
//   5. "nice weather".into()                 → 由参数类型推断成 String
//   6. format!(...)                          → String
//   7. &String::from("abc")[0..1]            → &str（对 String 切片再取引用）
//   8. "  hello there ".trim()               → &str
//   9. "Happy Monday!".to_string().replace(..) → String
//  10. "mY sHiFt...".to_lowercase()          → String
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● 一句话区分
//   String：拥有文本，存在堆上，可以改、可以增长，离开作用域自动释放。
//   &str  ：借用文本，只是“指针 + 长度”，不能改、不能增长，不负责释放。
//
// ● 哪些操作会“造出” String？
//   - String::from("...")        从字面量创建
//   - "....".to_string()         复制成 String
//   - "....".to_owned()          同上（ToOwned 特征）
//   - format!("...")             拼接出新 String
//   - s.replace(a, b)            替换后返回新 String
//   - s.to_lowercase()           转小写后返回新 String
//   - String::new() / String::with_capacity(n)
//   共同点：结果需要一块新的、可增长的内存，所以必须拥有所有权。
//
// ● 哪些操作得到的是 &str？
//   - 字符串字面量 "abc"（类型 &'static str）
//   - s.trim() / s.trim_start() / s.trim_end()
//   - &s[..] / &s[0..1]          对字符串切片并取引用
//   - s.as_str()
//   共同点：只是“指向原文本的某一段”，没有复制内容。
//
// ● `.into()` 为什么能变成 String？
//   `into()` 是 Into 特征的方法，它把“自己”转换成“目标类型”。
//   目标类型由上下文决定：这里函数参数要求 String，编译器就推断
//   `"nice weather".into()` 的结果是 String（底层调用 String::from）。
//   提示：因为 &str 到 &str 也有一个“恒等转换”，所以如果参数是 &str，
//   这一行其实也能编译；但本题的语义是“创建一个拥有所有权的字符串”，
//   标准答案选择 string，与 to_string / to_owned 保持一致。
//
// ● 为什么 `&String::from("abc")[0..1]` 是 &str？
//   先算 `String::from("abc")`：得到一个 String；
//   再做 `[0..1]` 切片：Rust 对 String 的索引会得到 `str`（一段文本，不定长）；
//   最后前面的 `&` 取引用：得到 `&str`。
//   注意这里取的是第 0 个字节到第 1 个字节（不含 1），结果就是 "a"。
//
// ● 为什么传参时“类型必须完全对上”？
//   `string(arg: String)` 会把实参**移动**进函数；
//   `string_slice(arg: &str)` 只借用，不会移动。
//   Rust 不会在函数调用处自动把 String 变成 &str（反过来 &str→String 更不会），
//   所以必须由你判断清楚。唯一的例外是 strings2 讲的“&String 自动变 &str”，
//   但这里给的很多是 String 本身，不适用。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

fn string_slice(arg: &str) {
    println!("{}", arg);
}
fn string(arg: String) {
    println!("{}", arg);
}

fn main() {
    // 1. 字面量：类型 &'static str，借用
    string_slice("blue");

    // 2. to_string()：复制成拥有所有权的 String
    string("red".to_string());

    // 3. String::from：从字面量创建 String
    string(String::from("hi"));

    // 4. to_owned()：&str → String（与 to_string 等价）
    string("rust is fun!".to_owned());

    // 5. into()：目标类型由参数 String 推断，得到 String
    string("nice weather".into());

    // 6. format!：拼接并返回新的 String
    string(format!("Interpolation {}", "Station"));

    // 7. 先对临时 String 切片得到 str，再取 & 得到 &str（内容是 "a"）
    string_slice(&String::from("abc")[0..1]);

    // 8. trim()：去掉首尾空白，返回原文本的一段视图 &str
    string_slice("  hello there ".trim());

    // 9. to_string() 得到 String，replace 又返回新的 String
    string("Happy Monday!".to_string().replace("Mon", "Tues"));

    // 10. to_lowercase()：转小写并返回新的 String
    string("mY sHiFt KeY iS sTiCkY".to_lowercase());
}

// ============================================================================
//                            详 细 解 析
// ============================================================================
//
// 1）第 7 行拆开看
//        let temp: String = String::from("abc");  // 临时的 String
//        let piece: &str = &temp[0..1];           // 借用其中 "a"
//        string_slice(piece);
//    原题把三步写在一行里。临时 String 会活到这条语句结束，
//    所以借出来的 &str 在调用期间一直有效，不会变成悬垂引用。
//
// 2）第 6 行 format! 里的 "Station" 是什么？
//    format! 只是把 "Interpolation " 和 "Station" 拼起来，生成
//    "Interpolation Station"，并返回 String。参数本身不会被移动或修改。
//
// 3）第 9 行为什么链式调用最后是 String？
//    "Happy Monday!".to_string()  → String
//    .replace("Mon", "Tues")      → String 的 replace 方法返回新的 String
//    所以整个表达式是 String，用 string 接收，输出 "Happy Tuesday!"。
//
// 4）第 10 行 to_lowercase 为什么不是 &str？
//    因为大小写转换可能改变字节长度（某些 Unicode 字符），
//    不能原地改，必须新建一个 String 返回。
//
// 5）如果第 5 行写 string_slice("nice weather".into()) 会怎样？
//    也能编译：此时 into() 的目标类型是 &str，走的是“恒等转换”。
//    但这样一来就没有创建新字符串，“into”的意义体现不出来；
//    题目答案按语义选择 string，让每个“拥有型”表达式都交给 string。
//
// 6）这两个函数打印结果完全一样，为什么还要区分？
//    因为真实函数往往要保存数据、修改数据或返回数据。
//    接收 String 的函数可以把值存起来长期使用；接收 &str 的函数只能“看一眼”，
//    不能把借用存到函数外（除非有生命周期标注，见 lifetimes 系列）。
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. 把 String 传给 string_slice：
//        string_slice("red".to_string());
//    → error[E0308]: mismatched types，expected `&str`, found `String`
//      help: consider borrowing here: `&"red".to_string()`
//
// 2. 把 &str 传给 string：
//        string("blue");
//    → expected `String`, found `&str`
//
// 3. 第 7 行漏掉 &：
//        string_slice(String::from("abc")[0..1]);
//    → error[E0277]: the size for values of type `str` cannot be known...
//      （str 是不定长类型，必须用 & 借用）
//
// 4. 以为 trim 返回 String：
//        string("  hi  ".trim());
//    → expected `String`, found `&str`
//
// 5. 给 to_lowercase 后面又加 to_string：
//        string("ABC".to_lowercase().to_string());
//    能编译，但纯属多余（to_lowercase 已经是 String）。
//
// 6. 试图用 `as` 强转：`"blue" as String`
//    → error[E0605]: non-primitive cast，as 只能用于数值等基本转换。
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. 字面量、trim、切片借用 → &str；
//   2. to_string、to_owned、String::from、format!、replace、to_lowercase → String；
//   3. `&String[范围]` 得到 &str；
//   4. `into()` 的结果由上下文（目标类型）决定；
//   5. 传参时类型必须对得上：String 要移动，&str 只借用。
//
// 一句话记忆：**“新建/复制”得到 String，“指向一段”得到 &str。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 strings4.rs -o strings4.exe
//   .\strings4.exe
// 【预期输出】
//   blue
//   red
//   hi
//   rust is fun!
//   nice weather
//   Interpolation Station
//   a
//   hello there
//   Happy Tuesday!
//   my shift key is sticky
// ============================================================================
