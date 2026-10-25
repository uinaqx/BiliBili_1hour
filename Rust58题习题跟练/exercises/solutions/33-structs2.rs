// ============================================================================
// 第 33 题 · structs2 —— 结构体更新语法：在模板上"改几处"
// ----------------------------------------------------------------------------
// 题目类型：test（让 #[test] 测试通过就算过关）
// 课件位置：第 3 章 · 3.3 结构体更新语法 .. 与字段所有权转移
// 难度：★★★☆☆
// 前置知识：structs1（结构体定义与实例化）、move_semantics2（移动与 clone）
// ============================================================================
//
// 【题目要求】
// 已有模板函数 create_order_template() 返回一个标准的 Order。
// 用"结构体更新语法"基于这个模板造出 your_order：
//   - name 改成 "Hacker in Rust"
//   - count 改成 1
//   - 其余字段全部照抄模板
//
// 原题代码（未完成，仅供对照）：
//     #[derive(Debug)]
//     struct Order {
//         name: String,
//         year: u32,
//         made_by_phone: bool,
//         made_by_mobile: bool,
//         made_by_email: bool,
//         item_number: u32,
//         count: u32,
//     }
//
//     fn create_order_template() -> Order {
//         Order {
//             name: String::from("Bob"),
//             year: 2019,
//             made_by_phone: false,
//             made_by_mobile: false,
//             made_by_email: true,
//             item_number: 123,
//             count: 0,
//         }
//     }
//
//     #[test]
//     fn your_order() {
//         let order_template = create_order_template();
//         // let your_order = ...
//         assert_eq!(your_order.name, "Hacker in Rust");
//         assert_eq!(your_order.year, order_template.year);
//         ... 其余字段都要和模板一致，count 要是 1
//     }
//
// 【解题思路】
// 1. Rust 提供"结构体更新语法"：先写要改的字段，最后用 `..模板变量` 表示
//    "剩下的字段都从模板里拿"。
// 2. 本题只需要改两个字段，其余照抄：
//        let your_order = Order {
//            name: String::from("Hacker in Rust"),
//            count: 1,
//            ..order_template
//        };
// 3. `..order_template` 必须放在**最后一行**，而且后面不能有逗号之外的东西。
// 4. 注意：`..` 后面不能写表达式，只能写一个"结构体变量"。
// 5. 注意顺序问题：模板变量要先用（..order_template），再被后面的断言读取。
//
// ============================================================================
//                              知 识 铺 垫
// ============================================================================
//
// ● 结构体更新语法（struct update syntax）
//   语法长这样：
//       let b = 结构体名 {
//           要改的字段: 新值,
//           ..a          // 其余字段从 a 里拿
//       };
//   它相当于"复制 a 的剩余字段过来"，但**不是无脑复制**，
//   而是按 Rust 的所有权规则处理：能复制的复制，不能复制的就"移动"。
//
// ● 字段的"复制"与"移动"
//   - u32、bool 这类简单类型实现了 Copy，所以是"复制"，a 里的值还在；
//   - String 没有实现 Copy，所以是"移动"，a 里的那个字段会被搬走、作废。
//   记忆：**Copy 类型抄一份，非 Copy 类型搬走。**
//
// ● 本题为什么模板还能继续用？
//   因为 `..order_template` 只会处理"你没有显式列出的字段"。
//   本题显式列出了 name 和 count，所以：
//       name  —— 你给了新的 String，模板里的 name 没被动过；
//       count —— 你给了 1，模板里的 count 没被动过；
//       其余 5 个字段（year、三个 bool、item_number）都是 Copy 类型，复制而已。
//   因此 order_template 整体依然完整可用，后面的断言才能读它。
//   反过来，如果 Order 里还有一个 String 字段没被显式赋值，
//   它就会被"移动"出模板，模板就变成"部分被移走"的状态，
//   之后就不能再把 order_template 当成整体来用了（读剩余字段还可以）。
//
// ● String::from("...") 是什么？
//   把字符串字面量（&str）变成拥有所有权的 String。
//   等价写法还有 "...".to_string()。
//   本题字段类型是 String，必须给 String，不能直接给 &str。
//
// ● 为什么字段类型里有 String 就要格外小心？
//   因为 String 管理堆内存，赋值默认是"移动"而不是"复制"。
//   这也是 rustlings 把 structs2 挂在"字段所有权转移"知识点下的原因。
//
// ● #[derive(Debug)] 在这里有什么用？
//   本题其实没有直接打印 Order，但加上没坏处；
//   调试时可以用 {:?} 一次看清所有字段。
//
// ============================================================================
//                              参 考 答 案
// ============================================================================

#[derive(Debug)]
struct Order {
    name: String,
    year: u32,
    made_by_phone: bool,
    made_by_mobile: bool,
    made_by_email: bool,
    item_number: u32,
    count: u32,
}

