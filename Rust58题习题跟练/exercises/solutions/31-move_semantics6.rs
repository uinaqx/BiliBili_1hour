// ============================================================================
// 第 31 题 · move_semantics6 —— 该借的借，该拿的拿（&String 与 String）
// ----------------------------------------------------------------------------
// 题目类型：compile（把代码改到能编译通过就算过关）
// 课件位置：第 2 章 · 2.3.2 用 & 借用避免所有权转移（&String / &str）
// 难度：★★★☆☆
// 前置知识：move_semantics1~4（移动、mut、返回值转移所有权）、String 基础
// 题目约束：**只能加或删 &: 引用符号**，不能改别的结构
// ============================================================================
//
// 【题目要求】
// 只允许"增加或删除引用（&）"，让代码编译通过。
// 两个函数旁边的注释已经给了提示：
//     get_char        —— Should not take ownership（不该拿走所有权）
//     string_uppercase—— Should take ownership（应该拿走所有权）
//
// 原题代码（未完成，仅供对照）：
//     fn main() {
//         let data = "Rust is great!".to_string();
//         get_char(data);            // ← 这里把 data 送走了
//         string_uppercase(&data);   // ← 这里又借 data
//     }
//
//     // Should not take ownership
//     fn get_char(data: String) -> char {
//         data.chars().last().unwrap()
//     }
//
//     // Should take ownership
//     fn string_uppercase(mut data: &String) {
//         data = &data.to_uppercase();   // ← 借用了临时值
//         println!("{}", data);
//     }
//
// 编译会报两类错：
//     error[E0382]: borrow of moved value: `data`
//     （data 的所有权已经被 get_char 拿走了，后面不能再借）
//     error[E0716]: temporary value dropped while borrowed
//     （data.to_uppercase() 产生的临时 String 在语句结束时就被释放了，
//      而 data 还指着它，成了悬垂引用）
//
// 【解题思路】
// 1. get_char 只是"看一眼最后一个字符"，完全不需要拥有整个字符串，
//    所以应该借用：参数改成 `data: &String`，调用处写成 `get_char(&data)`。
//    这样 data 仍然归 main 所有，后面还能继续用。
// 2. string_uppercase 要把字符串变成大写，相当于"我接管它、改造它"，
//    所以应该拿走所有权：参数改成 `mut data: String`，
//    调用处写成 `string_uppercase(data)`（不加 &）。
//    函数体内部的 `data = &data.to_uppercase();` 也要去掉 &，
//    变成 `data = data.to_uppercase();`，直接用一个新 String 覆盖旧的。
// 3. 两处一改，借用与移动的账就平了：
//    先借（读）→ 借完归还 → 再把所有权交出去（消费）。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● String 和 &str 是什么关系？
//   String   ：拥有堆上的字符串数据，可以增长、修改，所有权明确。
//   &str     ：字符串切片，只是"借来看的一段文字"，不拥有数据。
//   本题 main 里用 "Rust is great!".to_string() 把字面量（&str）
//   变成一个拥有所有权的 String，这样它才能被传来传去。
//
// ● & 是什么？
//   &x 是"对 x 的不可变借用"：我能读 x，但不能改，也不负责释放它。
//   用借书打比方：& 就是"办一张借阅卡"，书还是图书馆的，你只是拿来看看。
//   借阅期间书不能被扔掉（不能释放），这就是借用检查器要保证的事。
//
// ● 为什么"只读函数"不该拿所有权？
//   如果 get_char(data: String) 拿走了 String，调用者就失去了它。
//   只是一个"读最后一个字符"的小操作却把数据吞掉，非常不划算。
//   Rust 的惯例：
//       只需要读     → &T        （&String、&str）
//       需要修改     → &mut T
//       需要保存/消费→ T         （拿走所有权）
//
// ● 那参数该写 &String 还是 &str？
//   本题约束"只加删 &"，所以保留 &String。
//   实际开发更推荐 `&str`：因为 String 可以自动"降级"成 &str（解引用强制转换），
//   这样 "abc" 字面量和 String 都能传进来，更通用。
//   例：fn get_char(data: &str) -> char 也能被 get_char(&data) 调用。
//
// ● `mut data: &String` 为什么是错的？
//   它表示"这个引用本身可以改指向别处"，而不是"被指向的字符串可以改"。
//   想改字符串内容，应该写 `&mut String`（可变借用），
//   想要接管整个字符串，就直接写 `String`。
//   本题的 string_uppercase 会把整个字符串换成大写的新字符串，
//   所以最合适的是"拿走所有权"：`mut data: String`。
//
// ● 什么是"临时值"（temporary）？
//   `data.to_uppercase()` 返回一个**新的 String**，但它没有名字，
//   是个"临时值"。临时值默认在**语句结束时**就被释放。
//   原题写 `data = &data.to_uppercase();`，
//   等于让 data 指向一个马上就要被销毁的 String —— 这就是悬垂引用。
//   Rust 在编译期就把它拦住了（E0716），不会等到运行时出错。
//
// ● unwrap() 是什么？
//   `data.chars().last()` 返回 Option<char>：字符串可能为空，空的时候是 None。
//   `.unwrap()` 的意思是"如果是 Some(c) 就把 c 拿出来；如果是 None 就 panic"。
//   本题字符串非空，所以一定拿到 Some('!')。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

