// ============================================================================
// 第 40 题 · strings3 —— 字符串常用操作：trim / format! / replace
// ----------------------------------------------------------------------------
// 题目类型：test（让三个 #[test] 全部通过就算过关）
// 课件位置：第 3 章 · 3.1 字符串常用方法（trim、push_str、format!、replace）
// 难度：★★☆☆☆
// 前置知识：strings1、strings2（String 与 &str、借用）、函数返回值（functions5）
// ============================================================================
//
// 【题目要求】
// 补全三个函数的小问号，使下面的测试全部通过：
//   trim_me("Hello!     ")        == "Hello!"
//   compose_me("Hello")           == "Hello world!"
//   replace_me("I think cars ...") == "I think balloons ..."
// 函数签名不要改，测试代码不要改。
//
// 原题代码（未完成，仅供对照）：
//     fn trim_me(input: &str) -> String {
//         // TODO: Remove whitespace from both ends of a string!
//         ???
//     }
//
//     fn compose_me(input: &str) -> String {
//         // TODO: Add " world!" to the string! There's multiple ways to do this!
//         ???
//     }
//
//     fn replace_me(input: &str) -> String {
//         // TODO: Replace "cars" in the string with "balloons"!
//         ???
//     }
//
// 【解题思路】
// 1. 看函数签名：参数是 `&str`（借来的文本），返回值是 `String`（自己拥有的新文本）。
//    所以每个函数都要“读 input，造一个新的 String 还回去”。
// 2. trim_me：去掉首尾空白。标准库方法 `str::trim()` 正好干这个，
//    但它返回的是原文本的一段借用（&str），所以还要 `.to_string()` 变成 String。
// 3. compose_me：在末尾追加 " world!"。最方便的是 `format!("{} world!", input)`，
//    它像 println! 一样拼接，但结果不是打印，而是返回一个 String。
// 4. replace_me：把 "cars" 全部换成 "balloons"。标准库方法 `str::replace(旧, 新)`
//    会返回一个新的 String，直接返回即可。
// 5. 每个函数体最后一行不加分号，它的值就是返回值。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● 三个函数共同点：输入是借用，输出是新建
//   `input: &str` 只是“看一眼”调用方的文本，不能修改它，也不需要复制它。
//   要返回 String，就必须新建一块堆内存，把结果放进去。
//
// ● trim：去掉首尾的空白字符
//   空白包括空格、制表符 \t、换行 \n 等。
//   - `"  hi  ".trim()`       → "hi"
//   - `"  hi  ".trim_start()` → "hi  "（只去开头）
//   - `"  hi  ".trim_end()`   → "  hi"（只去结尾）
//   trim 返回 &str，是原字符串的一段“视图”，不会复制文本。
//   所以如果函数要 String，还得 `.to_string()`（或 `.to_owned()`）。
//
// ● format!：拼接字符串并返回 String
//   `format!("{} world!", input)` 的用法和 println! 几乎一样，
//   区别是 println! 把结果打印到屏幕，format! 把结果作为 String 返回。
//   它不会修改 input，而是新建一个 String。
//   其他等价写法：
//       let mut s = input.to_string();
//       s.push_str(" world!");
//       s
//   这种写法先用 to_string 复制一份，再用 push_str 在末尾追加。
//
// ● replace：替换所有匹配的子串
//   `input.replace("cars", "balloons")` 会把 input 里**所有** "cars" 换成 "balloons"，
//   返回一个全新的 String（原字符串不变）。
//   如果只想替换第一次出现，用 `replacen(旧, 新, 1)`。
//
// ● 方法链（method chaining）
//   `input.trim().to_string()` 是从左到右依次调用：
//   先 trim 得到 &str，再对它调用 to_string 得到 String。
//   每一步的返回值就是下一步的调用者，读的时候从左往右看即可。
//
// ● 为什么 `assert_eq!(String, &str)` 也能比较？
//   标准库为 String 实现了与 &str 的比较（PartialEq<&str>），
//   比较的是文本内容而不是类型。所以断言里左边是 String、右边是字面量没问题。
//
// ● `#[cfg(test)]` 与 `--test`
//   本题没有 main，只有测试模块。必须用 `rustc --test` 编译，
//   生成的可执行文件会自动运行所有 #[test] 函数。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

fn trim_me(input: &str) -> String {
    // trim()：去掉首尾空白，返回 &str（原文本的一段视图）
    // to_string()：把这段视图复制成新的 String，满足返回类型
    input.trim().to_string()
}

fn compose_me(input: &str) -> String {
    // format!：按格式拼出新字符串并返回 String。
    // {} 会被 input 替换，得到 "原内容 world!"
    format!("{} world!", input)

    // 等价写法（可以对比理解）：
    // let mut s = input.to_string();  // 先复制一份可变的 String
    // s.push_str(" world!");          // 在末尾追加
    // s                               // 最后一行作为返回值
}

