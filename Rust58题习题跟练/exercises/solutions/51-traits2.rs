// ============================================================================
// 第 51 题 · traits2 —— 为 Vec<String> 实现 trait：把 "Bar" 塞进向量
// ----------------------------------------------------------------------------
// 题目类型：test（让 #[test] 测试通过就算过关）
// 课件位置：第 5 章 · 5.3 特征（为具体类型实现 trait，self 的所有权）
// 难度：★★★☆☆
// 前置知识：第 50 题 traits1（trait 与 impl）、Vec 基础（vecs1）、String（strings1）
// ============================================================================
//
// 【题目要求】
// 为“字符串向量” `Vec<String>` 实现 AppendBar：
// 往向量末尾追加一个内容为 "Bar" 的 String，然后返回这个向量。
// 测试要求：
//     vec![String::from("Foo")].append_bar()
//     之后先 pop 出 "Bar"，再 pop 出 "Foo"
// 也就是说 "Bar" 必须在**末尾**。
//
// 原题代码（未完成，仅供对照）：
//     trait AppendBar {
//         fn append_bar(self) -> Self;
//     }
//
//     // TODO: Implement trait `AppendBar` for a vector of strings.
//     （这里什么都没有）
//
// 编译器会报（测试调用不到方法）：
//     error[E0599]: no method named `append_bar` found for struct `Vec<String>`
//
// 【解题思路】
// 1. 先想清楚“给一个字符串向量追加 Bar”是什么意思：
//    向量里装的是 String，不是 &str。所以推入的必须是
//    `String` 类型的值，最直接的写法是 `String::from("Bar")`。
//    （写 `self.push("Bar")` 会类型不匹配，因为 push 要的是 String，不是 &str。）
// 2. 再照抄 trait 的签名：`fn append_bar(self) -> Self`，
//    Self 在这里就是 `Vec<String>`。
// 3. 因为要调用 push 修改向量，self 必须可变 → 写成 `mut self`。
// 4. 返回 self（最后一行不加分号），就完成了。
// 5. 测试验证的是“顺序”：pop 从**尾部**弹出，
//    先弹出 "Bar" 说明 Bar 在末尾，再弹出 "Foo" 说明原来的元素还在前面。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● impl Trait for 一个“带参数的类型”，怎么写？
//   上一题是 `impl AppendBar for String`，类型名是光秃秃的 String。
//   本题是 `impl AppendBar for Vec<String>`：
//   把 `Vec<String>` 整体当成“一个类型”写上去即可。
//   （Vec<String> 是 Vec<T> 把 T 填成 String 之后的具体类型。）
//   注意：这**不是**泛型 impl。如果写成 `impl AppendBar for Vec<T>`，
//   那就变成“给所有 Vec<T> 实现”，需要 `impl<T> AppendBar for Vec<T>`，
//   而且 T 上还得加约束（因为 push 需要类型匹配）。本题只需要 String 版本。
//
// ● Vec<String> 是什么？
//   Vec 是动态数组（堆上、可增长）。Vec<String> 表示每个元素都是 String。
//   创建方式：`vec![String::from("Foo")]`（vec! 宏）。
//   常用操作：
//       v.push(x)      在末尾追加（需要 &mut v）
//       v.pop()        从末尾弹出，返回 Option<T>（空向量返回 None）
//       v.len()        元素个数
//       v[0]           下标访问（越界会 panic）
//
// ● push 要什么类型？
//   对 `Vec<String>` 来说，push 的签名是 `fn push(&mut self, value: String)`。
//   所以必须传 String：
//       v.push(String::from("Bar"));   ✅
//       v.push("Bar");                 ❌ expected `String`, found `&str`
//       v.push("Bar".to_string());     ✅（to_string 把 &str 转成 String）
//
// ● 为什么 trait 规定的是 `self`（按值），不是 `&mut self`？
//   `self` 版本：把整个向量拿过来，改完再还给你。调用后原变量被移动。
//   `&mut self` 版本：原地修改，不转移所有权。
//   两种都合理，但 trait 已经定死成 `self` 了，我们只能照抄。
//   而且从测试写法 `vec![...].append_bar()` 看，它是对“临时值”调用，
//   临时值没有名字，没法借用给 &mut self —— 这也说明按值更合适。
//
// ● 为什么返回值类型 Self 能对上？
//   Self = Vec<String>，函数体最后的 `self` 也是 Vec<String>，类型一致。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

// trait 定义（与上一题相同）：追加 Bar 的能力
trait AppendBar {
    // 按值接收 self，返回同类型的新值
    fn append_bar(self) -> Self;
}

// 为具体类型 Vec<String> 实现 AppendBar
// 注意：`Vec<String>` 整体就是类型名，不需要再写 <T>
impl AppendBar for Vec<String> {
    // mut self：允许函数体内部修改这个向量（push 需要可变权限）
    fn append_bar(mut self) -> Self {
        // 向向量末尾追加一个元素
        // 元素类型必须是 String，所以用 String::from("Bar") 构造
        self.push(String::from("Bar"));

        // 返回修改后的向量（最后一行不加分号 = 返回值）
        self
    }
}

