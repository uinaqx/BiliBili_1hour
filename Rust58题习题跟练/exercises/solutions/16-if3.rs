// ============================================================================
// 第 16 题 · if3 —— 让 if 各分支的类型统一（整数 / 浮点 / 字符串的三选一）
// ----------------------------------------------------------------------------
// 题目类型：test（让 #[test] 测试通过就算过关）
// 课件位置：第 4 章 · 4.1 if 表达式的类型一致性
// 难度：★★★☆☆
// 前置知识：if 是表达式（第 14、15 题）、整数 i32 与浮点数 f64（2.2.1）
// ============================================================================
//
// 【题目要求】
// 只改 animal_habitat 里第一个 if 链（给 identifier 赋值那一段），
// 让 4 个测试全部通过；函数里第二段（注释写着 DO NOT CHANGE THIS STATEMENT
// BELOW 的部分）一个字都不能改。
//
// 原题代码（未完成，仅供对照）：
//     pub fn animal_habitat(animal: &str) -> &'static str {
//         let identifier = if animal == "crab" {
//             1
//         } else if animal == "gopher" {
//             2.0
//         } else if animal == "snake" {
//             3
//         } else {
//             "Unknown"
//         };
//
//         // DO NOT CHANGE THIS STATEMENT BELOW
//         let habitat = if identifier == 1 {
//             "Beach"
//         } else if identifier == 2 {
//             "Burrow"
//         } else if identifier == 3 {
//             "Desert"
//         } else {
//             "Unknown"
//         };
//
//         habitat
//     }
//
// 编译会报错：
//     error[E0308]: `if` and `else` have incompatible types
//     expected integer, found floating-point number
//     （后面还会继续报 &str 与整数不兼容）
//
// 【解题思路】
// 1. 先看第二段（不许改）在做什么：
//    它拿 identifier 去和 **整数** 1、2、3 比较，1 对应 "Beach"（crab），
//    2 对应 "Burrow"（gopher），3 对应 "Desert"（snake），
//    其它值 → "Unknown"。
// 2. 所以 identifier 必须是一个“能分别表示 1、2、3 和‘其它’”的类型，
//    最直观的选择就是整数 i32。
// 3. 原题第一个 if 链里三个分支分别是 1、2.0、"Unknown"，类型全不一样：
//      - 1      → 整数，默认 i32
//      - 2.0    → 浮点数，默认 f64
//      - "Unknown" → &str
//    if 表达式要求所有分支类型一致，所以编译失败。
// 4. 把 2.0 改成 2（整数），把 "Unknown" 改成 0 或 -1（整数）：
//      1 → crab，2 → gopher，3 → snake，0 → 其它动物。
// 5. 这样 identifier 就是 i32；第二段中 identifier == 1/2/3 也都能编译，
//    未知动物（比如 dinosaur）得到 0，落到最后的 else → "Unknown"，测试通过。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● 整数字面量 1 与浮点字面量 2.0 是两种完全不同的类型
//     1    → 默认推断为 i32（32 位有符号整数）
//     2.0  → 默认推断为 f64（64 位浮点数）
//   Rust 不会像 C 那样在 if 分支里“自动把 2.0 变成 2”，
//   它宁可报错，也不做隐式转换 —— 这是 Rust 避免精度事故的设计。
//
// ● 为什么 if 各分支类型必须一致？
//   因为整个 if 表达式要“算出一个值”，编译器必须先确定这个值的类型。
//   如果分支给出不同类型的值，那这个表达式到底算 i32 还是 f64？无法决定，
//   所以编译器直接拒绝：error[E0308]。
//
// ● 类型标注可以帮我们“钉死”类型
//     let identifier: i32 = if ... ;
//   本题其实不加标注也能推断出来（因为第二段用 1/2/3 比较），
//   但加上标注会让意图更清楚。
//
// ● 函数的返回类型 &'static str 是什么意思？
//   'static 是一个“生命周期”，表示这份数据在整个程序运行期间都有效。
//   字符串字面量 "Beach" 存于只读数据区，天然是 &'static str，
//   所以可以直接作为返回值返回，不会因离开作用域而失效。
//   注意：本题第一段只算出整数，真正的返回发生在最后 `habitat` 那一行。
//
// ● 别忘了分号的作用
//     let identifier = if ... { } ;   ← 这里的 if 只是“右值”，赋给 identifier
//     habitat                          ← 函数最后一行，不带分号，作为返回值
//
// ● 数字和字符串不能比较
//     1 == "1"   → error[E0308]：整数与 &str 不能比较
//   所以 identifier 一旦定为整数，第二段里的 identifier == 1 才成立；
//   如果 identifier 是 &str，第二段的比较就会全报错 —— 这也是题目
//   “不许改第二段”的约束在暗示我们：identifier 必须是整数。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