fn replace_me(input: &str) -> String {
    // replace(旧, 新)：把所有 "cars" 换成 "balloons"，返回新 String
    input.replace("cars", "balloons")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn trim_a_string() {
        assert_eq!(trim_me("Hello!     "), "Hello!");
        assert_eq!(trim_me("  What's up!"), "What's up!");
        assert_eq!(trim_me("   Hola!  "), "Hola!");
    }

    #[test]
    fn compose_a_string() {
        assert_eq!(compose_me("Hello"), "Hello world!");
        assert_eq!(compose_me("Goodbye"), "Goodbye world!");
    }

    #[test]
    fn replace_a_string() {
        assert_eq!(replace_me("I think cars are cool"), "I think balloons are cool");
        assert_eq!(replace_me("I love to look at cars"), "I love to look at balloons");
    }
}

// ============================================================================
//                            详 细 解 析
// ============================================================================
//
// 1）trim_me 为什么不能只写 `input.trim()`？
//    因为函数声明返回 String，而 trim 返回 &str。类型不匹配：
//        expected `String`, found `&str`
//    Rust 不会自动分配内存，所以必须显式 to_string()（或 to_owned()）。
//
// 2）trim 会改掉原来的字符串吗？
//    不会。`input` 是 &str（不可变借用），trim 只是算出“从第几个字节到第几个字节”
//    是有效内容，返回一个新的 &str 视图。原文本一个字节都没动。
//
// 3）compose_me 的 format! 与 `input + " world!"` 有什么区别？
//    `input + " world!"` 要求左边是 String（而且 + 会消耗左边），不能直接对 &str 用。
//    写成 `input.to_string() + " world!"` 才可以。
//    format! 不消耗任何参数，可读性也更好，是拼接多个片段时的首选。
//
// 4）compose_me 的等价写法里，为什么 push_str 前面要 to_string()？
//    push_str 是 String 的方法，会修改自己；而 input 是 &str，既不能改、也不是 String。
//    先 to_string() 复制出一份拥有所有权的可变字符串，才能往里追加内容。
//
// 5）replace_me 会替换所有出现的位置吗？
//    会。测试里每条只出现一次 "cars"，所以看不出差别；
//    如果有 "cars cars"，两个都会变成 "balloons"。
//    只替换一次要用 replacen("cars", "balloons", 1)。
//
// 6）三个函数的返回值都需要新分配内存吗？
//    需要。返回类型是 String，而输入只是借用，函数不能把借来的东西当自己的返回
//    （那会变成悬垂引用）。所以必须新建 String，把结果复制进去。
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. trim_me 只写 `input.trim()`：
//    → error[E0308]: mismatched types，expected `String`, found `&str`
//
// 2. compose_me 写 `input + " world!"`：
//    → error[E0369]: cannot add `&str` to `&str`
//    （+ 左边必须是 String）
//
// 3. compose_me 写成 `format!("{} world!")` 漏了参数：
//    → error: 1 positional argument in format string, but no arguments were given
//
// 4. compose_me 写成 `println!("{} world!", input)`：
//    能编译（返回 ()），但类型不匹配 → expected `String`, found `()`
//
// 5. replace_me 写 `input.replace("cars")`（少一个参数）：
//    → error[E0061]: this method takes 2 arguments but 1 argument was supplied
//
// 6. replace_me 写 `input.replace("cars", "balloons");` 加了分号：
//    → 函数返回 ()，expected `String`, found `()`
//
// 7. 把参数改成 `input: String`：
//    会与测试里的 `trim_me("Hello!     ")`（字面量是 &str）冲突，
//    → error[E0308]: expected `String`, found `&str`
//
// 8. 用 rustc 编译时忘记 --test：
//    → error[E0601]: `main` function not found in crate
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. `trim()` 去首尾空白，返回 &str；要 String 就 `.to_string()`；
//   2. `format!("...{}...", x)` 拼接并返回 String，不修改参数；
//   3. `replace(旧, 新)` 替换所有匹配，返回新 String；
//   4. &str 是只读借用，想修改或返回，先转成 String；
//   5. 函数最后一行不加分号，它的值就是返回值。
//
// 一句话记忆：**输入借来看，输出造新的；要改先 to_string，要拼用 format!。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 --test strings3.rs -o strings3.exe
//   .\strings3.exe
// 【预期输出】
//   running 3 tests
//   test tests::compose_a_string ... ok
//   test tests::replace_a_string ... ok
//   test tests::trim_a_string ... ok
//
//   test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out;
// ============================================================================