#[cfg(test)]
mod tests {
    // 引入父模块的 trait 与 impl
    use super::*;

    #[test]
    fn is_vec_pop_eq_bar() {
        // vec![String::from("Foo")] 创建一个只含 "Foo" 的向量，
        // 立刻调用 append_bar()，得到 ["Foo", "Bar"]
        let mut foo = vec![String::from("Foo")].append_bar();

        // pop() 从末尾弹出：第一个弹出来的是 "Bar"
        // unwrap() 把 Option<String> 打开（这里一定有值）
        assert_eq!(foo.pop().unwrap(), String::from("Bar"));

        // 再弹一次，得到原来的 "Foo"
        assert_eq!(foo.pop().unwrap(), String::from("Foo"));
    }
}

// ============================================================================
//                            详 细 解 析
// ============================================================================
//
// 1）测试为什么先断言 "Bar" 再断言 "Foo"？
//    因为 pop() 是“后进先出”（栈式）：
//        ["Foo", "Bar"]  →  pop → "Bar"（剩 ["Foo"]）
//                        →  pop → "Foo"（剩 []）
//    如果实现成了 `self.insert(0, ...)`（插到开头），
//    第一次 pop 会得到 "Foo"，断言失败。
//
// 2）`let mut foo = ...` 里的 mut 是给谁用的？
//    是给测试里的 `foo.pop()` 用的 —— pop 需要 &mut foo。
//    它和 impl 里的 `mut self` 是两回事，只是碰巧都需要 mut。
//
// 3）为什么 `vec![String::from("Foo")].append_bar()` 能直接调用？
//    因为临时值也是一个完整的 Vec<String>，按值传入正好把它移动进去。
//    如果 trait 方法要求 &mut self，就必须先 `let mut v = vec![...];`，
//    因为不能对临时值取可变引用并长期使用。
//
// 4）这个 impl 能用于 `Vec<&str>` 吗？
//    不能。`impl AppendBar for Vec<String>` 只覆盖“元素为 String 的向量”。
//    `Vec<&str>` 是另一个完全不同的类型，需要单独 impl。
//    如果想让所有 `Vec<T>` 都能追加，可以写：
//        impl<T> AppendBar for Vec<T> { fn append_bar(mut self) -> Self { ... } }
//    但那样就没法 push "Bar"（T 不一定是 String），
//    除非给 T 加约束，比如 `T: From<&'static str>`，那就复杂了。
//
// 5）如果把 `self.push(...)` 写成 `self.push("Bar")` 会怎样？
//    → error[E0308]: mismatched types
//      expected `String`, found `&str`
//    Rust 不会自动把 &str 转成 String（它反对隐式分配），
//    必须显式写 `.to_string()`、`String::from(...)` 或 `.into()`。
//
// 6）能不能不返回 self，直接返回 ()？
//    不能，签名写的是 `-> Self`。少了返回值会报
//    error[E0308]: mismatched types，expected `Vec<String>`, found `()`。
//
// 7）这个 impl 里 `self` 被移动了吗？
//    是的。调用 `v.append_bar()` 之后，原来的 v 就被移进函数，
//    函数把（可能扩容过的）向量返回出来，需要用变量接住。
//    所以 `v.append_bar();` 不加接收会让这个向量被直接丢弃。
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. impl 写成泛型却没有约束：
//        impl<T> AppendBar for Vec<T> { self.push("Bar"); ... }
//    → error[E0308]: mismatched types（T 不一定是 String）
//
// 2. push 传 &str：
//        self.push("Bar");
//    → error[E0308]: expected `String`, found `&str`
//
// 3. 忘了 mut：
//        fn append_bar(self) -> Self { self.push(...); self }
//    → error[E0596]: cannot borrow `self` as mutable
//
// 4. 追加到了开头：
//        self.insert(0, String::from("Bar"));
//    → 编译能过，但测试 FAILED（pop 出来先遇到 "Foo"）
//
// 5. 返回 ()（忘记 self）：
//    → error[E0308]: mismatched types, expected `Vec<String>`, found `()`
//
// 6. 在 impl 里重新定义了一遍 trait 方法之外的东西（比如又写了一次 trait AppendBar）：
//    → error[E0428]: the name `AppendBar` is defined multiple times
//
// 7. 忘记 `use super::*;`（如果测试模块里删掉了）：
//    → error[E0599]: no method named `append_bar` found
//      （方法存在，但 trait 不在作用域里，方法就“看不见”）
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. `impl Trait for Vec<String>` 就是为一个“填好参数的具体类型”实现 trait；
//   2. 元素类型是 String 时，push 必须传 String，&str 不会自动转换；
//   3. trait 要求 `self` 时，impl 里也只能是 `self`（可加 mut 修饰）；
//   4. 按值 self 的写法 = “拿走 → 修改 → 还回”，返回值必须用变量接住。
//
// 一句话记忆：**给 Vec<String> 加能力，推入的必须是 String；pop 是后进先出，Bar 得放末尾。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 --test traits2.rs -o traits2.exe
//   .\traits2.exe
// 【预期输出】
//   running 1 test
//   test tests::is_vec_pop_eq_bar ... ok
//
//   test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
// ============================================================================