// 模板工厂：返回一份标准订单
fn create_order_template() -> Order {
    // 这里每个字段都写成"字段名: 值"的完整形式
    Order {
        name: String::from("Bob"), // String 字段，需要堆上的 String
        year: 2019,
        made_by_phone: false,
        made_by_mobile: false,
        made_by_email: true,       // 模板默认走邮件下单
        item_number: 123,
        count: 0,                  // 模板默认数量 0
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn your_order() {
        // 先拿到模板（所有权归 order_template）
        let order_template = create_order_template();

        // 结构体更新语法：
        //   ├─ name: String::from("Hacker in Rust") —— 显式覆盖字段
        //   ├─ count: 1                             —— 显式覆盖字段
        //   └─ ..order_template                     —— 其余字段照抄模板
        //       （year / 三个 bool / item_number 都是 Copy 类型，复制过来即可，
        //         所以 order_template 本身没有被破坏，下面还能继续读它）
        let your_order = Order {
            name: String::from("Hacker in Rust"),
            count: 1,
            ..order_template
        };

        // 下面逐个字段验证：改的两个是新值，其余和模板一致
        assert_eq!(your_order.name, "Hacker in Rust");
        assert_eq!(your_order.year, order_template.year);
        assert_eq!(your_order.made_by_phone, order_template.made_by_phone);
        assert_eq!(your_order.made_by_mobile, order_template.made_by_mobile);
        assert_eq!(your_order.made_by_email, order_template.made_by_email);
        assert_eq!(your_order.item_number, order_template.item_number);
        assert_eq!(your_order.count, 1);
    }
}

// ============================================================================
//                            逐 行 解 析
// ============================================================================
//
// let order_template = create_order_template();
//   └─ 返回的 Order 所有权交给 order_template
//
// Order {
//     name: String::from("Hacker in Rust"),
//     count: 1,
//     ..order_template
// }
//   ├─ 显式字段：name（新 String）、count（1）
//   ├─ ..order_template：把剩余字段从模板拿过来
//   │    ├─ year: u32        → Copy，复制
//   │    ├─ made_by_phone    → Copy，复制
//   │    ├─ made_by_mobile   → Copy，复制
//   │    ├─ made_by_email    → Copy，复制
//   │    └─ item_number: u32 → Copy，复制
//   └─ 结果：your_order 是一个完整的新 Order
//
// assert_eq!(your_order.name, "Hacker in Rust");
//   └─ 注意：&String 和 &str 比较，标准库实现了这种比较，所以能直接写字符串字面量
//
// assert_eq!(your_order.year, order_template.year);
//   └─ u32 是 Copy，读字段不会移动，模板仍然可用
//
// ============================================================================
//               如果模板里也有一个没被覆盖的 String 字段，会怎样？
// ============================================================================
//
// 假设 Order 再加一个字段 note: String，而你的更新语法没有提到它：
//     let your_order = Order {
//         name: String::from("Hacker in Rust"),
//         count: 1,
//         ..order_template      // note 会被"移动"出模板
//     };
//     println!("{:?}", order_template);   // ❌ 整体使用已部分移动的模板
//
// 这时 order_template.note 已经被搬进 your_order，模板处于"部分移动"状态：
//   - 可以用 order_template.year（没被移走的字段）；
//   - 不能把 order_template 当成整体使用（不能打印、不能整体传参）。
// 如果想保留模板，就在更新语法里显式给出 note: order_template.note.clone()，
// 或者干脆先 clone 整个模板：`..order_template.clone()`。
//
// 这就是本题被归到"字段所有权转移"知识点下的原因：
// `..` 不是"复制所有字段"，而是"按所有权规则处理剩余字段"。
//
// ============================================================================
//                          常 见 错 误 与 提 示
// ============================================================================
//
// 1. `..` 写在了前面：
//        Order { ..order_template, count: 1 }
//    → error: base struct expression must be the last field
//    （更新语法的 .. 必须放在最后）
//
// 2. 忘了 .. 直接只写两个字段：
//        Order { name: ..., count: 1 }
//    → error[E0063]: missing fields `year`, `made_by_phone`, ... in initializer
//
// 3. 把 .. 后面的变量写成表达式：
//        ..create_order_template()
//    → error: expected expression, found `.`（.. 后面只能跟一个变量/路径）
//
// 4. name 给了 &str 而不是 String：
//        name: "Hacker in Rust",
//    → error[E0308]: mismatched types（expected `String`, found `&str`）
//    要么 String::from(...)，要么 "...".to_string()。
//
// 5. 先移动模板，再想读模板：
//        let your_order = Order { ..order_template };
//        println!("{:?}", order_template);   // 若还有非 Copy 字段未覆盖就会报错
//    本题因为剩余字段全是 Copy，所以不会出问题，但要理解背后的规则。
//
// 6. 想"偷懒"直接改模板：
//        let mut order_template = ...;
//        order_template.name = String::from("Hacker in Rust");
//    这能通过测试，但题目要练的是"更新语法 .."，不是原地修改。
//
// ============================================================================
//                          小 结
// ============================================================================
//
// 本题你需要记住：
//   1. 结构体更新语法：`结构体名 { 改的字段: 新值, ..旧变量 }`；
//   2. `..旧变量` 必须写在最后一个字段的位置；
//   3. `..` 处理的是"你没显式列出的字段"，按 Copy / 移动规则处理；
//   4. Copy 类型（u32、bool）是复制，String 是移动；
//   5. 模板能否继续整体使用，取决于有没有非 Copy 字段被移走。
//
// 一句话记忆：**先写要改的，最后一句 `..旧模板` 把剩下的照抄过来。**
//
// ============================================================================
// 【运行方式】在本文件所在目录执行：
//   rustc --edition 2021 --test structs2.rs -o structs2.exe
//   .\structs2.exe
// 【预期输出】
//   running 1 test
//   test tests::your_order ... ok
//
//   test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
// ============================================================================
