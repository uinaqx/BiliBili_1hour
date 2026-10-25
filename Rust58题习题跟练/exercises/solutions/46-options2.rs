// ============================================================================
// 第 46 题 · options2 —— if let 与 while let：只关心“有值”的那一种情况
// ----------------------------------------------------------------------------
// 题目类型：test（让 #[test] 测试通过就算过关）
// 课件位置：第 4 章 · 4.3 模式匹配（if let / while let）；第 3 章 · 3.4.3 Option
// 难度：★★★☆☆
// 前置知识：Option 的 Some/None（参考第 45 题 options1）、match、Vec 基础（参考 vecs1）
// ============================================================================
//
// 【题目要求】
// 1. simple_option：把原来写坏的赋值语句改成 `if let` 语句，
//    当 optional_target 是 Some 时，把里面的字符串绑定给 word。
// 2. layered_option：把写坏的循环改成 `while let` 语句，
//    每次从 Vec 尾部弹出一个元素，直到弹不出“有值的整数”为止。
//    （提示：Vec::pop 本身返回 Option<T>，而 T 又是 Option<i8>，所以是两层盒子。）
//
// 原题代码（未完成，仅供对照）：
//     let optional_target = Some(target);
//     word = optional_target {           // ← 这不是合法语法，要改成 if let
//         assert_eq!(word, target);
//     }
//
//     integer = optional_integers.pop() {  // ← 要改成 while let
//         assert_eq!(integer, cursor);
//         cursor -= 1;
//     }
//
// 【解题思路】
// 1. `if let 模式 = 表达式 { 代码块 }` 的意思是：
//    “如果这个值能匹配上左边的模式，就把里面的东西绑到变量上，然后执行代码块；
//      匹配不上就整个跳过。”
//    于是第一题写成：`if let Some(word) = optional_target { ... }`。
// 2. 第二题要“反复弹、反复判断”，所以用 while let：
//    `while let 模式 = 表达式 { ... }` 表示“只要还能匹配上，就一直循环”。
// 3. 关键在模式要写几层 Some：`optional_integers` 里装的是 Option<i8>，
//    `pop()` 又把它包了一层，返回 Option<Option<i8>>：
//        None                 ← Vec 空了，什么都没弹出来
//        Some(None)           ← 弹出了一个“空盒子”
//        Some(Some(7))        ← 弹出了一个“装着 7 的盒子”
//    我们要的是最后一种，所以模式写成 `Some(Some(integer))`。
// 4. 循环结束时 cursor 从 10 一路减到 0，断言 assert_eq!(cursor, 0) 通过。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● if let：只关心一种模式的“精简版 match”
//       if let Some(v) = opt {
//           // 这里能用 v
//       }
//   完全等价于：
//       match opt {
//           Some(v) => { /* 这里能用 v */ }
//           _ => {}                 // 其他情况什么都不做
//       }
//   什么时候用 if let？——当你只在乎“匹配成功”那一种情况，
//   不想为了写全分支而写一堆 `_ => {}` 的时候。
//
// ● while let：循环版的 if let
//       while let Some(v) = stack.pop() {
//           // 每轮拿到一个 v；一旦 pop() 返回 None，循环自动结束
//       }
//   等价于：
//       loop {
//           match stack.pop() {
//               Some(v) => { /* 循环体 */ }
//               None => break,      // 弹不出来就退出
//           }
//       }
//   这是“消费一个容器直到取空”的标准写法，比手写 match + break 清爽得多。
//
// ● 盒子套盒子（嵌套 Option）
//   Option<Option<i8>> 就像“快递柜里放了一个小快递柜”：
//       外层 Some/None 回答“大柜子里有没有小柜子”
//       内层 Some/None 回答“小柜子里有没有东西”
//   要拿到最里面的整数，模式就得写 `Some(Some(x))` 两层。
//   如果用 `Some(x)` 只拆一层，x 的类型就是 Option<i8>，不是 i8。
//
// ● Vec::pop() 是什么？
//   `Vec` 是可变长数组（动态数组）。`pop()` 从**尾部**删掉并返回最后一个元素。
//   因为“空 Vec 弹不出东西”，所以返回值被包成 Option<T>：
//        vec![1,2,3].pop() → Some(3)
//        Vec::<i32>::new().pop() → None
//   本题 Vec 里装的元素类型是 Option<i8>，所以 pop 返回 Option<Option<i8>>。
//
// ● i8 是什么？
//   8 位有符号整数，范围 -128..=127。题目里的 1..=10 完全放得下。
//   注意 `let range = 10;` 的类型会被推断成 i8，
//   因为 `for i in 1..(range + 1)` 里的 i 要 push 进 Vec<Option<i8>>。
//
// ● 为什么循环能正确停下？
//   Vec 初始化时先塞了一个 None，之后 push 了 Some(1) 到 Some(10)。
//   从尾部弹出顺序是 Some(Some(10))、Some(Some(9)) …… Some(Some(1))，
//   最后弹出 Some(None) —— 内层是 None，匹配不上 `Some(Some(integer))`，
//   循环到此结束，此时 cursor 正好减到 0。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

