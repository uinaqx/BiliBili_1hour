// ============================================================================
// 第 50 题 · traits1 —— 第一个 trait：给 String 装一个 append_bar 能力
// ----------------------------------------------------------------------------
// 题目类型：test（让 #[test] 测试通过就算过关）
// 课件位置：第 5 章 · 5.3 特征（trait 的定义与实现）
// 难度：★★★☆☆
// 前置知识：结构体/方法（structs3）、String 与 push_str（strings3）、self 参数
// ============================================================================
//
// 【题目要求】
// trait AppendBar 只有一个方法：把 "Bar" 追加到对象后面，并返回修改后的自己。
// 请为 `String` 实现这个 trait（补全 `impl AppendBar for String { ... }`），
// 让两个测试都通过：
//     String::from("Foo").append_bar()          == "FooBar"
//     String::from("").append_bar().append_bar()== "BarBar"
//
// 原题代码（未完成，仅供对照）：
//     trait AppendBar {
//         fn append_bar(self) -> Self;
//     }
//
//     impl AppendBar for String {
//         // TODO: Implement `AppendBar` for type `String`.
//     }
//
// 编译器会报：
//     error[E0046]: not all trait items implemented, missing: `append_bar`
//
// 【解题思路】
// 1. trait 里写的是“说明书”：`fn append_bar(self) -> Self;`
//    意思是“这个能力叫 append_bar，它吃掉自己（self），再还回一个同类型的新值”。
//    注意只有签名、没有函数体 —— 具体怎么做，由实现者填写。
// 2. 为 String 实现时，签名必须和 trait 一致：
//        fn append_bar(self) -> Self
//    在参数前加 `mut` 是允许的（`mut self`），这只影响函数体内部能否修改，
//    不改变对外签名。
// 3. String 追加文本的方法是 `push_str("Bar")`，它把 &str 拼接到末尾。
//    因为 push_str 需要 &mut self，所以 self 必须是可变的 → 写 `mut self`。
// 4. 最后把 self 返回（不写分号），类型就是 Self = String。
// 5. 测试里连续调用两次 append_bar，第一次返回 String，第二次继续追加，
//    所以 "" → "Bar" → "BarBar"，正确。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● trait 是什么？—— “行为说明书 / 能力证书”
//   trait 定义“某类东西**能做什么**”，但不关心“它具体是什么”。
//       trait AppendBar {
//           fn append_bar(self) -> Self;   // 只声明，不实现
//       }
//   打个比方：trait 是一份“会游泳”的证书模板。
//   谁去考（impl）谁就获得这项能力。鸭子会游泳、人会游泳，
//   但它们是完全不同的类型 —— trait 只统一“能力”，不统一“身份”。
//   这和 Java 的 interface 很像，但 Rust 的 trait 还能有默认实现（第 52 题）、
//   能给别人的类型实现（有孤儿规则限制）。
//
// ● `impl Trait for Type` 怎么读？
//       impl AppendBar for String { ... }
//   读作：“为 String 这个类型，实现 AppendBar 这份说明书”。
//   写完之后，所有 String 值都能调用 `.append_bar()`。
//
// ● self、&self、&mut self 三兄弟（非常重要）
//       fn f(self)           拿走所有权，调用后原来的变量不能再用
//       fn f(&self)          只读借用，不复制、不移走
//       fn f(&mut self)      可读可写借用，能修改内容
//   本题 trait 规定的是 `self`（按值拿走），因为要把“追加后的新字符串”返回，
//   最自然的做法就是“把原来的字符串拿过来改一改再还给你”。
//   调用 `s.append_bar()` 之后，s 就被“消费”了（移动进函数），不能再使用。
//   所以 main 里写的是 `let s = s.append_bar();` —— 用同名新变量接住返回值，
//   这在 Rust 里叫“变量遮蔽（shadowing）”，不是修改原变量。
//
// ● String 和 push_str
//       let mut s = String::from("Foo");
//       s.push_str("Bar");     // s 变成 "FooBar"
//   `push_str(&mut self, string: &str)`：在末尾追加一段文本。
//   注意它返回 ()（什么都不返回），所以我们需要自己 `self` 返回出去。
//
// ● `-> Self` 里的 Self 是什么？
//   和上一题一样：Self = 当前 impl 的那个类型。
//   在 `impl AppendBar for String` 里，Self 就是 String。
//
// ● 为什么测试里能直接调用 `.append_bar()`？
//   因为 trait 和 impl 都在同一个文件（同一个 crate）里，
//   方法已经“在作用域内”。如果 trait 定义在别的模块，还需要 `use` 它才能调用。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

// 定义一份“说明书”：凡是实现 AppendBar 的类型，都必须提供 append_bar 方法
trait AppendBar {
    // 签名：吃掉 self（按值），返回同类型 Self
    // 只有声明，没有函数体，具体实现交给 impl 的人
    fn append_bar(self) -> Self;
}

// 为 String 实现 AppendBar
impl AppendBar for String {
    // `mut self`：self 是按值传入的（符合 trait 签名），
    // 加 mut 只是允许函数体内部修改它，对调用者没有影响
    fn append_bar(mut self) -> Self {
        // push_str(&mut self, &str)：把 "Bar" 追加到字符串末尾
        // 这里 self 是 mut 的，所以可以调用
        self.push_str("Bar");

        // 把修改后的 self 返回出去
        // 最后一行表达式不加分号 = 返回值，类型是 String（即 Self）
        self
    }
}

