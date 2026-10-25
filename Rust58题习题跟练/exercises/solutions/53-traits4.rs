// ============================================================================
// 第 53 题 · traits4 —— impl Trait 作参数：只要“有这能力”就行
// ----------------------------------------------------------------------------
// 题目类型：test（让 #[test] 测试通过就算过关）
// 课件位置：第 5 章 · 5.3 特征（把 trait 用作函数参数：impl Trait）
// 难度：★★★☆☆
// 前置知识：第 50~52 题（trait、impl、默认实现）、函数参数类型（functions2）
// ============================================================================
//
// 【题目要求】
// 只允许修改 `fn compare_license_types(software: ??, software_two: ??) -> bool`
// 这一行，把两个 `??` 换成合适的类型，让代码编译并通过两个测试。
// 两个测试分别传入 `(SomeSoftware, OtherSoftware)` 和 `(OtherSoftware, SomeSoftware)`。
//
// 原题代码（未完成，仅供对照）：
//     fn compare_license_types(software: ??, software_two: ??) -> bool {
//         software.licensing_info() == software_two.licensing_info()
//     }
//
// 如果两个 ?? 都填 SomeSoftware，会报：
//     error[E0308]: mismatched types, expected `SomeSoftware`, found `OtherSoftware`
//
// 【解题思路】
// 1. 函数体对参数做的唯一事情是调用 `.licensing_info()`，
//    说明它**不关心参数具体是什么类型**，只要求“实现了 Licensed”。
// 2. Rust 提供了一种简洁写法：`impl Trait`，意思是
//    “这里接收任意一个实现了 Trait 的类型”。
//        fn compare_license_types(software: impl Licensed,
//                                 software_two: impl Licensed) -> bool
// 3. 两处都写 `impl Licensed`，表示**两个参数可以是不同类型**
//    （一个是 SomeSoftware，一个是 OtherSoftware），只要各自实现了 Licensed。
//    这一点很关键：如果写成“同一个类型 T”，两个测试就都编译不过。
// 4. 函数体一个字都不用改。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● 为什么需要“trait 作参数”？
//   假设要写一个“打印授权信息”的函数。
//   如果参数写死具体类型，就得为每种软件各写一个函数：
//       fn print_license(s: SomeSoftware) { ... }
//       fn print_license(s: OtherSoftware) { ... }   // 名字还冲突了
//   而我们真正想要的约束是“能拿到 licensing_info 就行”，
//   这正是 trait 的用途：**用能力描述参数，而不是用身份**。
//
// ● 两种等价写法
//   写法 A（impl Trait，简洁）：
//       fn compare_license_types(a: impl Licensed, b: impl Licensed) -> bool
//   写法 B（泛型参数 + 约束，传统）：
//       fn compare_license_types<T: Licensed, U: Licensed>(a: T, b: U) -> bool
//   两者完全等价，编译后的代码也一样。A 更短，B 更灵活
//   （比如你需要在函数体里写 `T`、`Vec<T>` 这样的类型时，只能用 B）。
//   注意 B 里用了**两个**类型参数 T 和 U；如果只用一个 T：
//       fn compare_license_types<T: Licensed>(a: T, b: T)
//   就要求 a、b 是同一个类型，两个测试都过不了。
//
// ● “约束（bound）”是什么意思？
//   `impl Licensed` 和 `<T: Licensed>` 里的 `Licensed` 都是一个限制条件：
//   只有实现了 Licensed 的类型才能传进来。
//   在函数体里，编译器只会让你调用 Licensed 里声明过的方法 ——
//   参数的具体类型被“故意忘掉”了，这叫“静态分发（static dispatch）”。
//   打个比方：招聘要求写“会开车（C1 驾照）”，
//   你不需要知道应聘者是谁，只要他有这个证，就能让他开车。
//
// ● 为什么这里不能用 `&dyn Licensed`？
//   也可以用（叫“trait 对象 / 动态分发”），但需要写 `&dyn Licensed` 并传引用，
//   会引入运行时的虚表查找。`impl Trait` 是零成本抽象，优先用它。
//   （trait 对象属于进阶内容，本题不要求。）
//
// ● `assert!(条件)` 是什么？
//   和 assert_eq! 类似，只是它只检查“条件是否为真”。
//   条件为 false 时 panic，测试失败；为 true 时什么都不做。
//   本题里两个类型的默认 licensing_info 都返回 "some information"，
//   所以 `==` 为 true，两个测试都通过。
//
// ● 注意本题 default 实现里的字符串
//   本题 trait 的默认实现返回 `"some information"`（全小写），
//   和上一题 traits3 的 `"Some information"`（大写 S）不同！
//   测试只比较两个返回值是否相等，不比较具体内容，所以不会踩坑；
//   但抄答案时不要顺手把字符串改掉。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

// trait：带默认实现的 Licensed（本题原样保留，不需要改）
pub trait Licensed {
    fn licensing_info(&self) -> String {
        "some information".to_string()
    }
}

// 两个空结构体（单元结构体），只用来挂 trait 实现
struct SomeSoftware {}

struct OtherSoftware {}

// 两个类型都实现 Licensed，都使用默认实现
impl Licensed for SomeSoftware {}
impl Licensed for OtherSoftware {}