// 返回 &'static str：返回的字符串字面量在整个程序期间都有效
pub fn animal_habitat(animal: &str) -> &'static str {
    // 全部分支都返回 i32 整数，所以 identifier 的类型是 i32
    // 这里显式标注 : i32，让“我想要整数”这个意图一目了然
    let identifier: i32 = if animal == "crab" {
        1 // crab  → 1
    } else if animal == "gopher" {
        2 // gopher → 2（原题写的是 2.0，浮点数，类型不一致）
    } else if animal == "snake" {
        3 // snake → 3
    } else {
        0 // 其它动物 → 0（原题写的是 "Unknown"，字符串，类型不一致）
    };

    // ===== 下面这条语句题目要求一个字都不能改 =====
    // 它拿 identifier 和整数 1、2、3 比较：
    //   1 → Beach（crab）
    //   2 → Burrow（gopher）
    //   3 → Desert（snake）
    //   其它（包括我们用的 0）→ Unknown
    let habitat = if identifier == 1 {
        "Beach"
    } else if identifier == 2 {
        "Burrow"
    } else if identifier == 3 {
        "Desert"
    } else {
        "Unknown"
    };

    // 最后一行不带分号：它的值（&'static str）就是函数的返回值
    habitat
}

// ---------------------------------------------------------------------------
// 下面这段是原题自带的测试代码，完全没有改动。
// ---------------------------------------------------------------------------
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn gopher_lives_in_burrow() {
        assert_eq!(animal_habitat("gopher"), "Burrow")
    }

    #[test]
    fn snake_lives_in_desert() {
        assert_eq!(animal_habitat("snake"), "Desert")
    }

    #[test]
    fn crab_lives_on_beach() {
        assert_eq!(animal_habitat("crab"), "Beach")
    }

    #[test]
    fn unknown_animal() {
        // "dinosaur" 不在前三支里，identifier = 0，最终走 else → "Unknown"
        assert_eq!(animal_habitat("dinosaur"), "Unknown")
    }
}

// ============================================================================
//                            逐 行 解 析
// ============================================================================
//
// let identifier: i32 = if animal == "crab" { 1 } ...
//   ├─ identifier : i32 ：显式声明类型为 32 位有符号整数
//   ├─ animal == "crab" ：字符串按内容比较
//   └─ 1 / 2 / 3 / 0    ：四个整数分支，类型统一为 i32 → if 表达式类型是 i32
//
// let habitat = if identifier == 1 { "Beach" } ...
//   ├─ identifier == 1  ：整数与整数比较（因为 identifier 现在是 i32）
//   └─ 四个分支都是 &'static str → if 表达式类型是 &'static str
//
// habitat   ← 最后一行不带分号，直接成为返回值
//
// 为什么“0”能表示未知？因为题目第二段没给 0 任何分支，
// 它自动落进最后的 else → "Unknown"。只要能编译、能区分即可。
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. 只把 2.0 改成 2，却保留 "Unknown"：
//    → error[E0308]: `if` and `else` have incompatible types
//      expected integer, found `&str`
//
// 2. 把整数都改成字符串：
//        "1" / "2" / "Unknown"
//    → 第一段能过，但第二段 identifier == 1 报错
//      （&str 与整数不能比较），而第二段不许改 → 此路不通。
//
// 3. 全部改成浮点：
//        1.0 / 2.0 / 3.0 / 0.0，然后第二段 identifier == 1 仍报错
//      （f64 不能和整数字面量直接比较），同样违反“第二段不许改”。
//
// 4. 用字符串比较但忘了写 &：
//        if animal == crab
//    → error[E0425]: cannot find value `crab` in this scope
//
// 5. 在函数最后加了分号：
//        habitat;
//    → error[E0308]: mismatched types，expected `&'static str`, found `()`
//
// 6. 用普通方式编译（本题只有测试，没有 main）：
//        rustc if3.rs
//    → error[E0601]: `main` function not found in crate
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. if 表达式所有分支必须同类型，否则 E0308；
//   2. 整数 1 和浮点 2.0 是不同类型，Rust 不做隐式转换；
//   3. 同一个值可以用不同“编码”表示不同含义（1/2/3/0 代表四种动物）；
//   4. 读题时要先看“不许改的那段代码”需要什么类型，再倒推答案。
//
// 一句话记忆：**if 分支必须交同一种类型的值；先看没被改的那段，反推类型。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 --test if3.rs -o if3.exe
//   .\if3.exe
// 【预期输出】
//   running 4 tests
//   test tests::crab_lives_on_beach ... ok
//   test tests::gopher_lives_in_burrow ... ok
//   test tests::snake_lives_in_desert ... ok
//   test tests::unknown_animal ... ok
//   test result: ok. 4 passed; 0 failed; ...
// ============================================================================