fn main() {
    // 创建一个 String
    let s = String::from("Foo");

    // 调用 trait 方法：s 被移动进 append_bar，返回一个新的 String
    // 用同名变量 s 接住返回值（变量遮蔽），旧的 s 已经失效
    let s = s.append_bar();

    // 打印结果：FooBar
    println!("s: {}", s);
}

#[cfg(test)]
mod tests {
    // 引入父模块的 trait 和 impl，测试里才能调用 .append_bar()
    use super::*;

    #[test]
    fn is_foo_bar() {
        // "Foo" 追加一次 "Bar" → "FooBar"
        assert_eq!(String::from("Foo").append_bar(), String::from("FooBar"));
    }

    #[test]
    fn is_bar_bar() {
        // 空字符串追加两次："" → "Bar" → "BarBar"
        // 第一次返回 String，可以立刻接着调用第二次（链式调用）
        assert_eq!(
            String::from("").append_bar().append_bar(),
            String::from("BarBar")
        );
    }
}

// ============================================================================
//                            详 细 解 析
// ============================================================================
//
// 1）trait 里的方法为什么没有函数体？
//    这是“纯声明”写法，强制每个实现者自己写。
//    也可以给默认实现（`fn f(&self) -> bool { true }`），
//    那样实现者不写也能用，见第 52 题 traits3。
//
// 2）`fn append_bar(self)` 和 `fn append_bar(&self)` 的区别有多大？
//    参数类型一旦不同，就**不是同一个方法**了。
//    trait 里写的是 `self`，impl 里也必须写 `self`，
//    写成 `&self` 会报：
//        error[E0053]: method `append_bar` has an incompatible type for trait
//    而且 `&self` 也无法返回 Self（借来的东西不能直接当自己的还回去），
//    所以这里必须按值拿走。
//
// 3）为什么 `mut self` 不算改签名？
//    `mut` 是对“局部变量”的修饰，属于函数体内部的事，
//    对外看来参数类型仍然是 `Self`。所以 trait 写 `self`、impl 写 `mut self` 完全合法。
//
// 4）main 里为什么写 `let s = s.append_bar();` 而不是 `s.append_bar();`？
//    因为 append_bar 返回一个新的 String，直接丢弃返回值虽然能编译，
//    但就打印不到结果了。用同名变量接住是 Rust 常见写法（遮蔽），
//    也可以写成 `let s2 = s.append_bar();`。
//
// 5）为什么测试里 `String::from("Foo").append_bar()` 能直接链式调用？
//    因为返回值是 String，而 String 也实现了 AppendBar，
//    所以可以继续 `.append_bar()`。这叫“方法链（method chaining）”。
//
// 6）如果不想移动原字符串，能不能改成 `&mut self`？
//    能，但那样 trait 签名就变了，测试里的
//    `String::from("Foo").append_bar()` 需要改成
//    `let mut s = String::from("Foo"); s.append_bar(); s`
//    —— 题目要求签名不变，所以不要动。
//
// 7）孤儿规则（orphan rule）小贴士
//    Rust 规定：`impl Trait for Type` 中，Trait 和 Type 至少要有一个是“本 crate 定义的”。
//    本题 trait AppendBar 是自己定义的，所以可以为标准库的 String 实现。
//    如果 trait 和类型都来自标准库，就不允许实现（防止不同库互相冲突）。
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. impl 里函数体空着：
//    → error[E0046]: not all trait items implemented, missing: `append_bar`
//
// 2. 签名写成 `&self`：
//    → error[E0053]: method `append_bar` has an incompatible type for trait
//
// 3. 忘了 mut：
//        fn append_bar(self) -> Self { self.push_str("Bar"); self }
//    → error[E0596]: cannot borrow `self` as mutable, as it is not declared as mutable
//
// 4. 忘记返回 self（最后一行加了分号）：
//        self.push_str("Bar");
//    → error[E0308]: mismatched types, expected `String`, found `()`
//      （函数最后是语句，返回值成了 ()）
//
// 5. 用 `self + "Bar"` 之外的错误拼接方式：
//        self.push("Bar");   // push 只接受单个 char
//    → error[E0308]: mismatched types, expected `char`, found `&str`
//
// 6. 在 main 里调用后继续用旧的 s：
//        let s = String::from("Foo");
//        s.append_bar();
//        println!("{}", s);       // s 已被移动
//    → error[E0382]: borrow of moved value: `s`
//
// 7. 测试文件用普通 rustc 编译（不加 --test）：
//    → 能编译也能跑 main，但测试根本不会执行；
//      要验证测试必须 `rustc --test`。
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. trait 是“行为说明书”，只写方法签名；impl Trait for Type 是“填表交作业”；
//   2. impl 的方法签名必须和 trait 里完全一致（self / &self / &mut self 不能换）；
//   3. `mut self` 只影响函数体内部，不改变签名；
//   4. 按值 self 意味着调用后原变量被移动，需要用返回值接住。
//
// 一句话记忆：**trait 是能力清单，impl 是履行合同；签名照抄，body 自己写。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 --test traits1.rs -o traits1.exe
//   .\traits1.exe
// 【预期输出】
//   running 2 tests
//   test tests::is_bar_bar ... ok
//   test tests::is_foo_bar ... ok
//
//   test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
//
// （想单独看程序输出，也可以用普通方式编译运行：
//    rustc --edition 2021 traits1.rs -o traits1.exe   →  s: FooBar）
// ============================================================================