#[cfg(test)]
mod tests {
    #[test]
    fn simple_option() {
        // target 是 &str（字符串字面量），指向程序里的只读数据
        let target = "rustlings";
        // Some(target) 把 &str 装进 Option，类型是 Option<&str>
        let optional_target = Some(target);

        // if let：只处理“有值”的情况
        //   `Some(word)` 是模式，word 是新绑定的变量，类型 &str
        //   `= optional_target` 是被匹配的值
        if let Some(word) = optional_target {
            // 这里 word 已经拿到盒子里的 &str，可以直接和 target 比较
            assert_eq!(word, target);
        }
        // 如果 optional_target 是 None，上面的代码块会被整体跳过，不会报错
    }

    #[test]
    fn layered_option() {
        // 10 是循环上界；它的类型稍后被推断为 i8
        let range = 10;
        // 一个装着 Option<i8> 的动态数组，先放一个“空盒子” None 进去
        let mut optional_integers: Vec<Option<i8>> = vec![None];

        // 1..(range + 1) 是左闭右开区间：1,2,...,10
        // 每轮把 Some(i) push 到数组尾部
        for i in 1..(range + 1) {
            optional_integers.push(Some(i));
        }

        // cursor 是“期待弹出的数字”，开始时是 10
        let mut cursor = range;

        // while let：只要还能匹配上 `Some(Some(integer))` 就继续循环
        //   外层 Some  ← pop() 成功弹出一个元素
        //   内层 Some  ← 这个元素本身是“有值的盒子”
        //   integer    ← 最里面真正的 i8
        // 一旦弹出 Some(None) 或 None，模式不匹配，循环结束
        while let Some(Some(integer)) = optional_integers.pop() {
            // 弹出的数字应该正好等于 cursor（10、9、8 ……）
            assert_eq!(integer, cursor);
            // 期待值减 1，进入下一轮
            cursor -= 1;
        }

        // 循环跑了 10 轮，cursor 从 10 减到 0
        assert_eq!(cursor, 0);
    }
}