fn main() {
    // "Rust is great!" 是 &str 字面量；to_string() 复制成拥有所有权的 String
    // 从这里开始，data 是这份堆内存的唯一所有者
    let data = "Rust is great!".to_string();

    // get_char 只需要"看一眼"，所以传 &data（借用，不交出所有权）
    // 借用在本行结束时就归还了，data 依然可用
    get_char(&data);

    // string_uppercase 要接管并改造整个字符串，所以把所有权交出去
    // 注意：这里不加 &（加了就变成借用，函数签名对不上）
    // 因为 data 此后不再使用，移动出去完全没问题
    string_uppercase(data);
}

// 参数改成 &String：只借用，不拿走所有权
// 函数结束时只是"还书"，不会释放这份字符串数据
fn get_char(data: &String) -> char {
    // chars()：把字符串按"字符"逐个取出（注意不是字节）
    // last() ：取最后一个，返回 Option<char>
    // unwrap()：取出 Some 里的值；本题非空，一定能取到 '!'
    data.chars().last().unwrap()
}

// 参数改成 mut data: String：接管所有权，并且允许修改这个绑定
// （因为下面要整体替换成一个新的大写字符串）
fn string_uppercase(mut data: String) {
    // to_uppercase() 返回一个全新的 String（大写版本）
    // 直接把它赋给 data：旧字符串在这里被释放，data 现在拥有新字符串
    // 注意不能写 &data.to_uppercase()，那会指向一个马上被销毁的临时值
    data = data.to_uppercase();

    // 打印：RUST IS GREAT!
    println!("{}", data);
}

// 函数结束时，data 是它唯一的所有者，于是新字符串在这里被自动释放。
// 整个过程没有 GC，也没有内存泄漏。
//
// ============================================================================
//                            逐 行 解 析
// ============================================================================
//
// let data = "Rust is great!".to_string();
//   ├─ "Rust is great!"  ：&str 字面量，存放在程序的只读区
//   ├─ .to_string()      ：复制到堆上，返回 String
//   └─ data              ：String 的所有者
//
// get_char(&data);
//   ├─ &data  ：不可变借用，类型 &String
//   └─ 借用范围只到本行结束（NLL：非词法生命周期）
//
// string_uppercase(data);
//   └─ 移动：data 的所有权进入函数参数，main 里 data 作废
//      （后面没有再用 data，所以合法）
//
// fn get_char(data: &String) -> char
//   └─ 参数是引用；函数不能改、也不能释放被借用的字符串
//
// fn string_uppercase(mut data: String)
//   └─ 参数是拥有所有权的 String；mut 允许赋值替换
//
// data = data.to_uppercase();
//   ├─ 右边：造一个新的全大写 String
//   └─ 左边：把新 String 赋给 data，旧 String 被 drop
//
// ============================================================================
//                    "先借后移"为什么是合法且常见的模式？
// ============================================================================
//
// 借用检查器的时间线：
//   1. get_char(&data) 借出 → 本行结束立刻归还（NLL）
//   2. string_uppercase(data) 移动 → 此时没有未结束的借用，安全
// 如果顺序反过来呢？
//   string_uppercase(data);   // data 被移动
//   get_char(&data);          // ❌ E0382：borrow of moved value
// 所以顺序也很重要：**先借用、后移交**。
//
// 这也是 Rust 比 C 安全的地方：
// C 里函数拿到指针后你依然可能去 free 它，运行时才炸；
// Rust 里"移动"和"借用"不能重叠，编译器直接拒绝。
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. 只给 main 加 &，不改函数签名：
//        get_char(&data);  fn get_char(data: String)
//    → error[E0308]: mismatched types（expected `String`, found `&String`）
//
// 2. 改反了：get_char 拿走所有权，string_uppercase 借用
//    → 要么 E0382（先移动后借用），要么 E0308（类型不符）。
//
// 3. string_uppercase 里保留 `data = &data.to_uppercase();`
//    → error[E0716]: temporary value dropped while borrowed
//    临时 String 在语句结束时被释放，引用立刻悬垂。去掉 & 即可。
//
// 4. 写成 `fn string_uppercase(data: String)` 却又要赋值：
//    → error[E0384]: cannot assign twice to immutable variable `data`
//    （参数默认不可变，需要 mut）
//
// 5. 试图用 `string_uppercase(&mut data)`：
//    → 需要 main 里 data 是 mut，且函数签名是 &mut String；
//      但题目要求的是"接管所有权"，方向不对。
//
// 6. 想靠 clone 蒙混过关：
//        get_char(data.clone());
//    能编译，但违背题意（题目要求"只加删引用"），也白白复制了一次内存。
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. 只读用 &T，修改用 &mut T，接管用 T —— 这是 Rust 的参数三件套；
//   2. 借用在"最后一次使用"后结束，所以"先借后移"是合法的；
//   3. 函数返回新值时，别把引用指向临时值（E0716）；
//   4. 所有权移动后原变量失效（E0382），这是编译期就能发现的错误；
//   5. 加不加 & 不是风格问题，而是"所有权归谁"的语义问题。
//
// 一句话记忆：**看一眼就借（&），要改造就接管（T）；别把引用指向临时值。**
//
// 至此 move_semantics 1~6 串成一条线：
//   1 移动 + mut → 2 clone 保留原件 → 3 参数 mut → 4 返回值转移所有权
//   → 5 可变借用不能重叠 → 6 用 & 避免不必要的移动。
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 move_semantics6.rs -o move_semantics6.exe
//   .\move_semantics6.exe
// 【预期输出】
//   RUST IS GREAT!
// ============================================================================