// YOU MAY ONLY CHANGE THE NEXT LINE
// 把两个 ?? 换成 `impl Licensed`：
//   每个参数都独立地表示“某个实现了 Licensed 的类型”
//   （两个参数的类型可以不同，也可以是同一个）
fn compare_license_types(software: impl Licensed, software_two: impl Licensed) -> bool {
    // 分别调用两个参数的 licensing_info()，比较返回的 String 是否相等
    // String 的 == 比较的是**内容**（逐字符），不是地址
    software.licensing_info() == software_two.licensing_info()
    // 最后一行表达式即返回值，类型 bool
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn compare_license_information() {
        // 两个不同的类型
        let some_software = SomeSoftware {};
        let other_software = OtherSoftware {};

        // assert! 断言括号里的表达式为 true
        assert!(compare_license_types(some_software, other_software));
    }

    #[test]
    fn compare_license_information_backwards() {
        let some_software = SomeSoftware {};
        let other_software = OtherSoftware {};

        // 交换参数顺序，依然能编译、依然为 true
        // （如果两个参数被约束成同一个类型 T，这一行就编译不过）
        assert!(compare_license_types(other_software, some_software));
    }
}

// ============================================================================
//                            详 细 解 析
// ============================================================================
//
// 1）`impl Licensed` 出现在参数位置，含义到底是什么？
//    它是“匿名泛型参数”的语法糖：
//        fn f(x: impl Licensed)
//    编译器会把它展开成：
//        fn f<T: Licensed>(x: T)
//    只不过这个 T 你没有名字可用。
//    所以 `impl Licensed` 只能用在**参数**和**返回值**位置，
//    不能用在 let 绑定的类型标注里（`let x: impl Licensed` 不合法）。
//
// 2）为什么两处 `impl Licensed` 不是同一个类型？
//    每一个 `impl Trait` 参数都会被展开成一个**独立的**类型参数，
//    相当于 `fn f<T: Licensed, U: Licensed>(a: T, b: U)`。
//    这正是本题能同时接收 SomeSoftware 和 OtherSoftware 的原因。
//    如果你想让两个参数是同一类型，就得显式写 `fn f<T: Licensed>(a: T, b: T)`。
//
// 3）为什么测试能通过（返回 true）？
//    两个类型都用默认实现，返回的都是 "some information"，
//    `"some information" == "some information"` → true。
//
// 4）函数体为什么不需要改？
//    因为 `impl Licensed` 保证了两件事：
//      a. 参数类型实现了 Licensed；
//      b. 所以可以调用 `.licensing_info()`。
//    除此之外函数体不碰任何具体字段，所以完全不用动。
//
// 5）如果改成 `software: SomeSoftware` 会怎样？
//    第一个测试里 `compare_license_types(other_software, some_software)` 传反了，
//    会报 error[E0308]: mismatched types
//    （expected `SomeSoftware`, found `OtherSoftware`）。
//    这正是题目故意设计的：让你不能用具体类型。
//
// 6）`impl Trait` 还能用在返回值上：
//        fn make() -> impl Licensed { SomeSoftware {} }
//    意思是“我返回某个实现了 Licensed 的类型，但我不告诉你是哪个”。
//    这和参数位置的 `impl Trait` 是两套语义，本题不涉及。
//
// 7）为什么 `SomeSoftware {}` 后面有花括号？
//    这是“单元结构体（unit-like struct）”的实例化写法，
//    它没有任何字段，但依然需要 `{}` 才能造出一个值。
//    也可以定义成 `struct SomeSoftware;`（不带花括号），
//    那实例化就写 `SomeSoftware`。本题沿用原题写法。
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. 两处都填具体的一个类型：
//        fn compare_license_types(a: SomeSoftware, b: SomeSoftware)
//    → error[E0308]: mismatched types（另一个测试传了 OtherSoftware）
//
// 2. 用同一个泛型参数：
//        fn compare_license_types<T: Licensed>(a: T, b: T)
//    → 两个测试都报 E0308：expected `SomeSoftware`, found `OtherSoftware`
//
// 3. 只给一个参数加 impl：
//        fn compare_license_types(a: impl Licensed, b: SomeSoftware)
//    → 反向测试编译失败
//
// 4. 写成 `impl Licensed + ?Sized` 或其他多余约束：
//    虽然有时合法，但这里没必要，容易引入难懂的错误。
//
// 5. 忘记 `?` 只改一处：
//    → error: expected type, found `?`
//
// 6. 以为 `impl Trait` 是“动态类型”：
//    它是编译期确定的静态分发，每个具体类型都会生成一份专用函数。
//
// 7. 把 `assert!` 写成 `assert_eq!`：
//        assert_eq!(compare_license_types(a, b), true);
//    这样也能过，但不符合习惯，而且 true 的类型推断可能带来噪音。
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. `参数: impl Trait` 表示“接收任意实现了 Trait 的类型”，是泛型参数的简写；
//   2. 每个 `impl Trait` 参数都是**独立的**类型参数，彼此可以不同；
//   3. 用能力（trait）描述参数，比用具体类型更通用，也不用为每个类型写一遍函数；
//   4. 等价的传统写法是 `<T: Trait, U: Trait>`。
//
// 一句话记忆：**参数写 impl Trait = 英雄不问出处，只要有证（实现了 trait）就能上岗。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 --test traits4.rs -o traits4.exe
//   .\traits4.exe
// 【预期输出】
//   running 2 tests
//   test tests::compare_license_information ... ok
//   test tests::compare_license_information_backwards ... ok
//
//   test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
// ============================================================================