// ============================================================================
//                            详 细 解 析
// ============================================================================
//
// 1）为什么 simple_option 里不需要 mut？
//    if let 只是“读” optional_target（准确说是把它按值匹配），
//    没有修改它，所以不用 mut。
//    注意：`Option<&str>` 里的 &str 是 Copy 的，所以这里按值匹配也没问题。
//
// 2）`if let Some(word) = optional_target` 里的 word 从哪来？
//    这叫“模式绑定”：匹配成功时，Rust 把 Some 里的值“拆出来”并绑定到 word。
//    这个 word 只在 if let 的 { } 内部有效，出了花括号就消失（作用域结束）。
//
// 3）为什么写 `Some(Some(integer))`，而不是 `Some(integer)`？
//    因为 pop() 的返回类型是 Option<Option<i8>>：
//      第 1 个 Some 来自 pop()（能不能弹出东西）
//      第 2 个 Some 来自元素自身的类型 Option<i8>（这个元素有没有值）
//    如果只写 `Some(integer)`，integer 的类型就是 Option<i8>，
//    接下来 `assert_eq!(integer, cursor)` 会拿 Option<i8> 和 i8 比较，
//    直接类型不匹配，编译失败。
//
// 4）循环的退出条件到底是什么？
//    弹出顺序：Some(Some(10)) → ... → Some(Some(1)) → Some(None) → 循环结束。
//    注意不是因为“Vec 空了”才结束（Vec 里确实空了，但最后那次弹出返回的是
//    Some(None) 而不是 None）。两个退出路径都写对了：
//      - 空 Vec：pop() 返回 None，不匹配；
//      - 弹出的元素本身是 None：返回 Some(None)，也不匹配。
//    所以这个 while let 对两种情况都安全。
//
// 5）如果非要用 match 写，长什么样？
//       loop {
//           match optional_integers.pop() {
//               Some(Some(integer)) => {
//                   assert_eq!(integer, cursor);
//                   cursor -= 1;
//               }
//               _ => break,
//           }
//       }
//    对比一下就能体会到 while let 省掉了多少样板代码。
//
// 6）另一个等价写法：Option::flatten()
//    `optional_integers.pop().flatten()` 会把 Option<Option<i8>> 压成 Option<i8>，
//    这时模式写 `while let Some(integer) = ...` 就够了。
//    （flatten 属于标准库进阶 API，了解即可，本题不需要。）
//
// 7）这两段代码在 rustlings 里为什么必须用 --test 编译？
//    因为整个文件只有 `#[cfg(test)] mod tests`，没有 fn main。
//    `#[cfg(test)]` 表示“只有在测试模式下才编译这个模块”，
//    而 `rustc --test` 会打开测试模式并生成测试运行器。
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. 忘了 if let 的 `let`：
//        if Some(word) = optional_target { ... }
//    → error: expected `{`, found `=`
//      （if let 是固定搭配，`let` 不能省）
//
// 2. 模式只拆一层：
//        while let Some(integer) = optional_integers.pop()
//    → error[E0308]: mismatched types
//      expected `i8`, found `Option<i8>`
//
// 3. 把 while let 写成 if let：
//    → 只弹出一个元素（10），cursor 变成 9，
//      assert_eq!(cursor, 0) 失败：test tests::layered_option ... FAILED
//
// 4. 忘了把 Vec 声明成 mut：
//        let optional_integers: Vec<Option<i8>> = vec![None];
//    → error[E0596]: cannot borrow `optional_integers` as mutable,
//      as it is not declared as mutable
//      （push 和 pop 都要修改 Vec，必须 mut）
//
// 5. cursor 忘了减 1：
//    → 第二轮就 assert_eq!(9, 10) 失败
//
// 6. 以为 `while let` 会在模式不匹配时报错：
//    不会。模式不匹配只是“循环正常结束”，这正是 while let 的设计目的。
//
// 7. 在 if let 的花括号外面使用 word：
//    → error[E0425]: cannot find value `word` in this scope
//      （模式绑定的变量只活在代码块内部）
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. `if let 模式 = 值 { ... }` 只处理匹配成功的那一种情况，是 match 的简化版；
//   2. `while let 模式 = 值 { ... }` 反复取值直到模式匹配失败，是“取空容器”的标准写法；
//   3. Option 可以嵌套，Option<Option<T>> 需要 `Some(Some(x))` 两层模式来拆；
//   4. Vec::pop() 返回 Option<T>，空的时候是 None，所以特别适合配 while let。
//
// 一句话记忆：**if let 管一次，while let 管到底；盒子有几层，Some 就写几个。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 --test options2.rs -o options2.exe
//   .\options2.exe
// 【预期输出】
//   running 2 tests
//   test tests::layered_option ... ok
//   test tests::simple_option ... ok
//
//   test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
// ============================================================================
